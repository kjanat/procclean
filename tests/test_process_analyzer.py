"""Tests for process_analyzer module."""

from unittest.mock import MagicMock, patch

import psutil
import pytest

from procclean.process_analyzer import (
    filter_high_memory,
    filter_orphans,
    find_similar_processes,
    get_cwd,
    get_memory_summary,
    get_process_list,
    get_tmux_env,
    kill_process,
    kill_processes,
    sort_processes,
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


class TestGetProcessList:
    """Tests for get_process_list function."""

    def _mock_proc_info(  # noqa: PLR0913, PLR0917
        self,
        pid=1234,
        name="python",
        cmdline=None,
        ppid=1000,
        rss=100 * 1024 * 1024,
        cpu_percent=5.0,
        username="testuser",
        create_time=1000.0,
        status="running",
    ):
        """Create a mock process info dict."""
        mock_mem = MagicMock()
        mock_mem.rss = rss
        return {
            "pid": pid,
            "name": name,
            "cmdline": cmdline or ["python", "script.py"],
            "ppid": ppid,
            "memory_info": mock_mem,
            "cpu_percent": cpu_percent,
            "username": username,
            "create_time": create_time,
            "status": status,
        }

    @patch("procclean.process_analyzer.get_cwd")
    @patch("procclean.process_analyzer.get_tmux_env")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_returns_process_list(
        self, mock_login, mock_iter, mock_process, mock_tmux, mock_cwd
    ):
        """Should return list of ProcessInfo objects."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/home/testuser"
        mock_tmux.return_value = False

        mock_proc = MagicMock()
        mock_proc.info = self._mock_proc_info()
        mock_iter.return_value = [mock_proc]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].pid == 1234
        assert result[0].name == "python"
        assert result[0].parent_name == "bash"

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_filters_by_user(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should filter processes by username."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc1 = MagicMock()
        mock_proc1.info = self._mock_proc_info(pid=1, username="testuser")
        mock_proc2 = MagicMock()
        mock_proc2.info = self._mock_proc_info(pid=2, username="otheruser")
        mock_iter.return_value = [mock_proc1, mock_proc2]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].pid == 1

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_filters_by_min_memory(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should filter processes below min_memory_mb."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        # 50 MB process (below default 10 MB threshold but above 5 MB)
        mock_proc1 = MagicMock()
        mock_proc1.info = self._mock_proc_info(pid=1, rss=50 * 1024 * 1024)
        # 1 MB process (below threshold)
        mock_proc2 = MagicMock()
        mock_proc2.info = self._mock_proc_info(pid=2, rss=1 * 1024 * 1024)
        mock_iter.return_value = [mock_proc1, mock_proc2]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=10.0)

        assert len(result) == 1
        assert result[0].pid == 1

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_handles_no_such_process(
        self, mock_login, mock_iter, mock_process, mock_cwd
    ):
        """Should skip processes that disappear during iteration."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc = MagicMock()
        mock_proc.info = self._mock_proc_info()

        # First call raises NoSuchProcess, second returns normally
        mock_iter.return_value = [mock_proc]

        # Accessing .info raises NoSuchProcess
        type(mock_proc).info = property(
            lambda self: (_ for _ in ()).throw(psutil.NoSuchProcess(1234))
        )

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 0

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_handles_access_denied_for_parent(
        self, mock_login, mock_iter, mock_process, mock_cwd
    ):
        """Should handle AccessDenied when getting parent process."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc = MagicMock()
        mock_proc.info = self._mock_proc_info()
        mock_iter.return_value = [mock_proc]

        mock_process.side_effect = psutil.AccessDenied(1000)

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].parent_name == "?"

    @patch("procclean.process_analyzer.get_cwd")
    @patch("procclean.process_analyzer.get_tmux_env")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_detects_orphan_with_ppid_1(
        self, mock_login, mock_iter, mock_process, mock_tmux, mock_cwd
    ):
        """Should mark process as orphan when ppid is 1."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"
        mock_tmux.return_value = False

        mock_proc = MagicMock()
        mock_proc.info = self._mock_proc_info(ppid=1)
        mock_iter.return_value = [mock_proc]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "systemd"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].is_orphan is True

    @patch("procclean.process_analyzer.get_cwd")
    @patch("procclean.process_analyzer.get_tmux_env")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_checks_tmux_for_orphans(
        self, mock_login, mock_iter, mock_process, mock_tmux, mock_cwd
    ):
        """Should check tmux env for orphan processes."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"
        mock_tmux.return_value = True

        mock_proc = MagicMock()
        mock_proc.info = self._mock_proc_info(ppid=1)
        mock_iter.return_value = [mock_proc]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "systemd"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].is_orphan is True
        assert result[0].in_tmux is True
        mock_tmux.assert_called_once_with(1234)

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_sorts_by_memory(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should sort by memory when sort_by='memory'."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc1 = MagicMock()
        mock_proc1.info = self._mock_proc_info(pid=1, rss=50 * 1024 * 1024)
        mock_proc2 = MagicMock()
        mock_proc2.info = self._mock_proc_info(pid=2, rss=200 * 1024 * 1024)
        mock_iter.return_value = [mock_proc1, mock_proc2]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(sort_by="memory", min_memory_mb=5.0)

        assert result[0].pid == 2  # Higher memory first
        assert result[1].pid == 1

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_sorts_by_cpu(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should sort by CPU when sort_by='cpu'."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc1 = MagicMock()
        mock_proc1.info = self._mock_proc_info(pid=1, cpu_percent=10.0)
        mock_proc2 = MagicMock()
        mock_proc2.info = self._mock_proc_info(pid=2, cpu_percent=50.0)
        mock_iter.return_value = [mock_proc1, mock_proc2]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(sort_by="cpu", min_memory_mb=5.0)

        assert result[0].pid == 2  # Higher CPU first
        assert result[1].pid == 1

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_sorts_by_name(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should sort by name when sort_by='name'."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc1 = MagicMock()
        mock_proc1.info = self._mock_proc_info(pid=1, name="zsh")
        mock_proc2 = MagicMock()
        mock_proc2.info = self._mock_proc_info(pid=2, name="bash")
        mock_iter.return_value = [mock_proc1, mock_proc2]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "systemd"
        mock_process.return_value = mock_parent

        result = get_process_list(sort_by="name", min_memory_mb=5.0)

        assert result[0].name == "bash"  # Alphabetically first
        assert result[1].name == "zsh"

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_handles_empty_cmdline(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should use name as cmdline when cmdline is empty."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_mem = MagicMock()
        mock_mem.rss = 100 * 1024 * 1024

        mock_proc = MagicMock()
        mock_proc.info = {
            "pid": 1234,
            "name": "kernel_proc",
            "cmdline": [],  # Empty cmdline
            "ppid": 1000,
            "memory_info": mock_mem,
            "cpu_percent": 5.0,
            "username": "testuser",
            "create_time": 1000.0,
            "status": "running",
        }
        mock_iter.return_value = [mock_proc]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].cmdline == "kernel_proc"

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_handles_none_memory_info(
        self, mock_login, mock_iter, mock_process, mock_cwd
    ):
        """Should handle None memory_info gracefully."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc = MagicMock()
        info = self._mock_proc_info()
        info["memory_info"] = None
        mock_proc.info = info
        mock_iter.return_value = [mock_proc]

        result = get_process_list(min_memory_mb=5.0)

        # Should be filtered out because 0 MB < 5 MB min
        assert len(result) == 0

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_handles_zombie_process(
        self, mock_login, mock_iter, mock_process, mock_cwd
    ):
        """Should skip zombie processes."""
        mock_login.return_value = "testuser"

        mock_proc = MagicMock()
        # Accessing .info raises ZombieProcess
        type(mock_proc).info = property(
            lambda self: (_ for _ in ()).throw(psutil.ZombieProcess(1234))
        )
        mock_iter.return_value = [mock_proc]

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 0

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_uses_custom_filter_user(
        self, mock_login, mock_iter, mock_process, mock_cwd
    ):
        """Should filter by custom user when specified."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc1 = MagicMock()
        mock_proc1.info = self._mock_proc_info(pid=1, username="testuser")
        mock_proc2 = MagicMock()
        mock_proc2.info = self._mock_proc_info(pid=2, username="admin")
        mock_iter.return_value = [mock_proc1, mock_proc2]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "bash"
        mock_process.return_value = mock_parent

        result = get_process_list(filter_user="admin", min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].pid == 2

    @patch("procclean.process_analyzer.get_cwd")
    @patch("psutil.Process")
    @patch("psutil.process_iter")
    @patch("os.getlogin")
    def test_handles_none_ppid(self, mock_login, mock_iter, mock_process, mock_cwd):
        """Should handle None ppid gracefully."""
        mock_login.return_value = "testuser"
        mock_cwd.return_value = "/tmp"

        mock_proc = MagicMock()
        info = self._mock_proc_info()
        info["ppid"] = None
        mock_proc.info = info
        mock_iter.return_value = [mock_proc]

        mock_parent = MagicMock()
        mock_parent.name.return_value = "init"
        mock_process.return_value = mock_parent

        result = get_process_list(min_memory_mb=5.0)

        assert len(result) == 1
        assert result[0].ppid == 0


class TestFindSimilarProcesses:
    """Tests for find_similar_processes function."""

    def test_groups_similar_processes(self, make_process):
        """Should group processes with same command."""
        procs = [
            make_process(pid=1, name="python", cmdline="python script.py"),
            make_process(pid=2, name="python", cmdline="python other.py"),
            make_process(pid=3, name="node", cmdline="node server.js"),
        ]
        groups = find_similar_processes(procs)
        assert "python" in groups
        assert len(groups["python"]) == 2
        assert "node" not in groups  # only 1 process

    def test_returns_empty_for_unique_processes(self, make_process):
        """Should return empty dict when all processes are unique."""
        procs = [
            make_process(pid=1, name="python", cmdline="python script.py"),
            make_process(pid=2, name="node", cmdline="node server.js"),
            make_process(pid=3, name="ruby", cmdline="ruby app.rb"),
        ]
        groups = find_similar_processes(procs)
        assert groups == {}

    def test_normalizes_paths_in_cmdline(self, make_process):
        """Should normalize full paths to just the executable name."""
        procs = [
            make_process(pid=1, name="python", cmdline="/usr/bin/python script.py"),
            make_process(
                pid=2, name="python", cmdline="/home/user/.venv/bin/python other.py"
            ),
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
            success, _msg = kill_process(1234, force=True)
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

    def test_generic_exception(self):
        """Should catch and return generic exceptions."""
        with patch("psutil.Process") as mock_proc:
            mock_proc.return_value.terminate.side_effect = OSError("Unexpected error")
            success, msg = kill_process(1234)
            assert success is False
            assert "Error:" in msg
            assert "Unexpected error" in msg


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

    def test_is_orphan_candidate_true(self, make_process):
        """Should return True when orphan and not in tmux."""
        proc = make_process(is_orphan=True, in_tmux=False)
        assert proc.is_orphan_candidate is True

    def test_is_orphan_candidate_false_when_in_tmux(self, make_process):
        """Should return False when orphan but in tmux."""
        proc = make_process(is_orphan=True, in_tmux=True)
        assert proc.is_orphan_candidate is False

    def test_is_orphan_candidate_false_when_not_orphan(self, make_process):
        """Should return False when not orphan."""
        proc = make_process(is_orphan=False, in_tmux=False)
        assert proc.is_orphan_candidate is False


class TestFilterOrphans:
    """Tests for filter_orphans function."""

    def test_filters_orphans_only(self, sample_processes):
        """Should return only orphaned processes."""
        result = filter_orphans(sample_processes)
        assert all(p.is_orphan for p in result)
        # sample_processes has 3 orphans (pid 2, 3, 5)
        assert len(result) == 3

    def test_empty_list(self):
        """Should return empty list for empty input."""
        assert filter_orphans([]) == []

    def test_no_orphans(self, make_process):
        """Should return empty list when no orphans."""
        procs = [make_process(is_orphan=False), make_process(pid=2, is_orphan=False)]
        assert filter_orphans(procs) == []


class TestFilterHighMemory:
    """Tests for filter_high_memory function."""

    def test_filters_above_threshold(self, sample_processes):
        """Should return processes above default threshold."""
        result = filter_high_memory(sample_processes, threshold_mb=500.0)
        assert all(p.rss_mb > 500.0 for p in result)
        # sample_processes: python=500 (not >500), app=800
        assert len(result) == 1

    def test_custom_threshold(self, sample_processes):
        """Should use custom threshold."""
        result = filter_high_memory(sample_processes, threshold_mb=100.0)
        # python=500, node=300, rust=200, app=800 (all > 100)
        assert len(result) == 4

    def test_empty_list(self):
        """Should return empty list for empty input."""
        assert filter_high_memory([]) == []


class TestSortProcesses:
    """Tests for sort_processes function."""

    def test_sort_by_memory_descending(self, sample_processes):
        """Should sort by memory descending by default."""
        result = sort_processes(sample_processes, sort_by="memory", reverse=True)
        assert result[0].rss_mb >= result[-1].rss_mb
        assert result[0].pid == 5  # app has 800 MB

    def test_sort_by_memory_ascending(self, sample_processes):
        """Should sort by memory ascending when reverse=False."""
        result = sort_processes(sample_processes, sort_by="memory", reverse=False)
        assert result[0].rss_mb <= result[-1].rss_mb
        assert result[0].pid == 4  # zsh has 50 MB

    def test_sort_by_cpu(self, sample_processes):
        """Should sort by CPU percent."""
        result = sort_processes(sample_processes, sort_by="cpu", reverse=True)
        assert result[0].cpu_percent >= result[-1].cpu_percent
        assert result[0].pid == 3  # rust has 50%

    def test_sort_by_pid(self, sample_processes):
        """Should sort by PID."""
        result = sort_processes(sample_processes, sort_by="pid", reverse=False)
        assert result[0].pid == 1
        assert result[-1].pid == 5

    def test_sort_by_name(self, sample_processes):
        """Should sort by name alphabetically."""
        result = sort_processes(sample_processes, sort_by="name", reverse=False)
        names = [p.name.lower() for p in result]
        assert names == sorted(names)

    def test_mem_alias(self, sample_processes):
        """Should accept 'mem' as alias for 'memory'."""
        result = sort_processes(sample_processes, sort_by="mem", reverse=True)
        assert result[0].rss_mb >= result[-1].rss_mb

    def test_unknown_sort_defaults_to_memory(self, sample_processes):
        """Should default to memory for unknown sort key."""
        result = sort_processes(sample_processes, sort_by="unknown", reverse=True)
        assert result[0].rss_mb >= result[-1].rss_mb
