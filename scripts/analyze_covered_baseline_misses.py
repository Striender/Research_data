#!/usr/bin/env python3
"""Match baseline L1D misses to Bingo prefetch hits from normal result files."""

import argparse
from collections import defaultdict


def baseline_records(path):
    """Yield (instruction ID, source index, exposed, stall cycles)."""
    with open(path, "r", encoding="utf-8", errors="replace") as result:
        for line in result:
            if not line.startswith("CRIT_BASE,"):
                continue
            _, instruction, data_index, exposed, cycles = line.rstrip().split(",")
            yield (int(instruction), int(data_index), int(exposed), int(cycles))


def prefetch_records(path):
    """Yield (instruction ID, source index, prefetch level)."""
    with open(path, "r", encoding="utf-8", errors="replace") as result:
        for line in result:
            if not line.startswith("CRIT_PREF,"):
                continue
            _, instruction, data_index, level = line.rstrip().split(",")
            yield (int(instruction), int(data_index), level)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_result", help="baseline normal text result containing CRIT_BASE lines")
    parser.add_argument("bingo_result", help="Bingo normal text result containing CRIT_PREF lines")
    args = parser.parse_args()

    baseline = iter(baseline_records(args.baseline_result))
    current = next(baseline, None)
    baseline_count = 0
    bingo_prefetch_hits = 0
    covered = 0
    hidden = 0
    exposed = 0
    baseline_exposed_stall_cycles = 0
    by_level = defaultdict(lambda: [0, 0, 0, 0])  # covered, hidden, exposed, baseline stalls

    for instruction, data_index, level in prefetch_records(args.bingo_result):
        bingo_prefetch_hits += 1
        key = (instruction, data_index)
        while current is not None and current[:2] < key:
            baseline_count += 1
            current = next(baseline, None)

        if current is None or current[:2] != key:
            continue  # Prefetch hit, but not a baseline L1D miss.

        _, _, was_exposed, stall_cycles = current
        covered += 1
        row = by_level[level]
        row[0] += 1
        if was_exposed:
            exposed += 1
            baseline_exposed_stall_cycles += stall_cycles
            row[2] += 1
            row[3] += stall_cycles
        else:
            hidden += 1
            row[1] += 1

    # Finish counting only for a useful diagnostic; it is not needed for join.
    while current is not None:
        baseline_count += 1
        current = next(baseline, None)

    print("BASELINE-MATCHED PREFETCH COVERAGE")
    print(f"  BASELINE_L1D_MISS_OR_MERGE_LOADS: {baseline_count}")
    print(f"  BINGO_PREFETCH_HIT_LOADS: {bingo_prefetch_hits}")
    print(f"  COVERED_BASELINE_MISSES: {covered}")
    print(f"  COVERED_BASELINE_HIDDEN: {hidden}")
    print(f"  COVERED_BASELINE_ROB_HEAD_EXPOSED: {exposed}")
    print(f"  BASELINE_STALL_CYCLES_OF_COVERED_EXPOSED_MISSES: {baseline_exposed_stall_cycles}")
    for level in ("L1", "L2", "LLC"):
        count, level_hidden, level_exposed, level_stalls = by_level[level]
        print(f"  COVERED_AT_{level}: {count} HIDDEN: {level_hidden} "
              f"ROB_HEAD_EXPOSED: {level_exposed} BASELINE_STALL_CYCLES: {level_stalls}")


if __name__ == "__main__":
    main()
