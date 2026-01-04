"""Process kill actions."""

import psutil


def kill_process(pid: int, force: bool = False) -> tuple[bool, str]:
    """Kill a process by PID.

    Args:
        pid: Process ID to kill.
        force: If True, force kill the process; otherwise, terminate gracefully.

    Returns:
        A tuple of (success, message) indicating whether the operation succeeded and
        providing a human-readable message.
    """
    try:
        proc = psutil.Process(pid)
        if force:
            proc.kill()
        else:
            proc.terminate()
        return True, f"Process {pid} terminated"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Access denied for process {pid}"
    except OSError as e:
        return False, f"Error: {e}"


def kill_processes(pids: list[int], force: bool = False) -> list[tuple[int, bool, str]]:
    """Kill multiple processes.

    Args:
        pids: Process IDs to kill.
        force: If True, force kill the processes; otherwise, terminate gracefully.

    Returns:
        A list of tuples (pid, success, message) for each PID attempted.
    """
    results: list[tuple[int, bool, str]] = []
    for pid in pids:
        success, msg = kill_process(pid, force)
        results.append((pid, success, msg))
    return results
