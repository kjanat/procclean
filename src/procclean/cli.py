"""CLI interface for procclean (non-TUI)."""

import argparse
import json
import os
import sys
from importlib.metadata import version

from .formatters import format_output, get_available_columns
from .process_analyzer import (
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


def cmd_list(args: argparse.Namespace) -> int:
    """List processes command."""
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
    """Show grouped processes command."""
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
    """Get processes with all filters from args applied."""
    procs = get_process_list(min_memory_mb=getattr(args, "min_memory", 5.0))

    # Apply cwd filter
    if getattr(args, "cwd", None) is not None:
        cwd_path = args.cwd or os.getcwd()
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
    """Get target processes for kill command from PIDs or filters."""
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
    """Show preview of what would be killed."""
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
    """Prompt for kill confirmation. Returns True if confirmed."""
    if args.yes or not sys.stdin.isatty():
        return True
    action = "FORCE KILL" if args.force else "terminate"
    print(f"About to {action} {len(procs)} process(es):")
    for p in procs[:5]:
        print(f"  {p.pid}: {p.name} ({p.rss_mb:.1f} MB)")
    if len(procs) > 5:
        print(f"  ... and {len(procs) - 5} more")
    try:
        response = input("Continue? [y/N] ")
        return response.lower() in ("y", "yes")
    except EOFError:
        return True  # Non-interactive


def cmd_kill(args: argparse.Namespace) -> int:
    """Kill processes command."""
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
    for pid, success, msg in results:
        status = "OK" if success else "FAILED"
        print(f"[{status}] {msg}")
        if not success:
            exit_code = 1
    return exit_code


def cmd_memory(args: argparse.Namespace) -> int:
    """Show memory summary command."""
    mem = get_memory_summary()

    if args.format == "json":
        print(json.dumps(mem, indent=2))
    else:
        print(f"Total:  {mem['total_gb']:.2f} GB")
        print(f"Used:   {mem['used_gb']:.2f} GB ({mem['percent']:.1f}%)")
        print(f"Free:   {mem['free_gb']:.2f} GB")
        print(f"Swap:   {mem['swap_used_gb']:.2f} / {mem['swap_total_gb']:.2f} GB")

    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="procclean",
        description="Process cleanup tool with TUI and CLI interfaces.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version('procclean')}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List processes")
    list_parser.add_argument(
        "-f",
        "--format",
        choices=["table", "json", "csv", "md"],
        default="table",
        help="Output format (default: table)",
    )
    list_parser.add_argument(
        "-s",
        "--sort",
        choices=["memory", "mem", "cpu", "pid", "name", "cwd"],
        default="memory",
        help="Sort by field (default: memory)",
    )
    list_parser.add_argument(
        "-a",
        "--ascending",
        action="store_true",
        help="Sort ascending instead of descending",
    )
    list_parser.add_argument(
        "-F",
        "--filter",
        choices=["killable", "orphans", "high-memory"],
        help="Filter preset: killable (orphans, not tmux, not system), orphans, high-memory",
    )
    list_parser.add_argument(
        "-k",
        "--killable",
        action="store_true",
        help="Shorthand for --filter killable",
    )
    list_parser.add_argument(
        "-o",
        "--orphans",
        action="store_true",
        help="Shorthand for --filter orphans",
    )
    list_parser.add_argument(
        "-m",
        "--high-memory",
        action="store_true",
        help="Shorthand for --filter high-memory",
    )
    list_parser.add_argument(
        "--high-memory-threshold",
        type=float,
        default=500.0,
        metavar="MB",
        help="Threshold for high memory filter (default: 500 MB)",
    )
    list_parser.add_argument(
        "--min-memory",
        type=float,
        default=5.0,
        metavar="MB",
        help="Minimum memory to include (default: 5 MB)",
    )
    list_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        metavar="N",
        help="Limit output to N processes",
    )
    list_parser.add_argument(
        "-c",
        "--columns",
        type=str,
        metavar="COLS",
        help=f"Comma-separated columns ({','.join(get_available_columns())})",
    )
    list_parser.add_argument(
        "--cwd",
        nargs="?",
        const="",
        default=None,
        metavar="PATH",
        help="Filter by cwd (no value = current dir, or specify path/glob)",
    )
    list_parser.set_defaults(func=cmd_list)

    # Groups command
    groups_parser = subparsers.add_parser(
        "groups", aliases=["g"], help="Show process groups"
    )
    groups_parser.add_argument(
        "-f",
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    groups_parser.add_argument(
        "--min-memory",
        type=float,
        default=5.0,
        metavar="MB",
        help="Minimum memory to include (default: 5 MB)",
    )
    groups_parser.set_defaults(func=cmd_groups)

    # Kill command
    kill_parser = subparsers.add_parser("kill", help="Kill process(es)")
    kill_parser.add_argument(
        "pids",
        type=int,
        nargs="*",
        metavar="PID",
        help="Process ID(s) to kill (or use filters)",
    )
    kill_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force kill (SIGKILL instead of SIGTERM)",
    )
    kill_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    kill_parser.add_argument(
        "--cwd",
        nargs="?",
        const="",
        default=None,
        metavar="PATH",
        help="Kill processes in cwd (no value = current dir, or specify path/glob)",
    )
    kill_parser.add_argument(
        "-F",
        "--filter",
        choices=["killable", "orphans", "high-memory"],
        help="Filter preset to select processes",
    )
    kill_parser.add_argument(
        "-k",
        "--killable",
        action="store_true",
        help="Shorthand for --filter killable",
    )
    kill_parser.add_argument(
        "-o",
        "--orphans",
        action="store_true",
        help="Shorthand for --filter orphans",
    )
    kill_parser.add_argument(
        "-m",
        "--high-memory",
        action="store_true",
        help="Shorthand for --filter high-memory",
    )
    kill_parser.add_argument(
        "--min-memory",
        type=float,
        default=5.0,
        metavar="MB",
        help="Minimum memory for filter (default: 5 MB)",
    )
    kill_parser.add_argument(
        "--high-memory-threshold",
        type=float,
        default=500.0,
        metavar="MB",
        help="Threshold for high memory filter (default: 500 MB)",
    )
    kill_parser.add_argument(
        "--preview",
        "--dry-run",
        "--dry",
        action="store_true",
        dest="preview",
        help="Show what would be killed without killing",
    )
    kill_parser.add_argument(
        "-O",
        "--out-format",
        choices=["table", "json", "csv", "md"],
        default="table",
        dest="out_format",
        help="Output format for preview (default: table)",
    )
    kill_parser.add_argument(
        "-s",
        "--sort",
        choices=["memory", "mem", "cpu", "pid", "name", "cwd"],
        default=None,
        help="Sort by field for preview",
    )
    kill_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        metavar="N",
        help="Limit preview output to N processes",
    )
    kill_parser.add_argument(
        "-c",
        "--columns",
        type=str,
        metavar="COLS",
        help=f"Comma-separated columns for preview ({','.join(get_available_columns())})",
    )
    kill_parser.set_defaults(func=cmd_kill)

    # Memory command
    memory_parser = subparsers.add_parser(
        "memory", aliases=["mem"], help="Show memory summary"
    )
    memory_parser.add_argument(
        "-f",
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    memory_parser.set_defaults(func=cmd_memory)

    return parser


def run_cli(args: list[str] | None = None) -> int:
    """Run CLI with given args (or sys.argv if None)."""
    parser = create_parser()
    parsed = parser.parse_args(args)

    if parsed.command is None:
        # No subcommand - return None to signal TUI should run
        return -1

    return parsed.func(parsed)
