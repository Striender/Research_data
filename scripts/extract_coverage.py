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

DEFAULT_RESULTS_DIR = os.path.join(PROJECT_ROOT, "results_bingo" )
DEFAULT_OUTPUT_FILE = os.path.join(
    PROJECT_ROOT, "Excel_Output","aiml_bingo", "coverage.xlsx"
)

CACHE_LEVELS = ("L1D", "L2C", "LLC")
EXPECTED_TRACE_COUNT = 26

BASELINE_LOAD_MISSES = {
    "L1D": [
      1997050,
11981808,
2419603,
13752864,
10137577,
10524815,
1959825,
10874903,
10663679,
10266931,
1869640,
1556895,
2132644,
3756673,
2293729,
7111142,
8121652,
9207153,
8428487,
8836695,
7111591,
9208057,
9028785,
9201642,
7111234,
8426042,
7111218,
8440723,
9211650,
7290405,
6764837,
6674075,
6669945,
6941539,
6934231,
6941947,
7000284,
7000894,
7000683,
48271154,
25561490,
185231,
17843903,
67227082,
185290,
27408639,
46741039,
25554214,
185302,
33931778,
27829147,
25561504,
66461974,
17791225,
9642674,
1545769,
5643195,
1673435,
1633707,
1751041,
4210777,
3907735,
4099872,
10989683,
13708091,
17393228,
10386883,
4531547

    ],
    "L2C": [
       1179342,
1371722,
511018,
1427923,
4941612,
1390350,
1072349,
6000582,
5720693,
5206460,
729080,
428050,
903700,
626568,
787950,
7110646,
7114898,
7120660,
7117481,
7125407,
7110901,
7120979,
7119651,
7112639,
7110401,
7117496,
7110216,
7117551,
7120958,
7111193,
6735771,
6601897,
6596295,
6934350,
6925085,
6931434,
6996118,
6996785,
6996514,
3195297,
1571999,
24561,
1407662,
1684313,
7199,
1711117,
3620416,
1566170,
7567,
2081361,
1820294,
1562618,
1108315,
1042008,
887831,
597271,
848948,
734929,
395718,
717887,
1319092,
1318426,
1319712,
3170823,
3459991,
223951,
3049745,
1188247

    ],
    "LLC": [
       425970,
454367,
489617,
754307,
4681830,
673596,
625603,
5922125,
5548964,
4936689,
593602,
107762,
738086,
567505,
238162,
7110262,
7113711,
7118928,
7116566,
7124183,
7110493,
7119379,
7118014,
7110592,
7110071,
7116506,
7109802,
7116168,
7119233,
7110757,
6398395,
6265499,
6258205,
6839397,
6828480,
6815713,
6992022,
6992487,
6981778,
2581888,
1482959,
10979,
1277917,
1676891,
1186,
434175,
2464662,
1473731,
1018,
1286723,
1631410,
1477403,
1094501,
946708,
459847,
141528,
636178,
416924,
122844,
492501,
1028813,
1019116,
1027107,
3122879,
3459927,
223713,
2997112,
82352

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
