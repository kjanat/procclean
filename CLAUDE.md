# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session Setup

Run at the start of each session:

```bash
uv sync && uv run pre-commit install --install-hooks
```

## Commands

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Run app | `uv run procclean` or `./pc` |
| Lint | `uv run ruff check src/` and `uv run ruff format --check src/` |
| Type check | `uv run ty check` |
| Test all | `uv run pytest` |
| Single test | `uv run pytest tests/test_file.py::test_name -v` |
| Test coverage | `uv run pytest --cov -vv` |
| Pre-commit | `uv run pre-commit install --install-hooks` |
| Run hooks | `uv run pre-commit run --all-files` |
| Build | `uv build` |
| Bump version | `uv version --bump patch|minor|major` |

## Architecture

```
src/procclean/
  __init__.py       # Package init, __version__, main, ProcessInfo
  __main__.py       # Entry point, main() dispatcher (CLI vs TUI)
  core/             # Business logic (no UI deps)
    models.py       # ProcessInfo dataclass
    process.py      # get_process_list, find_similar_processes
    filters.py      # filter_*, sort_processes, is_system_service
    actions.py      # kill_process, kill_processes
    memory.py       # get_memory_summary
    constants.py    # SYSTEM_EXE_PATHS, CRITICAL_SERVICES
  cli/              # CLI interface
    parser.py       # create_parser(), run_cli()
    commands.py     # cmd_list, cmd_kill, cmd_groups, cmd_memory
  tui/              # TUI interface (Textual)
    app.py          # ProcessCleanerApp
    app.tcss        # Textual CSS styles
    screens.py      # ConfirmKillScreen
  formatters/       # Output formatters
    columns.py      # ColumnSpec, COLUMNS, DEFAULT_COLUMNS
    output.py       # format_table, format_json, format_csv, format_md
```

**Key design principle**: `core/` contains all business logic with no UI dependencies. Both `cli/` and `tui/` consume `core/` functions.

## Code Style

- **Python 3.14+** - Use modern type syntax: `list[X]`, `dict[K,V]`, `X | None`
- **Imports**: stdlib first, third-party, then relative (`.module`)
- **Format**: ruff (88 char lines, double quotes)
- **Data**: Dataclasses for data structures, not dicts
- **Errors**: Catch specific exceptions (`psutil.NoSuchProcess`, etc.)
- **Naming**: `snake_case` functions/vars, `PascalCase` classes

### Python 3.14 Features to Use

- **Template strings**: `t"Hello {name}"` for safe SQL/HTML/shell interpolation
- **Deferred annotations**: Forward references work without quotes
- **Multiple interpreters**: `concurrent.interpreters.Interpreter` for true parallelism
- **Exception groups**: `except ValueError, TypeError:` (brackets optional)

## Git Rules

- **All tags MUST be signed** (`-s` flag) with descriptions
- **Never delete tags** - use `git tag -f` to overwrite
- **Never amend pushed commits** - check `git status` for divergence first
- **When moving a tag, ALWAYS specify commit SHA**: `git tag -s -f v0.X.0 <SHA> -m "..."`

## GitHub Release Rules

- **Never delete a release** - it may trigger workflows (like PyPI publish)
- **To update release notes**: `gh release edit <tag> --notes "new notes"`
- **Deleting + recreating a release** triggers duplicate workflow runs
