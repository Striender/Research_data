#!/usr/bin/env python3
"""Extract DRAM RQ/WQ occupancy and write-watermark stats from result files."""

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
    os.path.join(SCRIPT_DIR, "..", "results", "speedup", "MSHR_FULL_STREAKS","baseline")
)

DEFAULT_OUTPUT_FILE = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "Excel_Output","baseline", "dram_queue_occupancy.xlsx")
)

NUMBER_PATTERN = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"

OCCUPANCY_PATTERN = re.compile(
    rf"^\s*(RQ|WQ) ACCESS-SAMPLED AVERAGE_OCCUPANCY:\s+({NUMBER_PATTERN})\s+/\s+"
    rf"(\d+)\s+\(({NUMBER_PATTERN})%\)(?:\s+SAMPLES:\s+(\d+))?",
    flags=re.MULTILINE,
)

WATERMARK_PATTERN = re.compile(
    r"^\s*Number time DRAM Write watermark reached:\s+(\d+)",
    flags=re.MULTILINE,
)


def natural_sort_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def parse_file(filepath):
    with open(filepath, "r", errors="ignore") as result_file:
        content = result_file.read()

    metrics = {}

    for match in OCCUPANCY_PATTERN.finditer(content):
        queue_name = match.group(1).lower()
        metrics[f"{queue_name}_average_occupancy"] = match.group(2)
        metrics[f"{queue_name}_capacity"] = int(match.group(3))
        metrics[f"{queue_name}_occupancy_percent"] = match.group(4)
        metrics[f"{queue_name}_samples"] = (
            int(match.group(5)) if match.group(5) is not None else ""
        )

    watermark_match = WATERMARK_PATTERN.search(content)
    metrics["write_watermark_reached"] = (
        int(watermark_match.group(1)) if watermark_match else ""
    )

    if not any(key.startswith(("rq_", "wq_")) for key in metrics):
        return None

    return metrics


def collect_records(results_dir):
    folder_records = {}

    for root, directories, files in os.walk(results_dir):
        directories.sort(key=natural_sort_key)
        records = []

        for filename in sorted(files, key=natural_sort_key):
            filepath = os.path.join(root, filename)

            if not os.path.isfile(filepath):
                continue

            metrics = parse_file(filepath)

            if metrics is None:
                continue

            records.append(
                {
                    "trace": filename,
                    "metrics": metrics,
                }
            )

        if records:
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
    sheet_name = re.sub(r'[:\\/*?\[\]]', "_", sheet_name)[:31]

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
    headers = [
        "Trace",
        "RQ Avg Occupancy",
        "RQ Capacity",
        "RQ Occupancy %",
        "RQ Samples",
        "WQ Avg Occupancy",
        "WQ Capacity",
        "WQ Occupancy %",
        "WQ Samples",
        "Number time DRAM Write watermark reached",
    ]

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for record in sorted(records, key=lambda item: natural_sort_key(item["trace"])):
        metrics = record["metrics"]
        worksheet.append(
            [
                record["trace"],
                metrics.get("rq_average_occupancy", ""),
                metrics.get("rq_capacity", ""),
                metrics.get("rq_occupancy_percent", ""),
                metrics.get("rq_samples", ""),
                metrics.get("wq_average_occupancy", ""),
                metrics.get("wq_capacity", ""),
                metrics.get("wq_occupancy_percent", ""),
                metrics.get("wq_samples", ""),
                metrics.get("write_watermark_reached", ""),
            ]
        )

    worksheet.freeze_panes = "B2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column_cells in worksheet.columns:
        max_len = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(
            max_len + 2, 48
        )


def write_workbook(folder_records, output_file):
    workbook = Workbook()
    workbook.remove(workbook.active)

    used_names = set()

    for folder_name in sorted(folder_records, key=natural_sort_key):
        worksheet = workbook.create_sheet(make_unique_sheet_name(folder_name, used_names))
        write_sheet(worksheet, folder_records[folder_name])

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    workbook.save(output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Extract DRAM RQ/WQ occupancy and write-watermark stats."
    )
    parser.add_argument(
        "results_dir",
        nargs="?",
        default=DEFAULT_RESULTS_DIR,
        help=f"Directory containing result files. Default: {DEFAULT_RESULTS_DIR}",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output Excel file. Default: {DEFAULT_OUTPUT_FILE}",
    )

    args = parser.parse_args()

    folder_records = collect_records(args.results_dir)

    if not folder_records:
        raise SystemExit(f"No DRAM queue occupancy stats found in {args.results_dir}")

    write_workbook(folder_records, args.output)

    total_files = sum(len(records) for records in folder_records.values())
    print(f"Extracted {total_files} files from {len(folder_records)} folders")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
