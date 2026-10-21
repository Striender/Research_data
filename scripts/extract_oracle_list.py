#!/usr/bin/env python3
"""
Batch Oracle Zero-Reuse List Extractor for ChampSim.

Extracts ground-truth pure zero-reuse cache block addresses from ChampSim
simulation output logs and generates:
  oracle_lists/oracle_zero_reuse_<trace_name>.txt

Supports:
  - Direct block addresses (e.g. 0x27edcd9192a)
  - Legacy full addresses with trailing-6 print artifacts
  - Auto-detection mode (default)
"""

import os
import sys
import time
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

DEFAULT_INPUT_DIR = "../results_bingo/testing_mlp_warmup/pref_l1/bingo_dpc3/exp14_srrip_mockingjay"
DEFAULT_OUTPUT_DIR = "../oracle_lists_pref_warmup_1"

def clean_trace_name(filepath):
    """Extract clean trace name from filepath."""
    fname = os.path.basename(filepath)
    for ext in [".champsimtrace.gz", ".champsimtrace.xz", ".gz", ".xz", ".out"]:
        if fname.endswith(ext):
            fname = fname[:-len(ext)]
    return fname

def detect_log_address_mode(input_log):
    """Inspects first few lines to determine whether addresses are direct block addresses or legacy."""
    sample_addrs = []
    try:
        with open(input_log, 'r', errors='ignore') as f:
            for line in f:
                if "L1D" in line and "DEMAND" in line.upper() and "ADDRESS:" in line:
                    parts = line.strip().split()
                    for i, p in enumerate(parts):
                        if p == "ADDRESS:" and i + 1 < len(parts):
                            sample_addrs.append(parts[i+1])
                            break
                    if len(sample_addrs) >= 50:
                        break
    except Exception:
        pass

    if not sample_addrs:
        return "direct"

    # In legacy logs, addresses look like 0x9fb736464a8c6 (13+ chars, ending in 6)
    trailing_6_count = sum(1 for a in sample_addrs if a.startswith("0x") and a.endswith("6") and len(a) >= 13)
    if (trailing_6_count / len(sample_addrs)) > 0.8:
        return "legacy_trailing_6"
    return "direct"

def process_single_trace(input_log, output_dir=DEFAULT_OUTPUT_DIR, overwrite=False, mode="auto"):
    """Extracts pure zero-reuse addresses from a single trace output log."""
    trace_name = clean_trace_name(input_log)
    output_file = os.path.join(output_dir, f"oracle_zero_reuse_{trace_name}.txt")

    if not overwrite and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        return {
            "trace": trace_name,
            "status": "SKIPPED",
            "message": f"File already exists: {output_file}",
            "pure_count": -1,
            "total_evictions": -1,
            "elapsed": 0.0
        }

    # Determine parsing mode
    active_mode = mode
    if active_mode == "auto":
        active_mode = detect_log_address_mode(input_log)

    zero_addrs = set()
    reused_addrs = set()
    total_lines = 0

    start_t = time.time()
    try:
        with open(input_log, 'r', errors='ignore') as f:
            for line in f:
                if "L1D" in line and "DEMAND" in line.upper() and "REUSE:" in line:
                    total_lines += 1
                    parts = line.strip().split()
                    addr_str = None
                    reuse_val = None
                    for i, p in enumerate(parts):
                        if p == "ADDRESS:" and i + 1 < len(parts):
                            addr_str = parts[i+1]
                        elif p == "REUSE:" and i + 1 < len(parts):
                            try:
                                reuse_val = int(parts[i+1])
                            except ValueError:
                                pass

                    if addr_str is not None and reuse_val is not None:
                        try:
                            if active_mode == "legacy_trailing_6":
                                # Strip trailing '6' artifact and shift by 6
                                full_addr_hex = addr_str[:-1] if (addr_str.startswith("0x") and addr_str.endswith("6") and len(addr_str) > 3) else addr_str
                                block_addr = int(full_addr_hex, 16) >> 6
                            elif active_mode == "byte_addr":
                                # Clean byte address -> shift by 6 to get block address
                                block_addr = int(addr_str, 16) >> 6
                            else:
                                # Direct block address (no shift needed)
                                block_addr = int(addr_str, 16)

                            if reuse_val == 0:
                                zero_addrs.add(block_addr)
                            else:
                                reused_addrs.add(block_addr)
                        except ValueError:
                            pass

        if total_lines == 0:
            return {
                "trace": trace_name,
                "status": "WARNING",
                "message": f"No L1D Demand reuse records found in {input_log}",
                "pure_count": 0,
                "total_evictions": 0,
                "elapsed": time.time() - start_t
            }

        # Option A: Strictly Pure 0-reuse block addresses (0 reuse 100% of the time)
        pure_zero_addrs = zero_addrs - reused_addrs
        overlap = zero_addrs.intersection(reused_addrs)

        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'w') as out:
            for b in sorted(pure_zero_addrs):
                out.write(f"0x{b:x}\n")

        elapsed = time.time() - start_t
        return {
            "trace": trace_name,
            "status": "SUCCESS",
            "message": f"Saved {len(pure_zero_addrs):,} addresses -> {output_file} (Mode: {active_mode})",
            "pure_count": len(pure_zero_addrs),
            "unique_zero": len(zero_addrs),
            "overlap": len(overlap),
            "total_evictions": total_lines,
            "output_file": output_file,
            "elapsed": elapsed
        }

    except Exception as e:
        return {
            "trace": trace_name,
            "status": "ERROR",
            "message": str(e),
            "pure_count": 0,
            "total_evictions": 0,
            "elapsed": time.time() - start_t
        }

