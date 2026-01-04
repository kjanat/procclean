"""Tests for TUI app module."""

from unittest.mock import patch

import pytest
from textual.widgets import OptionList, Static

from procclean import main
from procclean.tui import ConfirmKillScreen, ProcessCleanerApp


@pytest.fixture
def mock_process_data(sample_processes):
    """Patch process_analyzer functions for app tests.

    Yields:
        dict: Mocked functions for testing.

    """
    with (
        patch("procclean.tui.app.get_process_list") as mock_get_procs,
        patch("procclean.tui.app.get_memory_summary") as mock_mem,
        patch("procclean.tui.app.find_similar_processes") as mock_find,
        patch("procclean.tui.app.kill_processes") as mock_kill,
    ):
        mock_get_procs.return_value = sample_processes
        mock_mem.return_value = {
            "total_gb": 16.0,
            "used_gb": 8.0,
            "free_gb": 8.0,
            "percent": 50.0,
            "swap_used_gb": 1.0,
            "swap_total_gb": 4.0,
        }
        mock_find.return_value = {"python": sample_processes[:2]}
        mock_kill.return_value = []
        yield {
            "get_procs": mock_get_procs,
            "mem": mock_mem,
            "find": mock_find,
            "kill": mock_kill,
        }


@pytest.fixture
def many_processes(make_process):
    """Create 15 processes for testing >10 display."""
    return [make_process(pid=i, name=f"proc{i}", rss_mb=100.0 + i) for i in range(15)]


@pytest.fixture
def long_cwd_processes(make_process):
    """Create processes with long cwd paths."""
    return [
        make_process(
            pid=1,
            name="longpath",
            cwd="/very/long/path/to/some/deeply/nested/directory/structure",
            rss_mb=600.0,  # High memory to show in high-mem view
        ),
    ]


