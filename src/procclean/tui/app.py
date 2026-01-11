"""Main TUI application."""

from typing import ClassVar, Literal

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.reactive import reactive
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    OptionList,
    Static,
)
from textual.widgets.option_list import Option

from procclean.core import (
    CWD_MAX_WIDTH,
    CWD_TRUNCATE_WIDTH,
    HIGH_MEMORY_THRESHOLD_MB,
    ProcessInfo,
    filter_by_cwd,
    find_similar_processes,
    get_memory_summary,
    get_process_list,
    kill_processes,
)

from .screens import ConfirmKillScreen

# Type aliases
ViewType = Literal["all", "orphans", "killable", "groups", "high-mem"]
SortKey = Literal["memory", "cpu", "pid", "name", "cwd"]


class ProcessCleanerApp(App):
    """TUI for exploring and cleaning up processes."""

    CSS_PATH = "app.tcss"

    # Reactive state - watchers auto-trigger UI updates
    current_view = reactive[ViewType]("all")
    sort_key = reactive[SortKey]("memory")
    sort_reverse = reactive(True)
    cwd_filter = reactive[str | None](None)

    BINDINGS: ClassVar = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("k", "kill_selected", "Kill"),
        Binding("K", "force_kill_selected", "Force Kill"),
        Binding("o", "show_orphans", "Orphans"),
        Binding("O", "show_killable", "Killable"),
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

    def __init__(self) -> None:
        """Initialize the TUI application."""
        super().__init__()
        self.processes: list[ProcessInfo] = []
        self.selected_pids: set[int] = set()

    def compose(self) -> ComposeResult:  # noqa: PLR6301
        """Build the TUI layout.

        Yields:
            ComposeResult: Widgets that form the application layout.
        """
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
                    Option("Killable", id="view-killable"),
                    Option("Process Groups", id="view-groups"),
                    Option("High Memory (>500MB)", id="view-high-mem"),
                    id="view-selector",
                )
            with Vertical(id="content"):
                yield DataTable(id="process-table")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize app after mounting."""
        self.title = "ProcClean"
        self.sub_title = "Process Cleanup Tool"

        table = self.query_one("#process-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "", "PID", "Name", "RAM (MB)", "CPU%", "CWD", "PPID", "Parent", "Status"
        )

        self.refresh_data()
        # Auto-refresh every 5 seconds
        self.set_interval(5.0, self.refresh_data)

    # Reactive watchers - auto-update table when state changes
    def watch_current_view(self) -> None:
        """Update table when view changes."""
        self.update_table()

    def watch_sort_key(self) -> None:
        """Update table when sort key changes."""
        self.update_table()

    def watch_sort_reverse(self) -> None:
        """Update table when sort order changes."""
        self.update_table()

    def watch_cwd_filter(self) -> None:
        """Update table when cwd filter changes."""
        self.update_table()

    def refresh_data(self) -> None:
        """Trigger async refresh of process list and memory info."""
        self._fetch_data()

    @work(thread=True)
    def _fetch_data(self) -> None:
        """Fetch process data in background thread."""
        mem = get_memory_summary()
        procs = get_process_list(min_memory_mb=5.0)
        self.call_from_thread(self._update_data, mem, procs)

    def _update_data(self, mem: dict[str, float], procs: list[ProcessInfo]) -> None:
        """Update UI with fetched data (called from main thread)."""
        self.query_one("#mem-total", Static).update(f"Total: {mem['total_gb']:.1f}G")
        self.query_one("#mem-used", Static).update(
            f"Used: {mem['used_gb']:.1f}G ({mem['percent']:.0f}%)"
        )
        self.query_one("#mem-free", Static).update(f"Free: {mem['free_gb']:.1f}G")
        self.query_one("#swap", Static).update(
            f"Swap: {mem['swap_used_gb']:.1f}G/{mem['swap_total_gb']:.1f}G"
        )
        self.processes = procs
        self.update_table()

    def _sort_processes(self, procs: list[ProcessInfo]) -> list[ProcessInfo]:
        """Sort processes by current sort key and order.

        Args:
            procs: The processes to sort.

        Returns:
            A new list of processes sorted according to the current sort settings.
        """
        sort_keys = {
            "memory": lambda p: p.rss_mb,
            "cpu": lambda p: p.cpu_percent,
            "pid": lambda p: p.pid,
            "name": lambda p: p.name.lower(),
            "cwd": lambda p: (p.cwd or "").lower(),
        }
        key_func = sort_keys.get(self.sort_key, sort_keys["memory"])
        return sorted(procs, key=key_func, reverse=self.sort_reverse)

    def _filter_by_view(self) -> list[ProcessInfo]:
        """Filter processes based on current view.

        Returns:
            Filtered list of processes for the current view.
        """
        if self.current_view == "orphans":
            return [p for p in self.processes if p.is_orphan]
        if self.current_view == "killable":
            return [p for p in self.processes if p.is_orphan_candidate]
        if self.current_view == "high-mem":
            return [p for p in self.processes if p.rss_mb > HIGH_MEMORY_THRESHOLD_MB]
        if self.current_view == "groups":
            groups = find_similar_processes(self.processes)
            procs: list[ProcessInfo] = []
            for group_procs in groups.values():
                procs.extend(group_procs)
            return procs
        return list(self.processes)

    @staticmethod
    def _restore_cursor(table: DataTable, cursor_pid: int | None) -> None:
        """Restore cursor to the row with the given PID.

        Args:
            table: The DataTable to restore cursor in.
            cursor_pid: The PID to restore cursor to, or None to skip.
        """
        if cursor_pid is None:
            return
        for row_idx in range(table.row_count):
            row_data = table.get_row_at(row_idx)
            if int(row_data[1]) == cursor_pid:
                table.move_cursor(row=row_idx)
                break

    def update_table(self) -> None:
        """Update the process table based on current view and sort."""
        table = self.query_one("#process-table", DataTable)
        cursor_pid = self._get_pid_at_cursor()
        table.clear()

        procs = self._filter_by_view()
        if self.cwd_filter:
            procs = filter_by_cwd(procs, self.cwd_filter)
        procs = self._sort_processes(procs)

        for proc in procs:
            selected = "[X]" if proc.pid in self.selected_pids else "[ ]"
            orphan_marker = " [orphan]" if proc.is_orphan else ""
            tmux_marker = " [tmux]" if proc.in_tmux else ""
            status = f"{proc.status}{orphan_marker}{tmux_marker}"

            cwd = proc.cwd or "?"
            if len(cwd) > CWD_MAX_WIDTH:
                cwd = "..." + cwd[-CWD_TRUNCATE_WIDTH:]

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

        self._restore_cursor(table, cursor_pid)
        self.update_status()

    def update_status(self) -> None:
        """Update status bar with selection info."""
        selected_mb = sum(
            p.rss_mb for p in self.processes if p.pid in self.selected_pids
        )
        msg = f"Selected: {len(self.selected_pids)} processes ({selected_mb:.1f} MB)"
        self.query_one("#status-bar", Static).update(msg)

    @on(OptionList.OptionSelected, "#view-selector")
    def on_view_change(self, event: OptionList.OptionSelected) -> None:
        """Handle view selection changes."""
        view_map: dict[str, ViewType] = {
            "view-all": "all",
            "view-orphans": "orphans",
            "view-killable": "killable",
            "view-groups": "groups",
            "view-high-mem": "high-mem",
        }
        if event.option.id and event.option.id in view_map:
            self.current_view = view_map[event.option.id]

    @on(DataTable.RowSelected, "#process-table")
    def on_row_clicked(self, event: DataTable.RowSelected) -> None:
        """Toggle selection when a row is clicked."""
        # Get PID from the row data (column 1 is PID)
        row_data = event.data_table.get_row(event.row_key)
        pid = int(row_data[1])

        # Toggle selection
        if pid in self.selected_pids:
            self.selected_pids.remove(pid)
            new_value = "[ ]"
        else:
            self.selected_pids.add(pid)
            new_value = "[X]"

        # Update the clicked row's selection cell using row_key (not cursor_row)
        selection_column_key = event.data_table.ordered_columns[0].key
        event.data_table.update_cell(event.row_key, selection_column_key, new_value)
        self.update_status()

    @on(DataTable.HeaderSelected, "#process-table")
    def on_header_clicked(self, event: DataTable.HeaderSelected) -> None:
        """Sort by column when header is clicked."""
        # Map column index to sort key
        column_sort_map: dict[int, SortKey] = {
            1: "pid",  # PID column
            2: "name",  # Name column
            3: "memory",  # RAM (MB) column
            4: "cpu",  # CPU% column
            5: "cwd",  # CWD column
        }
        col_idx = event.column_index
        if col_idx in column_sort_map:
            self._set_sort(column_sort_map[col_idx])

    def action_refresh(self) -> None:
        """Refresh process data."""
        self.refresh_data()
        self.notify("Refreshed")

    def _get_pid_at_cursor(self) -> int | None:
        """Get the PID of the process at the current cursor position.

        Returns:
            The PID at the current cursor position, or ``None`` if there is no
            current row selected or the table is empty.
        """
        table = self.query_one("#process-table", DataTable)
        if table.cursor_row is None or table.row_count == 0:
            return None
        row_data = table.get_row_at(table.cursor_row)
        # row_data is a list of cell values: [selected, pid, name, ...]
        return int(row_data[1])

    def _get_process_at_cursor(self) -> ProcessInfo | None:
        """Get the ProcessInfo at the current cursor position.

        Returns:
            The ``ProcessInfo`` for the process at the current cursor position,
            or ``None`` if there is no current row selected or the PID cannot be
            resolved to a process in the current list.
        """
        pid = self._get_pid_at_cursor()
        if pid is None:
            return None
        return next((p for p in self.processes if p.pid == pid), None)

    def action_toggle_select(self) -> None:
        """Toggle selection of current row."""
        table = self.query_one("#process-table", DataTable)
        if table.cursor_row is None:
            return

        pid = self._get_pid_at_cursor()
        if pid is not None:
            # Toggle selection
            if pid in self.selected_pids:
                self.selected_pids.remove(pid)
                new_value = "[ ]"
            else:
                self.selected_pids.add(pid)
                new_value = "[X]"

            # Update just the selection cell, not the entire table
            table.update_cell_at(Coordinate(table.cursor_row, 0), new_value)
            self.update_status()

    def action_select_all_visible(self) -> None:
        """Select all visible processes."""
        table = self.query_one("#process-table", DataTable)
        for row_idx in range(table.row_count):
            row = table.get_row_at(row_idx)
            pid = int(row[1])
            self.selected_pids.add(pid)
        self.update_table()

    def action_clear_selection(self) -> None:
        """Clear all selections."""
        self.selected_pids.clear()
        self.update_table()

    def action_show_orphans(self) -> None:
        """Switch to orphans view."""
        self.current_view = "orphans"

    def action_show_killable(self) -> None:
        """Switch to killable orphans view (orphans not in tmux)."""
        self.current_view = "killable"

    def action_show_all(self) -> None:
        """Switch to all processes view."""
        self.current_view = "all"

    def action_show_groups(self) -> None:
        """Switch to process groups view."""
        self.current_view = "groups"

    def _set_sort(self, key: SortKey) -> None:
        """Set sort key and update table."""
        if self.sort_key == key:
            # Same key, toggle order
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            # Default order: descending for numeric, ascending for name
            self.sort_reverse = key != "name"
        order = "desc" if self.sort_reverse else "asc"
        self.notify(f"Sort: {key} ({order})")

    def action_sort_memory(self) -> None:
        """Sort the table by resident memory usage."""
        self._set_sort("memory")

    def action_sort_cpu(self) -> None:
        """Sort the table by CPU usage percentage."""
        self._set_sort("cpu")

    def action_sort_pid(self) -> None:
        """Sort the table by PID."""
        self._set_sort("pid")

    def action_sort_name(self) -> None:
        """Sort the table by process name."""
        self._set_sort("name")

    def action_sort_cwd(self) -> None:
        """Sort the table by current working directory."""
        self._set_sort("cwd")

    def action_toggle_sort_order(self) -> None:
        """Toggle the current sort order (ascending/descending)."""
        self.sort_reverse = not self.sort_reverse
        order = "desc" if self.sort_reverse else "asc"
        self.notify(f"Sort: {self.sort_key} ({order})")

    def action_filter_cwd(self) -> None:
        """Filter by cwd of currently selected row."""
        proc = self._get_process_at_cursor()
        if proc and proc.cwd and proc.cwd != "?":
            self.cwd_filter = proc.cwd
            self.notify(f"Filter: cwd={self.cwd_filter}")
        else:
            self.notify("Cannot filter: unknown cwd", severity="warning")

    def action_clear_cwd_filter(self) -> None:
        """Clear the cwd filter."""
        self.cwd_filter = None
        self.notify("CWD filter cleared")

    def _do_kill(self, force: bool = False) -> None:
        if not self.selected_pids:
            self.notify("No processes selected", severity="warning")
            return

        procs = [p for p in self.processes if p.pid in self.selected_pids]

        def handle_confirm(confirmed: bool | None) -> None:
            if confirmed:
                self._execute_kill(list(self.selected_pids), force)

        self.push_screen(ConfirmKillScreen(procs, force=force), handle_confirm)

    @work(thread=True)
    def _execute_kill(self, pids: list[int], force: bool) -> None:
        """Execute kill in background thread."""
        results = kill_processes(pids, force=force)
        success = sum(1 for _, ok, _ in results if ok)
        self.call_from_thread(self._on_kill_complete, success, len(results))

    def _on_kill_complete(self, success: int, total: int) -> None:
        """Handle kill completion (called from main thread)."""
        self.notify(f"Killed {success}/{total} processes")
        self.selected_pids.clear()
        self.refresh_data()

    def action_kill_selected(self) -> None:
        """Send SIGTERM to all selected processes (after confirmation)."""
        self._do_kill(force=False)

    def action_force_kill_selected(self) -> None:
        """Send SIGKILL to all selected processes (after confirmation)."""
        self._do_kill(force=True)
