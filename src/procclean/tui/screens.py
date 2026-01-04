"""TUI modal screens."""

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from procclean.core import ProcessInfo


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

    def compose(self):
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
