"""Main TUI application."""

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    OptionList,
    Static,
)
from textual.widgets.option_list import Option

from .process_analyzer import (
    ProcessInfo,
    filter_by_cwd,
    find_similar_processes,
    get_memory_summary,
    get_process_list,
    kill_processes,
)


class ConfirmKillScreen(ModalScreen[bool]):
    """Modal screen to confirm killing processes."""

    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, processes: list[ProcessInfo], force: bool = False):
        super().__init__()
        self.processes = processes
        self.force = force

    def compose(self) -> ComposeResult:
        total_mb = sum(p.rss_mb for p in self.processes)
        action = "FORCE KILL" if self.force else "Kill"

        with Container(id="confirm-dialog"):
            yield Label(
                f"{action} {len(self.processes)} process(es)?", id="confirm-title"
            )
            yield Label(f"Will free ~{total_mb:.1f} MB", id="confirm-subtitle")
            with Vertical(id="process-list-container"):
                for proc in self.processes[:10]:
                    yield Label(f"  {proc.pid}: {proc.name} ({proc.rss_mb:.1f} MB)")
                if len(self.processes) > 10:
                    yield Label(f"  ... and {len(self.processes) - 10} more")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (y)", id="yes", variant="error")
                yield Button("No (n)", id="no", variant="primary")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#yes")
    def on_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def on_no(self) -> None:
        self.dismiss(False)


