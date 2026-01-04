"""CLI interface for procclean."""

# Internal helpers - exported for testing
from .commands import (
    _confirm_kill,
    _do_preview,
    _get_kill_targets,
    cmd_groups,
    cmd_kill,
    cmd_list,
    cmd_memory,
    get_filtered_processes,
)
from .parser import create_parser, run_cli

__all__ = [
    "_confirm_kill",
    "_do_preview",
    "_get_kill_targets",
    "cmd_groups",
    "cmd_kill",
    "cmd_list",
    "cmd_memory",
    "create_parser",
    "get_filtered_processes",
    "run_cli",
]
