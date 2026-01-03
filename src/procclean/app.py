"""Main TUI application."""

import argparse
from importlib.metadata import version

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


class ProcessCleanerApp(App):
    """TUI for exploring and cleaning up processes."""

    CSS = """
    #confirm-dialog {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #confirm-title {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }

    #confirm-subtitle {
        color: $text-muted;
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }

    #process-list-container {
        height: auto;
        max-height: 15;
        margin-bottom: 1;
    }

    #confirm-buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    #confirm-buttons Button {
        margin: 0 1;
    }

    #memory-bar {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $primary;
    }

    #memory-bar Static {
        width: auto;
        margin-right: 2;
    }

    #main-container {
        height: 1fr;
    }

    #sidebar {
        width: 30;
        border-right: solid $primary;
        padding: 1;
    }

    #sidebar-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #content {
        width: 1fr;
        padding: 1;
    }

    #status-bar {
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    DataTable {
        height: 1fr;
    }

    .selected-count {
        color: $warning;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("k", "kill_selected", "Kill"),
        Binding("K", "force_kill_selected", "Force Kill"),
        Binding("o", "show_orphans", "Orphans"),
        Binding("a", "show_all", "All"),
        Binding("g", "show_groups", "Groups"),
        Binding("space", "toggle_select", "Select"),
        Binding("s", "select_all_visible", "Select All"),
        Binding("c", "clear_selection", "Clear"),
    ]

    def __init__(self):
        super().__init__()
        self.processes: list[ProcessInfo] = []
        self.selected_pids: set[int] = set()
        self.current_view = "all"
        self.status_message = ""

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

    def update_table(self) -> None:
        """Update the process table based on current view."""
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

        for proc in procs:
            selected = "[X]" if proc.pid in self.selected_pids else "[ ]"
            orphan_marker = " [orphan]" if proc.is_orphan else ""
            tmux_marker = " [tmux]" if proc.in_tmux else ""
            status = f"{proc.status}{orphan_marker}{tmux_marker}"

            cwd = proc.cwd
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
    parser = argparse.ArgumentParser(
        prog="procclean",
        description="TUI for exploring and cleaning up processes.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version('procclean')}",
    )
    parser.parse_args()

    app = ProcessCleanerApp()
    app.run()


if __name__ == "__main__":
    main()
