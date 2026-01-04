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
    """Extract headers and formatted rows from processes.

    Args:
        procs: Processes to extract rows from.
        columns: Optional ordered list of column keys to include.

    Returns:
        A tuple of (headers, rows), where headers is a list of column headers and
        rows is a list of formatted string rows.
    """
    cols = columns or DEFAULT_COLUMNS
    specs = [COLUMNS[c] for c in cols if c in COLUMNS]
    headers = [s.header for s in specs]
    rows = [[s.extract(p) for s in specs] for p in procs]
    return headers, rows


def format_table(
    procs: list[ProcessInfo],
    columns: Sequence[str] | None = None,
) -> str:
    """Format processes as ASCII table.

    Args:
        procs: Processes to format.
        columns: Optional ordered list of column keys to include.

    Returns:
        A formatted ASCII table string, or a message if no processes are found.
    """
    if not procs:
        return "No processes found."
    headers, rows = get_rows(procs, columns)
    return tabulate(rows, headers=headers, tablefmt="simple_outline")


def format_markdown(
    procs: list[ProcessInfo],
    columns: Sequence[str] | None = None,
) -> str:
    """Format processes as a GitHub-flavored Markdown table.

    Args:
        procs: Processes to format.
        columns: Optional ordered list of column keys to include.

    Returns:
        A formatted Markdown table string, or a message if no processes are found.
    """
    if not procs:
        return "No processes found."
    headers, rows = get_rows(procs, columns)
    return tabulate(rows, headers=headers, tablefmt="pipe")


def _serialize_process(p: ProcessInfo) -> dict:
    """Convert a process to a JSON-serializable dictionary.

    Float values are rounded to 2 decimal places for stable output.

    Args:
        p: Process to serialize.

    Returns:
        A JSON-serializable dict representation of the process.
    """
    data = asdict(p)
    data["rss_mb"] = round(data["rss_mb"], 2)
    data["cpu_percent"] = round(data["cpu_percent"], 2)
    return data


def format_json(procs: list[ProcessInfo]) -> str:
    """Format processes as JSON.

    Args:
        procs: Processes to format.

    Returns:
        A pretty-printed JSON string representing the processes.
    """
    return json.dumps([_serialize_process(p) for p in procs], indent=2)


def format_csv(procs: list[ProcessInfo]) -> str:
    """Format processes as CSV.

    Args:
        procs: Processes to format.

    Returns:
        A CSV string representing the processes. If no processes are provided,
        returns an empty string.
    """
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
    """Format processes in the requested format.

    Args:
        procs: Processes to format.
        fmt: Output format key (e.g., "json", "csv", "md"/"markdown").
        columns: Optional ordered list of column keys to include (table/markdown).

    Returns:
        The formatted output string.
    """
    match fmt:
        case "json":
            return format_json(procs)
        case "csv":
            return format_csv(procs)
        case "md" | "markdown":
            return format_markdown(procs, columns)
        case _:
            return format_table(procs, columns)
