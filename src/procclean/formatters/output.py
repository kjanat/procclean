"""Output format functions for process data."""

import csv
import io
import json
from collections.abc import Sequence
from dataclasses import asdict, fields

from tabulate import tabulate

from procclean.core import ProcessInfo

from .columns import COLUMNS, DEFAULT_COLUMNS


def get_rows(
    procs: list[ProcessInfo],
    columns: Sequence[str] | None = None,
) -> tuple[list[str], list[list[str]]]:
    """Extract headers and formatted rows from processes."""
    cols = columns or DEFAULT_COLUMNS
    specs = [COLUMNS[c] for c in cols if c in COLUMNS]
    headers = [s.header for s in specs]
    rows = [[s.extract(p) for s in specs] for p in procs]
    return headers, rows


def format_table(
    procs: list[ProcessInfo],
    columns: Sequence[str] | None = None,
) -> str:
    """Format processes as ASCII table."""
    if not procs:
        return "No processes found."
    headers, rows = get_rows(procs, columns)
    return tabulate(rows, headers=headers, tablefmt="simple_outline")


def format_markdown(
    procs: list[ProcessInfo],
    columns: Sequence[str] | None = None,
) -> str:
    """Format processes as GitHub-flavored Markdown table."""
    if not procs:
        return "No processes found."
    headers, rows = get_rows(procs, columns)
    return tabulate(rows, headers=headers, tablefmt="pipe")


def _serialize_process(p: ProcessInfo) -> dict:
    """Convert process to JSON-serializable dict with rounded floats."""
    data = asdict(p)
    data["rss_mb"] = round(data["rss_mb"], 2)
    data["cpu_percent"] = round(data["cpu_percent"], 2)
    return data


def format_json(procs: list[ProcessInfo]) -> str:
    """Format processes as JSON."""
    return json.dumps([_serialize_process(p) for p in procs], indent=2)


def format_csv(procs: list[ProcessInfo]) -> str:
    """Format processes as CSV."""
    if not procs:
        return ""
    output = io.StringIO()
    writer = csv.writer(output)

    # Get field names from dataclass
    fieldnames = [f.name for f in fields(ProcessInfo)]
    writer.writerow(fieldnames)

    for p in procs:
        row = []
        for name in fieldnames:
            val = getattr(p, name)
            if isinstance(val, float):
                val = f"{val:.2f}"
            row.append(val)
        writer.writerow(row)

    return output.getvalue()


def format_output(
    procs: list[ProcessInfo],
    fmt: str,
    columns: Sequence[str] | None = None,
) -> str:
    """Format processes in requested format."""
    match fmt:
        case "json":
            return format_json(procs)
        case "csv":
            return format_csv(procs)
        case "md" | "markdown":
            return format_markdown(procs, columns)
        case _:
            return format_table(procs, columns)
