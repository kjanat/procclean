<p align="center">
  <img src="logo/procclean-transparent.svg" alt="procclean" width="500">
</p>

<p align="center">
  <em>Interactive TUI for exploring and cleaning up processes - find orphans, memory hogs, and kill them.</em>
</p>

<p align="center">
  <a href="https://github.com/kjanat/procclean/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kjanat/procclean" alt="License"></a>
  <a href="https://github.com/kjanat/procclean/releases"><img src="https://img.shields.io/github/v/release/kjanat/procclean" alt="Release"></a>
  <img src="https://img.shields.io/badge/python-3.14%2B-blue" alt="Python 3.14+">
  <img src="https://img.shields.io/badge/platform-linux-lightgrey" alt="Linux">
</p>

## Features

- **Memory overview** - Real-time total/used/free/swap display
- **Multiple views** - All processes, Orphaned, Process Groups, High Memory
  (>500MB)
- **Orphan detection** - Finds processes whose parent died (PPID=1)
- **Tmux awareness** - Won't flag tmux processes as orphan candidates
- **Batch operations** - Select multiple processes and kill them at once
- **Process grouping** - Find duplicate/similar processes consuming resources
- **CLI mode** - Scriptable commands with JSON/CSV/Markdown output

## Installation

```bash
uv tool install git+https://github.com/kjanat/procclean
```

Or run directly:

```bash
uvx git+https://github.com/kjanat/procclean
```

## Usage

### TUI Mode (default)

```bash
procclean
```

### CLI Commands

```bash
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
procclean kill --cwd /path -y       # Kill all in cwd (skip confirm)
procclean kill -k -y                # Kill all killable orphans
procclean kill -k --preview         # Preview what would be killed

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
| `Space` | Toggle selection        |
| `s`     | Select all visible      |
| `c`     | Clear selection         |
| `1`     | Sort by memory          |
| `2`     | Sort by CPU             |
| `3`     | Sort by PID             |
| `4`     | Sort by name            |
| `5`     | Sort by cwd             |
| `!`     | Reverse sort order      |

## Views

- **All Processes** - All user processes sorted by memory usage
- **Orphaned** - Processes with PPID=1 (parent died)
- **Process Groups** - Similar processes grouped together
- **High Memory** - Processes using >500MB RAM

## Output Formats

CLI supports multiple output formats via `-f`:

- `table` - Human-readable table (default)
- `json` - JSON array for scripting
- `csv` - CSV for spreadsheets
- `md` - Markdown table

## Requirements

- Python 3.14+
- Linux (uses `/proc` filesystem)

## Development

```bash
git clone https://github.com/kjanat/procclean
cd procclean
uv sync
uv run pre-commit install
```

Run tests:

```bash
uv run pytest
```

## License

[MIT][license]

<!--link definitions-->

[license]: https://github.com/kjanat/procclean/blob/master/LICENSE "MIT License"

<!--markdownlint-disable-file MD033 MD041-->
