"""Memory summary utilities."""

import psutil


def get_memory_summary() -> dict:
    """Get system memory summary.

    Returns:
        dict: A dictionary containing total, used, and available memory in GB,
        memory usage percentage, and swap usage/total in GB.
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": mem.total / 1024**3,
        "used_gb": mem.used / 1024**3,
        "free_gb": mem.available / 1024**3,
        "percent": mem.percent,
        "swap_used_gb": swap.used / 1024**3,
        "swap_total_gb": swap.total / 1024**3,
    }
