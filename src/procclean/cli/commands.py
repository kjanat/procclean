"""CLI command handlers."""

import argparse
import json
import sys
from pathlib import Path

from rich import print  # pylint: disable=redefined-builtin

from procclean.core import (
    PREVIEW_LIMIT,
    filter_by_cwd,
    filter_high_memory,
    filter_killable,
    filter_orphans,
    find_similar_processes,
    get_memory_summary,
    get_process_list,
    kill_processes,
    sort_processes,
)
from procclean.formatters import format_output


def cmd_list(args: argparse.Namespace) -> int:
    """List processes command.

    Returns:
        int: Exit code (0 on success).
    """
    procs = get_filtered_processes(args)

    # Apply sorting
    reverse = not args.ascending
    procs = sort_processes(procs, sort_by=args.sort, reverse=reverse)

    # Limit output
    if args.limit:
        procs = procs[: args.limit]

    # Parse columns
    columns = args.columns.split(",") if args.columns else None

    print(format_output(procs, args.format, columns=columns))
    return 0


def cmd_groups(args: argparse.Namespace) -> int:
    """Show grouped processes command.

    Returns:
        int: Exit code (0 on success).
    """
    procs = get_process_list(min_memory_mb=args.min_memory)
    groups = find_similar_processes(procs)

    if not groups:
        print("No process groups found.")
        return 0

    if args.format == "json":
        data = {
            cmd: [
                {"pid": p.pid, "name": p.name, "rss_mb": round(p.rss_mb, 2)}
                for p in group_procs
            ]
            for cmd, group_procs in groups.items()
        }
        print(json.dumps(data, indent=2))
    else:
        for cmd, group_procs in sorted(
            groups.items(), key=lambda x: sum(p.rss_mb for p in x[1]), reverse=True
        ):
            total_mb = sum(p.rss_mb for p in group_procs)
            print(f"\n{cmd} ({len(group_procs)} processes, {total_mb:.1f} MB total)")
            for p in sorted(group_procs, key=lambda x: x.rss_mb, reverse=True):
                print(f"  PID {p.pid}: {p.rss_mb:.1f} MB")

    return 0


def get_filtered_processes(args: argparse.Namespace) -> list:
    """Get processes with all filters from args applied.

    Returns:
        list: Filtered list of processes.
    """
    procs = get_process_list(min_memory_mb=getattr(args, "min_memory", 5.0))

    # Apply cwd filter
    if getattr(args, "cwd", None) is not None:
        cwd_path = args.cwd or str(Path.cwd())
        procs = filter_by_cwd(procs, cwd_path)

    # Apply preset filters
    filt = getattr(args, "filter", None)
    threshold = getattr(args, "high_memory_threshold", 500.0)
    if filt == "killable" or getattr(args, "killable", False):
        procs = filter_killable(procs)
    elif filt == "orphans" or getattr(args, "orphans", False):
        procs = filter_orphans(procs)
    elif filt == "high-memory" or getattr(args, "high_memory", False):
        procs = filter_high_memory(procs, threshold_mb=threshold)

    return procs


def _get_kill_targets(args: argparse.Namespace) -> list:
    """Get target processes for kill command from PIDs or filters.

    Returns:
        list: Target processes to kill.
    """
    if args.pids:
        all_procs = get_process_list(min_memory_mb=0)
        pid_set = set(args.pids)
        procs = [p for p in all_procs if p.pid in pid_set]
        found_pids = {p.pid for p in procs}
        for pid in args.pids:
            if pid not in found_pids:
                print(f"Warning: PID {pid} not found")
        return procs
    return get_filtered_processes(args)


def _do_preview(args: argparse.Namespace, procs: list) -> int:
    """Show preview of what would be killed.

    Returns:
        int: Exit code (0 on success).
    """
    if hasattr(args, "sort") and args.sort:
        procs = sort_processes(procs, sort_by=args.sort, reverse=True)
    if hasattr(args, "limit") and args.limit:
        procs = procs[: args.limit]
    columns = args.columns.split(",") if getattr(args, "columns", None) else None
    fmt = getattr(args, "out_format", "table")
    print(format_output(procs, fmt, columns=columns))
    print(f"\n{len(procs)} process(es) would be killed.")
    return 0


def _confirm_kill(args: argparse.Namespace, procs: list) -> bool:
    """Prompt for kill confirmation.

    Args:
        args: Parsed CLI arguments.
        procs: Processes that would be killed.

    Returns:
        True if the kill action is confirmed (or confirmation is skipped), otherwise
        False.
    """
    if args.yes or not sys.stdin.isatty():
        return True
    action = "FORCE KILL" if args.force else "terminate"
    print(f"About to {action} {len(procs)} process(es):")
    for p in procs[:PREVIEW_LIMIT]:
        print(f"  {p.pid}: {p.name} ({p.rss_mb:.1f} MB)")
    if len(procs) > PREVIEW_LIMIT:
        print(f"  ... and {len(procs) - PREVIEW_LIMIT} more")
    try:
        response = input("Continue? [y/N] ")
        return response.lower() in {"y", "yes"}
    except EOFError:
        return True  # Non-interactive


def cmd_kill(args: argparse.Namespace) -> int:
    """Kill processes command.

    Returns:
        int: Exit code (0 on success).
    """
    procs = _get_kill_targets(args)
    if not procs:
        print("No processes match the filters.")
        return 0

    if getattr(args, "preview", False):
        return _do_preview(args, procs)

    if not _confirm_kill(args, procs):
        print("Aborted.")
        return 1

    results = kill_processes([p.pid for p in procs], force=args.force)
    exit_code = 0
    for _, success, msg in results:
        status = "OK" if success else "FAILED"
        print(f"[{status}] {msg}")
        if not success:
            exit_code = 1
    return exit_code


def cmd_memory(args: argparse.Namespace) -> int:
    """Show memory summary command.

    Returns:
        int: Exit code (0 on success).
    """
    mem = get_memory_summary()

    if args.format == "json":
        print(json.dumps(mem, indent=2))
    else:
        print(f"Total:  {mem['total_gb']:.2f} GB")
        print(f"Used:   {mem['used_gb']:.2f} GB ({mem['percent']:.1f}%)")
        print(f"Free:   {mem['free_gb']:.2f} GB")
        print(f"Swap:   {mem['swap_used_gb']:.2f} / {mem['swap_total_gb']:.2f} GB")

    return 0
