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
- **Create tag**: `git tag -s v0.X.0 -m "v0.X.0 - Description"`
- **Update tag**: `git tag -s -f v0.X.0 -m "v0.X.0 - Description"`\
  (NEVER delete, use `-f`)

## Git Rules

- **All tags MUST be signed** (`-s` flag) with descriptions
- **Never delete tags** - use `git tag -f` to overwrite
- **Never amend pushed commits** - check `git status` for divergence first
- **When moving a tag, ALWAYS specify commit SHA**:
  `git tag -s -f v0.X.0 <SHA> -m "..."`\
  (without SHA, tag goes to HEAD - wrong!)

## Code Review Guidelines

**Verify before claiming.** Every assertion in a code review must be validated
against authoritative sources (official docs, Context7, actual testing) *before*
presenting to the user.

**Know your tools.** Understand the technologies being reviewed:

- YAML `|` block scalar strips common leading indentation automatically
- GitHub Actions `run: |` passes clean content to the shell
- Don't claim bugs in behavior you don't fully understand

**Express uncertainty.** If unsure, say "I'm not certain about X, let me verify"
instead of presenting speculation as fact.

**Stop after correction.** When proven wrong on one claim, re-verify *all*
claims in the review before proceeding.

**Don't "fix" working code.** Even if something looks wrong, verify it's
actually broken before touching it. Making readable code uglier is not a fix.

**Read context, not just diffs.** A heredoc inside `run: |` behaves differently
than a standalone heredoc. Understand the full context before judging.

**Core principle:** Confidence without verification is the root failure.

## Code Style

- Python 3.14+, use modern type syntax: `list[X]`, `dict[K,V]`, `X | None`
  - Make sure to actually exploit new features. See [Python 3.14 whatsnew]
- Imports: `stdlib` first, third-party, then relative (`.module`)
- Format: `ruff` (88 char line length, double quotes)
- `Dataclasses` for data structures, not `dicts`
- Docstrings: triple-quoted, first line is summary
- Error handling: catch specific exceptions (`psutil.NoSuchProcess`, etc.)
- Naming: `snake_case` functions/vars, `PascalCase` classes

### Python 3.14

#### Template Strings (t-strings)

```python
name = "value"
template = t"Hello {name}"  # Returns Template object, not str
# Use for safe SQL/HTML/shell interpolation
```

#### Deferred Annotations

- Forward references work without quotes: `def foo(x: SomeClass)` just works
- Use
  `annotationlib.get_annotations(obj, format=Format.VALUE|FORWARDREF|STRING)`

#### Multiple Interpreters

```python
from concurrent.interpreters import Interpreter
from concurrent.futures import InterpreterPoolExecutor
# True parallelism, no GIL, isolated memory
```

#### Other Changes

- `except ValueError, TypeError:` → brackets optional
- `compression.zstd` → Zstandard support
- REPL has syntax highlighting
- Free-threaded mode officially supported

## Structure

```tree
src/procclean/
  __init__.py       # Package init, __version__, main, ProcessInfo
  __main__.py       # Entry point, main() dispatcher (CLI vs TUI)
  core/             # Business logic (no UI deps)
    __init__.py     # Re-exports all core symbols
    models.py       # ProcessInfo dataclass
    process.py      # get_process_list, find_similar_processes
    filters.py      # filter_*, sort_processes, is_system_service
    actions.py      # kill_process, kill_processes
    memory.py       # get_memory_summary
    constants.py    # SYSTEM_EXE_PATHS, CRITICAL_SERVICES
  cli/              # CLI interface
    __init__.py     # Re-exports
    parser.py       # create_parser(), run_cli()
    commands.py     # cmd_list, cmd_kill, cmd_groups, cmd_memory
  tui/              # TUI interface
    __init__.py     # Re-exports
    app.py          # ProcessCleanerApp
    app.tcss        # Textual CSS styles
    screens.py      # ConfirmKillScreen
  formatters/       # Output formatters
    __init__.py     # Re-exports
    columns.py      # ColumnSpec, COLUMNS, DEFAULT_COLUMNS
    output.py       # format_table, format_json, format_csv, format_md
```

## CLI Usage

```bash
procclean                           # Launch TUI (default)
procclean list                      # List processes (table)
procclean list -f json|csv|md       # Different output formats
procclean list -s mem|cpu|pid|name|cwd  # Sort by field
procclean list -o                   # Orphans only
procclean list -m                   # High memory only
procclean list -k                   # Killable orphans only
procclean list --cwd                # Filter by current directory
procclean list --cwd /path/to/dir   # Filter by specific cwd
procclean groups                    # Show process groups
procclean kill <PID> [PID...]       # Kill process(es)
procclean kill -f <PID>             # Force kill (SIGKILL)
procclean kill --cwd /path -y       # Kill all in cwd (with confirm skip)
procclean kill -k -y                # Kill all killable orphans
procclean kill -k --preview         # Preview what would be killed
procclean kill -k --dry-run         # Alias for --preview
procclean kill -k --preview -O json # Preview in JSON format
procclean mem                       # Show memory summary
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
| `w`     | Filter by selected cwd  |
| `W`     | Clear cwd filter        |
| `space` | Toggle selection        |
| `s`     | Select all visible      |
| `c`     | Clear selection         |
| `1`     | Sort by memory          |
| `2`     | Sort by CPU             |
| `3`     | Sort by PID             |
| `4`     | Sort by name            |
| `5`     | Sort by cwd             |
| `!`     | Reverse sort order      |

<!--link definitions-->

[Python 3.14 whatsnew]: https://docs.python.org/3/whatsnew/3.14.html "What’s new in Python 3.14"
