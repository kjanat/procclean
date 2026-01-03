# AGENTS.md

## Commands

- **Install deps**: `uv sync`
- **Run app**: `uv run procclean` or `./pc`
- **Lint**: `uv run ruff check src/` and `uv run ruff format --check src/`
- **Type check**: `uv run ty check`
- **Test all**: `uv run pytest`
- **Single test**: `uv run pytest tests/test_file.py::test_name -v`
- **Test coverage (verbose)**: `uv run pytest --cov -vv`
- **Pre-commit install**: `uv run pre-commit install --install-hooks`
- **Run hooks manually**: `uv run pre-commit run --all-files`
- **Build**: `uv build`
- **Show version**: `uv version` or `uv run procclean --version`
- **Bump version**: `uv version --bump patch|minor|major`

## Code Style

- Python 3.14+, use modern type syntax: `list[X]`, `dict[K,V]`, `X | None`
- Imports: `stdlib` first, third-party, then relative (`.module`)
- Format: `ruff` (88 char line length, double quotes)
- `Dataclasses` for data structures, not `dicts`
- Docstrings: triple-quoted, first line is summary
- Error handling: catch specific exceptions (`psutil.NoSuchProcess`, etc.)
- Naming: `snake_case` functions/vars, `PascalCase` classes

## Structure

- Source in [`src/procclean/`](./src/procclean/)
- Entry point: [`app.py:main()`](./src/procclean/app.py)
- CLI interface: [`cli.py`](./src/procclean/cli.py)
- Process logic: [`process_analyzer.py`](./src/procclean/process_analyzer.py)

## CLI Usage

```bash
procclean                         # Launch TUI (default)
procclean list                    # List processes (table)
procclean list -f json|csv|md     # Different output formats
procclean list -s mem|cpu|pid|name  # Sort by field
procclean list -o                 # Orphans only
procclean list -m                 # High memory only
procclean groups                  # Show process groups
procclean kill <PID> [PID...]     # Kill process(es)
procclean kill -f <PID>           # Force kill (SIGKILL)
procclean mem                     # Show memory summary
```

## TUI Keybindings

| Key     | Action                  |
| ------- | ----------------------- |
| `q`     | Quit                    |
| `r`     | Refresh                 |
| `k`     | Kill selected (SIGTERM) |
| `K`     | Force kill (SIGKILL)    |
| `o`     | Show orphans            |
| `a`     | Show all                |
| `g`     | Show groups             |
| `space` | Toggle selection        |
| `s`     | Select all visible      |
| `c`     | Clear selection         |
| `1`     | Sort by memory          |
| `2`     | Sort by CPU             |
| `3`     | Sort by PID             |
| `4`     | Sort by name            |
| `!`     | Reverse sort order      |
