#!/usr/bin/env python3
"""
Zero-Reuse Demand Line Distribution Analyzer for ChampSim.

Calculates the exact breakdown of all L1D 0-reuse demand lines into:
  1. Total 0-Reuse Demand Lines: All demand lines evicted with REUSE == 0
  2. Pure Zero-Reuse Lines:      Lines whose addresses were NEVER reused anywhere across the program
  3. Rest Lines:                 Lines whose addresses experienced REUSE > 0 in other residencies

Also reports the corresponding unique address counts:
  Total Unique 0-Reuse Addresses = Pure Zero Unique Addresses + Rest Unique Addresses
"""

import os
import sys
import csv
import time
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

DEFAULT_INPUT_DIR = "../results_bingo/testing_mlp_warmup/pref_l1/bingo_dpc3/exp14_srrip_mockingjay"
DEFAULT_OUTPUT_DIR = "../oracle_lists_pref_warmup_1"


def clean_trace_name(filepath):
    fname = os.path.basename(filepath)
    for ext in [".champsimtrace.gz", ".champsimtrace.xz", ".gz", ".xz", ".out"]:
        if fname.endswith(ext):
            fname = fname[:-len(ext)]
    return fname


def get_category(name):
    if name.startswith("bark"):
        return "bark"
    elif name.startswith("clip"):
        return "clip"
    elif name.startswith("llama2"):
        return "llama2"
    elif name.startswith("stable-diffusion"):
        return "stable-diffusion"
    elif name.startswith("vit"):
        return "vit"
    elif name.startswith("whisper"):
        return "whisper"
    return "other"


def parse_trace(filepath, out_dir=DEFAULT_OUTPUT_DIR, save_oracle=True, prefix="oracle_zero_reuse_"):
    """
    Parses a single ChampSim output log file and extracts the exact count of:
      - Total 0-reuse demand lines
      - Pure zero reuse lines
      - Rest lines
    """
    trace_name = clean_trace_name(filepath)
    start_t = time.time()

    if not os.path.isfile(filepath):
        return {"trace": trace_name, "status": "ERROR", "message": "File not found"}

    demand_0_counts = defaultdict(int)
    ever_reused_addrs = set()
    total_dem_0_lines = 0

    try:
        with open(filepath, "r", errors="ignore") as f:
            for line in f:
                if "L1D" not in line or "REUSE:" not in line or "ADDRESS:" not in line:
                    continue

                is_dem = "DEMAND" in line.upper() and "PREFETCH" not in line.upper()
                is_pref = "PREFETCH" in line.upper()

                if not is_dem and not is_pref:
                    continue

                parts = line.strip().split()
                addr = None
                reuse = None

                for i, p in enumerate(parts):
                    if p == "ADDRESS:" and i + 1 < len(parts):
                        try:
                            addr = int(parts[i + 1], 16)
                        except ValueError:
                            pass
                    elif p == "REUSE:" and i + 1 < len(parts):
                        try:
                            reuse = int(parts[i + 1])
                        except ValueError:
                            pass

                if addr is None or reuse is None:
                    continue

                if is_dem:
                    if reuse == 0:
                        total_dem_0_lines += 1
                        demand_0_counts[addr] += 1
                    else:
                        ever_reused_addrs.add(addr)

                elif is_pref:
                    if reuse > 0:
                        ever_reused_addrs.add(addr)

        if total_dem_0_lines == 0:
            return {
                "trace": trace_name,
                "status": "WARNING",
                "message": "No 0-reuse demand eviction lines found",
                "elapsed": time.time() - start_t
            }

        # Unique addresses
        all_dem_0_addrs = set(demand_0_counts.keys())
        pure_zero_addrs = all_dem_0_addrs - ever_reused_addrs
        rest_addrs      = all_dem_0_addrs & ever_reused_addrs

        # Eviction lines (counts)
        pure_zero_lines = sum(demand_0_counts[a] for a in pure_zero_addrs)
        rest_lines      = sum(demand_0_counts[a] for a in rest_addrs)

        # Percentages
        pure_line_pct = (100.0 * pure_zero_lines / total_dem_0_lines) if total_dem_0_lines else 0.0
        rest_line_pct = (100.0 * rest_lines / total_dem_0_lines) if total_dem_0_lines else 0.0

        total_unique_0 = len(all_dem_0_addrs)
        pure_addr_pct = (100.0 * len(pure_zero_addrs) / total_unique_0) if total_unique_0 else 0.0
        rest_addr_pct = (100.0 * len(rest_addrs) / total_unique_0) if total_unique_0 else 0.0

        oracle_path = None
        if save_oracle and out_dir:
            os.makedirs(out_dir, exist_ok=True)
            oracle_path = os.path.join(out_dir, f"{prefix}{trace_name}.txt")
            with open(oracle_path, "w") as out_fp:
                for b in sorted(pure_zero_addrs):
                    out_fp.write(f"0x{b:x}\n")

        return {
            "trace": trace_name,
            "category": get_category(trace_name),
            "status": "SUCCESS",
            # Lines
            "total_0_demand_lines": total_dem_0_lines,
            "pure_zero_lines": pure_zero_lines,
            "pure_line_pct": pure_line_pct,
            "rest_lines": rest_lines,
            "rest_line_pct": rest_line_pct,
            # Addresses
            "total_unique_0_addrs": total_unique_0,
            "pure_zero_unique_addrs": len(pure_zero_addrs),
            "pure_addr_pct": pure_addr_pct,
            "rest_unique_addrs": len(rest_addrs),
            "rest_addr_pct": rest_addr_pct,
            "oracle_file": oracle_path,
            "elapsed": time.time() - start_t
        }

    except Exception as e:
        return {
            "trace": trace_name,
            "status": "ERROR",
            "message": str(e),
            "elapsed": time.time() - start_t
        }


