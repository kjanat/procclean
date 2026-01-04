"""Process listing and grouping utilities."""

import os
from pathlib import Path

import psutil

from .models import ProcessInfo


def get_tmux_env(pid: int) -> bool:
    """Check if process has TMUX environment variable."""
    try:
        environ_path = Path(f"/proc/{pid}/environ")
        if environ_path.exists():
            environ = environ_path.read_bytes().decode("utf-8", errors="ignore")
            return "TMUX=" in environ
    except PermissionError, FileNotFoundError, ProcessLookupError:
        pass
    return False


def get_cwd(pid: int) -> str:
    """Get process working directory."""
    try:
        return os.readlink(f"/proc/{pid}/cwd")
    except PermissionError, FileNotFoundError, ProcessLookupError:
        return "?"


def get_process_list(
    sort_by: str = "memory",
    filter_user: str | None = None,
    min_memory_mb: float = 10.0,
) -> list[ProcessInfo]:
    """Get list of processes with detailed info."""
    processes = []
    current_user = os.getlogin()
    filter_user = filter_user or current_user

    for proc in psutil.process_iter([
        "pid",
        "name",
        "cmdline",
        "ppid",
        "memory_info",
        "cpu_percent",
        "username",
        "create_time",
        "status",
    ]):
        try:
            info = proc.info
            if info["username"] != filter_user:
                continue

            rss_mb = (
                (info["memory_info"].rss / 1024 / 1024) if info["memory_info"] else 0
            )
            if rss_mb < min_memory_mb:
                continue

            ppid = info["ppid"] or 0
            try:
                parent = psutil.Process(ppid)
                parent_name = parent.name()
            except psutil.NoSuchProcess, psutil.AccessDenied:
                parent_name = "?"

            # Check if orphaned (parent is init/systemd)
            is_orphan = ppid == 1 or parent_name in ("systemd", "init")

            cmdline = " ".join(info["cmdline"] or [])[:200]
            if not cmdline:
                cmdline = info["name"]

            processes.append(
                ProcessInfo(
                    pid=info["pid"],
                    name=info["name"],
                    cmdline=cmdline,
                    cwd=get_cwd(info["pid"]),
                    ppid=ppid,
                    parent_name=parent_name,
                    rss_mb=rss_mb,
                    cpu_percent=info["cpu_percent"] or 0,
                    username=info["username"],
                    create_time=info["create_time"] or 0,
                    is_orphan=is_orphan,
                    in_tmux=get_tmux_env(info["pid"]) if is_orphan else False,
                    status=info["status"] or "?",
                )
            )
        except psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess:
            continue

    if sort_by == "memory":
        processes.sort(key=lambda p: p.rss_mb, reverse=True)
    elif sort_by == "cpu":
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)
    elif sort_by == "name":
        processes.sort(key=lambda p: p.name.lower())

    return processes


def find_similar_processes(
    processes: list[ProcessInfo],
) -> dict[str, list[ProcessInfo]]:
    """Group processes by similar command patterns."""
    groups: dict[str, list[ProcessInfo]] = {}

    for proc in processes:
        # Extract key identifier from cmdline
        cmd = proc.cmdline.split()[0] if proc.cmdline else proc.name
        # Normalize paths
        if "/" in cmd:
            cmd = cmd.split("/")[-1]

        if cmd not in groups:
            groups[cmd] = []
        groups[cmd].append(proc)

    # Only return groups with multiple processes
    return {k: v for k, v in groups.items() if len(v) > 1}
