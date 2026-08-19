#!/usr/bin/env python3
"""Extract ROI retirement-distribution statistics into one Excel sheet per folder."""

import os
import re

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
except ImportError:
    raise SystemExit(
        "The 'openpyxl' library is required. Install it with: pip install openpyxl"
    )


# --------------------------- USER SETTINGS ---------------------------
# Set these three paths/names before running the script.
RESULTS_DIR = "../results/speedup/test/"
OUTPUT_DIR = "../Excel_Output/ROB_stall/"
EXCEL_OUTPUT_FILE = "test-rob_retirement_distribution.xlsx"
# ---------------------------------------------------------------------

RETIREMENT_DISTRIBUTION_PATTERN = re.compile(
    r"^\s*RETIREMENT_DISTRIBUTION:\s*"
    r"RETIRED_0:\s*(\d+)\s+"
    r"RETIRED_1:\s*(\d+)\s+"
    r"RETIRED_2:\s*(\d+)\s+"
    r"RETIRED_3:\s*(\d+)\s+"
    r"RETIRED_4:\s*(\d+)\s+"
    r"RETIRED_GT_4:\s*(\d+)",
    re.MULTILINE,
)

SUMMARY_PATTERN = re.compile(
    r"^\s*RETIRED_INSTRUCTIONS:\s*(\d+)\s+"
    r"LOST_RETIREMENT_SLOTS:\s*(\d+)",
    re.MULTILINE,
)


def natural_sort_key(value):
    """Sort names naturally: trace.2 before trace.10."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def parse_file(filepath):
    """Return the ROI retirement histogram, or None if the file lacks it."""
    with open(filepath, "r", errors="ignore") as result_file:
        content = result_file.read()

    distribution_match = RETIREMENT_DISTRIBUTION_PATTERN.search(content)
    if distribution_match is None:
        return None

    metrics = {
        "retired_0": int(distribution_match.group(1)),
        "retired_1": int(distribution_match.group(2)),
        "retired_2": int(distribution_match.group(3)),
        "retired_3": int(distribution_match.group(4)),
        "retired_4": int(distribution_match.group(5)),
        "retired_gt_4": int(distribution_match.group(6)),
        "retired_instructions": "N/A",
        "lost_retirement_slots": "N/A",
    }

    summary_match = SUMMARY_PATTERN.search(content)
    if summary_match is not None:
        metrics["retired_instructions"] = int(summary_match.group(1))
        metrics["lost_retirement_slots"] = int(summary_match.group(2))

    return metrics


def collect_records(results_dir):
    """Group trace records by the folder directly containing their result files."""
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

        # A folder containing valid result files becomes one Excel worksheet.
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
    """Convert a folder path into a unique Excel-compatible worksheet name."""
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
    """Write one results folder to a formatted worksheet."""
    worksheet.append(
        [
            "Trace",
            "RETIRED_0 Cycles",
            "RETIRED_1 Cycles",
            "RETIRED_2 Cycles",
            "RETIRED_3 Cycles",
            "RETIRED_4 Cycles",
            "RETIRED_GT_4 Cycles",
            "RETIRED_INSTRUCTIONS",
            "LOST_RETIREMENT_SLOTS",
        ]
    )

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for record in sorted(records, key=lambda item: natural_sort_key(item["trace"])):
        metrics = record["metrics"]
        worksheet.append([
            record["trace"],
            metrics["retired_0"],
            metrics["retired_1"],
            metrics["retired_2"],
            metrics["retired_3"],
            metrics["retired_4"],
            metrics["retired_gt_4"],
            metrics["retired_instructions"],
            metrics["lost_retirement_slots"],
        ])

    worksheet.freeze_panes = "B2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column_cells in worksheet.columns:
        max_length = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(
            max_length + 2,
            90,
        )


def write_workbook(folder_records, output_file):
    """Create the workbook, following the same per-folder-sheet layout."""
    workbook = Workbook()
    workbook.remove(workbook.active)
    used_names = set()

    for folder_name in sorted(folder_records, key=natural_sort_key):
        worksheet = workbook.create_sheet(
            title=make_unique_sheet_name(folder_name, used_names)
        )
        write_sheet(worksheet, folder_records[folder_name])

    workbook.save(output_file)


def main():
    if not os.path.isdir(RESULTS_DIR):
        raise SystemExit(f"Results directory not found: {RESULTS_DIR}")

    folder_records = collect_records(RESULTS_DIR)
    if not folder_records:
        raise SystemExit(
            "No RETIREMENT_DISTRIBUTION lines found under: "
            f"{RESULTS_DIR}"
        )

    output_file = os.path.abspath(os.path.join(OUTPUT_DIR, EXCEL_OUTPUT_FILE))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    write_workbook(folder_records, output_file)

    total_files = sum(len(records) for records in folder_records.values())
    print(f"Wrote {total_files} result files across {len(folder_records)} sheets.")
    print(f"Output: {output_file}")
    print("\nSheets created:")
    for folder_name in sorted(folder_records, key=natural_sort_key):
        print(f"  {folder_name}: {len(folder_records[folder_name])} files")


if __name__ == "__main__":
    main()
