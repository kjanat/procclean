# procclean

Interactive TUI for exploring and cleaning up processes - find orphans, memory
hogs, and kill them.

## Features

- **Memory overview** - Real-time total/used/free/swap display
- **Multiple views** - All processes, Orphaned, Process Groups, High Memory
  (>500MB)
- **Orphan detection** - Finds processes whose parent died (PPID=1)
- **Tmux awareness** - Won't flag tmux processes as orphan candidates
- **Batch operations** - Select multiple processes and kill them at once
- **Process grouping** - Find duplicate/similar processes consuming resources

## Installation

```bash
uv tool install git+https://github.com/kjanat/procclean
```

Or run directly:

```bash
uvx git+https://github.com/kjanat/procclean
```

## Usage

```bash
procclean
```

## Keybindings

| Key     | Action                        |
| ------- | ----------------------------- |
| `Space` | Toggle select process         |
| `s`     | Select all visible            |
| `c`     | Clear selection               |
| `k`     | Kill selected (SIGTERM)       |
| `K`     | Force kill selected (SIGKILL) |
| `r`     | Refresh process list          |
| `o`     | Show orphaned processes       |
| `a`     | Show all processes            |
| `g`     | Show process groups           |
| `q`     | Quit                          |

## Views

- **All Processes** - All user processes sorted by memory usage
- **Orphaned** - Processes with PPID=1 (parent died)
- **Process Groups** - Similar processes grouped together
- **High Memory** - Processes using >500MB RAM

## Requirements

- Python 3.14+
- Linux (uses `/proc` filesystem)

## License

MIT