def print_single_report(res):
    print("=" * 80)
    print(f"📊 0-REUSE DEMAND LINE BREAKDOWN: {res['trace']}")
    print("=" * 80)
    print(f"Total 0-Reuse Demand Lines  : {res['total_0_demand_lines']:,}")
    print(f"  ├─ Pure Zero Reuse Lines   : {res['pure_zero_lines']:,}  ({res['pure_line_pct']:.2f}%)")
    print(f"  └─ Rest Lines              : {res['rest_lines']:,}  ({res['rest_line_pct']:.2f}%)")
    print()
    print("Unique Addresses Breakdown:")
    print(f"Total Unique 0-Reuse Addrs   : {res['total_unique_0_addrs']:,}")
    print(f"  ├─ Pure Zero Unique Addrs  : {res['pure_zero_unique_addrs']:,}  ({res['pure_addr_pct']:.2f}%)")
    print(f"  └─ Rest Unique Addrs       : {res['rest_unique_addrs']:,}  ({res['rest_addr_pct']:.2f}%)")
    if res.get("oracle_file"):
        print()
        print(f"Saved Pure Zero Oracle List  : {res['oracle_file']}")
    print("=" * 80)


def print_table(results):
    print("=" * 125)
    print(f"{'Trace':<38} | {'Total 0-Demand':<15} | {'Pure Zero Lines':<20} | {'Rest Lines':<20} | {'Pure Addrs':<13} | {'Rest Addrs'}")
    print(f"{'':<38} | {'(Total Lines)':<15} | {'(Count / %)':<20} | {'(Count / %)':<20} | {'(Unique)':<13} | {'(Unique)'}")
    print("=" * 125)

    cat_groups = defaultdict(list)
    tot_all_dem0 = 0
    tot_all_pure = 0
    tot_all_rest = 0

    for r in results:
        if r["status"] == "SUCCESS":
            cat_groups[r["category"]].append(r)
            tot_all_dem0 += r["total_0_demand_lines"]
            tot_all_pure += r["pure_zero_lines"]
            tot_all_rest += r["rest_lines"]

            pure_s = f"{r['pure_zero_lines']:,} ({r['pure_line_pct']:.1f}%)"
            rest_s = f"{r['rest_lines']:,} ({r['rest_line_pct']:.1f}%)"
            print(f"{r['trace']:<38} | {r['total_0_demand_lines']:>15,d} | {pure_s:>20} | {rest_s:>20} | {r['pure_zero_unique_addrs']:>13,d} | {r['rest_unique_addrs']:>10,d}")

    print("-" * 125)
    print("CATEGORY TOTALS & AVERAGES:")
    print("-" * 125)
    for cat, items in sorted(cat_groups.items()):
        c_dem0 = sum(x["total_0_demand_lines"] for x in items)
        c_pure = sum(x["pure_zero_lines"] for x in items)
        c_rest = sum(x["rest_lines"] for x in items)
        c_pure_pct = (100.0 * c_pure / c_dem0) if c_dem0 else 0.0
        c_rest_pct = (100.0 * c_rest / c_dem0) if c_dem0 else 0.0

        c_u_pure = sum(x["pure_zero_unique_addrs"] for x in items)
        c_u_rest = sum(x["rest_unique_addrs"] for x in items)

        pure_s = f"{c_pure:,} ({c_pure_pct:.1f}%)"
        rest_s = f"{c_rest:,} ({c_rest_pct:.1f}%)"
        print(f"{cat.upper():<38} | {c_dem0:>15,d} | {pure_s:>20} | {rest_s:>20} | {c_u_pure:>13,d} | {c_u_rest:>10,d}")

    print("=" * 125)
    overall_pure_pct = (100.0 * tot_all_pure / tot_all_dem0) if tot_all_dem0 else 0.0
    overall_rest_pct = (100.0 * tot_all_rest / tot_all_dem0) if tot_all_dem0 else 0.0
    all_pure_s = f"{tot_all_pure:,} ({overall_pure_pct:.1f}%)"
    all_rest_s = f"{tot_all_rest:,} ({overall_rest_pct:.1f}%)"
    print(f"{'OVERALL TOTAL':<38} | {tot_all_dem0:>15,d} | {all_pure_s:>20} | {all_rest_s:>20}")
    print("=" * 125)


