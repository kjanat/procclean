"""Shared test fixtures."""

import pytest

from procclean.core import ProcessInfo


@pytest.fixture
def make_process():
    """Factory fixture to create ProcessInfo objects with defaults."""

    def _make(
        pid: int = 1234,
        name: str = "test",
        cmdline: str = "test cmd",
        cwd: str = "/tmp",
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
    """Sample list of processes for testing."""
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
