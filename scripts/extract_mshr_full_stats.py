#!/usr/bin/env python3
"""Extract L1D/L2C/LLC MSHR statistics from ChampSim results into Excel."""

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
    os.path.join(SCRIPT_DIR, "..", "results_bingo")
)

DEFAULT_OUTPUT_FILE = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "Excel_Output","aiml_bingo", "mshr_full_stats.xlsx")
)

DEFAULT_CACHES = ("L1D", "L2C", "LLC")

MSHR_FULL_PATTERN = re.compile(
    r"^(\S+)\s+MSHR FULL\s+TOTAL:\s+([0-9a-fA-F]+)\s+LOAD:\s+([0-9a-fA-F]+)\s+"
    r"RFO:\s+([0-9a-fA-F]+)\s+PREFETCH:\s+([0-9a-fA-F]+)\s+WRITEBACK:\s+([0-9a-fA-F]+)",
    flags=re.MULTILINE,
)

MSHR_ACCESSED_PATTERN = re.compile(
    r"^(\S+)\s+MSHR ACCESSED:\s+([0-9a-fA-F]+)\s+MSHR FULL ACCESSES:\s+([0-9a-fA-F]+)\s+"
    r"MSHR FULL ACCESS %:\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)",
    flags=re.MULTILINE,
)

FINAL_INSTRUCTIONS_PATTERN = re.compile(
    r"^CPU 0 cumulative IPC:.*?\binstructions:\s+([0-9a-fA-F]+)\b",
    flags=re.MULTILINE,
)


def parse_counter(value):
    """ChampSim prints these counters as hexadecimal values without a 0x prefix."""
    return int(value, 16)


def natural_sort_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def parse_file(filepath):
    with open(filepath, "r", errors="ignore") as result_file:
        content = result_file.read()

    metrics = {}
    instruction_matches = FINAL_INSTRUCTIONS_PATTERN.findall(content)
    instructions = (
        parse_counter(instruction_matches[-1]) if instruction_matches else None
    )

    for match in MSHR_FULL_PATTERN.finditer(content):
        cache_name = match.group(1)
        metrics.setdefault(cache_name, {}).update(
            {
                "mshr_full_total": parse_counter(match.group(2)),
                "mshr_full_load": parse_counter(match.group(3)),
                "mshr_full_rfo": parse_counter(match.group(4)),
                "mshr_full_prefetch": parse_counter(match.group(5)),
                "mshr_full_writeback": parse_counter(match.group(6)),
            }
        )

    for match in MSHR_ACCESSED_PATTERN.finditer(content):
        cache_name = match.group(1)
        metrics.setdefault(cache_name, {}).update(
            {
                "mshr_accessed": parse_counter(match.group(2)),
                "mshr_full_accesses": parse_counter(match.group(3)),
                "mshr_full_access_percent": match.group(4),
            }
        )

    return metrics, instructions


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

            metrics, instructions = parse_file(filepath)

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
                    "instructions": instructions,
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


def get_cache_order(records, requested_caches):
    cache_names = set()

    for record in records:
        cache_names.update(record["metrics"].keys())

    requested_order = [cache.upper() for cache in requested_caches]
    return [
        cache_name
        for cache_name in requested_order
        if cache_name in cache_names
    ] + sorted(
        cache_names - set(requested_order), key=natural_sort_key
    )


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


def write_folder_sheet(worksheet, records, cache_order):
    metric_headers = [
        ("MSHR Accessed", "mshr_accessed"),
        ("MSHR Full Accesses", "mshr_full_accesses"),
        ("MSHR Full Accesses / KI", "mshr_full_accesses_per_ki"),
        ("MSHR Full Access %", "mshr_full_access_percent"),
        ("MSHR Full Total", "mshr_full_total"),
        ("MSHR Full Load", "mshr_full_load"),
        ("MSHR Full RFO", "mshr_full_rfo"),
        ("MSHR Full Prefetch", "mshr_full_prefetch"),
        ("MSHR Full Writeback", "mshr_full_writeback"),
    ]
    sorted_records = sorted(records, key=lambda item: natural_sort_key(item["trace"]))

    for cache_index, cache_name in enumerate(cache_order):
        if cache_index:
            worksheet.append([])

        worksheet.append([f"{cache_name} MSHR Statistics"])
        title_cell = worksheet.cell(row=worksheet.max_row, column=1)
        title_cell.font = Font(bold=True)

        worksheet.append(["Trace"] + [label for label, _ in metric_headers])
        header_row = worksheet.max_row
        for cell in worksheet[header_row]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        for record in sorted_records:
            stats = record["metrics"].get(cache_name, {})
            full_accesses = stats.get("mshr_full_accesses")
            instructions = record["instructions"]
            stats["mshr_full_accesses_per_ki"] = (
                full_accesses * 1000 / instructions
                if full_accesses is not None and instructions
                else ""
            )
            worksheet.append(
                [record["trace"]]
                + [stats.get(key, "") for _, key in metric_headers]
            )

    worksheet.freeze_panes = "B3"

    for column_cells in worksheet.columns:
        max_len = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(
            max_len + 2, 48
        )


def write_workbook(folder_records, output_file, requested_caches):
    workbook = Workbook()
    workbook.remove(workbook.active)

    used_names = set()

    for folder_name in sorted(folder_records, key=natural_sort_key):
        records = folder_records[folder_name]
        worksheet = workbook.create_sheet(
            make_unique_sheet_name(folder_name, used_names)
        )
        write_folder_sheet(
            worksheet,
            records,
            get_cache_order(records, requested_caches),
        )

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

    write_workbook(folder_records, args.output, requested_caches)

    total_files = sum(len(records) for records in folder_records.values())
    print(f"Extracted {total_files} files from {len(folder_records)} folders")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
