# AGENTS.md

## Commands
- **Install deps**: `uv sync`
- **Run app**: `uv run procclean`
- **Lint**: `uv run ruff check src/` and `uv run ruff format --check src/`
- **Type check**: `uv run ty check`
- **Test all**: `uv run pytest`
- **Single test**: `uv run pytest tests/test_file.py::test_name -v`

## Code Style
- Python 3.14+, use modern type syntax: `list[X]`, `dict[K,V]`, `X | None`
- Imports: stdlib first, third-party, then relative (`.module`)
- Format: ruff (88 char line length, double quotes)
- Dataclasses for data structures, not dicts
- Docstrings: triple-quoted, first line is summary
- Error handling: catch specific exceptions (psutil.NoSuchProcess, etc.)
- Naming: snake_case functions/vars, PascalCase classes

## Structure
- Source in `src/procclean/`
- Entry point: `app.py:main()`
- Process logic: `process_analyzer.py`
