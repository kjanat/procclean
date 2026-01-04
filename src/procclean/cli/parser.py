"""CLI argument parser."""

import argparse
from importlib.metadata import version

from procclean.formatters import get_available_columns

from .commands import cmd_groups, cmd_kill, cmd_list, cmd_memory


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser for the CLI.
    """
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
        help="Filter preset: killable (orphans, not tmux, not system), "
        "orphans, high-memory",
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
        help=f"Comma-separated columns for preview "
        f"({','.join(get_available_columns())})",
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
    """Run CLI with given args (or sys.argv if None).

    Returns:
        int: Exit status code. Returns ``-1`` when no subcommand is provided to
        signal that the TUI should run.
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    if parsed.command is None:
        # No subcommand - return None to signal TUI should run
        return -1

    return parsed.func(parsed)