def export_csv(results, csv_path):
    headers = [
        "trace", "category", "total_0_demand_lines",
        "pure_zero_lines", "pure_line_pct", "rest_lines", "rest_line_pct",
        "total_unique_0_addrs", "pure_zero_unique_addrs", "pure_addr_pct",
        "rest_unique_addrs", "rest_addr_pct", "oracle_file"
    ]
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path, "w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            if r["status"] == "SUCCESS":
                writer.writerow(r)
    print(f"📁 CSV exported successfully to: {os.path.abspath(csv_path)}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract exact count of total 0-reuse demand lines, pure zero reuse lines, and rest lines."
    )
    parser.add_argument("files", nargs="*", help="Specific trace file(s) to analyze")
    parser.add_argument(
        "--dir", default=DEFAULT_INPUT_DIR,
        help=f"Directory containing trace logs (default: {DEFAULT_INPUT_DIR})"
    )
    parser.add_argument(
        "--out-dir", default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory to save oracle lists and CSV (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--prefix", default="oracle_zero_reuse_",
        help="Filename prefix for generated oracle list files (default: 'oracle_zero_reuse_')"
    )
    parser.add_argument(
        "--no-save-oracle", action="store_true",
        help="Do not save oracle list files to out-dir"
    )
    parser.add_argument(
        "--csv", default=None,
        help="Custom output CSV filepath (defaults to '<out-dir>/zero_reuse_distribution.csv')"
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help="Number of worker processes for parallel scanning (default: 8)"
    )
    args = parser.parse_args()

    save_oracle = not args.no_save_oracle
    csv_file = args.csv if args.csv else (os.path.join(args.out_dir, "zero_reuse_distribution.csv") if args.out_dir else None)

    target_files = []
    if args.files:
        target_files = [f for f in args.files if os.path.isfile(f)]
    else:
        target_dir = args.dir
        if os.path.isdir(target_dir):
            target_files = [
                os.path.join(target_dir, f)
                for f in sorted(os.listdir(target_dir))
                if os.path.isfile(os.path.join(target_dir, f)) and not f.startswith(".")
            ]

    if not target_files:
        print(f"❌ Error: No trace log files found in '{args.dir}'.")
        sys.exit(1)

    print("=" * 95)
    print("🎯 Zero-Reuse Demand Line Analyzer (Total 0-Reuse vs Pure Zero vs Rest)")
    print(f"   Input Directory:   {os.path.abspath(args.dir)}")
    print(f"   Output Directory:  {os.path.abspath(args.out_dir)}")
    print(f"   Save Oracle Lists: {save_oracle} (Prefix: '{args.prefix}')")
    print(f"   Parallel Workers:  {args.workers}")
    print("=" * 95)

    if len(target_files) == 1:
        res = parse_trace(
            target_files[0], out_dir=args.out_dir, save_oracle=save_oracle, prefix=args.prefix
        )
        if res["status"] == "SUCCESS":
            print_single_report(res)
            if csv_file:
                export_csv([res], csv_file)
        else:
            print(f"❌ Error analyzing {target_files[0]}: {res.get('message', 'Unknown error')}")
    else:
        print(f"🔍 Analyzing {len(target_files)} logs in parallel ({args.workers} workers)...")
        results = []
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_file = {
                executor.submit(
                    parse_trace, f, args.out_dir, save_oracle, args.prefix
                ): f
                for f in target_files
            }
            for future in as_completed(future_to_file):
                results.append(future.result())

        results.sort(key=lambda x: x.get("trace", ""))
        print_table(results)

        if csv_file:
            export_csv(results, csv_file)


if __name__ == "__main__":
    main()
