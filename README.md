<p align="center">
  <img src="https://raw.github.com/kjanat/procclean/master/logo/procclean-transparent.svg" alt="procclean" width="500">
</p>

<p align="center">
  <em>Interactive TUI for exploring and cleaning up processes - find orphans, memory hogs, and kill them.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/procclean/"><img src="https://img.shields.io/pypi/v/procclean" alt="PyPI"></a>
  <a href="https://pypi.org/project/procclean/"><img src="https://img.shields.io/pypi/dm/procclean" alt="Downloads"></a>
  <a href="https://github.com/kjanat/procclean/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/kjanat/procclean/ci.yml?branch=master" alt="CI"></a>
  <a href="https://github.com/kjanat/procclean/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kjanat/procclean" alt="License"></a>
  <a href="https://procclean.kjanat.com"><img src="https://img.shields.io/badge/docs-mkdocs-blue" alt="Docs"></a>
  <img src="https://img.shields.io/badge/python-3.14%2B-blue" alt="Python 3.14+">
  <img src="https://img.shields.io/badge/platform-linux-lightgrey" alt="Linux">
</p>

## Features

- **Memory overview** - Real-time total/used/free/swap display
- **Multiple views** - All, Orphaned, Killable, Process Groups, High Memory
- **Orphan detection** - Finds processes whose parent died (PPID=1)
- **Killable detection** - Orphans safe to kill (not tmux, not system services)
- **Stale detection** - Flags processes with deleted executables
- **Tmux awareness** - Won't flag tmux processes as orphan candidates
- **Batch operations** - Select multiple processes and kill them at once
- **Process grouping** - Find duplicate/similar processes consuming resources
- **Custom columns** - Select which columns to display in CLI output
- **Configurable thresholds** - Adjust memory filters via CLI flags
- **Preview mode** - Dry-run for kill operations with formatting options
- **CLI mode** - Scriptable commands with JSON/CSV/Markdown output
- **Clickable TUI** - Click headers to sort, rows to select

## Installation

```bash
pip install procclean
```

Or with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv tool install procclean
```

Or with [pipx](https://pipx.pypa.io/):

```bash
pipx install procclean
```

Run without installing:

```bash
uvx procclean
# or
pipx run procclean
```

## Usage

### TUI Mode (default)

```bash
procclean
```

### CLI Commands

```bash
# List processes
procclean list                      # List processes (table)
procclean ls                        # Alias for 'list'
procclean list -f json|csv|md       # Different output formats
procclean list -s mem|cpu|pid|name|cwd  # Sort by field
procclean list -a                   # Sort ascending (default: descending)
procclean list -o                   # Orphans only
procclean list -m                   # High memory only (>500MB)
procclean list -k                   # Killable orphans only
procclean list --cwd                # Filter by current directory
procclean list --cwd /path/to/dir   # Filter by specific cwd
procclean list -n 20                # Limit output to 20 processes
procclean list -c pid,name,rss_mb   # Custom columns
procclean list --min-memory 10      # Only processes using >10 MB
procclean list --high-memory-threshold 1000  # High-mem at 1000 MB

# Process groups
procclean groups                    # Show process groups
procclean g                         # Alias for 'groups'
procclean groups -f json            # Groups as JSON

# Kill processes
procclean kill <PID> [PID...]       # Kill process(es)
procclean kill -f <PID>             # Force kill (SIGKILL)
procclean kill --cwd /path -y       # Kill all in cwd (skip confirm)
procclean kill -k -y                # Kill all killable orphans
procclean kill -k --preview         # Preview what would be killed
procclean kill -k --dry-run         # Alias for --preview
procclean kill -k --preview -O json # Preview in JSON format

# Memory summary
procclean mem                       # Show memory summary
procclean memory                    # Full name for 'mem'
procclean mem -f json               # Memory info as JSON
```

## TUI Keybindings

| Key     | Action                  |
| ------- | ----------------------- |
| `q`     | Quit                    |
| `r`     | Refresh                 |
| `k`     | Kill selected (SIGTERM) |
| `K`     | Force kill (SIGKILL)    |
| `o`     | Show orphans            |
| `O`     | Show killable           |
| `a`     | Show all                |
| `g`     | Show groups             |
| `w`     | Filter by selected cwd  |
| `W`     | Clear cwd filter        |
| `Space` | Toggle selection        |
| `s`     | Select all visible      |
| `c`     | Clear selection         |
| `1`     | Sort by memory          |
| `2`     | Sort by CPU             |
| `3`     | Sort by PID             |
| `4`     | Sort by name            |
| `5`     | Sort by cwd             |
| `!`     | Reverse sort order      |

Click column headers to sort, click rows to toggle selection.

## Views

- **All Processes** - All user processes sorted by memory usage
- **Orphaned** - Processes with PPID=1 (parent died)
- **Killable** - Orphans safe to kill (not in tmux, not system services)
- **Process Groups** - Similar processes grouped together
- **High Memory** - Processes using >500MB RAM (configurable)

## Output Formats

CLI supports multiple output formats via `-f`:

- `table` - Human-readable table (default)
- `json` - JSON array for scripting
- `csv` - CSV for spreadsheets
- `md` - Markdown table

## Custom Columns

Use `-c` to specify which columns to display:

```bash
procclean list -c pid,name,rss_mb,cwd
```

Available columns: `pid`, `name`, `rss_mb`, `cpu_percent`, `cwd`, `ppid`,
`parent_name`, `status`, `cmdline`, `username`

## Requirements

- Python 3.14+
- Linux (uses `/proc` filesystem)

## Development

```bash
git clone https://github.com/kjanat/procclean
cd procclean
uv sync
uv run pre-commit install --install-hooks
```

Run tests:

```bash
uv run pytest                    # All tests
uv run pytest --cov -vv          # With coverage
```

Lint and type check:

```bash
uv run ruff check src/
uv run ty check
```

## License

[MIT][license]

<!--link definitions-->

[license]: https://github.com/kjanat/procclean/blob/master/LICENSE "MIT License"

<!--markdownlint-disable-file MD033 MD041-->
