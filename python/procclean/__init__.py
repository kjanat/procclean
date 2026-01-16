"""
procclean - Interactive TUI for exploring and cleaning up processes

This is a Python wrapper around the Rust implementation of procclean.
The core functionality is implemented in Rust for performance,
with Python bindings provided via PyO3.
"""

__version__ = "3.0.0"

# Import Rust bindings
try:
    from procclean._procclean import (
        ProcessInfo,
        MemorySummary,
        get_processes,
        get_memory,
        kill_process_py as kill_process,
        filter_orphans_py as filter_orphans,
        filter_killable_py as filter_killable,
    )

    _has_rust = True
except ImportError:
    _has_rust = False
    ProcessInfo = None
    MemorySummary = None
    get_processes = None
    get_memory = None
    kill_process = None
    filter_orphans = None
    filter_killable = None

# Import CLI entry point
from procclean.__main__ import main

__all__ = [
    "__version__",
    "main",
    "ProcessInfo",
    "MemorySummary",
    "get_processes",
    "get_memory",
    "kill_process",
    "filter_orphans",
    "filter_killable",
]
