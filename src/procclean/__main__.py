"""Entry point for procclean - runs as python -m procclean or via console script."""

from .cli import run_cli
from .tui import ProcessCleanerApp


def main() -> None:
    """Dispatch to CLI or run TUI.

    Raises:
        SystemExit: When CLI command returns non-zero exit code.
    """
    result = run_cli()
    if result == -1:
        # No subcommand - run TUI
        ProcessCleanerApp().run()
    else:
        raise SystemExit(result)


if __name__ == "__main__":
    main()
