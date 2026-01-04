"""Column specifications for process tables."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum, auto
from typing import Self

from procclean.core import ProcessInfo


class ClipSide(StrEnum):
    """Which side to truncate when clipping."""

    LEFT = auto()  # Keep right portion (good for paths)
    RIGHT = auto()  # Keep left portion (good for names)


def clip(s: str, max_len: int, side: ClipSide = ClipSide.RIGHT) -> str:
    """Truncate string, adding ellipsis on clipped side."""
    if len(s) <= max_len:
        return s
    match side:
        case ClipSide.LEFT:
            return f"...{s[-(max_len - 3) :]}"
        case ClipSide.RIGHT:
            return f"{s[: max_len - 3]}..."


@dataclass(frozen=True, slots=True)
class ColumnSpec[T]:
    """Specification for a table column."""

    key: str
    header: str
    get: Callable[[ProcessInfo], T]
    fmt: Callable[[T], str] = str
    max_width: int | None = None
    clip_side: ClipSide = ClipSide.RIGHT

    def extract(self, proc: ProcessInfo) -> str:
        """Extract and format value from process."""
        formatted = self.fmt(self.get(proc))
        if self.max_width and len(formatted) > self.max_width:
            return clip(formatted, self.max_width, self.clip_side)
        return formatted

    def with_width(self, width: int, side: ClipSide = ClipSide.RIGHT) -> Self:
        """Return a copy with specified max width and clip side."""
        return replace(self, max_width=width, clip_side=side)


def _fmt_float1(v: float) -> str:
    return f"{v:.1f}"


def _fmt_status(p: ProcessInfo) -> str:
    parts = [p.status]
    if p.is_orphan:
        parts.append("[orphan]")
    if p.in_tmux:
        parts.append("[tmux]")
    return " ".join(parts)


# Column definitions
COLUMNS: dict[str, ColumnSpec] = {
    "pid": ColumnSpec("pid", "PID", lambda p: p.pid),
    "name": ColumnSpec("name", "Name", lambda p: p.name, max_width=25),
    "rss_mb": ColumnSpec("rss_mb", "RAM (MB)", lambda p: p.rss_mb, _fmt_float1),
    "cpu_percent": ColumnSpec(
        "cpu_percent", "CPU%", lambda p: p.cpu_percent, _fmt_float1
    ),
    "cwd": ColumnSpec(
        "cwd", "CWD", lambda p: p.cwd, max_width=40, clip_side=ClipSide.LEFT
    ),
    "ppid": ColumnSpec("ppid", "PPID", lambda p: p.ppid),
    "parent_name": ColumnSpec(
        "parent_name", "Parent", lambda p: p.parent_name, max_width=15
    ),
    "status": ColumnSpec("status", "Status", lambda p: p, _fmt_status),
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
    return list(COLUMNS)
