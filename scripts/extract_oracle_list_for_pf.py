#!/usr/bin/env python3
"""
Batch Oracle Zero-Reuse List Extractor for ChampSim with Prefetching.

Extracts ground-truth pure zero-reuse demand cache block addresses from ChampSim
simulation output logs and generates oracle zero-reuse files for bypassing.

Exact Selection Criteria:
  1. The address MUST have been brought into L1D by a DEMAND request at least once.
  2. The address MUST have had REUSE == 0 on every demand fill throughout the simulation.
  3. The address MUST have had REUSE == 0 on every prefetch fill throughout the simulation.
  4. If an address was EVER reused (REUSE > 0) under EITHER demand OR prefetch, it is EXCLUDED.
  5. Addresses brought ONLY by prefetch (with 0 reuse) and never by demand are EXCLUDED.

Result:
  Only addresses that were demand-accessed, had zero reuse, and never received a single hit
  across their entire lifetime (neither by demand nor by prefetcher) are included.
"""

import os
import sys
import time
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

DEFAULT_INPUT_DIR = "../results_bingo/testing_mlp_warmup/pref_l1/bingo_dpc3/exp14_srrip_mockingjay"
DEFAULT_OUTPUT_DIR = "../oracle_lists_pref_warmup_2S"


def clean_trace_name(filepath):
    """Extract clean trace name from filepath."""
    fname = os.path.basename(filepath)
    for ext in [".champsimtrace.gz", ".champsimtrace.xz", ".gz", ".xz", ".out"]:
        if fname.endswith(ext):
            fname = fname[:-len(ext)]
    return fname


def detect_log_address_mode(input_log):
    """
    Inspects first few L1D Demand lines to determine address format.
    Returns: 'direct', 'legacy_trailing_6', or 'byte_addr'
    """
    sample_addrs = []
    try:
        with open(input_log, 'r', errors='ignore') as f:
            for line in f:
                if "L1D" in line and "DEMAND" in line.upper() and "ADDRESS:" in line:
                    parts = line.strip().split()
                    for i, p in enumerate(parts):
                        if p == "ADDRESS:" and i + 1 < len(parts):
                            sample_addrs.append(parts[i + 1])
                            break
                    if len(sample_addrs) >= 50:
                        break
    except Exception:
        pass

    if not sample_addrs:
        return "direct"

    trailing_6_count = sum(
        1 for a in sample_addrs
        if a.startswith("0x") and a.endswith("6") and len(a) >= 13
    )
    if (trailing_6_count / len(sample_addrs)) > 0.8:
        return "legacy_trailing_6"
    return "direct"


def parse_address(addr_str, mode):
    """Convert raw address string to block address integer based on mode."""
    if mode == "legacy_trailing_6":
        stripped = addr_str[:-1] if (
            addr_str.startswith("0x") and addr_str.endswith("6") and len(addr_str) > 3
        ) else addr_str
        return int(stripped, 16) >> 6
    elif mode == "byte_addr":
        return int(addr_str, 16) >> 6
    else:  # direct block address
        return int(addr_str, 16)


