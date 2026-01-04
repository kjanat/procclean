"""Main entry point for procclean."""

from .tui import ProcessCleanerApp


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
