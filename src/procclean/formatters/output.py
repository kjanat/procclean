"""Output format functions for process data."""

import csv
import io
import json
from collections.abc import Sequence

from tabulate import tabulate

from procclean.core import ProcessInfo

from .columns import COLUMNS, DEFAULT_COLUMNS


def get_rows(
    procs: list[ProcessInfo],
    columns: Sequence[str] | None = None,
) -> tuple[list[str], list[list[str]]]:
    """Extract headers and formatted rows from processes.

    Args:
        procs: List of processes
        columns: Column keys to include (default: DEFAULT_COLUMNS)

    Returns:
        Tuple of (headers, rows)

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


def format_json(procs: list[ProcessInfo]) -> str:
    """Format processes as JSON."""
    data = [
        {
            "pid": p.pid,
            "name": p.name,
            "cmdline": p.cmdline,
            "cwd": p.cwd,
            "ppid": p.ppid,
            "parent_name": p.parent_name,
            "rss_mb": round(p.rss_mb, 2),
            "cpu_percent": round(p.cpu_percent, 2),
            "username": p.username,
            "is_orphan": p.is_orphan,
            "in_tmux": p.in_tmux,
            "status": p.status,
        }
        for p in procs
    ]
    return json.dumps(data, indent=2)


def format_csv(procs: list[ProcessInfo]) -> str:
    """Format processes as CSV."""
    if not procs:
        return ""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "pid",
        "name",
        "cmdline",
        "cwd",
        "ppid",
        "parent_name",
        "rss_mb",
        "cpu_percent",
        "username",
        "is_orphan",
        "in_tmux",
        "status",
    ])
    for p in procs:
        writer.writerow([
            p.pid,
            p.name,
            p.cmdline,
            p.cwd,
            p.ppid,
            p.parent_name,
            f"{p.rss_mb:.2f}",
            f"{p.cpu_percent:.2f}",
            p.username,
            p.is_orphan,
            p.in_tmux,
            p.status,
        ])
    return output.getvalue()


def format_output(
    procs: list[ProcessInfo],
    fmt: str,
    columns: Sequence[str] | None = None,
) -> str:
    """Format processes in requested format.

    Args:
        procs: List of processes
        fmt: Output format (table, json, csv, md/markdown)
        columns: Column keys for table/md formats

    """
    if fmt == "json":
        return format_json(procs)
    if fmt == "csv":
        return format_csv(procs)
    if fmt in ("md", "markdown"):
        return format_markdown(procs, columns)
    return format_table(procs, columns)
