#!/usr/bin/env python3
import json
import os
import sys
from collections import defaultdict

files = {
    '16KB': 'results_bingo/testing/16KB.txt',
    '48KB': 'results_bingo/testing/48KB.txt',
    '64KB': 'results_bingo/testing/64KB.txt',
    '128KB': 'results_bingo/testing/128KB.txt',
    '256KB': 'results_bingo/testing/256KB.txt'
}

MAX_EVICTIONS = 50000

print(f"Reading first {MAX_EVICTIONS} evictions from each file...")

# data[size][addr] = list of reuses
data = {}
for size, path in files.items():
    addr_reuses = defaultdict(list)
    count = 0
    with open(path, 'r', buffering=8*1024*1024) as f:
        for line in f:
            if line.startswith('L1D Demand'):
                parts = line.split()
                addr = parts[5]
                reuse = int(parts[7])
                addr_reuses[addr].append(reuse)
                count += 1
                if count >= MAX_EVICTIONS:
                    break
    data[size] = addr_reuses
    print(f"Loaded {count} evictions for {size} ({len(addr_reuses)} unique lines)")

# Use 48KB as baseline
ref_size = '48KB'
ref_data = data[ref_size]

# Find common addresses present in 48KB and other sizes
other_sizes = ['16KB', '64KB', '128KB', '256KB']

print("\n" + "="*80)
print("ANALYSIS 1: FOR LINES IN 48KB, HOW DOES REUSE BEHAVE ACROSS CACHE SIZES?")
print("="*80)

# Categorize addresses in 48KB by their primary reuse
# (For multi-fill lines, take the mode or first reuse; here we take total hits / total fills)
categories = {
    'Zero Reuse (0)': lambda r: r == 0,
    'Low Reuse (1-4)': lambda r: 1 <= r <= 4,
    'Moderate Reuse (5-14)': lambda r: 5 <= r <= 14,
    'High Reuse (>=15)': lambda r: r >= 15
}

summary_results = []

for cat_name, cat_func in categories.items():
    # Filter 48KB lines matching this category
    matching_addrs = []
    for addr, reuses in ref_data.items():
        # Representative reuse for this line in 48KB: max or average
        rep_reuse = max(reuses)
        if cat_func(rep_reuse):
            matching_addrs.append(addr)
    
    print(f"\n--- Category: {cat_name} (Total Unique Lines in 48KB: {len(matching_addrs)}) ---")
    
    for target_size in other_sizes:
        common = [a for a in matching_addrs if a in data[target_size]]
        if not common:
            print(f"  vs {target_size}: No common lines in first {MAX_EVICTIONS} window")
            continue
        
        # Check how many have exactly the same max reuse
        same_reuse_count = 0
        higher_reuse_count = 0
        lower_reuse_count = 0
        
        fill_diffs = []
        reuse_diffs = []
        
        for a in common:
            ref_r = max(ref_data[a])
            tar_r = max(data[target_size][a])
            ref_fills = len(ref_data[a])
            tar_fills = len(data[target_size][a])
            
            fill_diffs.append(tar_fills - ref_fills)
            reuse_diffs.append(tar_r - ref_r)
            
            if tar_r == ref_r:
                same_reuse_count += 1
            elif tar_r > ref_r:
                higher_reuse_count += 1
            else:
                lower_reuse_count += 1
                
        same_pct = same_reuse_count / len(common) * 100
        higher_pct = higher_reuse_count / len(common) * 100
        lower_pct = lower_reuse_count / len(common) * 100
        avg_fill_diff = sum(fill_diffs) / len(fill_diffs)
        avg_reuse_diff = sum(reuse_diffs) / len(reuse_diffs)
        
        print(f"  vs {target_size:6} (N={len(common)}): Exactly Same Reuse: {same_pct:5.1f}% | Higher: {higher_pct:5.1f}% | Lower: {lower_pct:5.1f}% | Avg Fill Diff: {avg_fill_diff:+.2f}")

print("\n" + "="*80)
print("ANALYSIS 2: FILL FREQUENCY COMPARISON ACROSS SIZES")
print("="*80)
print(f"{'Address Sample (Top Common Lines)':35} | {'16KB Fills/Reuse':18} | {'48KB Fills/Reuse':18} | {'64KB Fills/Reuse':18} | {'128KB Fills/Reuse':18} | {'256KB Fills/Reuse':18}")
print("-" * 130)

# Sample some frequent addresses present in all sizes
all_common = [a for a in ref_data if all(a in data[s] for s in other_sizes)]
print(f"Found {len(all_common)} addresses present in the sample window across ALL 5 cache sizes.")

# Pick a sample of 15 interesting lines (some 0 reuse, some low, some high)
sample_addrs = []
for cat_name, cat_func in categories.items():
    cat_addrs = [a for a in all_common if cat_func(max(ref_data[a]))]
    sample_addrs.extend(cat_addrs[:4])

for a in sample_addrs[:16]:
    cols = []
    for s in ['16KB', '48KB', '64KB', '128KB', '256KB']:
        fills = len(data[s][a])
        # Format as fills x (reuses)
        max_r = max(data[s][a])
        cols.append(f"{fills}x (r={max_r})")
    print(f"{a:35} | " + " | ".join([f"{c:18}" for c in cols]))

print("\nDone.")