def process_single_trace(input_log, output_dir=DEFAULT_OUTPUT_DIR, prefix="oracle_zero_reuse_", overwrite=False, mode="auto"):
    """
    Extracts pure zero-reuse demand addresses from a single trace output log.

    Rules:
      - demand_zero_addrs: block addresses evicted as DEMAND with REUSE == 0
      - ever_reused_addrs: block addresses evicted with REUSE > 0 from ANY fill (DEMAND or PREFETCH)
      - pure_zero = demand_zero_addrs - ever_reused_addrs
    """
    trace_name = clean_trace_name(input_log)
    output_file = os.path.join(output_dir, f"{prefix}{trace_name}.txt")

    if not overwrite and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        return {
            "trace": trace_name,
            "status": "SKIPPED",
            "message": f"File already exists: {output_file}",
            "pure_count": -1,
            "demand_zero_count": -1,
            "removed_by_reuse": -1,
            "prefetch_only_count": -1,
            "total_demand_lines": -1,
            "total_prefetch_lines": -1,
            "elapsed": 0.0
        }

    # Determine parsing mode
    active_mode = mode
    if active_mode == "auto":
        active_mode = detect_log_address_mode(input_log)

    demand_zero_addrs = set()    # Seen as DEMAND with REUSE == 0
    ever_reused_addrs = set()    # Seen with REUSE > 0 (DEMAND or PREFETCH)
    prefetch_only_zero = set()   # Seen as PREFETCH with REUSE == 0

    total_demand_lines   = 0
    total_prefetch_lines = 0

    start_t = time.time()
    try:
        with open(input_log, 'r', errors='ignore') as f:
            for line in f:
                if "L1D" not in line or "REUSE:" not in line or "ADDRESS:" not in line:
                    continue

                is_demand   = "DEMAND"   in line.upper() and "PREFETCH" not in line.upper()
                is_prefetch = "PREFETCH" in line.upper()

                if not is_demand and not is_prefetch:
                    continue

                # Parse address and reuse value
                parts = line.strip().split()
                addr_str  = None
                reuse_val = None
                for i, p in enumerate(parts):
                    if p == "ADDRESS:" and i + 1 < len(parts):
                        addr_str = parts[i + 1]
                    elif p == "REUSE:" and i + 1 < len(parts):
                        try:
                            reuse_val = int(parts[i + 1])
                        except ValueError:
                            pass

                if addr_str is None or reuse_val is None:
                    continue

                try:
                    block_addr = parse_address(addr_str, active_mode)
                except ValueError:
                    continue

                if is_demand:
                    total_demand_lines += 1
                    if reuse_val == 0:
                        demand_zero_addrs.add(block_addr)
                    else:
                        ever_reused_addrs.add(block_addr)

                elif is_prefetch:
                    total_prefetch_lines += 1
                    if reuse_val > 0:
                        # Reused when prefetched -> strictly exclude from bypass
                        ever_reused_addrs.add(block_addr)
                    else:
                        prefetch_only_zero.add(block_addr)

        if total_demand_lines == 0:
            return {
                "trace": trace_name,
                "status": "WARNING",
                "message": f"No L1D Demand eviction records found in {input_log}",
                "pure_count": 0,
                "demand_zero_count": 0,
                "removed_by_reuse": 0,
                "prefetch_only_count": 0,
                "total_demand_lines": 0,
                "total_prefetch_lines": total_prefetch_lines,
                "elapsed": time.time() - start_t
            }

        # 1. Addresses that were demand-fetched with 0 reuse AND never reused under any fill
        pure_zero_addrs = demand_zero_addrs - ever_reused_addrs
        removed_count = len(demand_zero_addrs & ever_reused_addrs)

        # 2. Addresses that were prefetched with 0 reuse, but never brought by demand
        # (These are correctly excluded from pure_zero_addrs because they never entered demand_zero_addrs)
        pref_only_zero_count = len((prefetch_only_zero - demand_zero_addrs) - ever_reused_addrs)

        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'w') as out:
            for b in sorted(pure_zero_addrs):
                out.write(f"0x{b:x}\n")

        elapsed = time.time() - start_t
        return {
            "trace": trace_name,
            "status": "SUCCESS",
            "message": f"Saved {len(pure_zero_addrs):,} addresses -> {output_file}",
            "pure_count": len(pure_zero_addrs),
            "demand_zero_count": len(demand_zero_addrs),
            "removed_by_reuse": removed_count,
            "prefetch_only_count": pref_only_zero_count,
            "total_demand_lines": total_demand_lines,
            "total_prefetch_lines": total_prefetch_lines,
            "output_file": output_file,
            "elapsed": elapsed
        }

    except Exception as e:
        return {
            "trace": trace_name,
            "status": "ERROR",
            "message": str(e),
            "pure_count": 0,
            "demand_zero_count": 0,
            "removed_by_reuse": 0,
            "prefetch_only_count": 0,
            "total_demand_lines": 0,
            "total_prefetch_lines": 0,
            "elapsed": time.time() - start_t
        }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract pure zero-reuse demand cache block addresses for ChampSim.\n"
            "Only chooses addresses that were brought by demand, never reused under demand,\n"
            "and never reused under prefetch. Excludes prefetch-only 0-reuse lines."
        )
    )
    parser.add_argument(
        "files", nargs="*",
        help="Optional specific trace log file(s) to process"
    )
    parser.add_argument(
        "--dir", default=DEFAULT_INPUT_DIR,
        help=f"Directory containing trace logs (default: {DEFAULT_INPUT_DIR})"
    )
    parser.add_argument(
        "--out-dir", default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--prefix", default="oracle_zero_reuse_",
        help="Filename prefix for output files (default: 'oracle_zero_reuse_', matching ChampSim main.cc)"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "direct", "legacy_trailing_6", "byte_addr"],
        default="auto",
        help="Address parsing mode (default: auto)"
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help="Number of parallel worker processes (default: 8)"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing oracle list files"
    )
    args = parser.parse_args()

    files_to_process = []
    if args.files:
        files_to_process = [f for f in args.files if os.path.isfile(f)]
    elif os.path.isdir(args.dir):
        files_to_process = [
            os.path.join(args.dir, f)
            for f in sorted(os.listdir(args.dir))
            if os.path.isfile(os.path.join(args.dir, f)) and not f.startswith(".")
        ]

    if not files_to_process:
        print(f"❌ Error: No log files found to process in '{args.dir}'.")
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)

    print("=" * 105)
    print("🎯 Oracle Zero-Reuse Address Extractor (Demand-Brought & Never Reused)")
    print(f"   Input Files:       {len(files_to_process)}")
    print(f"   Output Directory:  {os.path.abspath(args.out_dir)}/{args.prefix}<trace>.txt")
    print(f"   Address Mode:      {args.mode}")
    print(f"   Workers:           {args.workers}")
    print(f"   Overwrite:         {args.overwrite}")
    print("=" * 105)
    print(f"  {'Trace':<42} {'Status':<8} {'PureZero':>10} {'DemandZero':>12} {'RemovedReuse':>14} {'PrefOnly(0)':>12} {'Time':>6}")
    print("-" * 105)

    start_all = time.time()
    results = []

    if len(files_to_process) == 1 or args.workers == 1:
        for f in files_to_process:
            res = process_single_trace(
                f, output_dir=args.out_dir, prefix=args.prefix,
                overwrite=args.overwrite, mode=args.mode
            )
            results.append(res)
            _print_row(res)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_file = {
                executor.submit(
                    process_single_trace, f, args.out_dir, args.prefix, args.overwrite, args.mode
                ): f
                for f in files_to_process
            }
            for future in as_completed(future_to_file):
                res = future.result()
                results.append(res)
                _print_row(res)

    total_time = time.time() - start_all
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    skipped_count = sum(1 for r in results if r["status"] == "SKIPPED")

    total_pure     = sum(r["pure_count"] for r in results if r["pure_count"] >= 0)
    total_dem_0    = sum(r.get("demand_zero_count", 0) for r in results if r["status"] == "SUCCESS")
    total_removed  = sum(r.get("removed_by_reuse", 0) for r in results if r["status"] == "SUCCESS")
    total_pref_ex  = sum(r.get("prefetch_only_count", 0) for r in results if r["status"] == "SUCCESS")

    print("=" * 105)
    print(f"✨ Extraction Complete!")
    print(f"   Successfully Processed : {success_count}/{len(files_to_process)}")
    if skipped_count:
        print(f"   Skipped (already exists): {skipped_count}")
    print(f"   Total Time Elapsed     : {total_time:.1f}s")
    print(f"   Destination Directory  : {os.path.abspath(args.out_dir)}")
    print()
    print("── Statistical Summary ──")
    print(f"   Demand Zero-Reuse Candidates    : {total_dem_0:,}")
    print(f"   Excluded due to Reuse > 0       : {total_removed:,}")
    print(f"   Excluded Prefetch-Only 0-Reuse  : {total_pref_ex:,}")
    print(f"   Final Pure Zero-Reuse Addresses : {total_pure:,}")
    print("=" * 105)


def _print_row(res):
    pure_str    = f"{res['pure_count']:,}"         if res['pure_count']         >= 0 else "SKIPPED"
    dem0_str    = f"{res.get('demand_zero_count', 0):,}"
    rem_str     = f"{res.get('removed_by_reuse', 0):,}"
    pref0_str   = f"{res.get('prefetch_only_count', 0):,}"
    print(
        f"  [{res['status']:<7}] {res['trace']:<42} {pure_str:>10} "
        f"{dem0_str:>12} {rem_str:>14} {pref0_str:>12} {res['elapsed']:>5.1f}s"
    )


if __name__ == "__main__":
    main()
