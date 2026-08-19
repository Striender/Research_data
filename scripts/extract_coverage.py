#!/usr/bin/env python3
"""Extract load misses and calculate coverage for L1D, L2C, and LLC.

Coverage formula:
    (baseline_load_miss - extracted_load_miss) * 100 / baseline_load_miss

The baseline miss counts are matched to result files by natural trace order.
Each directory containing ChampSim result files is written to one Excel sheet.
"""

import argparse
import os
import re
from decimal import Decimal, getcontext

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
except ImportError:
    raise SystemExit(
        "The 'openpyxl' library is required. Install it with: pip install openpyxl"
    )


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))

DEFAULT_RESULTS_DIR = os.path.join(PROJECT_ROOT, "results", "speedup", "test")
DEFAULT_OUTPUT_FILE = os.path.join(
    PROJECT_ROOT, "Excel_Output","Pref_l2", "test_coverage.xlsx"
)

CACHE_LEVELS = ("L1D", "L2C", "LLC")
EXPECTED_TRACE_COUNT = 26

BASELINE_LOAD_MISSES = {
    "L1D": [
       2316146,
       12269867,
       13995304,
       10164599,
       2078326,
       2160450,
       6765544,
       6675003,
       6671593,
       6941725,
       6934255,
       6942899,
       7000350,
       7000953,
       7000759,
       49598646,
       25561507,
       28209838,
       34004105,
       26593508,
       25561507,
       9659881,
       5337905,
       3718196,
       3568293,
       3469929

    ],
    "L2C": [
        1195792,
1411605,
1434140,
4945894,
729117,
907671,
6738388,
6604666,
6598369,
6936031,
6926159,
6933107,
6997161,
6998039,
6997726,
3196247,
1572853,
1711573,
2081076,
1801178,
1562746,
892048,
840355,
1319100,
1318476,
1319735

    ],
    "LLC": [
        451345,
478324,
754448,
4682317,
578367,
736701,
6400150,
6266600,
6259599,
6840186,
6828834,
6816691,
6992193,
6992713,
6980977,
2597777,
1482342,
432983,
1279728,
1605099,
1476425,
447024,
633772,
1020566,
1020554,
1031218

    ],
}

LOAD_MISS_RE = re.compile(
    r"^(L1D|L2C|LLC) LOAD\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)",
    flags=re.MULTILINE,
)


def natural_sort_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def parse_load_misses(filepath):
    with open(filepath, "r", errors="ignore") as result_file:
        content = result_file.read()

    metrics = {}
    for cache_name, load_misses in LOAD_MISS_RE.findall(content):
        metrics[cache_name] = int(load_misses)

    return metrics


def coverage_percent(baseline_misses, extracted_misses):
    if baseline_misses == 0 or extracted_misses is None:
        return None

    getcontext().prec = 50
    coverage = (
        (Decimal(baseline_misses) - Decimal(extracted_misses))
        * Decimal(100)
        / Decimal(baseline_misses)
    )
    return float(coverage.quantize(Decimal("0.01")))


def collect_folder_records(results_dir):
    folder_records = {}

    for root, directories, files in os.walk(results_dir):
        directories.sort(key=natural_sort_key)
        result_files = [
            filename
            for filename in sorted(files, key=natural_sort_key)
            if os.path.isfile(os.path.join(root, filename))
        ]

        records = []
        for trace_index, filename in enumerate(result_files):
            filepath = os.path.join(root, filename)
            metrics = parse_load_misses(filepath)
            if not metrics:
                continue

            records.append(
                {
                    "trace_index": trace_index,
                    "trace": filename,
                    "metrics": metrics,
                }
            )

        if not records:
            continue

        relative_folder = os.path.relpath(root, results_dir)
        folder_name = (
            os.path.basename(os.path.abspath(results_dir))
            if relative_folder == "."
            else relative_folder
        )
        folder_records[folder_name] = records

    return folder_records


def make_unique_sheet_name(folder_name, used_names):
    sheet_name = folder_name.replace(os.sep, "_")
    sheet_name = re.sub(r'[:\\/*?\[\]]', "_", sheet_name)[:31] or "Results"

    original_name = sheet_name
    counter = 1
    while sheet_name in used_names:
        suffix = f"_{counter}"
        sheet_name = original_name[: 31 - len(suffix)] + suffix
        counter += 1

    used_names.add(sheet_name)
    return sheet_name


def write_sheet(worksheet, records):
    headers = ["Trace"]
    for cache_name in CACHE_LEVELS:
        headers.extend(
            [
                f"{cache_name} Baseline Load Miss",
                f"{cache_name} Extracted Load Miss",
                f"{cache_name} Coverage %",
            ]
        )

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    sorted_records = sorted(records, key=lambda item: natural_sort_key(item["trace"]))

    if len(sorted_records) != EXPECTED_TRACE_COUNT:
        worksheet.append(
            [
                f"WARNING: found {len(sorted_records)} traces; "
                f"baseline list has {EXPECTED_TRACE_COUNT} entries."
            ]
        )

    for trace_index, record in enumerate(sorted_records):
        row = [record["trace"]]
        metrics = record["metrics"]

        for cache_name in CACHE_LEVELS:
            baseline_list = BASELINE_LOAD_MISSES[cache_name]
            baseline_misses = (
                baseline_list[trace_index]
                if trace_index < len(baseline_list)
                else None
            )
            extracted_misses = metrics.get(cache_name)

            row.extend(
                [
                    baseline_misses if baseline_misses is not None else "N/A",
                    extracted_misses if extracted_misses is not None else "N/A",
                    coverage_percent(baseline_misses, extracted_misses)
                    if baseline_misses is not None
                    else "N/A",
                ]
            )

        worksheet.append(row)

    worksheet.freeze_panes = "B2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column_cells in worksheet.columns:
        max_len = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )
        column_letter = column_cells[0].column_letter
        worksheet.column_dimensions[column_letter].width = min(max_len + 2, 45)


def write_workbook(folder_records, output_file):
    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    used_names = set()
    for folder_name in sorted(folder_records, key=natural_sort_key):
        sheet_name = make_unique_sheet_name(folder_name, used_names)
        worksheet = workbook.create_sheet(sheet_name)
        write_sheet(worksheet, folder_records[folder_name])

    output_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(output_dir, exist_ok=True)
    workbook.save(output_file)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        default=DEFAULT_RESULTS_DIR,
        help=f"directory to scan recursively (default: {DEFAULT_RESULTS_DIR})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"output .xlsx file (default: {DEFAULT_OUTPUT_FILE})",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.results_dir):
        raise SystemExit(f"Results directory not found: {args.results_dir}")

    folder_records = collect_folder_records(args.results_dir)
    if not folder_records:
        raise SystemExit(f"No ChampSim load-miss stats found under: {args.results_dir}")

    write_workbook(folder_records, args.output)
    print(f"Wrote coverage workbook: {args.output}")


if __name__ == "__main__":
    main()
