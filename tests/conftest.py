"""Shared test fixtures."""

import pytest

from procclean.core import ProcessInfo

# Test constants - expected values in assertions
# PIDs from sample_processes
PID_PYTHON = 1
PID_NODE = 2
PID_RUST = 3
PID_ZSH = 4
PID_APP = 5

# Memory values
MEM_PYTHON = 500.0
MEM_NODE = 300.0
MEM_RUST = 200.0
MEM_ZSH = 50.0
MEM_APP = 800.0

# CPU values
CPU_PYTHON = 25.0
CPU_NODE = 10.0
CPU_RUST = 50.0
CPU_ZSH = 0.5
CPU_APP = 5.0

# CLI test values
CLI_LIMIT_10 = 10
CLI_LIMIT_5 = 5
CLI_LIMIT_2 = 2
CLI_MIN_MEMORY = 50.0
CLI_HIGH_THRESHOLD = 1000.0
CLI_HIGH_THRESHOLD_200 = 200.0
CLI_TOTAL_GB = 16.0

# Filter thresholds
THRESHOLD_100 = 100.0
THRESHOLD_500 = 500.0
PERCENT_50 = 50.0

# Formatter test values
CLIP_WIDTH_8 = 8
CLIP_WIDTH_10 = 10
CLIP_WIDTH_15 = 15
COL_COUNT_3 = 3
MIN_TABLE_LINES = 3
TEST_PID_42 = 42
NAME_MAX_WIDTH = 25

# Kill results count
KILL_RESULTS_3 = 3

# Filter results
ORPHAN_COUNT = 3
HIGH_MEM_COUNT_1 = 1
HIGH_MEM_COUNT_4 = 4

# CWD filter counts
CWD_MATCH_COUNT = 2

# Test paths - using var instead of tmp for S108 compliance
TEST_PATH_A = "/var/test/a"
TEST_PATH_B = "/var/test/b"
TEST_PATH_AB = "/var/test/ab"
TEST_PATH_Z = "/var/test/z"
TEST_PATH_BUILD = "/var/build"
TEST_PATH_SINGLE = "/var/test"
TEST_PATH_GLOB = "/var/test/?"

# Default test PID
TEST_PID_DEFAULT = 1234


@pytest.fixture
def make_process():
    """Create ProcessInfo objects with configurable defaults.

    Returns:
        Callable[..., ProcessInfo]: Factory function that returns a ProcessInfo
        instance.
    """

    def _make(
        pid: int = 1234,
        name: str = "test",
        cmdline: str = "test cmd",
        cwd: str = "/var/test",
        ppid: int = 1,
        parent_name: str = "systemd",
        rss_mb: float = 100.0,
        cpu_percent: float = 1.0,
        username: str = "user",
        create_time: float = 0.0,
        is_orphan: bool = False,
        in_tmux: bool = False,
        status: str = "running",
    ) -> ProcessInfo:
        return ProcessInfo(
            pid=pid,
            name=name,
            cmdline=cmdline,
            cwd=cwd,
            ppid=ppid,
            parent_name=parent_name,
            rss_mb=rss_mb,
            cpu_percent=cpu_percent,
            username=username,
            create_time=create_time,
            is_orphan=is_orphan,
            in_tmux=in_tmux,
            status=status,
        )

    return _make


@pytest.fixture
def sample_processes(make_process):
    """Sample list of processes for testing.

    Returns:
        list[ProcessInfo]: List of sample processes.
    """
    return [
        make_process(pid=1, name="python", rss_mb=500.0, cpu_percent=25.0),
        make_process(
            pid=2, name="node", rss_mb=300.0, cpu_percent=10.0, is_orphan=True
        ),
        make_process(
            pid=3,
            name="rust",
            rss_mb=200.0,
            cpu_percent=50.0,
            is_orphan=True,
            in_tmux=True,
        ),
        make_process(pid=4, name="zsh", rss_mb=50.0, cpu_percent=0.5),
        make_process(pid=5, name="app", rss_mb=800.0, cpu_percent=5.0, is_orphan=True),
    ]
