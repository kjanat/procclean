"""TUI modal screens."""

from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from procclean.core import CONFIRM_PREVIEW_LIMIT, ProcessInfo


class ConfirmKillScreen(ModalScreen[bool]):
    """Modal screen to confirm killing processes."""

    BINDINGS: ClassVar = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, processes: list[ProcessInfo], force: bool = False) -> None:
        """Initialize the confirmation screen.

        Args:
            processes: Processes that may be killed if confirmed.
            force: Whether the operation is a force kill.
        """
        super().__init__()
        self.processes = processes
        self.force = force

    def compose(self) -> ComposeResult:
        """Compose child widgets for the confirmation dialog.

        This method is called by Textual when the screen is mounted or recomposed.
        It builds the dialog UI, including a preview list of processes and
        confirmation buttons.

        Yields:
            Child widgets that make up the confirmation dialog.
        """
        total_mb = sum(p.rss_mb for p in self.processes)
        action = "FORCE KILL" if self.force else "Kill"

        with Container(id="confirm-dialog"):
            yield Label(
                f"{action} {len(self.processes)} process(es)?", id="confirm-title"
            )
            yield Label(f"Will free ~{total_mb:.1f} MB", id="confirm-subtitle")
            with Vertical(id="process-list-container"):
                for proc in self.processes[:CONFIRM_PREVIEW_LIMIT]:
                    yield Label(f"  {proc.pid}: {proc.name} ({proc.rss_mb:.1f} MB)")
                if len(self.processes) > CONFIRM_PREVIEW_LIMIT:
                    remaining = len(self.processes) - CONFIRM_PREVIEW_LIMIT
                    yield Label(f"  ... and {remaining} more")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (y)", id="yes", variant="error")
                yield Button("No (n)", id="no", variant="primary")

    def action_confirm(self) -> None:
        """Confirm killing the selected processes."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel process killing."""
        self.dismiss(False)

    @on(Button.Pressed, "#yes")
    def on_yes(self) -> None:
        """Handle the Yes button being pressed."""
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def on_no(self) -> None:
        """Handle the No button being pressed."""
        self.dismiss(False)