def main():
    parser = argparse.ArgumentParser(description="Batch Oracle Zero-Reuse Address Extractor")
    parser.add_argument("files", nargs="*", help="Optional specific trace log file(s) to process")
    parser.add_argument("--dir", default=DEFAULT_INPUT_DIR, help=f"Directory containing trace logs (default: {DEFAULT_INPUT_DIR})")
    parser.add_argument("--out-dir", default=DEFAULT_OUTPUT_DIR, help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--mode", choices=["auto", "direct", "legacy_trailing_6", "byte_addr"], default="auto",
                        help="Address parsing mode: 'direct' for raw block addresses, 'legacy_trailing_6' for old logs, 'auto' for auto-detection (default: auto)")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel worker processes (default: 8)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing oracle list files")
    args = parser.parse_args()

    files_to_process = []
    if args.files:
        files_to_process = [f for f in args.files if os.path.isfile(f)]
    elif os.path.isdir(args.dir):
        files_to_process = [
            os.path.join(args.dir, f) for f in sorted(os.listdir(args.dir))
            if os.path.isfile(os.path.join(args.dir, f)) and not f.startswith(".")
        ]

    if not files_to_process:
        print(f"❌ Error: No log files found to process in '{args.dir}'.")
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)

    print("=" * 80)
    print(f"🚀 Oracle Zero-Reuse Extractor")
    print(f"   Input Files:      {len(files_to_process)}")
    print(f"   Output Directory: {args.out_dir}/oracle_zero_reuse_<trace_name>.txt")
    print(f"   Parsing Mode:     {args.mode}")
    print(f"   Parallel Workers: {args.workers}")
    print(f"   Overwrite:        {args.overwrite}")
    print("=" * 80)

    start_all = time.time()
    results = []

    if len(files_to_process) == 1 or args.workers == 1:
        for f in files_to_process:
            res = process_single_trace(f, output_dir=args.out_dir, overwrite=args.overwrite, mode=args.mode)
            results.append(res)
            pure_str = f"{res['pure_count']:,}" if res['pure_count'] >= 0 else "SKIPPED"
            print(f"[{res['status']}] {res['trace']:<45} | Pure 0-Reuse: {pure_str:>10} | {res['elapsed']:.2f}s")
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_file = {
                executor.submit(process_single_trace, f, args.out_dir, args.overwrite, args.mode): f
                for f in files_to_process
            }
            for i, future in enumerate(as_completed(future_to_file), 1):
                res = future.result()
                results.append(res)
                pure_str = f"{res['pure_count']:,}" if res['pure_count'] >= 0 else "SKIPPED"
                print(f"[{i:2d}/{len(files_to_process)}] [{res['status']:<7}] {res['trace']:<45} | Pure 0-Reuse: {pure_str:>10} | {res['elapsed']:.1f}s")

    total_time = time.time() - start_all
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    skipped_count = sum(1 for r in results if r['status'] == 'SKIPPED')

    print("=" * 80)
    print(f"✨ Extraction Complete!")
    print(f"   Successfully Processed: {success_count}/{len(files_to_process)}")
    if skipped_count:
        print(f"   Skipped (Already Exists): {skipped_count}")
    print(f"   Total Time Elapsed:     {total_time:.1f}s")
    print(f"   Destination:            {os.path.abspath(args.out_dir)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
