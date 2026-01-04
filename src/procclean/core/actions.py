"""Process kill actions."""

import psutil


def kill_process(pid: int, force: bool = False) -> tuple[bool, str]:
    """Kill a process by PID."""
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
    except Exception as e:
        return False, f"Error: {e}"


def kill_processes(pids: list[int], force: bool = False) -> list[tuple[int, bool, str]]:
    """Kill multiple processes."""
    results = []
    for pid in pids:
        success, msg = kill_process(pid, force)
        results.append((pid, success, msg))
    return results
