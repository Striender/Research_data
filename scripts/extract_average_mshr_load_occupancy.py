#!/usr/bin/env python3
"""Extract ROI average demand-load MSHR occupancy for L1D, L2C, and LLC.

The script recursively scans ChampSim output files and writes an Excel row per
CPU/result-file pair. Only the ``Region of Interest Statistics`` section is
parsed, so warmup and optional cumulative-statistics output are ignored.
"""

import argparse
import re
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
except ImportError:
    raise SystemExit(
        "The 'openpyxl' library is required. Install it with: pip install openpyxl"
    )


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results_bingo"
DEFAULT_OUTPUT_FILE = (
    PROJECT_ROOT
    / "Excel_Output"
    / "aiml_bingo"
    / "average_mshr_load_occupancy.xlsx"
)

CACHES = ("L1D", "L2C", "LLC")
CPU_PATTERN = re.compile(r"^CPU\s+(\d+)\s+cumulative IPC:")
OCCUPANCY_PATTERN = re.compile(
    r"^(L1D|L2C|LLC)\s+Average MSHR (?:Load )?Occupancy:\s+([^\s]+)"
)


def natural_sort_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", str(value))
    ]


def parse_roi_occupancy(result_file):
    """Return ``{cpu_id: {cache_name: printed_value}}`` for one result file."""
    metrics_by_cpu = {}
    in_roi = False
    current_cpu = None

    with result_file.open(errors="ignore") as stream:
        for raw_line in stream:
            line = raw_line.strip()

            if line == "Region of Interest Statistics":
                in_roi = True
                current_cpu = None
                continue

            if not in_roi:
                continue

            cpu_match = CPU_PATTERN.match(line)
            if cpu_match:
                current_cpu = int(cpu_match.group(1))
                metrics_by_cpu.setdefault(current_cpu, {})
                continue

            occupancy_match = OCCUPANCY_PATTERN.match(line)
            if occupancy_match and current_cpu is not None:
                cache_name, occupancy = occupancy_match.groups()
                metrics_by_cpu[current_cpu][cache_name] = occupancy

    return metrics_by_cpu


def collect_records(results_dir):
    folder_records = {}

    folders = [results_dir] + [
        path for path in results_dir.rglob("*") if path.is_dir()
    ]
    for folder in sorted(folders, key=natural_sort_key):
        records = []

        for result_file in sorted(folder.iterdir(), key=natural_sort_key):
            if not result_file.is_file():
                continue

            metrics_by_cpu = parse_roi_occupancy(result_file)
            for cpu_id in sorted(metrics_by_cpu):
                metrics = metrics_by_cpu[cpu_id]
                if any(cache_name in metrics for cache_name in CACHES):
                    records.append(
                        {
                            "trace": result_file.name,
                            "cpu": cpu_id,
                            "metrics": metrics,
                        }
                    )

        if records:
            relative_folder = folder.relative_to(results_dir)
            folder_name = (
                results_dir.name if str(relative_folder) == "." else str(relative_folder)
            )
            folder_records[folder_name] = records

    return folder_records


def make_unique_sheet_name(folder_name, used_names):
    sheet_name = re.sub(r'[:\\/*?\[\]]', "_", folder_name.replace("/", "_"))[:31]
    sheet_name = sheet_name or "Results"
    original_name = sheet_name
    suffix_index = 1

    while sheet_name in used_names:
        suffix = f"_{suffix_index}"
        sheet_name = original_name[: 31 - len(suffix)] + suffix
        suffix_index += 1

    used_names.add(sheet_name)
    return sheet_name


def write_sheet(worksheet, records):
    headers = ["Trace", "CPU"] + [f"{cache} Average MSHR Load Occupancy" for cache in CACHES]
    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for record in sorted(records, key=lambda item: (natural_sort_key(item["trace"]), item["cpu"])):
        worksheet.append(
            [record["trace"], record["cpu"]]
            + [record["metrics"].get(cache_name, "") for cache_name in CACHES]
        )

    worksheet.freeze_panes = "A2"
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(
            max_length + 2, 48
        )


def write_workbook(folder_records, output_file):
    workbook = Workbook()
    workbook.remove(workbook.active)
    used_names = set()

    for folder_name in sorted(folder_records, key=natural_sort_key):
        worksheet = workbook.create_sheet(make_unique_sheet_name(folder_name, used_names))
        write_sheet(worksheet, folder_records[folder_name])

    output_file.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Extract ROI average demand-load MSHR occupancy into Excel."
    )
    parser.add_argument(
        "results_dir",
        nargs="?",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory containing ChampSim output files (searched recursively).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output Excel file path (default: {DEFAULT_OUTPUT_FILE}).",
    )
    args = parser.parse_args()

    if not args.results_dir.is_dir():
        raise SystemExit(f"Results directory does not exist: {args.results_dir}")

    folder_records = collect_records(args.results_dir)
    if not folder_records:
        raise SystemExit(f"No average MSHR occupancy metrics found in {args.results_dir}")

    write_workbook(folder_records, args.output)
    total_rows = sum(len(records) for records in folder_records.values())
    print(f"Extracted {total_rows} row(s) from {len(folder_records)} folder(s)")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
