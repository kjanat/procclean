#!/usr/bin/env -S uv run
# ruff: noqa: T201, DOC201
"""Generate TUI screenshots for documentation.

Uses mock process data for consistent, reproducible screenshots across CI runs.
"""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from unittest.mock import patch

from procclean.core import ProcessInfo
from procclean.tui.app import ProcessCleanerApp

# Mock process data for consistent screenshots
MOCK_PROCESSES: list[ProcessInfo] = [
    ProcessInfo(
        pid=1234,
        name="python",
        cmdline="python manage.py runserver",
        cwd="/home/user/projects/myapp",
        ppid=1,
        parent_name="systemd",
        rss_mb=512.4,
        cpu_percent=15.2,
        username="user",
        create_time=1704067200.0,
        is_orphan=True,
        in_tmux=False,
        status="running",
    ),
    ProcessInfo(
        pid=2345,
        name="node",
        cmdline="node server.js",
        cwd="/home/user/projects/webapp",
        ppid=1234,
        parent_name="python",
        rss_mb=384.7,
        cpu_percent=8.5,
        username="user",
        create_time=1704067300.0,
        is_orphan=False,
        in_tmux=False,
        status="running",
    ),
    ProcessInfo(
        pid=3456,
        name="cargo",
        cmdline="cargo build --release",
        cwd="/home/user/projects/rustproject",
        ppid=1,
        parent_name="systemd",
        rss_mb=892.1,
        cpu_percent=45.3,
        username="user",
        create_time=1704067400.0,
        is_orphan=True,
        in_tmux=False,
        status="running",
    ),
    ProcessInfo(
        pid=4567,
        name="vim",
        cmdline="vim config.yaml",
        cwd="/home/user/dotfiles",
        ppid=5678,
        parent_name="tmux",
        rss_mb=45.2,
        cpu_percent=0.1,
        username="user",
        create_time=1704067500.0,
        is_orphan=False,
        in_tmux=True,
        status="sleeping",
    ),
    ProcessInfo(
        pid=5678,
        name="tmux",
        cmdline="tmux new-session",
        cwd="/home/user",
        ppid=1,
        parent_name="systemd",
        rss_mb=12.8,
        cpu_percent=0.0,
        username="user",
        create_time=1704067600.0,
        is_orphan=False,
        in_tmux=False,
        status="sleeping",
    ),
    ProcessInfo(
        pid=6789,
        name="gopls",
        cmdline="gopls serve",
        cwd="/home/user/projects/goservice",
        ppid=1,
        parent_name="systemd",
        rss_mb=678.9,
        cpu_percent=12.4,
        username="user",
        create_time=1704067700.0,
        is_orphan=True,
        in_tmux=False,
        status="running",
    ),
    ProcessInfo(
        pid=7890,
        name="rust-analyzer",
        cmdline="rust-analyzer",
        cwd="/home/user/projects/rustproject",
        ppid=1,
        parent_name="systemd",
        rss_mb=1024.5,
        cpu_percent=22.1,
        username="user",
        create_time=1704067800.0,
        is_orphan=True,
        in_tmux=False,
        status="running",
    ),
    ProcessInfo(
        pid=8901,
        name="webpack",
        cmdline="webpack --watch",
        cwd="/home/user/projects/webapp",
        ppid=2345,
        parent_name="node",
        rss_mb=256.3,
        cpu_percent=5.7,
        username="user",
        create_time=1704067900.0,
        is_orphan=False,
        in_tmux=False,
        status="running",
    ),
]

MOCK_MEMORY = {
    "total_gb": 32.0,
    "used_gb": 18.5,
    "free_gb": 13.5,
    "percent": 57.8,
    "swap_total_gb": 8.0,
    "swap_used_gb": 0.5,
}


def mock_get_process_list(min_memory_mb: float = 0.0) -> list[ProcessInfo]:
    """Return mock process list."""
    return [p for p in MOCK_PROCESSES if p.rss_mb >= min_memory_mb]


def mock_get_memory_summary() -> dict:
    """Return mock memory summary."""
    return MOCK_MEMORY


async def take_screenshot(
    output_dir: Path,
    filename: str,
    view: str = "all",
    selected_pids: set[int] | None = None,
) -> Path:
    """Take a screenshot of the TUI in a specific state.

    Args:
        output_dir: Directory to save screenshots.
        filename: Name of the screenshot file (without extension).
        view: The view to show ("all", "orphans", "groups", "high-mem").
        selected_pids: PIDs to mark as selected.

    Returns:
        Path to the generated screenshot.
    """
    with (
        patch("procclean.tui.app.get_process_list", mock_get_process_list),
        patch("procclean.tui.app.get_memory_summary", mock_get_memory_summary),
    ):
        app = ProcessCleanerApp()

        async with app.run_test(size=(120, 30)) as pilot:
            # Set view
            if view == "orphans":
                await pilot.press("o")
            elif view == "groups":
                await pilot.press("g")
            elif view == "high-mem":
                # Navigate to high-mem via sidebar would be complex,
                # just filter manually
                app.current_view = "high-mem"
                app.update_table()

            # Apply selections
            if selected_pids:
                app.selected_pids = selected_pids
                app.update_table()

            # Wait for render
            await pilot.pause()

            # Save screenshot
            output_path = output_dir / f"{filename}.svg"
            app.save_screenshot(filename=f"{filename}.svg", path=str(output_dir))

            return output_path


async def main() -> None:
    """Generate all documentation screenshots."""
    # Output to docs/assets/screenshots/
    output_dir = Path(__file__).parent.parent / "docs" / "assets" / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating screenshots to {output_dir}")

    # Main view - all processes
    path = await take_screenshot(output_dir, "tui-main", view="all")
    print(f"  Created: {path}")

    # Orphans view
    path = await take_screenshot(output_dir, "tui-orphans", view="orphans")
    print(f"  Created: {path}")

    # With selections
    path = await take_screenshot(
        output_dir,
        "tui-selected",
        view="all",
        selected_pids={1234, 3456, 7890},
    )
    print(f"  Created: {path}")

    # High memory view
    path = await take_screenshot(output_dir, "tui-high-memory", view="high-mem")
    print(f"  Created: {path}")

    # Optimize SVGs
    print("Optimizing SVGs with SVGO...")
    subprocess.run(
        ["npx", "-y", "svgo", "--multipass", *output_dir.glob("*.svg")],
        check=True,
    )

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
