"""Process filtering and sorting utilities."""

import fnmatch

import psutil

from .constants import CRITICAL_SERVICES, SYSTEM_EXE_PATHS
from .models import ProcessInfo


def is_system_service(proc: ProcessInfo) -> bool:
    """Check if process is a system service that shouldn't be killed.

    Uses two heuristics:
    1. Exe path in system directories (/usr/lib, /usr/libexec)
    2. Name matches critical services list (shells, audio, display)

    Returns:
        True if the process looks like a system/critical service, otherwise False.
    """
    # Check exe path - most system services live in /usr/lib
    try:
        exe = psutil.Process(proc.pid).exe() or ""
        if exe.startswith(SYSTEM_EXE_PATHS):
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    # Check critical services by name
    return proc.name.lower() in {s.lower() for s in CRITICAL_SERVICES}


def filter_orphans(procs: list[ProcessInfo]) -> list[ProcessInfo]:
    """Filter to only orphaned processes.

    Args:
        procs: List of processes to filter.

    Returns:
        Processes that are marked as orphaned.
    """
    return [p for p in procs if p.is_orphan]


def filter_killable(procs: list[ProcessInfo]) -> list[ProcessInfo]:
    """Filter to orphaned processes that are safe to kill.

    Returns:
        Processes that are:
        - Orphaned (parent is init/systemd)
        - Not running in tmux
        - Not a system service (GNOME, pipewire, etc.)
    """
    return [p for p in procs if p.is_orphan_candidate and not is_system_service(p)]


def filter_high_memory(
    procs: list[ProcessInfo], threshold_mb: float = 500.0
) -> list[ProcessInfo]:
    """Filter to processes using more than threshold memory.

    Args:
        procs: List of processes to filter.
        threshold_mb: Memory threshold in MB.

    Returns:
        Processes whose RSS memory usage is greater than threshold_mb.
    """
    return [p for p in procs if p.rss_mb > threshold_mb]


def filter_by_cwd(procs: list[ProcessInfo], cwd_path: str) -> list[ProcessInfo]:
    """Filter processes by current working directory.

    Args:
        procs: List of processes to filter
        cwd_path: Path to match. If contains '*', uses glob matching.
                  Otherwise, uses prefix matching.

    Returns:
        Processes whose cwd starts with cwd_path (or matches glob pattern)
    """
    if "*" in cwd_path or "?" in cwd_path:
        # Glob matching
        return [p for p in procs if p.cwd and fnmatch.fnmatch(p.cwd, cwd_path)]
    # Prefix matching (normalized)
    cwd_path = cwd_path.rstrip("/")
    return [
        p
        for p in procs
        if p.cwd
        and p.cwd != "?"
        and (p.cwd == cwd_path or p.cwd.startswith(cwd_path + "/"))
    ]


def sort_processes(
    procs: list[ProcessInfo],
    sort_by: str = "memory",
    reverse: bool = True,
) -> list[ProcessInfo]:
    """Sort processes by given key.

    Args:
        procs: List of processes to sort
        sort_by: One of 'memory', 'cpu', 'pid', 'name', 'cwd'
        reverse: If True, sort descending (default for numeric)

    Returns:
        A new list of processes sorted by the requested key.
    """
    sort_keys = {
        "memory": lambda p: p.rss_mb,
        "mem": lambda p: p.rss_mb,
        "cpu": lambda p: p.cpu_percent,
        "pid": lambda p: p.pid,
        "name": lambda p: p.name.lower(),
        "cwd": lambda p: p.cwd.lower() if p.cwd else "",
    }
    key_func = sort_keys.get(sort_by, sort_keys["memory"])
    return sorted(procs, key=key_func, reverse=reverse)
