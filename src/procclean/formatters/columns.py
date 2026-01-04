"""Column specifications for process tables."""

from collections.abc import Callable
from dataclasses import dataclass

from procclean.core import ProcessInfo


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


def get_available_columns() -> list[str]:
    """Return list of available column keys."""
    return list(COLUMNS.keys())
