#!/usr/bin/env python3

import os
import csv

ROOT_DIR = "../results/spec/MSHR/pref_l1_l2/vberti_bingo_dpc3/exp14_srrip_mockingjay"

OUTPUT_CSV = "reuse_distance_summary.csv"

CACHE_BINS = {
    "l1d": [
    ("short[0-L1D_WAY)", "short"),
    ("mid[L1D_WAY-32)", "mid"),
        ("long[32+]", "long"),
    ],
    "l2c": [
        ("short[0-L2C_WAY)", "short"),
        ("mid[L2C_WAY-32)", "mid"),
        ("long[32+]", "long"),
    ],
}

TABLE_TITLES = {
    "l1d": "L1D reuse distance bin frequency table",
    "l2c": "L2C reuse distance bin frequency table",
}


def parse_reuse_table(lines, cache_name):
    bins = CACHE_BINS[cache_name]
    bin_freq = {label: 0 for label, _ in bins}

    for i, line in enumerate(lines):
        if TABLE_TITLES[cache_name] not in line:
            continue

        j = i + 1
        while j < len(lines) and "reuse_distance_bin,frequency" not in lines[j]:
            if lines[j].startswith("="):
                return None
            j += 1

        if j == len(lines):
            return None

        j += 1
        while j < len(lines):
            row = lines[j].strip()

            if row.startswith("=") or "," not in row:
                break

            parts = row.rsplit(",", 1)
            if len(parts) != 2:
                break

            rd_bin = parts[0].strip()
            freq = parts[1].strip()

            if rd_bin in bin_freq:
                bin_freq[rd_bin] = int(freq)

            j += 1

        return bin_freq

    return None


def percentages(bin_freq, bins):
    total = sum(bin_freq.values())
    if total == 0:
        return [0.0 for _ in bins], total

    return [round((bin_freq[label] / total) * 100.0, 4) for label, _ in bins], total

rows = []

for root, _, files in os.walk(ROOT_DIR):

    for file in sorted(files):

        filepath = os.path.join(root, file)

        try:
            with open(filepath, "r", errors="ignore") as f:
                lines = f.readlines()

            parsed = {
                cache_name: parse_reuse_table(lines, cache_name)
                for cache_name in CACHE_BINS
            }

            if all(values is None for values in parsed.values()):
                continue

            row = [file]
            for cache_name, bins in CACHE_BINS.items():
                bin_freq = parsed[cache_name]
                if bin_freq is None:
                    bin_freq = {label: 0 for label, _ in bins}

                pct, total_freq = percentages(bin_freq, bins)
                row += [bin_freq[label] for label, _ in bins]
                row += pct
                row.append(total_freq)

            rows.append(row)

        except Exception as e:
            print(f"Skipping {filepath}: {e}")

rows.sort(key=lambda x: x[0])

header = (
    ["benchmark"]
)

for cache_name, bins in CACHE_BINS.items():
    header += [f"{cache_name}_{name}" for _, name in bins]
    header += [f"{cache_name}_{name}_pct" for _, name in bins]
    header += [f"{cache_name}_total_frequency"]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)

print(f"Processed {len(rows)} files")
print(f"Output written to {OUTPUT_CSV}")
