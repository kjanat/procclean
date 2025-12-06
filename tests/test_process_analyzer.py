"""Tests for process_analyzer module."""

from unittest.mock import MagicMock, patch

import psutil
import pytest

from procclean.process_analyzer import (
    ProcessInfo,
    find_similar_processes,
    get_cwd,
    get_memory_summary,
    get_tmux_env,
    kill_process,
    kill_processes,
)


class TestGetTmuxEnv:
    """Tests for get_tmux_env function."""

    def test_returns_true_when_tmux_in_environ(self, tmp_path):
        """Should return True when TMUX= is in process environ."""
        with patch("procclean.process_analyzer.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_bytes.return_value = (
                b"PATH=/bin\x00TMUX=/tmp/tmux\x00"
            )
            assert get_tmux_env(1234) is True

    def test_returns_false_when_no_tmux(self, tmp_path):
        """Should return False when TMUX= is not in environ."""
        with patch("procclean.process_analyzer.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_bytes.return_value = (
                b"PATH=/bin\x00HOME=/home/user\x00"
            )
            assert get_tmux_env(1234) is False

    def test_returns_false_on_permission_error(self):
        """Should return False when PermissionError is raised."""
        with patch("procclean.process_analyzer.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_bytes.side_effect = PermissionError
            assert get_tmux_env(1234) is False

    def test_returns_false_when_file_not_exists(self):
        """Should return False when environ file doesn't exist."""
        with patch("procclean.process_analyzer.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            assert get_tmux_env(1234) is False


class TestGetCwd:
    """Tests for get_cwd function."""

    def test_returns_cwd_path(self):
        """Should return the process working directory."""
        with patch("os.readlink", return_value="/home/user/project"):
            assert get_cwd(1234) == "/home/user/project"

    def test_returns_question_mark_on_error(self):
        """Should return '?' when readlink fails."""
        with patch("os.readlink", side_effect=PermissionError):
            assert get_cwd(1234) == "?"

    def test_returns_question_mark_on_no_such_process(self):
        """Should return '?' when process doesn't exist."""
        with patch("os.readlink", side_effect=FileNotFoundError):
            assert get_cwd(1234) == "?"


class TestFindSimilarProcesses:
    """Tests for find_similar_processes function."""

    def _make_process(self, pid: int, name: str, cmdline: str) -> ProcessInfo:
        """Helper to create ProcessInfo objects."""
        return ProcessInfo(
            pid=pid,
            name=name,
            cmdline=cmdline,
            cwd="/tmp",
            ppid=1,
            parent_name="systemd",
            rss_mb=100.0,
            cpu_percent=1.0,
            username="user",
            create_time=0.0,
            is_orphan=False,
            in_tmux=False,
            status="running",
        )

    def test_groups_similar_processes(self):
        """Should group processes with same command."""
        procs = [
            self._make_process(1, "python", "python script.py"),
            self._make_process(2, "python", "python other.py"),
            self._make_process(3, "node", "node server.js"),
        ]
        groups = find_similar_processes(procs)
        assert "python" in groups
        assert len(groups["python"]) == 2
        assert "node" not in groups  # only 1 process

    def test_returns_empty_for_unique_processes(self):
        """Should return empty dict when all processes are unique."""
        procs = [
            self._make_process(1, "python", "python script.py"),
            self._make_process(2, "node", "node server.js"),
            self._make_process(3, "ruby", "ruby app.rb"),
        ]
        groups = find_similar_processes(procs)
        assert groups == {}

    def test_normalizes_paths_in_cmdline(self):
        """Should normalize full paths to just the executable name."""
        procs = [
            self._make_process(1, "python", "/usr/bin/python script.py"),
            self._make_process(2, "python", "/home/user/.venv/bin/python other.py"),
        ]
        groups = find_similar_processes(procs)
        assert "python" in groups
        assert len(groups["python"]) == 2


class TestKillProcess:
    """Tests for kill_process function."""

    def test_terminate_success(self):
        """Should return success when process is terminated."""
        with patch("psutil.Process") as mock_proc:
            mock_proc.return_value.terminate.return_value = None
            success, msg = kill_process(1234, force=False)
            assert success is True
            assert "terminated" in msg
            mock_proc.return_value.terminate.assert_called_once()

    def test_kill_success(self):
        """Should use kill() when force=True."""
        with patch("psutil.Process") as mock_proc:
            mock_proc.return_value.kill.return_value = None
            success, msg = kill_process(1234, force=True)
            assert success is True
            mock_proc.return_value.kill.assert_called_once()

    def test_no_such_process(self):
        """Should return failure when process doesn't exist."""
        with patch("psutil.Process") as mock_proc:
            mock_proc.side_effect = psutil.NoSuchProcess(1234)
            success, msg = kill_process(1234)
            assert success is False
            assert "not found" in msg

    def test_access_denied(self):
        """Should return failure when access is denied."""
        with patch("psutil.Process") as mock_proc:
            mock_proc.side_effect = psutil.AccessDenied(1234)
            success, msg = kill_process(1234)
            assert success is False
            assert "denied" in msg.lower()


class TestKillProcesses:
    """Tests for kill_processes function."""

    def test_kills_multiple_processes(self):
        """Should return results for each PID."""
        with patch("procclean.process_analyzer.kill_process") as mock_kill:
            mock_kill.side_effect = [
                (True, "killed"),
                (False, "not found"),
                (True, "killed"),
            ]
            results = kill_processes([1, 2, 3])
            assert len(results) == 3
            assert results[0] == (1, True, "killed")
            assert results[1] == (2, False, "not found")
            assert results[2] == (3, True, "killed")


class TestGetMemorySummary:
    """Tests for get_memory_summary function."""

    def test_returns_memory_stats(self):
        """Should return dict with memory statistics."""
        mock_mem = MagicMock()
        mock_mem.total = 16 * 1024**3  # 16 GB
        mock_mem.used = 8 * 1024**3  # 8 GB
        mock_mem.available = 8 * 1024**3  # 8 GB
        mock_mem.percent = 50.0

        mock_swap = MagicMock()
        mock_swap.used = 1 * 1024**3  # 1 GB
        mock_swap.total = 4 * 1024**3  # 4 GB

        with patch("psutil.virtual_memory", return_value=mock_mem):
            with patch("psutil.swap_memory", return_value=mock_swap):
                summary = get_memory_summary()

        assert summary["total_gb"] == pytest.approx(16.0)
        assert summary["used_gb"] == pytest.approx(8.0)
        assert summary["free_gb"] == pytest.approx(8.0)
        assert summary["percent"] == 50.0
        assert summary["swap_used_gb"] == pytest.approx(1.0)
        assert summary["swap_total_gb"] == pytest.approx(4.0)


class TestProcessInfo:
    """Tests for ProcessInfo dataclass."""

    def test_is_orphan_candidate_true(self):
        """Should return True when orphan and not in tmux."""
        proc = ProcessInfo(
            pid=1,
            name="test",
            cmdline="test",
            cwd="/tmp",
            ppid=1,
            parent_name="systemd",
            rss_mb=100.0,
            cpu_percent=1.0,
            username="user",
            create_time=0.0,
            is_orphan=True,
            in_tmux=False,
            status="running",
        )
        assert proc.is_orphan_candidate is True

    def test_is_orphan_candidate_false_when_in_tmux(self):
        """Should return False when orphan but in tmux."""
        proc = ProcessInfo(
            pid=1,
            name="test",
            cmdline="test",
            cwd="/tmp",
            ppid=1,
            parent_name="systemd",
            rss_mb=100.0,
            cpu_percent=1.0,
            username="user",
            create_time=0.0,
            is_orphan=True,
            in_tmux=True,
            status="running",
        )
        assert proc.is_orphan_candidate is False

    def test_is_orphan_candidate_false_when_not_orphan(self):
        """Should return False when not orphan."""
        proc = ProcessInfo(
            pid=1,
            name="test",
            cmdline="test",
            cwd="/tmp",
            ppid=1000,
            parent_name="bash",
            rss_mb=100.0,
            cpu_percent=1.0,
            username="user",
            create_time=0.0,
            is_orphan=False,
            in_tmux=False,
            status="running",
        )
        assert proc.is_orphan_candidate is False
