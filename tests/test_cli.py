"""Tests for CLI module."""

import json
from unittest.mock import patch

import pytest

from procclean.cli import (
    cmd_groups,
    cmd_kill,
    cmd_list,
    cmd_memory,
    create_parser,
    run_cli,
)


class TestCreateParser:
    """Tests for create_parser function."""

    def test_list_command_defaults(self):
        """Should parse list command with defaults."""
        parser = create_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"
        assert args.format == "table"
        assert args.sort == "memory"
        assert args.ascending is False
        assert args.orphans is False
        assert args.high_memory is False
        assert args.limit is None

    def test_list_with_all_options(self):
        """Should parse list command with all options."""
        parser = create_parser()
        args = parser.parse_args([
            "list",
            "-f",
            "json",
            "-s",
            "cpu",
            "-a",
            "-o",
            "-m",
            "-n",
            "10",
            "-c",
            "pid,name",
            "--min-memory",
            "50",
            "--high-memory-threshold",
            "1000",
        ])
        assert args.format == "json"
        assert args.sort == "cpu"
        assert args.ascending is True
        assert args.orphans is True
        assert args.high_memory is True
        assert args.limit == 10
        assert args.columns == "pid,name"
        assert args.min_memory == 50.0
        assert args.high_memory_threshold == 1000.0

    def test_list_alias_ls(self):
        """Should support 'ls' alias for list."""
        parser = create_parser()
        args = parser.parse_args(["ls"])
        assert args.command in ("list", "ls")
        assert hasattr(args, "func")

    def test_groups_command(self):
        """Should parse groups command."""
        parser = create_parser()
        args = parser.parse_args(["groups"])
        assert args.command == "groups"
        assert args.format == "table"

    def test_groups_alias_g(self):
        """Should support 'g' alias for groups."""
        parser = create_parser()
        args = parser.parse_args(["g", "-f", "json"])
        assert args.command in ("groups", "g")
        assert args.format == "json"

    def test_kill_command_requires_pids(self):
        """Should require at least one PID for kill."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["kill"])

    def test_kill_command_with_pids(self):
        """Should parse kill command with PIDs."""
        parser = create_parser()
        args = parser.parse_args(["kill", "123", "456", "-f", "-y"])
        assert args.pids == [123, 456]
        assert args.force is True
        assert args.yes is True

    def test_memory_command(self):
        """Should parse memory command."""
        parser = create_parser()
        args = parser.parse_args(["memory"])
        assert args.command == "memory"
        assert args.format == "table"

    def test_memory_alias_mem(self):
        """Should support 'mem' alias for memory."""
        parser = create_parser()
        args = parser.parse_args(["mem", "-f", "json"])
        assert args.command in ("memory", "mem")
        assert args.format == "json"


class TestCmdList:
    """Tests for cmd_list function."""

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.format_output")
    def test_outputs_table_format(self, mock_format, mock_get_procs, capsys):
        """Should call format_output and print result."""
        mock_get_procs.return_value = []
        mock_format.return_value = "formatted output"

        parser = create_parser()
        args = parser.parse_args(["list"])
        result = cmd_list(args)

        assert result == 0
        mock_format.assert_called_once()
        captured = capsys.readouterr()
        assert "formatted output" in captured.out

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_orphans")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_filters_orphans(
        self, mock_format, mock_sort, mock_filter, mock_get_procs, sample_processes
    ):
        """Should apply orphan filter when -o flag set."""
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:2]
        mock_sort.return_value = sample_processes[:2]
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "-o"])
        cmd_list(args)

        mock_filter.assert_called_once_with(sample_processes)

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_high_memory")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_filters_high_memory(
        self, mock_format, mock_sort, mock_filter, mock_get_procs, sample_processes
    ):
        """Should apply high memory filter when -m flag set."""
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]
        mock_sort.return_value = sample_processes[:1]
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "-m", "--high-memory-threshold", "400"])
        cmd_list(args)

        mock_filter.assert_called_once_with(sample_processes, threshold_mb=400.0)

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_sorts_processes(
        self, mock_format, mock_sort, mock_get_procs, sample_processes
    ):
        """Should sort processes by specified field."""
        mock_get_procs.return_value = sample_processes
        mock_sort.return_value = sample_processes
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "-s", "cpu", "-a"])
        cmd_list(args)

        mock_sort.assert_called_once_with(
            sample_processes, sort_by="cpu", reverse=False
        )

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_limits_output(
        self, mock_format, mock_sort, mock_get_procs, sample_processes
    ):
        """Should limit output to N processes."""
        mock_get_procs.return_value = sample_processes
        mock_sort.return_value = sample_processes
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "-n", "2"])
        cmd_list(args)

        # format_output should receive limited list
        call_args = mock_format.call_args[0]
        assert len(call_args[0]) == 2


class TestCmdGroups:
    """Tests for cmd_groups function."""

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.find_similar_processes")
    def test_no_groups_found(self, mock_find, mock_get_procs, capsys):
        """Should print message when no groups found."""
        mock_get_procs.return_value = []
        mock_find.return_value = {}

        parser = create_parser()
        args = parser.parse_args(["groups"])
        result = cmd_groups(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No process groups found" in captured.out

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.find_similar_processes")
    def test_json_output(self, mock_find, mock_get_procs, sample_processes, capsys):
        """Should output JSON when format is json."""
        mock_get_procs.return_value = sample_processes
        mock_find.return_value = {"python": sample_processes[:2]}

        parser = create_parser()
        args = parser.parse_args(["groups", "-f", "json"])
        result = cmd_groups(args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "python" in data

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.find_similar_processes")
    def test_table_output(self, mock_find, mock_get_procs, sample_processes, capsys):
        """Should output formatted text when format is table."""
        mock_get_procs.return_value = sample_processes
        mock_find.return_value = {"python": sample_processes[:2]}

        parser = create_parser()
        args = parser.parse_args(["groups"])
        result = cmd_groups(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "python" in captured.out
        assert "processes" in captured.out


class TestCmdKill:
    """Tests for cmd_kill function."""

    @patch("procclean.cli.kill_processes")
    def test_with_yes_flag(self, mock_kill, capsys):
        """Should skip confirmation when -y flag set."""
        mock_kill.return_value = [(123, True, "Process 123 terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "123", "-y"])
        result = cmd_kill(args)

        assert result == 0
        mock_kill.assert_called_once_with([123], force=False)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out

    @patch("procclean.cli.kill_processes")
    def test_with_force_flag(self, mock_kill, capsys):
        """Should pass force=True when -f flag set."""
        mock_kill.return_value = [(123, True, "Process 123 killed")]

        parser = create_parser()
        args = parser.parse_args(["kill", "123", "-f", "-y"])
        cmd_kill(args)

        mock_kill.assert_called_once_with([123], force=True)

    @patch("procclean.cli.kill_processes")
    def test_returns_exit_code_on_failure(self, mock_kill, capsys):
        """Should return non-zero exit code on any failure."""
        mock_kill.return_value = [
            (123, True, "OK"),
            (456, False, "Access denied"),
        ]

        parser = create_parser()
        args = parser.parse_args(["kill", "123", "456", "-y"])
        result = cmd_kill(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "[FAILED]" in captured.out

    @patch("procclean.cli.kill_processes")
    @patch("sys.stdin")
    @patch("builtins.input", return_value="n")
    def test_confirmation_abort(self, mock_input, mock_stdin, mock_kill, capsys):
        """Should abort when user says no."""
        mock_stdin.isatty.return_value = True

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        result = cmd_kill(args)

        assert result == 1
        mock_kill.assert_not_called()
        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    @patch("procclean.cli.kill_processes")
    @patch("sys.stdin")
    @patch("builtins.input", return_value="y")
    def test_confirmation_yes(self, mock_input, mock_stdin, mock_kill, capsys):
        """Should proceed when user says yes."""
        mock_stdin.isatty.return_value = True
        mock_kill.return_value = [(123, True, "Process 123 terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        result = cmd_kill(args)

        assert result == 0
        mock_kill.assert_called_once()

    @patch("procclean.cli.kill_processes")
    @patch("sys.stdin")
    @patch("builtins.input", side_effect=EOFError)
    def test_confirmation_eof(self, mock_input, mock_stdin, mock_kill, capsys):
        """Should proceed on EOFError (non-interactive pipe)."""
        mock_stdin.isatty.return_value = True
        mock_kill.return_value = [(123, True, "Process 123 terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        result = cmd_kill(args)

        assert result == 0
        mock_kill.assert_called_once()


class TestCmdMemory:
    """Tests for cmd_memory function."""

    @patch("procclean.cli.get_memory_summary")
    def test_json_output(self, mock_mem, capsys):
        """Should output JSON when format is json."""
        mock_mem.return_value = {
            "total_gb": 16.0,
            "used_gb": 8.0,
            "free_gb": 8.0,
            "percent": 50.0,
            "swap_used_gb": 1.0,
            "swap_total_gb": 4.0,
        }

        parser = create_parser()
        args = parser.parse_args(["mem", "-f", "json"])
        result = cmd_memory(args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["total_gb"] == 16.0

    @patch("procclean.cli.get_memory_summary")
    def test_table_output(self, mock_mem, capsys):
        """Should output formatted text when format is table."""
        mock_mem.return_value = {
            "total_gb": 16.0,
            "used_gb": 8.0,
            "free_gb": 8.0,
            "percent": 50.0,
            "swap_used_gb": 1.0,
            "swap_total_gb": 4.0,
        }

        parser = create_parser()
        args = parser.parse_args(["mem"])
        result = cmd_memory(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Total:" in captured.out
        assert "Used:" in captured.out
        assert "Free:" in captured.out
        assert "Swap:" in captured.out


class TestRunCli:
    """Tests for run_cli function."""

    def test_no_command_returns_minus_one(self):
        """Should return -1 when no subcommand given (signal for TUI)."""
        result = run_cli([])
        assert result == -1

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_routes_to_list_command(self, mock_format, mock_sort, mock_get):
        """Should route to list command handler."""
        mock_get.return_value = []
        mock_sort.return_value = []
        mock_format.return_value = ""

        result = run_cli(["list"])
        assert result == 0
        mock_get.assert_called_once()

    @patch("procclean.cli.get_memory_summary")
    def test_routes_to_memory_command(self, mock_mem, capsys):
        """Should route to memory command handler."""
        mock_mem.return_value = {
            "total_gb": 16.0,
            "used_gb": 8.0,
            "free_gb": 8.0,
            "percent": 50.0,
            "swap_used_gb": 1.0,
            "swap_total_gb": 4.0,
        }

        result = run_cli(["mem"])
        assert result == 0
