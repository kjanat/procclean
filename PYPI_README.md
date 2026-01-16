# procclean

<p align="center">
  <em>Interactive TUI for exploring and cleaning up processes - find orphans, memory hogs, and kill them.</em>
</p>

**Version 2.0** is a complete rewrite in Rust for maximum performance, with Python bindings for seamless PyPI distribution.

## Features

- **Memory overview** - Real-time total/used/free/swap display
- **Multiple views** - All, Orphaned, Killable, High Memory
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
- **Fast & Lightweight** - Written in Rust for maximum performance

## Installation

Install via pip:

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
procclean list -f json|csv|md       # Different output formats
procclean list -s mem|cpu|pid|name|cwd  # Sort by field
procclean list -o                   # Orphans only
procclean list -m                   # High memory only (>500MB)
procclean list -k                   # Killable orphans only
procclean list --cwd                # Filter by current directory

# Process groups
procclean groups                    # Show process groups

# Kill processes
procclean kill <PID> [PID...]       # Kill process(es)
procclean kill -f <PID>             # Force kill (SIGKILL)
procclean kill --cwd /path -y       # Kill all in cwd (skip confirm)
procclean kill -k --preview         # Preview what would be killed

# Memory summary
procclean memory                    # Show memory summary
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
| `m`     | Show high memory        |
| `w`     | Filter by selected cwd  |
| `W`     | Clear cwd filter        |
| `space` | Toggle selection        |
| `s`     | Select all visible      |
| `c`     | Clear selection         |
| `1-5`   | Sort by field           |
| `!`     | Reverse sort order      |

## Python API

You can also use procclean as a Python library:

```python
from procclean import get_processes, get_memory, kill_process

# Get all processes
processes = get_processes(sort_by="memory", min_memory_mb=10.0)

# Get memory summary
memory = get_memory()
print(f"Memory: {memory.used_gb:.1f}/{memory.total_gb:.1f} GB ({memory.percent:.1f}%)")

# Kill a process
success, message = kill_process(pid=12345, force=False)
```

## License

MIT License - see [LICENSE](https://github.com/kjanat/procclean/blob/master/LICENSE) for details.

## Links

- **GitHub**: https://github.com/kjanat/procclean
- **Documentation**: https://procclean.kjanat.com
- **Issues**: https://github.com/kjanat/procclean/issues
