"""CLI interface for procclean (non-TUI)."""

import argparse
import json
import sys
from importlib.metadata import version

from .formatters import format_output, get_available_columns
from .process_analyzer import (
    filter_high_memory,
    filter_orphans,
    find_similar_processes,
    get_memory_summary,
    get_process_list,
    kill_processes,
    sort_processes,
)


def cmd_list(args: argparse.Namespace) -> int:
    """List processes command."""
    procs = get_process_list(min_memory_mb=args.min_memory)

    # Apply filters
    if args.orphans:
        procs = filter_orphans(procs)
    if args.high_memory:
        procs = filter_high_memory(procs, threshold_mb=args.high_memory_threshold)

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


def cmd_kill(args: argparse.Namespace) -> int:
    """Kill processes command."""
    pids = args.pids

    # Confirmation unless --yes or non-interactive
    if not args.yes and sys.stdin.isatty():
        print(
            f"About to {'FORCE KILL' if args.force else 'terminate'} {len(pids)} process(es): {pids}"
        )
        try:
            response = input("Continue? [y/N] ")
            if response.lower() not in ("y", "yes"):
                print("Aborted.")
                return 1
        except EOFError:
            # Non-interactive
            pass

    results = kill_processes(pids, force=args.force)
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
        choices=["memory", "mem", "cpu", "pid", "name"],
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
        "-o",
        "--orphans",
        action="store_true",
        help="Show only orphaned processes",
    )
    list_parser.add_argument(
        "-m",
        "--high-memory",
        action="store_true",
        help="Show only high memory processes",
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
        nargs="+",
        metavar="PID",
        help="Process ID(s) to kill",
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
