"""CLI interface for procclean (non-TUI)."""

import argparse
import csv
import io
import json
import sys
from collections.abc import Sequence
from importlib.metadata import version

from .process_analyzer import (
    ProcessInfo,
    filter_high_memory,
    filter_orphans,
    find_similar_processes,
    get_memory_summary,
    get_process_list,
    kill_processes,
    sort_processes,
)

DEFAULT_COLUMNS = ("pid", "name", "rss_mb", "cpu_percent", "cwd", "ppid", "status")
COLUMN_HEADERS = {
    "pid": "PID",
    "name": "Name",
    "rss_mb": "RAM (MB)",
    "cpu_percent": "CPU%",
    "cwd": "CWD",
    "ppid": "PPID",
    "parent_name": "Parent",
    "status": "Status",
    "cmdline": "Command",
    "username": "User",
}


def _format_cell(col: str, val: object) -> str:
    """Format a single cell value for table output."""
    if col in ("rss_mb", "cpu_percent"):
        return f"{val:.1f}"
    if col == "cwd" and len(str(val)) > 40:
        return "..." + str(val)[-37:]
    if col == "name" and len(str(val)) > 25:
        return str(val)[:25]
    return str(val)


def format_table(procs: list[ProcessInfo], columns: Sequence[str] | None = None) -> str:
    """Format processes as ASCII table."""
    if not procs:
        return "No processes found."

    cols = columns or DEFAULT_COLUMNS
    header_row = [COLUMN_HEADERS.get(c, c) for c in cols]
    rows = [[_format_cell(col, getattr(p, col, "")) for col in cols] for p in procs]

    # Calculate column widths
    widths = [len(h) for h in header_row]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Format output
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_line = (
        "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(header_row)) + "|"
    )
    lines = [sep, header_line, sep]
    lines.extend(
        "|" + "|".join(f" {c:<{widths[i]}} " for i, c in enumerate(row)) + "|"
        for row in rows
    )
    lines.append(sep)
    return "\n".join(lines)


def format_json(procs: list[ProcessInfo]) -> str:
    """Format processes as JSON."""
    data = [
        {
            "pid": p.pid,
            "name": p.name,
            "cmdline": p.cmdline,
            "cwd": p.cwd,
            "ppid": p.ppid,
            "parent_name": p.parent_name,
            "rss_mb": round(p.rss_mb, 2),
            "cpu_percent": round(p.cpu_percent, 2),
            "username": p.username,
            "is_orphan": p.is_orphan,
            "in_tmux": p.in_tmux,
            "status": p.status,
        }
        for p in procs
    ]
    return json.dumps(data, indent=2)


def format_csv(procs: list[ProcessInfo]) -> str:
    """Format processes as CSV."""
    if not procs:
        return ""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "pid",
        "name",
        "cmdline",
        "cwd",
        "ppid",
        "parent_name",
        "rss_mb",
        "cpu_percent",
        "username",
        "is_orphan",
        "in_tmux",
        "status",
    ])
    for p in procs:
        writer.writerow([
            p.pid,
            p.name,
            p.cmdline,
            p.cwd,
            p.ppid,
            p.parent_name,
            f"{p.rss_mb:.2f}",
            f"{p.cpu_percent:.2f}",
            p.username,
            p.is_orphan,
            p.in_tmux,
            p.status,
        ])
    return output.getvalue()


def format_markdown(procs: list[ProcessInfo]) -> str:
    """Format processes as Markdown table."""
    if not procs:
        return "No processes found."

    lines = [
        "| PID | Name | RAM (MB) | CPU% | CWD | PPID | Status |",
        "|-----|------|----------|------|-----|------|--------|",
    ]
    for p in procs:
        cwd = p.cwd if len(p.cwd) <= 30 else "..." + p.cwd[-27:]
        name = p.name if len(p.name) <= 20 else p.name[:20]
        status = p.status
        if p.is_orphan:
            status += " [orphan]"
        if p.in_tmux:
            status += " [tmux]"
        lines.append(
            f"| {p.pid} | {name} | {p.rss_mb:.1f} | {p.cpu_percent:.1f} | {cwd} | {p.ppid} | {status} |"
        )
    return "\n".join(lines)


def format_output(procs: list[ProcessInfo], fmt: str) -> str:
    """Format processes in requested format."""
    formatters = {
        "table": format_table,
        "json": format_json,
        "csv": format_csv,
        "md": format_markdown,
        "markdown": format_markdown,
    }
    formatter = formatters.get(fmt, format_table)
    return formatter(procs)


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

    print(format_output(procs, args.format))
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