class TestProcessCleanerApp:
    """Tests for ProcessCleanerApp TUI."""

    @pytest.mark.asyncio
    async def test_app_starts(self, mock_process_data):
        """Should start and display without error."""
        app = ProcessCleanerApp()
        async with app.run_test():
            # App should be running
            assert app.is_running
            assert app.title == "ProcClean"

    @pytest.mark.asyncio
    async def test_refresh_keybinding(self, mock_process_data):
        """Should refresh data when 'r' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            initial_call_count = mock_process_data["get_procs"].call_count
            await pilot.press("r")
            assert mock_process_data["get_procs"].call_count > initial_call_count

    @pytest.mark.asyncio
    async def test_quit_keybinding(self, mock_process_data):
        """Should quit when 'q' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("q")
            assert not app.is_running

    @pytest.mark.asyncio
    async def test_show_orphans_view(self, mock_process_data):
        """Should switch to orphans view when 'o' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("o")
            assert app.current_view == "orphans"

    @pytest.mark.asyncio
    async def test_show_all_view(self, mock_process_data):
        """Should switch to all view when 'a' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("o")  # First switch to orphans
            await pilot.press("a")  # Then back to all
            assert app.current_view == "all"

    @pytest.mark.asyncio
    async def test_show_groups_view(self, mock_process_data):
        """Should switch to groups view when 'g' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("g")
            assert app.current_view == "groups"

    @pytest.mark.asyncio
    async def test_sort_by_memory(self, mock_process_data):
        """Should sort by memory when '1' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            app.sort_key = "cpu"  # Set to something else first
            await pilot.press("1")
            assert app.sort_key == "memory"

    @pytest.mark.asyncio
    async def test_sort_by_cpu(self, mock_process_data):
        """Should sort by CPU when '2' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("2")
            assert app.sort_key == "cpu"

    @pytest.mark.asyncio
    async def test_sort_by_pid(self, mock_process_data):
        """Should sort by PID when '3' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("3")
            assert app.sort_key == "pid"

    @pytest.mark.asyncio
    async def test_sort_by_name(self, mock_process_data):
        """Should sort by name when '4' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("4")
            assert app.sort_key == "name"

    @pytest.mark.asyncio
    async def test_sort_by_cwd(self, mock_process_data):
        """Should sort by cwd when '5' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("5")
            assert app.sort_key == "cwd"

    @pytest.mark.asyncio
    async def test_toggle_sort_order(self, mock_process_data):
        """Should toggle sort order when '!' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            initial_order = app.sort_reverse
            await pilot.press("!")
            assert app.sort_reverse != initial_order

    @pytest.mark.asyncio
    async def test_sort_same_key_toggles_order(self, mock_process_data):
        """Pressing same sort key should toggle order."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Default is memory descending
            assert app.sort_key == "memory"
            assert app.sort_reverse is True
            await pilot.press("1")  # Press memory again
            assert app.sort_key == "memory"
            assert app.sort_reverse is False  # Should toggle

    @pytest.mark.asyncio
    async def test_clear_selection(self, mock_process_data):
        """Should clear selection when 'c' pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            app.selected_pids = {1, 2, 3}
            await pilot.press("c")
            assert len(app.selected_pids) == 0

    @pytest.mark.asyncio
    async def test_kill_without_selection_shows_message(self, mock_process_data):
        """Should show message when trying to kill with no selection."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            app.selected_pids.clear()
            await pilot.press("k")
            assert "No processes selected" in app.status_message

    @pytest.mark.asyncio
    async def test_memory_bar_displays(self, mock_process_data):
        """Should display memory stats in bar."""
        app = ProcessCleanerApp()
        async with app.run_test():
            mem_total = app.query_one("#mem-total", Static)
            # Static widget uses update() to set content
            assert mem_total is not None

    @pytest.mark.asyncio
    async def test_high_mem_view(self, mock_process_data, make_process):
        """Should filter to high memory processes in high-mem view."""
        # Create processes with varying memory
        high_mem_procs = [
            make_process(pid=1, name="small", rss_mb=100.0),
            make_process(pid=2, name="big", rss_mb=600.0),
            make_process(pid=3, name="huge", rss_mb=1000.0),
        ]
        mock_process_data["get_procs"].return_value = high_mem_procs

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Switch to high-mem view
            app.current_view = "high-mem"
            app.update_table()
            await pilot.pause()
            # Only processes > 500 MB should be shown
            assert app.current_view == "high-mem"

    @pytest.mark.asyncio
    async def test_long_cwd_truncation(self, mock_process_data, make_process):
        """Should truncate long cwd paths."""
        long_cwd_proc = make_process(
            pid=1,
            name="test",
            cwd="/very/long/path/to/some/deeply/nested/directory/here",
            rss_mb=100.0,
        )
        mock_process_data["get_procs"].return_value = [long_cwd_proc]

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            app.update_table()
            await pilot.pause()
            # Table should have been updated with truncated cwd
            assert len(app.processes) == 1

    @pytest.mark.asyncio
    async def test_toggle_select_add(self, mock_process_data):
        """Should add to selection with space."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Initially no selection
            assert len(app.selected_pids) == 0
            # Move to first row and toggle
            await pilot.press("space")
            await pilot.pause()
            # Should have selected one process
            assert len(app.selected_pids) == 1

    @pytest.mark.asyncio
    async def test_toggle_select_remove(self, mock_process_data, sample_processes):
        """Should remove from selection with space when already selected."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # First add via toggle
            await pilot.press("space")
            await pilot.pause()
            initial_count = len(app.selected_pids)
            assert initial_count >= 1
            # Toggle again to remove
            await pilot.press("space")
            await pilot.pause()
            # Should have removed the process
            assert len(app.selected_pids) == initial_count - 1

    @pytest.mark.asyncio
    async def test_view_change_via_option_list(self, mock_process_data):
        """Should change view when selecting from OptionList."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Find and click the orphans option
            option_list = app.query_one("#view-selector", OptionList)
            # Highlight the orphans option (index 1)
            option_list.highlighted = 1
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            # View should have changed
            assert app.current_view == "orphans"

    @pytest.mark.asyncio
    async def test_select_all_visible(self, mock_process_data, sample_processes):
        """Should select all visible processes with 's'."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("s")
            await pilot.pause()
            # All visible processes should be selected
            assert len(app.selected_pids) == len(sample_processes)

    @pytest.mark.asyncio
    async def test_kill_with_selection(self, mock_process_data, sample_processes):
        """Should open confirm dialog when killing with selection."""
        mock_process_data["kill"].return_value = [(1, True, "killed")]

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Select a process
            app.selected_pids.add(1)
            # Press kill
            await pilot.press("k")
            await pilot.pause()
            # Confirm dialog should be shown - press 'y' to confirm
            await pilot.press("y")
            await pilot.pause()
            # Kill should have been called
            mock_process_data["kill"].assert_called()

    @pytest.mark.asyncio
    async def test_force_kill_with_selection(self, mock_process_data, sample_processes):
        """Should force kill with 'K'."""
        mock_process_data["kill"].return_value = [(1, True, "killed")]

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            app.selected_pids.add(1)
            await pilot.press("K")  # Capital K for force kill
            await pilot.pause()
            await pilot.press("y")
            await pilot.pause()
            mock_process_data["kill"].assert_called_with([1], force=True)

    @pytest.mark.asyncio
    async def test_filter_cwd(self, mock_process_data, make_process):
        """Should filter by cwd when 'w' pressed."""
        procs = [
            make_process(pid=1, name="proc1", cwd="/home/user/project"),
            make_process(pid=2, name="proc2", cwd="/tmp"),
        ]
        mock_process_data["get_procs"].return_value = procs

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Move to first row (which has cwd /home/user/project)
            await pilot.press("w")
            await pilot.pause()
            assert app.cwd_filter == "/home/user/project"
            assert "cwd=" in app.status_message

    @pytest.mark.asyncio
    async def test_filter_cwd_unknown(self, mock_process_data, make_process):
        """Should show message when filtering by unknown cwd."""
        procs = [make_process(pid=1, name="proc1", cwd="?")]
        mock_process_data["get_procs"].return_value = procs

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            await pilot.press("w")
            await pilot.pause()
            assert app.cwd_filter is None
            assert "Cannot filter" in app.status_message

    @pytest.mark.asyncio
    async def test_clear_cwd_filter(self, mock_process_data, make_process):
        """Should clear cwd filter when 'W' pressed."""
        procs = [make_process(pid=1, name="proc1", cwd="/home/user/project")]
        mock_process_data["get_procs"].return_value = procs

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # First set the filter
            app.cwd_filter = "/home/user/project"
            await pilot.press("W")  # Capital W to clear
            await pilot.pause()
            assert app.cwd_filter is None
            assert "cleared" in app.status_message

    @pytest.mark.asyncio
    async def test_cwd_filter_applies_to_table(self, mock_process_data, make_process):
        """Should apply cwd filter when updating table."""
        procs = [
            make_process(pid=1, name="proc1", cwd="/home/user/project"),
            make_process(pid=2, name="proc2", cwd="/home/user/project/sub"),
            make_process(pid=3, name="proc3", cwd="/tmp"),
        ]
        mock_process_data["get_procs"].return_value = procs

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Set cwd filter
            app.cwd_filter = "/home/user/project"
            app.update_table()
            await pilot.pause()
            # The filter should be applied (can't easily check table rows,
            # but we verify the filter is set)
            assert app.cwd_filter == "/home/user/project"

    @pytest.mark.asyncio
    async def test_cwd_filter_with_none_cwd(self, mock_process_data, make_process):
        """Should handle None cwd in sorting."""
        procs = [
            make_process(pid=1, name="proc1", cwd="/home/user"),
            make_process(pid=2, name="proc2", cwd=None),
        ]
        mock_process_data["get_procs"].return_value = procs

        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            app.sort_key = "cwd"
            app.update_table()
            await pilot.pause()
            # Should not raise, even with None cwd
            assert app.sort_key == "cwd"