class ProcessCleanerApp(App):  # noqa: PLR0904
    """TUI for exploring and cleaning up processes."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("k", "kill_selected", "Kill"),
        Binding("K", "force_kill_selected", "Force Kill"),
        Binding("o", "show_orphans", "Orphans"),
        Binding("a", "show_all", "All"),
        Binding("g", "show_groups", "Groups"),
        Binding("w", "filter_cwd", "Filter CWD"),
        Binding("W", "clear_cwd_filter", "Clear CWD"),
        Binding("space", "toggle_select", "Select"),
        Binding("s", "select_all_visible", "Select All"),
        Binding("c", "clear_selection", "Clear"),
        # Sorting bindings
        Binding("1", "sort_memory", "Sort:Mem"),
        Binding("2", "sort_cpu", "Sort:CPU"),
        Binding("3", "sort_pid", "Sort:PID"),
        Binding("4", "sort_name", "Sort:Name"),
        Binding("5", "sort_cwd", "Sort:CWD"),
        Binding("!", "toggle_sort_order", "Reverse"),
    ]

    def __init__(self):
        super().__init__()
        self.processes: list[ProcessInfo] = []
        self.selected_pids: set[int] = set()
        self.current_view = "all"
        self.status_message = ""
        self.sort_key = "memory"  # memory, cpu, pid, name, cwd
        self.sort_reverse = True  # descending by default
        self.cwd_filter: str | None = None  # Filter by cwd path

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="memory-bar"):
            yield Static("", id="mem-total")
            yield Static("", id="mem-used")
            yield Static("", id="mem-free")
            yield Static("", id="swap")
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                yield Label("Views", id="sidebar-title")
                yield OptionList(
                    Option("All Processes", id="view-all"),
                    Option("Orphaned", id="view-orphans"),
                    Option("Process Groups", id="view-groups"),
                    Option("High Memory (>500MB)", id="view-high-mem"),
                    id="view-selector",
                )
            with Vertical(id="content"):
                yield DataTable(id="process-table")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "ProcClean"
        self.sub_title = "Process Cleanup Tool"

        table = self.query_one("#process-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "", "PID", "Name", "RAM (MB)", "CPU%", "CWD", "PPID", "Parent", "Status"
        )

        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh process list and memory info."""
        mem = get_memory_summary()
        self.query_one("#mem-total", Static).update(f"Total: {mem['total_gb']:.1f}G")
        self.query_one("#mem-used", Static).update(
            f"Used: {mem['used_gb']:.1f}G ({mem['percent']:.0f}%)"
        )
        self.query_one("#mem-free", Static).update(f"Free: {mem['free_gb']:.1f}G")
        self.query_one("#swap", Static).update(
            f"Swap: {mem['swap_used_gb']:.1f}G/{mem['swap_total_gb']:.1f}G"
        )

        self.processes = get_process_list(min_memory_mb=5.0)
        self.update_table()

    def _sort_processes(self, procs: list[ProcessInfo]) -> list[ProcessInfo]:
        """Sort processes by current sort key and order."""
        sort_keys = {
            "memory": lambda p: p.rss_mb,
            "cpu": lambda p: p.cpu_percent,
            "pid": lambda p: p.pid,
            "name": lambda p: p.name.lower(),
            "cwd": lambda p: (p.cwd or "").lower(),
        }
        key_func = sort_keys.get(self.sort_key, sort_keys["memory"])
        return sorted(procs, key=key_func, reverse=self.sort_reverse)

    def update_table(self) -> None:
        """Update the process table based on current view and sort."""
        table = self.query_one("#process-table", DataTable)
        table.clear()

        if self.current_view == "orphans":
            procs = [p for p in self.processes if p.is_orphan]
        elif self.current_view == "high-mem":
            procs = [p for p in self.processes if p.rss_mb > 500]
        elif self.current_view == "groups":
            groups = find_similar_processes(self.processes)
            procs = []
            for group_procs in groups.values():
                procs.extend(group_procs)
        else:
            procs = self.processes

        # Apply cwd filter
        if self.cwd_filter:
            procs = filter_by_cwd(procs, self.cwd_filter)

        # Apply sorting
        procs = self._sort_processes(procs)

        for proc in procs:
            selected = "[X]" if proc.pid in self.selected_pids else "[ ]"
            orphan_marker = " [orphan]" if proc.is_orphan else ""
            tmux_marker = " [tmux]" if proc.in_tmux else ""
            status = f"{proc.status}{orphan_marker}{tmux_marker}"

            cwd = proc.cwd or "?"
            if len(cwd) > 35:
                cwd = "..." + cwd[-32:]

            table.add_row(
                selected,
                str(proc.pid),
                proc.name[:20],
                f"{proc.rss_mb:.1f}",
                f"{proc.cpu_percent:.1f}",
                cwd,
                str(proc.ppid),
                proc.parent_name[:15],
                status,
                key=str(proc.pid),
            )

        self.update_status()

    def update_status(self) -> None:
        """Update status bar."""
        selected_mb = sum(
            p.rss_mb for p in self.processes if p.pid in self.selected_pids
        )
        msg = f"Selected: {len(self.selected_pids)} processes ({selected_mb:.1f} MB)"
        if self.status_message:
            msg += f" | {self.status_message}"
        self.query_one("#status-bar", Static).update(msg)

    @on(OptionList.OptionSelected, "#view-selector")
    def on_view_change(self, event: OptionList.OptionSelected) -> None:
        view_map = {
            "view-all": "all",
            "view-orphans": "orphans",
            "view-groups": "groups",
            "view-high-mem": "high-mem",
        }
        if event.option.id:
            self.current_view = view_map.get(event.option.id, "all")
            self.update_table()

    def action_refresh(self) -> None:
        self.refresh_data()
        self.status_message = "Refreshed"
        self.update_status()

    def action_toggle_select(self) -> None:
        table = self.query_one("#process-table", DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)
            pid = int(row_key[1])
            if pid in self.selected_pids:
                self.selected_pids.remove(pid)
            else:
                self.selected_pids.add(pid)
            self.update_table()

    def action_select_all_visible(self) -> None:
        table = self.query_one("#process-table", DataTable)
        for row_idx in range(table.row_count):
            row = table.get_row_at(row_idx)
            pid = int(row[1])
            self.selected_pids.add(pid)
        self.update_table()

    def action_clear_selection(self) -> None:
        self.selected_pids.clear()
        self.update_table()

    def action_show_orphans(self) -> None:
        self.current_view = "orphans"
        self.update_table()

    def action_show_all(self) -> None:
        self.current_view = "all"
        self.update_table()

    def action_show_groups(self) -> None:
        self.current_view = "groups"
        self.update_table()

    def _set_sort(self, key: str) -> None:
        """Set sort key and update table."""
        if self.sort_key == key:
            # Same key, toggle order
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            # Default order: descending for numeric, ascending for name
            self.sort_reverse = key != "name"
        order = "desc" if self.sort_reverse else "asc"
        self.status_message = f"Sort: {key} ({order})"
        self.update_table()

    def action_sort_memory(self) -> None:
        self._set_sort("memory")

    def action_sort_cpu(self) -> None:
        self._set_sort("cpu")

    def action_sort_pid(self) -> None:
        self._set_sort("pid")

    def action_sort_name(self) -> None:
        self._set_sort("name")

    def action_sort_cwd(self) -> None:
        self._set_sort("cwd")

    def action_toggle_sort_order(self) -> None:
        self.sort_reverse = not self.sort_reverse
        order = "desc" if self.sort_reverse else "asc"
        self.status_message = f"Sort: {self.sort_key} ({order})"
        self.update_table()

    def action_filter_cwd(self) -> None:
        """Filter by cwd of currently selected row."""
        table = self.query_one("#process-table", DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            pid = int(row[1])
            proc = next((p for p in self.processes if p.pid == pid), None)
            if proc and proc.cwd and proc.cwd != "?":
                self.cwd_filter = proc.cwd
                self.status_message = f"Filter: cwd={self.cwd_filter}"
                self.update_table()
            else:
                self.status_message = "Cannot filter: unknown cwd"
                self.update_status()

    def action_clear_cwd_filter(self) -> None:
        """Clear the cwd filter."""
        self.cwd_filter = None
        self.status_message = "CWD filter cleared"
        self.update_table()

    def _do_kill(self, force: bool = False) -> None:
        if not self.selected_pids:
            self.status_message = "No processes selected"
            self.update_status()
            return

        procs = [p for p in self.processes if p.pid in self.selected_pids]

        def handle_confirm(confirmed: bool | None) -> None:
            if confirmed:
                results = kill_processes(list(self.selected_pids), force=force)
                success = sum(1 for _, ok, _ in results if ok)
                self.status_message = f"Killed {success}/{len(results)} processes"
                self.selected_pids.clear()
                self.refresh_data()

        self.push_screen(ConfirmKillScreen(procs, force=force), handle_confirm)

    def action_kill_selected(self) -> None:
        self._do_kill(force=False)

    def action_force_kill_selected(self) -> None:
        self._do_kill(force=True)


def main():
    """Entry point: dispatch to CLI or run TUI.

    Raises:
        SystemExit: When CLI command returns non-zero exit code.

    """
    from .cli import run_cli  # noqa: PLC0415

    result = run_cli()
    if result == -1:
        # No subcommand - run TUI
        app = ProcessCleanerApp()
        app.run()
    else:
        raise SystemExit(result)


if __name__ == "__main__":
    main()
