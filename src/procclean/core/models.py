"""Process data models."""

from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Process information data class."""

    pid: int
    name: str
    cmdline: str
    cwd: str
    ppid: int
    parent_name: str
    rss_mb: float
    cpu_percent: float
    username: str
    create_time: float
    is_orphan: bool
    in_tmux: bool
    status: str

    @property
    def is_orphan_candidate(self) -> bool:
        """Check if process is orphaned (PPID=1 or user systemd)."""
        return self.is_orphan and not self.in_tmux
