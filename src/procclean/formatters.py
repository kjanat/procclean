"""Output formatters for process data."""

import csv
import io
import json
from collections.abc import Sequence

from .process_analyzer import ProcessInfo

DEFAULT_COLUMNS = ("pid", "name", "rss_mb", "cpu_percent", "cwd", "ppid", "status")
COLUMN_HEADERS = {
    "pid": "PID",
    "name": "Name",
    "rss_mb": "RAM (MB)",
    "cpu_percent": "CPU%",
    "cwd": "CWD",
    "ppid": "PPID",
    "parent_name": "Parent",
    "status": "Status",
    "cmdline": "Command",
    "username": "User",
}


def _format_cell(col: str, val: object) -> str:
    """Format a single cell value for table output."""
    if col in ("rss_mb", "cpu_percent"):
        return f"{val:.1f}"
    if col == "cwd" and len(str(val)) > 40:
        return "..." + str(val)[-37:]
    if col == "name" and len(str(val)) > 25:
        return str(val)[:25]
    return str(val)


def format_table(procs: list[ProcessInfo], columns: Sequence[str] | None = None) -> str:
    """Format processes as ASCII table."""
    if not procs:
        return "No processes found."

    cols = columns or DEFAULT_COLUMNS
    header_row = [COLUMN_HEADERS.get(c, c) for c in cols]
    rows = [[_format_cell(col, getattr(p, col, "")) for col in cols] for p in procs]

    # Calculate column widths
    widths = [len(h) for h in header_row]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Format output
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_line = (
        "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(header_row)) + "|"
    )
    lines = [sep, header_line, sep]
    lines.extend(
        "|" + "|".join(f" {c:<{widths[i]}} " for i, c in enumerate(row)) + "|"
        for row in rows
    )
    lines.append(sep)
    return "\n".join(lines)


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


def format_markdown(procs: list[ProcessInfo]) -> str:
    """Format processes as Markdown table."""
    if not procs:
        return "No processes found."

    lines = [
        "| PID | Name | RAM (MB) | CPU% | CWD | PPID | Status |",
        "|-----|------|----------|------|-----|------|--------|",
    ]
    for p in procs:
        cwd = p.cwd if len(p.cwd) <= 30 else "..." + p.cwd[-27:]
        name = p.name if len(p.name) <= 20 else p.name[:20]
        status = p.status
        if p.is_orphan:
            status += " [orphan]"
        if p.in_tmux:
            status += " [tmux]"
        lines.append(
            f"| {p.pid} | {name} | {p.rss_mb:.1f} | {p.cpu_percent:.1f} | {cwd} | {p.ppid} | {status} |"
        )
    return "\n".join(lines)


def format_output(procs: list[ProcessInfo], fmt: str) -> str:
    """Format processes in requested format."""
    formatters = {
        "table": format_table,
        "json": format_json,
        "csv": format_csv,
        "md": format_markdown,
        "markdown": format_markdown,
    }
    formatter = formatters.get(fmt, format_table)
    return formatter(procs)
