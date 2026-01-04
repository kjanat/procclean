#!/usr/bin/env -S uv run
"""Generate TUI screenshots for documentation.

Uses mock process data for consistent, reproducible screenshots across CI runs.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple
from unittest.mock import patch

from textual.widgets import OptionList

from procclean.core import HIGH_MEMORY_THRESHOLD_MB, ProcessInfo
from procclean.tui.app import ProcessCleanerApp, ViewType

log = logging.getLogger(__name__)

# Output directory for screenshots
SCREENSHOTS_DIR = Path(__file__).parent.parent / "docs" / "assets" / "screenshots"

# -----------------------------------------------------------------------------
# Mock Process Data - Declarative Specs
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ProcessSpec:
    """Minimal declarative spec - only what matters for screenshots."""

    name: str
    cmdline_suffix: str
    cwd_suffix: str
    rss_mb: float
    cpu_weight: float  # Relative weight, normalized later
    is_orphan: bool = True
    in_tmux: bool = False
    status: str = "running"
    parent_ref: str | None = None  # Reference another spec by name:cmdline_suffix


# Compact, easy to review in diffs
# fmt: off
PROCESS_SPECS: tuple[ProcessSpec, ...] = (
    ProcessSpec("python", "manage.py runserver", "myapp", 512.4, 3.0),
    ProcessSpec("python", "celery worker", "myapp", 328.6, 1.0),
    ProcessSpec("python", "-m pytest", "myapp", 156.2, 15.0),
    ProcessSpec("node", "server.js", "webapp", 384.7, 2.0,
                is_orphan=False, parent_ref="python:manage.py runserver"),
    ProcessSpec("node", "worker.js", "webapp", 412.1, 2.5),
    ProcessSpec("cargo", "build --release", "rustproject", 892.1, 8.0),
    ProcessSpec("vim", "config.yaml", "dotfiles", 45.2, 0.02,
                is_orphan=False, in_tmux=True, status="sleeping",
                parent_ref="tmux:new-session"),
    ProcessSpec("tmux", "new-session", "", 12.8, 0.0,
                is_orphan=False, status="sleeping"),
    ProcessSpec("gopls", "serve", "goservice", 678.9, 2.5),
    ProcessSpec("rust-analyzer", "", "rustproject", 1024.5, 4.0),
    ProcessSpec("webpack", "--watch", "webapp", 256.3, 1.2,
                is_orphan=False, parent_ref="node:server.js"),
)
# fmt: on

# Minimum high-memory processes needed for screenshot
MIN_HIGH_MEM_PROCESSES = 2


def _spec_key(spec: ProcessSpec) -> str:
    return f"{spec.name}:{spec.cmdline_suffix}"


def _stable_pid(spec: ProcessSpec) -> int:
    h = hashlib.md5(_spec_key(spec).encode(), usedforsecurity=False)
    return 1000 + (int(h.hexdigest()[:4], 16) % 9000)


def _normalize_cpu(
    specs: tuple[ProcessSpec, ...], target_total: float = 85.0
) -> dict[ProcessSpec, float]:
    total_weight = sum(s.cpu_weight for s in specs)
    if total_weight == 0:
        return dict.fromkeys(specs, 0.0)
    return {s: round(s.cpu_weight / total_weight * target_total, 1) for s in specs}


def _generate_mock_processes() -> list[ProcessInfo]:
    # Validate unique PIDs
    pids = [_stable_pid(s) for s in PROCESS_SPECS]
    assert len(pids) == len(set(pids)), "PID collision - rename a process"

    # Validate high-memory processes for screenshot
    high_mem_count = sum(
        1 for s in PROCESS_SPECS if s.rss_mb >= HIGH_MEMORY_THRESHOLD_MB
    )
    assert high_mem_count >= MIN_HIGH_MEM_PROCESSES, (
        f"Need >={MIN_HIGH_MEM_PROCESSES} high-memory processes, got {high_mem_count}"
    )

    cpu_map = _normalize_cpu(PROCESS_SPECS)

    # Build PID mapping
    pid_map: dict[str, int] = {}
    for spec in PROCESS_SPECS:
        pid_map[_spec_key(spec)] = _stable_pid(spec)

    # Base timestamp (2024-01-01 00:00:00 UTC)
    base_time = 1704067200.0

    processes = []
    for i, spec in enumerate(PROCESS_SPECS):
        # Resolve parent
        if spec.parent_ref:
            ppid = pid_map.get(spec.parent_ref, 1)
            parent_name = spec.parent_ref.split(":")[0]
        else:
            ppid = 1
            parent_name = "systemd"

        cwd = (
            f"/home/user/projects/{spec.cwd_suffix}"
            if spec.cwd_suffix
            else "/home/user"
        )
        cmdline = f"{spec.name} {spec.cmdline_suffix}".strip()

        processes.append(
            ProcessInfo(
                pid=pid_map[_spec_key(spec)],
                name=spec.name,
                cmdline=cmdline,
                cwd=cwd,
                ppid=ppid,
                parent_name=parent_name,
                rss_mb=spec.rss_mb,
                cpu_percent=cpu_map[spec],
                username="user",
                create_time=base_time + (i * 50.0),
                is_orphan=spec.is_orphan,
                in_tmux=spec.in_tmux,
                status=spec.status,
            )
        )

    return processes


def _calculate_mock_memory(
    processes: list[ProcessInfo],
    total_gb: float = 32.0,
    system_overhead_gb: float = 6.0,
    swap_total_gb: float = 8.0,
    swap_used_gb: float = 0.5,
) -> dict[str, float]:
    """Derive memory stats from process list for consistency.

    Args:
        processes: List of mock processes to sum RSS from.
        total_gb: Total system RAM.
        system_overhead_gb: Realistic overhead (kernel, buffers, page cache).
        swap_total_gb: Total swap space.
        swap_used_gb: Used swap space.

    Returns:
        Memory stats dict matching get_memory_summary() format.
    """
    process_rss_gb = sum(p.rss_mb for p in processes) / 1024
    used_gb = round(process_rss_gb + system_overhead_gb, 1)

    return {
        "total_gb": total_gb,
        "used_gb": used_gb,
        "free_gb": round(total_gb - used_gb, 1),
        "percent": round(used_gb / total_gb * 100, 1),
        "swap_total_gb": swap_total_gb,
        "swap_used_gb": swap_used_gb,
    }


# Single source of truth - generated at module load
MOCK_PROCESSES: list[ProcessInfo] = _generate_mock_processes()
MOCK_MEMORY: dict[str, float] = _calculate_mock_memory(MOCK_PROCESSES)

# -----------------------------------------------------------------------------
# Screenshot Configuration
# -----------------------------------------------------------------------------


class ScreenshotConfig(NamedTuple):
    """Configuration for a single screenshot."""

    filename: str
    view: ViewType = "all"
    selected_pids: frozenset[int] = frozenset()


# Get some PIDs for the "selected" screenshot (first 3 orphans)
_orphan_pids = frozenset(p.pid for p in MOCK_PROCESSES if p.is_orphan)
_selected_pids = frozenset(list(_orphan_pids)[:3])

SCREENSHOT_CONFIGS: list[ScreenshotConfig] = [
    ScreenshotConfig("tui-main", view="all"),
    ScreenshotConfig("tui-orphans", view="orphans"),
    ScreenshotConfig("tui-groups", view="groups"),
    ScreenshotConfig("tui-selected", view="all", selected_pids=_selected_pids),
    ScreenshotConfig("tui-high-memory", view="high-mem"),
]

# -----------------------------------------------------------------------------
# Mock Functions for TUI
# -----------------------------------------------------------------------------


def mock_get_process_list(min_memory_mb: float = 0.0) -> list[ProcessInfo]:
    """Return a filtered list of mock processes.

    Args:
        min_memory_mb: Minimum RSS memory (in MB) required for a process to be
            included.

    Returns:
        A list of mock ProcessInfo objects whose rss_mb >= min_memory_mb.
    """
    return [p for p in MOCK_PROCESSES if p.rss_mb >= min_memory_mb]


def mock_get_memory_summary() -> dict[str, float]:
    """Return mock memory summary for TUI patching.

    Returns:
        MOCK_MEMORY dict with total/used/free GB, percent, and swap values.
    """
    return MOCK_MEMORY


# -----------------------------------------------------------------------------
# Screenshot Generation
# -----------------------------------------------------------------------------


async def take_screenshot(
    output_dir: Path,
    config: ScreenshotConfig,
) -> Path:
    """Take a screenshot of the TUI in a specific state.

    Args:
        output_dir: Directory to save screenshots.
        config: Screenshot configuration.

    Returns:
        Path to the generated screenshot.
    """
    with (
        patch("procclean.tui.app.get_process_list", mock_get_process_list),
        patch("procclean.tui.app.get_memory_summary", mock_get_memory_summary),
    ):
        app = ProcessCleanerApp()

        async with app.run_test(size=(120, 30)) as pilot:
            # Map view names to sidebar option indices
            view_index = {"all": 0, "orphans": 1, "groups": 2, "high-mem": 3}

            # Set view and update sidebar selection
            if config.view != "all":
                app.current_view = config.view
                app.update_table()

            # Update sidebar highlight to match view
            sidebar = app.query_one("#view-selector", OptionList)
            sidebar.highlighted = view_index.get(config.view, 0)

            # Apply selections
            if config.selected_pids:
                app.selected_pids = set(config.selected_pids)
                app.update_table()

            # Wait for render
            await pilot.pause()

            # Save screenshot
            output_path = output_dir / f"{config.filename}.svg"
            app.save_screenshot(filename=f"{config.filename}.svg", path=str(output_dir))

            return output_path


def optimize_svgs(output_dir: Path) -> bool:
    """Optimize SVGs with SVGO if available.

    Args:
        output_dir: Directory containing SVG files.

    Returns:
        True if optimization was performed, False if SVGO not available.
    """
    npx_path = shutil.which("npx")
    if not npx_path:
        return False

    svg_files = list(output_dir.glob("*.svg"))
    if not svg_files:
        return False

    try:
        subprocess.run(
            ["npx", "-y", "svgo", "--multipass", "--pretty", *svg_files],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError, FileNotFoundError:
        return False


async def generate_screenshots_async() -> list[Path]:
    """Generate all screenshots asynchronously.

    Returns:
        List of paths to generated screenshots.
    """
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    for config in SCREENSHOT_CONFIGS:
        path = await take_screenshot(SCREENSHOTS_DIR, config)
        generated.append(path)

    return generated


def write_screenshots() -> bool:
    """Generate screenshots and return whether any were created/updated.

    This is the main entry point for both hooks and CLI usage.

    Returns:
        True if screenshots were generated (always True when called).
    """
    log.info("Generating screenshots to %s", SCREENSHOTS_DIR)

    generated = asyncio.run(generate_screenshots_async())

    for path in generated:
        log.info("  Created: %s", path)

    log.info("Optimizing SVGs with SVGO...")
    optimized = optimize_svgs(SCREENSHOTS_DIR)

    if optimized:
        log.info("  SVGs optimized")
    else:
        log.info("  SVGO not available, skipping optimization")

    log.info("Done!")

    return len(generated) > 0


def main() -> int:
    """Generate all documentation screenshots.

    Returns:
        Exit code (0 for success).
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    write_screenshots()
    return 0


if __name__ == "__main__":
    sys.exit(main())
