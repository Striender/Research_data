#!/usr/bin/env python3
"""Extract MSHR full breakdown and MSHR access stats from ChampSim results."""

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
    os.path.join(SCRIPT_DIR, "..", "Excel_Output","baseline", "mshr_full_stats.xlsx")
)

DEFAULT_CACHES = ("L1D", "L2C", "LLC")

MSHR_FULL_PATTERN = re.compile(
    r"^(\S+)\s+MSHR FULL\s+TOTAL:\s+(\d+)\s+LOAD:\s+(\d+)\s+"
    r"RFO:\s+(\d+)\s+PREFETCH:\s+(\d+)\s+WRITEBACK:\s+(\d+)",
    flags=re.MULTILINE,
)

MSHR_ACCESSED_PATTERN = re.compile(
    r"^(\S+)\s+MSHR ACCESSED:\s+(\d+)\s+MSHR FULL ACCESSES:\s+(\d+)\s+"
    r"MSHR FULL ACCESS %:\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
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

    for match in MSHR_FULL_PATTERN.finditer(content):
        cache_name = match.group(1)
        metrics.setdefault(cache_name, {}).update(
            {
                "mshr_full_total": int(match.group(2)),
                "mshr_full_load": int(match.group(3)),
                "mshr_full_rfo": int(match.group(4)),
                "mshr_full_prefetch": int(match.group(5)),
                "mshr_full_writeback": int(match.group(6)),
            }
        )

    for match in MSHR_ACCESSED_PATTERN.finditer(content):
        cache_name = match.group(1)
        metrics.setdefault(cache_name, {}).update(
            {
                "mshr_accessed": int(match.group(2)),
                "mshr_full_accesses": int(match.group(3)),
                "mshr_full_access_percent": match.group(4),
            }
        )

    return metrics


def collect_records(results_dir, requested_caches):
    folder_records = {}
    requested = {cache.upper() for cache in requested_caches}

    for root, directories, files in os.walk(results_dir):
        directories.sort(key=natural_sort_key)
        records = []

        for filename in sorted(files, key=natural_sort_key):
            filepath = os.path.join(root, filename)

            if not os.path.isfile(filepath):
                continue

            metrics = parse_file(filepath)

            if requested:
                metrics = {
                    cache_name: stats
                    for cache_name, stats in metrics.items()
                    if cache_name.upper() in requested
                }

            if not metrics:
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


def get_cache_order(records):
    cache_names = set()

    for record in records:
        cache_names.update(record["metrics"].keys())

    return sorted(cache_names, key=natural_sort_key)


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


def write_cache_sheet(worksheet, records, cache_name):
    headers = [
        "Trace",
        "MSHR Accessed",
        "MSHR Full Accesses",
        "MSHR Full Access %",
        "MSHR Full Total",
        "MSHR Full Load",
        "MSHR Full RFO",
        "MSHR Full Prefetch",
        "MSHR Full Writeback",
    ]

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for record in sorted(records, key=lambda item: natural_sort_key(item["trace"])):
        stats = record["metrics"].get(cache_name, {})
        worksheet.append(
            [
                record["trace"],
                stats.get("mshr_accessed", ""),
                stats.get("mshr_full_accesses", ""),
                stats.get("mshr_full_access_percent", ""),
                stats.get("mshr_full_total", ""),
                stats.get("mshr_full_load", ""),
                stats.get("mshr_full_rfo", ""),
                stats.get("mshr_full_prefetch", ""),
                stats.get("mshr_full_writeback", ""),
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
        records = folder_records[folder_name]

        for cache_name in get_cache_order(records):
            sheet_base_name = f"{cache_name}"
            worksheet = workbook.create_sheet(
                make_unique_sheet_name(sheet_base_name, used_names)
            )
            write_cache_sheet(worksheet, records, cache_name)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    workbook.save(output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Extract MSHR full/accessed stats from result files."
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
    parser.add_argument(
        "--cache",
        action="append",
        default=None,
        help=(
            "Cache level to extract, e.g. --cache L2C. Can be used multiple times. "
            "Default: L1D, L2C, LLC."
        ),
    )

    args = parser.parse_args()
    requested_caches = args.cache if args.cache is not None else DEFAULT_CACHES

    folder_records = collect_records(args.results_dir, requested_caches)

    if not folder_records:
        raise SystemExit(f"No MSHR full/accessed stats found in {args.results_dir}")

    write_workbook(folder_records, args.output)

    total_files = sum(len(records) for records in folder_records.values())
    print(f"Extracted {total_files} files from {len(folder_records)} folders")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
