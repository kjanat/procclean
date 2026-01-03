"""Output formatters for process data."""

import csv
import io
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from tabulate import tabulate

from .process_analyzer import ProcessInfo


def clip_right(s: str, max_len: int) -> str:
    """Truncate string from right, keeping left portion."""
    return s if len(s) <= max_len else s[:max_len]


def clip_left(s: str, max_len: int) -> str:
    """Truncate string from left, keeping right portion with ellipsis."""
    return s if len(s) <= max_len else "..." + s[-(max_len - 3) :]


def fmt_float1(v: object) -> str:
    """Format as float with 1 decimal."""
    return f"{float(v):.1f}"  # type: ignore[arg-type]


def fmt_status(p: ProcessInfo) -> str:
    """Format status with optional markers."""
    status = p.status
    if p.is_orphan:
        status += " [orphan]"
    if p.in_tmux:
        status += " [tmux]"
    return status


@dataclass(frozen=True)
class ColumnSpec:
    """Specification for a table column."""

    key: str
    header: str
    get: Callable[[ProcessInfo], object]
    fmt: Callable[[object], str] = str
    max_width: int | None = None

    def extract(self, proc: ProcessInfo) -> str:
        """Extract and format value from process."""
        raw = self.get(proc)
        formatted = self.fmt(raw)
        if self.max_width and len(formatted) > self.max_width:
            # Use clip_left for paths (cwd), clip_right for names
            if self.key == "cwd":
                return clip_left(formatted, self.max_width)
            return clip_right(formatted, self.max_width)
        return formatted


# Column definitions - single source of truth
COLUMNS: dict[str, ColumnSpec] = {
    "pid": ColumnSpec("pid", "PID", lambda p: p.pid),
    "name": ColumnSpec("name", "Name", lambda p: p.name, max_width=25),
    "rss_mb": ColumnSpec("rss_mb", "RAM (MB)", lambda p: p.rss_mb, fmt_float1),
    "cpu_percent": ColumnSpec(
        "cpu_percent", "CPU%", lambda p: p.cpu_percent, fmt_float1
    ),
    "cwd": ColumnSpec("cwd", "CWD", lambda p: p.cwd, max_width=40),
    "ppid": ColumnSpec("ppid", "PPID", lambda p: p.ppid),
    "parent_name": ColumnSpec(
        "parent_name", "Parent", lambda p: p.parent_name, max_width=15
    ),
    "status": ColumnSpec("status", "Status", fmt_status),
    "cmdline": ColumnSpec("cmdline", "Command", lambda p: p.cmdline, max_width=60),
    "username": ColumnSpec("username", "User", lambda p: p.username),
}

DEFAULT_COLUMNS: tuple[str, ...] = (
    "pid",
    "name",
    "rss_mb",
    "cpu_percent",
    "cwd",
    "ppid",
    "status",
)


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


def get_available_columns() -> list[str]:
    """Return list of available column keys."""
    return list(COLUMNS.keys())
