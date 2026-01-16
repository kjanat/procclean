"""Type stubs for procclean"""

from typing import Optional

__version__: str

class ProcessInfo:
    """Information about a process"""

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
    exe_deleted: bool

    def is_orphan_candidate(self) -> bool: ...
    def display_status(self) -> str: ...

class MemorySummary:
    """System memory summary"""

    total_gb: float
    used_gb: float
    free_gb: float
    percent: float
    swap_total_gb: float
    swap_used_gb: float

def get_processes(
    sort_by: Optional[str] = None, min_memory_mb: Optional[float] = None
) -> list[ProcessInfo]:
    """Get list of processes"""
    ...

def get_memory() -> MemorySummary:
    """Get memory summary"""
    ...

def kill_process(pid: int, force: Optional[bool] = None) -> tuple[bool, str]:
    """Kill a process"""
    ...

def filter_orphans(processes: list[ProcessInfo]) -> list[ProcessInfo]:
    """Filter orphan processes"""
    ...

def filter_killable(processes: list[ProcessInfo]) -> list[ProcessInfo]:
    """Filter killable processes"""
    ...

def main() -> None:
    """Main entry point"""
    ...
