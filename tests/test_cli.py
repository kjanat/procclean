"""Tests for CLI module."""

import json
from unittest.mock import patch

from procclean.cli import (
    _confirm_kill,
    _do_preview,
    _get_kill_targets,
    cmd_groups,
    cmd_kill,
    cmd_list,
    cmd_memory,
    create_parser,
    get_filtered_processes,
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

    def test_list_cwd_no_value(self):
        """Should parse --cwd with no value (uses current dir)."""
        parser = create_parser()
        args = parser.parse_args(["list", "--cwd"])
        assert args.cwd is not None
        assert not args.cwd  # Empty string

    def test_list_cwd_with_path(self):
        """Should parse --cwd with a path value."""
        parser = create_parser()
        args = parser.parse_args(["list", "--cwd", "/home/user/project"])
        assert args.cwd == "/home/user/project"

    def test_list_cwd_not_set(self):
        """Should have None cwd when flag not used."""
        parser = create_parser()
        args = parser.parse_args(["list"])
        assert args.cwd is None

    def test_list_sort_by_cwd(self):
        """Should allow sorting by cwd."""
        parser = create_parser()
        args = parser.parse_args(["list", "-s", "cwd"])
        assert args.sort == "cwd"

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

    def test_kill_command_no_pids_allowed(self):
        """Should allow kill without PIDs (uses filters instead)."""
        parser = create_parser()
        args = parser.parse_args(["kill", "--cwd", "/tmp"])
        assert args.pids == []
        assert args.cwd == "/tmp"

    def test_kill_command_with_pids(self):
        """Should parse kill command with PIDs."""
        parser = create_parser()
        args = parser.parse_args(["kill", "123", "456", "-f", "-y"])
        assert args.pids == [123, 456]
        assert args.force is True
        assert args.yes is True

    def test_kill_with_cwd_filter(self):
        """Should parse kill with --cwd filter."""
        parser = create_parser()
        args = parser.parse_args(["kill", "--cwd", "/home/user", "-y"])
        assert args.cwd == "/home/user"
        assert args.pids == []

    def test_kill_with_filter_flags(self):
        """Should parse kill with filter flags."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "-y"])
        assert args.killable is True
        assert args.pids == []

    def test_kill_preview_flag(self):
        """Should parse --preview flag."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview"])
        assert args.preview is True

    def test_kill_dry_run_alias(self):
        """Should parse --dry-run as alias for --preview."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--dry-run"])
        assert args.preview is True

    def test_kill_dry_alias(self):
        """Should parse --dry as alias for --preview."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--dry"])
        assert args.preview is True

    def test_kill_preview_with_format(self):
        """Should parse preview with output format."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-O", "json"])
        assert args.preview is True
        assert args.out_format == "json"

    def test_kill_preview_with_sort_limit(self):
        """Should parse preview with sort and limit."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-s", "cpu", "-n", "5"])
        assert args.sort == "cpu"
        assert args.limit == 5

    def test_kill_preview_with_columns(self):
        """Should parse preview with custom columns."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-c", "pid,name,rss"])
        assert args.columns == "pid,name,rss"

    def test_kill_high_memory_threshold(self):
        """Should parse --high-memory-threshold for kill."""
        parser = create_parser()
        args = parser.parse_args(["kill", "-m", "--high-memory-threshold", "200", "-y"])
        assert args.high_memory_threshold == 200.0

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
    @patch("procclean.cli.filter_killable")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_filters_killable(
        self, mock_format, mock_sort, mock_filter, mock_get_procs, sample_processes
    ):
        """Should apply killable filter when -k flag set."""
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]
        mock_sort.return_value = sample_processes[:1]
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "-k"])
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

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_by_cwd")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_filters_by_cwd_with_path(
        self, mock_format, mock_sort, mock_filter, mock_get_procs, sample_processes
    ):
        """Should apply cwd filter with given path."""
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]
        mock_sort.return_value = sample_processes[:1]
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "--cwd", "/home/user/project"])
        cmd_list(args)

        mock_filter.assert_called_once_with(sample_processes, "/home/user/project")

    @patch("os.getcwd", return_value="/current/working/dir")
    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_by_cwd")
    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_filters_by_cwd_empty_uses_getcwd(
        self,
        mock_format,
        mock_sort,
        mock_filter,
        mock_get_procs,
        _mock_getcwd,
        sample_processes,
    ):
        """Should use current directory when --cwd has no value."""
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]
        mock_sort.return_value = sample_processes[:1]
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["list", "--cwd"])
        cmd_list(args)

        mock_filter.assert_called_once_with(sample_processes, "/current/working/dir")


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

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.kill_processes")
    def test_with_yes_flag(self, mock_kill, mock_get, sample_processes, capsys):
        """Should skip confirmation when -y flag set."""
        mock_get.return_value = sample_processes
        mock_kill.return_value = [(1, True, "Process 1 terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "1", "-y"])
        result = cmd_kill(args)

        assert result == 0
        mock_kill.assert_called_once_with([1], force=False)
        captured = capsys.readouterr()
        assert "[OK]" in captured.out

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.kill_processes")
    def test_with_force_flag(self, mock_kill, mock_get, sample_processes, capsys):
        """Should pass force=True when -f flag set."""
        mock_get.return_value = sample_processes
        mock_kill.return_value = [(1, True, "Process 1 killed")]

        parser = create_parser()
        args = parser.parse_args(["kill", "1", "-f", "-y"])
        cmd_kill(args)

        mock_kill.assert_called_once_with([1], force=True)

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.kill_processes")
    def test_returns_exit_code_on_failure(
        self, mock_kill, mock_get, sample_processes, capsys
    ):
        """Should return non-zero exit code on any failure."""
        mock_get.return_value = sample_processes
        mock_kill.return_value = [
            (1, True, "OK"),
            (2, False, "Access denied"),
        ]

        parser = create_parser()
        args = parser.parse_args(["kill", "1", "2", "-y"])
        result = cmd_kill(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "[FAILED]" in captured.out

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.kill_processes")
    @patch("sys.stdin")
    @patch("builtins.input", return_value="n")
    def test_confirmation_abort(
        self, mock_input, mock_stdin, mock_kill, mock_get, sample_processes, capsys
    ):
        """Should abort when user says no."""
        mock_stdin.isatty.return_value = True
        mock_get.return_value = sample_processes

        parser = create_parser()
        args = parser.parse_args(["kill", "1"])
        result = cmd_kill(args)

        assert result == 1
        mock_kill.assert_not_called()
        captured = capsys.readouterr()
        assert "Aborted" in captured.out

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.kill_processes")
    @patch("sys.stdin")
    @patch("builtins.input", return_value="y")
    def test_confirmation_yes(
        self, mock_input, mock_stdin, mock_kill, mock_get, sample_processes, capsys
    ):
        """Should proceed when user says yes."""
        mock_stdin.isatty.return_value = True
        mock_get.return_value = sample_processes
        mock_kill.return_value = [(1, True, "Process 1 terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "1"])
        result = cmd_kill(args)

        assert result == 0
        mock_kill.assert_called_once()

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.kill_processes")
    @patch("sys.stdin")
    @patch("builtins.input", side_effect=EOFError)
    def test_confirmation_eof(
        self, mock_input, mock_stdin, mock_kill, mock_get, sample_processes, capsys
    ):
        """Should proceed on EOFError (non-interactive pipe)."""
        mock_stdin.isatty.return_value = True
        mock_get.return_value = sample_processes
        mock_kill.return_value = [(1, True, "Process 1 terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "1"])
        result = cmd_kill(args)

        assert result == 0
        mock_kill.assert_called_once()

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_by_cwd")
    @patch("procclean.cli.kill_processes")
    def test_kill_with_cwd_filter(
        self, mock_kill, mock_filter, mock_get_procs, sample_processes, capsys
    ):
        """Should kill processes matching cwd filter."""
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:2]
        mock_kill.return_value = [
            (1, True, "terminated"),
            (2, True, "terminated"),
        ]

        parser = create_parser()
        args = parser.parse_args(["kill", "--cwd", "/home/user", "-y"])
        result = cmd_kill(args)

        assert result == 0
        mock_filter.assert_called_once_with(sample_processes, "/home/user")
        mock_kill.assert_called_once_with([1, 2], force=False)

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_by_cwd")
    @patch("procclean.cli.kill_processes")
    @patch("os.getcwd")
    def test_kill_with_cwd_empty_uses_getcwd(
        self, mock_getcwd, mock_kill, mock_filter, mock_get_procs, sample_processes
    ):
        """Should use current directory when --cwd has no value."""
        mock_getcwd.return_value = "/current/dir"
        mock_get_procs.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]
        mock_kill.return_value = [(1, True, "terminated")]

        parser = create_parser()
        args = parser.parse_args(["kill", "--cwd", "-y"])
        cmd_kill(args)

        mock_filter.assert_called_once_with(sample_processes, "/current/dir")

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_by_cwd")
    def test_kill_with_no_matches(self, mock_filter, mock_get_procs, capsys):
        """Should print message when no processes match filters."""
        mock_get_procs.return_value = []
        mock_filter.return_value = []

        parser = create_parser()
        args = parser.parse_args(["kill", "--cwd", "/nonexistent", "-y"])
        result = cmd_kill(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No processes match" in captured.out


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


class TestGetFilteredProcesses:
    """Tests for get_filtered_processes function."""

    @patch("procclean.cli.get_process_list")
    def test_returns_all_when_no_filters(self, mock_get, sample_processes):
        """Should return all processes when no filters applied."""
        mock_get.return_value = sample_processes

        parser = create_parser()
        args = parser.parse_args(["list"])
        result = get_filtered_processes(args)

        assert result == sample_processes

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_killable")
    def test_applies_killable_filter(self, mock_filter, mock_get, sample_processes):
        """Should apply killable filter."""
        mock_get.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]

        parser = create_parser()
        args = parser.parse_args(["list", "-k"])
        result = get_filtered_processes(args)

        mock_filter.assert_called_once()
        assert result == sample_processes[:1]

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_by_cwd")
    def test_applies_cwd_filter(self, mock_filter, mock_get, sample_processes):
        """Should apply cwd filter."""
        mock_get.return_value = sample_processes
        mock_filter.return_value = sample_processes[:1]

        parser = create_parser()
        args = parser.parse_args(["list", "--cwd", "/home"])
        result = get_filtered_processes(args)

        mock_filter.assert_called_once_with(sample_processes, "/home")
        assert result == sample_processes[:1]


class TestGetKillTargets:
    """Tests for _get_kill_targets function."""

    @patch("procclean.cli.get_process_list")
    def test_with_explicit_pids(self, mock_get, sample_processes, capsys):
        """Should filter by explicit PIDs."""
        mock_get.return_value = sample_processes

        parser = create_parser()
        args = parser.parse_args(["kill", "1", "2", "-y"])
        result = _get_kill_targets(args)

        assert len(result) == 2
        assert {p.pid for p in result} == {1, 2}

    @patch("procclean.cli.get_process_list")
    def test_warns_missing_pids(self, mock_get, sample_processes, capsys):
        """Should warn about PIDs not found."""
        mock_get.return_value = sample_processes

        parser = create_parser()
        args = parser.parse_args(["kill", "1", "9999", "-y"])
        _get_kill_targets(args)

        captured = capsys.readouterr()
        assert "Warning: PID 9999 not found" in captured.out

    @patch("procclean.cli.get_filtered_processes")
    def test_uses_filters_when_no_pids(self, mock_filter, sample_processes):
        """Should use filters when no explicit PIDs."""
        mock_filter.return_value = sample_processes

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "-y"])
        result = _get_kill_targets(args)

        mock_filter.assert_called_once()
        assert result == sample_processes


class TestDoPreview:
    """Tests for _do_preview function."""

    @patch("procclean.cli.format_output")
    def test_outputs_formatted_list(self, mock_format, sample_processes, capsys):
        """Should output formatted process list."""
        mock_format.return_value = "formatted output"

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview"])
        result = _do_preview(args, sample_processes)

        assert result == 0
        mock_format.assert_called_once()
        captured = capsys.readouterr()
        assert "formatted output" in captured.out
        assert "would be killed" in captured.out

    @patch("procclean.cli.sort_processes")
    @patch("procclean.cli.format_output")
    def test_applies_sort(self, mock_format, mock_sort, sample_processes):
        """Should apply sorting when specified."""
        mock_sort.return_value = sample_processes
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-s", "cpu"])
        _do_preview(args, sample_processes)

        mock_sort.assert_called_once_with(sample_processes, sort_by="cpu", reverse=True)

    @patch("procclean.cli.format_output")
    def test_applies_limit(self, mock_format, sample_processes):
        """Should apply limit when specified."""
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-n", "2"])
        _do_preview(args, sample_processes)

        # format_output should receive limited list
        call_args = mock_format.call_args[0]
        assert len(call_args[0]) == 2

    @patch("procclean.cli.format_output")
    def test_uses_specified_format(self, mock_format, sample_processes):
        """Should use specified output format."""
        mock_format.return_value = ""

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-O", "json"])
        _do_preview(args, sample_processes)

        mock_format.assert_called_once()
        call_args = mock_format.call_args
        assert call_args[0][1] == "json"


class TestConfirmKill:
    """Tests for _confirm_kill function."""

    def test_returns_true_with_yes_flag(self, sample_processes):
        """Should return True when -y flag set."""
        parser = create_parser()
        args = parser.parse_args(["kill", "123", "-y"])
        result = _confirm_kill(args, sample_processes)
        assert result is True

    @patch("sys.stdin")
    def test_returns_true_non_interactive(self, mock_stdin, sample_processes):
        """Should return True when not interactive."""
        mock_stdin.isatty.return_value = False

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        result = _confirm_kill(args, sample_processes)

        assert result is True

    @patch("sys.stdin")
    @patch("builtins.input", return_value="y")
    def test_returns_true_on_yes(self, mock_input, mock_stdin, sample_processes):
        """Should return True when user confirms."""
        mock_stdin.isatty.return_value = True

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        result = _confirm_kill(args, sample_processes)

        assert result is True

    @patch("sys.stdin")
    @patch("builtins.input", return_value="n")
    def test_returns_false_on_no(self, mock_input, mock_stdin, sample_processes):
        """Should return False when user declines."""
        mock_stdin.isatty.return_value = True

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        result = _confirm_kill(args, sample_processes)

        assert result is False

    @patch("sys.stdin")
    @patch("builtins.input", return_value="y")
    def test_shows_process_details(
        self, mock_input, mock_stdin, sample_processes, capsys
    ):
        """Should show process details in confirmation."""
        mock_stdin.isatty.return_value = True

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        _confirm_kill(args, sample_processes)

        captured = capsys.readouterr()
        # Should show process name and memory
        assert "python" in captured.out or sample_processes[0].name in captured.out
        assert "MB" in captured.out

    @patch("sys.stdin")
    @patch("builtins.input", return_value="y")
    def test_shows_more_indicator(
        self, mock_input, mock_stdin, sample_processes, capsys
    ):
        """Should show '... and N more' for many processes."""
        mock_stdin.isatty.return_value = True
        # Need more than 5 processes
        many_procs = sample_processes * 3  # 9 processes

        parser = create_parser()
        args = parser.parse_args(["kill", "123"])
        _confirm_kill(args, many_procs)

        captured = capsys.readouterr()
        assert "... and" in captured.out
        assert "more" in captured.out


class TestCmdKillPreview:
    """Tests for cmd_kill preview mode."""

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_killable")
    @patch("procclean.cli.format_output")
    def test_preview_does_not_kill(
        self, mock_format, mock_filter, mock_get, sample_processes, capsys
    ):
        """Should not call kill_processes in preview mode."""
        mock_get.return_value = sample_processes
        mock_filter.return_value = sample_processes
        mock_format.return_value = "preview output"

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview"])
        result = cmd_kill(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "preview output" in captured.out
        assert "would be killed" in captured.out

    @patch("procclean.cli.get_process_list")
    @patch("procclean.cli.filter_killable")
    @patch("procclean.cli.format_output")
    def test_preview_json_format(
        self, mock_format, mock_filter, mock_get, sample_processes
    ):
        """Should support JSON output in preview."""
        mock_get.return_value = sample_processes
        mock_filter.return_value = sample_processes
        mock_format.return_value = "{}"

        parser = create_parser()
        args = parser.parse_args(["kill", "-k", "--preview", "-O", "json"])
        cmd_kill(args)

        mock_format.assert_called()
        call_args = mock_format.call_args
        assert call_args[0][1] == "json"


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
