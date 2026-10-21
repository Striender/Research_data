#!/usr/bin/env python3
import os
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

WORKLOAD_DIR = "../results_bingo/testing_mlp/baseline/exp14_srrip_mockingjay/"

def process_file(fname):
    t0 = time.time()
    path = os.path.join(WORKLOAD_DIR, fname)
    if not os.path.exists(path):
        return None
    page_counts = defaultdict(lambda: [0, 0])
    lines = 0
    with open(path, "r", errors="ignore") as f:
        for line in f:
            if "L1D DEMAND" in line and "ADDRESS: 0x" in line:
                parts = line.split()
                try:
                    raw_hex = parts[parts.index("ADDRESS:") + 1].lower().replace("0x", "")
                    if raw_hex.endswith("6"):
                        raw_hex = raw_hex[:-1]
                    page = int(raw_hex, 16) >> 12
                    reuse = int(parts[parts.index("REUSE:") + 1])
                    page_counts[page][0 if reuse == 0 else 1] += 1
                    lines += 1
                except:
                    pass
    tot_p = len(page_counts)
    if tot_p == 0:
        return None
    
    # Updated thresholds requested by user:
    # - Pure 0-Reuse: >= 95% lines with 0-reuse (at most 3 reused lines out of 64)
    # - Mostly 0-Reuse: 50.0% to 95.0% lines with 0-reuse
    # - Mixed: 5.0% to 50.0% lines with 0-reuse
    # - Pure Reused: > 95.0% reused lines (< 5% 0-reuse)
    pz = sum(1 for z, nz in page_counts.values() if (z / (z + nz)) >= 0.95)
    mz = sum(1 for z, nz in page_counts.values() if 0.50 <= (z / (z + nz)) < 0.95)
    mx = sum(1 for z, nz in page_counts.values() if 0.05 <= (z / (z + nz)) < 0.50)
    pr = sum(1 for z, nz in page_counts.values() if (z / (z + nz)) < 0.05)
    pr_strict = sum(1 for z, nz in page_counts.values() if z == 0)
    
    elapsed = time.time() - t0
    return {
        "name": fname,
        "lines": lines,
        "pages": tot_p,
        "pz": pz,
        "mz": mz,
        "mx": mx,
        "pr": pr,
        "pr_strict": pr_strict,
        "pz_pct": pz / tot_p * 100,
        "mz_pct": mz / tot_p * 100,
        "mx_pct": mx / tot_p * 100,
        "pr_pct": pr / tot_p * 100,
        "pr_strict_pct": pr_strict / tot_p * 100,
        "time": elapsed
    }

if __name__ == "__main__":
    files = sorted([f for f in os.listdir(WORKLOAD_DIR) if not f.endswith(".txt") and not f.endswith(".py")])
    num_workers = min(len(files), os.cpu_count() or 8)
    print(f"Starting processing of all {len(files)} files in {WORKLOAD_DIR} with {num_workers} workers...", flush=True)
    t_start = time.time()

    results = []
    with Pool(processes=num_workers) as pool:
        for i, r in enumerate(pool.imap_unordered(process_file, files), 1):
            if r is not None:
                results.append(r)
                print(f"[{i:2d}/{len(files)}] Done: {r['name']:42s} | Pages: {r['pages']:7d} | Pure0: {r['pz_pct']:5.2f}% | Mostly0: {r['mz_pct']:5.2f}% | Time: {r['time']:.1f}s", flush=True)

    total_time = time.time() - t_start
    print(f"\nSuccessfully processed {len(results)} workloads in {total_time:.1f}s!\n", flush=True)

    # Calculate Macro Averages (average percentage across all 68 workloads)
    avg_pz_pct = sum(r['pz_pct'] for r in results) / len(results)
    avg_mz_pct = sum(r['mz_pct'] for r in results) / len(results)
    avg_mx_pct = sum(r['mx_pct'] for r in results) / len(results)
    avg_pr_pct = sum(r['pr_pct'] for r in results) / len(results)

    # Calculate Average Counts per workload
    avg_pages = sum(r['pages'] for r in results) / len(results)
    avg_pz_cnt = sum(r['pz'] for r in results) / len(results)
    avg_mz_cnt = sum(r['mz'] for r in results) / len(results)
    avg_mx_cnt = sum(r['mx'] for r in results) / len(results)
    avg_pr_cnt = sum(r['pr'] for r in results) / len(results)

    # Calculate Aggregate / Weighted Totals across all 68 workloads
    tot_pages = sum(r['pages'] for r in results)
    tot_pz = sum(r['pz'] for r in results)
    tot_mz = sum(r['mz'] for r in results)
    tot_mx = sum(r['mx'] for r in results)
    tot_pr = sum(r['pr'] for r in results)

    print("=" * 80)
    print("AVERAGE BREAKDOWN ACROSS ALL 68 WORKLOADS")
    print("=" * 80)
    print(f"Total Workloads Analyzed: {len(results)}")
    print(f"Average Total Pages per Workload: {avg_pages:.1f} pages")
    print("-" * 80)
    print(f"{'Category':32s} | {'Avg Page Count / Trace':>22s} | {'Macro-Avg %':>11s} | {'Weighted % (All Pages)':>22s}")
    print("-" * 80)
    print(f"{'Pure Zero-Reuse (>= 95% 0-Reuse)':32s} | {avg_pz_cnt:22.1f} | {avg_pz_pct:10.2f}% | {tot_pz/tot_pages*100:21.2f}%")
    print(f"{'Mostly Zero-Reuse (50% to 95%)':32s} | {avg_mz_cnt:22.1f} | {avg_mz_pct:10.2f}% | {tot_mz/tot_pages*100:21.2f}%")
    print(f"{'Mixed Pages (5% to 50% 0-Reuse)':32s} | {avg_mx_cnt:22.1f} | {avg_mx_pct:10.2f}% | {tot_mx/tot_pages*100:21.2f}%")
    print(f"{'Pure Reused (> 95% Reused)':32s} | {avg_pr_cnt:22.1f} | {avg_pr_pct:10.2f}% | {tot_pr/tot_pages*100:21.2f}%")
    print("=" * 80)

    # Save detailed CSV for record
    out_csv = "all_68_workloads_page_reuse_breakdown.csv"
    with open(out_csv, "w") as f:
        f.write("Workload,Lines,Total_Pages,Pure_0_Pages,Pure_0_Pct,Mostly_0_Pages,Mostly_0_Pct,Mixed_Pages,Mixed_Pct,Pure_Reused_Pages,Pure_Reused_Pct\n")
        for r in results:
            f.write(f"{r['name']},{r['lines']},{r['pages']},{r['pz']},{r['pz_pct']:.2f},{r['mz']},{r['mz_pct']:.2f},{r['mx']},{r['mx_pct']:.2f},{r['pr']},{r['pr_pct']:.2f}\n")
    print(f"\nDetailed per-trace breakdown saved to {out_csv}")
