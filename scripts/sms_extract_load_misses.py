#!/usr/bin/env python3
"""Extract load-miss counts for each cache level from ChampSim results."""

import argparse
import re
from pathlib import Path

import pandas as pd


CACHE_LEVELS = ("L1D", "L2C", "LLC")
DEFAULT_INSTRUCTIONS = 200_000_000


def natural_sort_key(path: Path):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def extract_load_misses(result_file: Path):
    content = result_file.read_text(encoding="utf-8", errors="ignore")
    row = {"Trace": result_file.name}

    for cache in CACHE_LEVELS:
        matches = re.findall(
            rf"^Core_\d+_{cache}_load_miss\s+(\d+)\s*$",
            content,
            flags=re.MULTILINE,
        )
        row[f"{cache} Load Miss"] = sum(map(int, matches)) if matches else None

    return row


def main():
    parser = argparse.ArgumentParser(
        description="Extract L1D, L2C, and LLC load misses into an Excel file."
    )
    parser.add_argument(
        "--results-dir",
        default="../results/sms_ai_ml/no-pf",
        help="Directory containing ChampSim output files",
    )
    parser.add_argument(
        "--output",
        default="scripts/sms_ai_ml_load_misses_no-pf.xlsx",
        help="Output Excel file",
    )
    parser.add_argument(
        "--instructions",
        type=int,
        default=DEFAULT_INSTRUCTIONS,
        help="Simulation instruction count used to calculate MPKI",
    )
    args = parser.parse_args()

    if args.instructions <= 0:
        parser.error("--instructions must be greater than zero")

    results_dir = Path(args.results_dir)
    if not results_dir.is_dir():
        parser.error(f"results directory does not exist: {results_dir}")

    result_files = sorted(results_dir.rglob("*.out"), key=natural_sort_key)
    if not result_files:
        parser.error(f"no .out files found under: {results_dir}")

    rows = [extract_load_misses(path) for path in result_files]
    for row in rows:
        for cache in CACHE_LEVELS:
            misses = row[f"{cache} Load Miss"]
            row[f"{cache} Load MPKI"] = (
                misses * 1000 / args.instructions if misses is not None else None
            )
    missing = [
        row["Trace"]
        for row in rows
        if any(row[f"{cache} Load Miss"] is None for cache in CACHE_LEVELS)
    ]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(
        rows,
        columns=[
            "Trace",
            "L1D Load Miss",
            "L1D Load MPKI",
            "L2C Load Miss",
            "L2C Load MPKI",
            "LLC Load Miss",
            "LLC Load MPKI",
        ],
    )
    dataframe.to_excel(output, sheet_name="Load Misses", index=False)

    print(f"Extracted {len(rows)} traces to {output}")
    if missing:
        print(f"Warning: {len(missing)} traces have one or more missing values")


if __name__ == "__main__":
    main()