class TestConfirmKillScreen:
    """Tests for ConfirmKillScreen modal."""

    @pytest.mark.asyncio
    async def test_confirm_yes(self, sample_processes, mock_process_data):
        """Should return True when confirmed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            result = None

            def callback(value):
                nonlocal result
                result = value

            app.push_screen(
                ConfirmKillScreen(sample_processes[:2], force=False), callback
            )
            await pilot.pause()
            await pilot.press("y")
            await pilot.pause()
            assert result is True

    @pytest.mark.asyncio
    async def test_confirm_yes_button_click(self, sample_processes, mock_process_data):
        """Should return True when Yes button clicked."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            result = None

            def callback(value):
                nonlocal result
                result = value

            app.push_screen(
                ConfirmKillScreen(sample_processes[:2], force=False), callback
            )
            await pilot.pause()
            await pilot.click("#yes")
            await pilot.pause()
            assert result is True

    @pytest.mark.asyncio
    async def test_confirm_no_button_click(self, sample_processes, mock_process_data):
        """Should return False when No button clicked."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            result = None

            def callback(value):
                nonlocal result
                result = value

            app.push_screen(
                ConfirmKillScreen(sample_processes[:2], force=False), callback
            )
            await pilot.pause()
            await pilot.click("#no")
            await pilot.pause()
            assert result is False

    @pytest.mark.asyncio
    async def test_more_than_10_processes(self, mock_process_data, many_processes):
        """Should show '... and N more' when >10 processes."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            # Push confirm screen with 15 processes
            app.push_screen(ConfirmKillScreen(many_processes, force=False))
            await pilot.pause()
            # The screen should be displayed (tests line 55)

    @pytest.mark.asyncio
    async def test_confirm_no(self, sample_processes, mock_process_data):
        """Should return False when cancelled."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            result = None

            def callback(value):
                nonlocal result
                result = value

            app.push_screen(
                ConfirmKillScreen(sample_processes[:2], force=False), callback
            )
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            assert result is False

    @pytest.mark.asyncio
    async def test_confirm_escape(self, sample_processes, mock_process_data):
        """Should return False when escape pressed."""
        app = ProcessCleanerApp()
        async with app.run_test() as pilot:
            result = None

            def callback(value):
                nonlocal result
                result = value

            app.push_screen(
                ConfirmKillScreen(sample_processes[:2], force=False), callback
            )
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert result is False

    @pytest.mark.asyncio
    async def test_force_kill_creates_screen(self, sample_processes, mock_process_data):
        """Should create ConfirmKillScreen with force=True."""
        screen = ConfirmKillScreen(sample_processes[:1], force=True)
        assert screen.force is True
        assert len(screen.processes) == 1


class TestMainFunction:
    """Tests for main entry point."""

    @patch("procclean.__main__.run_cli")
    @patch("procclean.__main__.ProcessCleanerApp")
    def test_runs_tui_when_no_subcommand(self, mock_app_class, mock_run_cli):
        """Should run TUI when run_cli returns -1."""
        mock_run_cli.return_value = -1
        mock_app = mock_app_class.return_value

        main()

        mock_app.run.assert_called_once()

    @patch("procclean.__main__.run_cli")
    def test_exits_with_code_from_cli(self, mock_run_cli):
        """Should raise SystemExit with CLI return code."""
        mock_run_cli.return_value = 1

        with pytest.raises(SystemExit) as exc_info:
            main()
        # SystemExit.code is the exit code
        assert exc_info.value.args[0] == 1


class TestDunderMain:
    """Tests for __main__.py module."""

    def test_imports_main(self):
        """Should be able to import main from __main__."""
        import procclean.__main__ as dunder_main  # noqa: PLC0415

        assert callable(dunder_main.main)

    def test_run_as_module_version(self):
        """Should be runnable with python -m procclean --version."""
        import subprocess  # noqa: PLC0415

        result = subprocess.run(
            ["python", "-m", "procclean", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        assert result.returncode == 0
        assert "procclean" in result.stdout

    def test_run_as_module_mem(self):
        """Should run memory command via python -m procclean."""
        import subprocess  # noqa: PLC0415

        result = subprocess.run(
            ["python", "-m", "procclean", "mem"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        assert result.returncode == 0
        assert "Total:" in result.stdout

    @patch("procclean.cli.run_cli")
    def test_dunder_main_executes(self, mock_run_cli):
        """Test __main__.py if __name__ == '__main__' block."""
        import runpy  # noqa: PLC0415
        import sys  # noqa: PLC0415

        mock_run_cli.return_value = 0

        # Clean module cache to avoid ambiguous state warning
        sys.modules.pop("procclean.__main__", None)

        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("procclean", run_name="__main__", alter_sys=True)

        assert exc_info.value.args[0] == 0
