#!/usr/bin/env python3
"""Extract average load miss latency for L1D, L2C, and LLC from ChampSim results.

Each results folder is written to a separate Excel worksheet.
"""

import argparse
import os
import re

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
except ImportError:
    raise SystemExit(
        "The 'openpyxl' library is required. Install it with: pip install openpyxl"
    )


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_RESULTS_DIR = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "results", "speedup","baseline")
)

DEFAULT_OUTPUT_FILE = os.path.normpath(
    os.path.join(
        SCRIPT_DIR,
        "..",
        "Excel_Output",
        "baseline",
        "Bingo_average_load_miss_latency.xlsx",
    )
)

CACHE_LEVELS = ("L1D", "L2C", "LLC")

NUMBER_PATTERN = r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"


def natural_sort_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def parse_file(filepath):
    with open(filepath, "r", errors="ignore") as result_file:
        content = result_file.read()

    metrics = {}

    for cache_name in CACHE_LEVELS:
        match = re.search(
            rf"^{cache_name} AVERAGE MISS LATENCY:\s+{NUMBER_PATTERN} cycles "
            rf"AVERAGE LOAD MISS LATENCY:\s+{NUMBER_PATTERN} cycles "
            rf"Load Miss\s+(\d+)",
            content,
            flags=re.MULTILINE,
        )

        if not match:
            continue

        metrics[cache_name] = {
            "average_miss_latency": match.group(1),
            "average_load_miss_latency": match.group(2),
            "load_misses": int(match.group(3)),
        }

    return metrics


def collect_records(results_dir):
    """
    Group result files by the folder containing them.

    Example:

    results/speedup/
        baseline/
            trace1.txt
            trace2.txt
        gaze/
            trace1.txt
            trace2.txt

    becomes:

    {
        "baseline": [...],
        "gaze": [...]
    }
    """

    folder_records = {}

    for root, directories, files in os.walk(results_dir):
        directories.sort(key=natural_sort_key)

        records = []

        for filename in sorted(files, key=natural_sort_key):
            filepath = os.path.join(root, filename)

            if not os.path.isfile(filepath):
                continue

            metrics = parse_file(filepath)

            if not metrics:
                continue

            records.append(
                {
                    "trace": filename,
                    "metrics": metrics,
                }
            )

        # Only create a sheet for folders containing valid result files
        if records:
            relative_folder = os.path.relpath(root, results_dir)

            if relative_folder == ".":
                folder_name = os.path.basename(
                    os.path.abspath(results_dir)
                )
            else:
                folder_name = relative_folder

            folder_records[folder_name] = records

    return folder_records


def make_unique_sheet_name(folder_name, used_names):
    """
    Convert folder path/name into a valid unique Excel worksheet name.
    """

    # Replace path separators so nested folders remain recognizable
    sheet_name = folder_name.replace(os.sep, "_")

    # Remove characters forbidden by Excel
    sheet_name = re.sub(r'[:\\/*?\[\]]', "_", sheet_name)

    # Excel worksheet names are limited to 31 characters
    sheet_name = sheet_name[:31]

    if not sheet_name:
        sheet_name = "Results"

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
                f"{cache_name} Avg Load Miss Latency",
                f"{cache_name} Load Misses",
                f"{cache_name} Avg Miss Latency",
            ]
        )

    worksheet.append(headers)

    # Header formatting
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Write results
    for record in sorted(records, key=lambda item: natural_sort_key(item["trace"])):
        row = [record["trace"]]

        for cache_name in CACHE_LEVELS:
            stats = record["metrics"].get(cache_name)

            if stats:
                row.extend(
                    [
                        float(stats["average_load_miss_latency"]),
                        stats["load_misses"],
                        float(stats["average_miss_latency"]),
                    ]
                )
            else:
                row.extend(["N/A", "N/A", "N/A"])

        worksheet.append(row)

    # Freeze header / first column
    worksheet.freeze_panes = "B2"

    # Add filters
    worksheet.auto_filter.ref = worksheet.dimensions

    # Automatically size columns
    for column_cells in worksheet.columns:
        max_len = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )

        worksheet.column_dimensions[
            column_cells[0].column_letter
        ].width = min(max_len + 2, 90)


def write_workbook(folder_records, output_file):
    workbook = Workbook()

    # Remove the automatically created default sheet
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    used_names = set()

    for folder_name in sorted(
        folder_records,
        key=natural_sort_key,
    ):
        sheet_name = make_unique_sheet_name(
            folder_name,
            used_names,
        )

        worksheet = workbook.create_sheet(
            title=sheet_name
        )

        write_sheet(
            worksheet,
            folder_records[folder_name],
        )

    workbook.save(output_file)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract average load miss latency for "
            "L1D, L2C, and LLC. "
            "Each folder is written to a separate Excel sheet."
        )
    )

    parser.add_argument(
        "results_dir",
        nargs="?",
        default=DEFAULT_RESULTS_DIR,
        help=f"Results directory to scan. Default: {DEFAULT_RESULTS_DIR}",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Excel output file. Default: {DEFAULT_OUTPUT_FILE}",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.results_dir):
        raise SystemExit(
            f"Results directory not found: {args.results_dir}"
        )

    folder_records = collect_records(args.results_dir)

    if not folder_records:
        raise SystemExit(
            f"No average load miss latency lines found under: "
            f"{args.results_dir}"
        )

    output_file = os.path.abspath(args.output)

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True,
    )

    write_workbook(
        folder_records,
        output_file,
    )

    total_files = sum(
        len(records)
        for records in folder_records.values()
    )

    print(
        f"Wrote {total_files} result files "
        f"across {len(folder_records)} sheets."
    )

    print(f"Output: {output_file}")

    print("\nSheets created:")

    for folder_name in sorted(
        folder_records,
        key=natural_sort_key,
    ):
        print(
            f"  {folder_name}: "
            f"{len(folder_records[folder_name])} files"
        )


if __name__ == "__main__":
    main()