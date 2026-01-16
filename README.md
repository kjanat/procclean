<p align="center">
  <img src="https://raw.github.com/kjanat/procclean/master/logo/procclean-transparent.svg" alt="procclean" width="500">
</p>

<p align="center">
  <em>Interactive TUI for exploring and cleaning up processes - find orphans, memory hogs, and kill them.</em>
</p>

<p align="center">
  <a href="https://crates.io/crates/procclean"><img src="https://img.shields.io/crates/v/procclean" alt="Crates.io"></a>
  <a href="https://github.com/kjanat/procclean/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/kjanat/procclean/ci.yml?branch=master" alt="CI"></a>
  <a href="https://github.com/kjanat/procclean/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kjanat/procclean" alt="License"></a>
  <img src="https://img.shields.io/badge/rust-1.70%2B-orange" alt="Rust 1.70+">
  <img src="https://img.shields.io/badge/platform-linux-lightgrey" alt="Linux">
</p>

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

### Option 1: Python (via PyPI)

The easiest way to install procclean is via pip. The Python package includes pre-compiled Rust binaries:

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

### Option 2: Rust (via Cargo)

Install directly from source with Cargo:

```bash
cargo install --path .
```

Or build manually:

```bash
cargo build --release
sudo cp target/release/procclean /usr/local/bin/
```

### Option 3: From Crates.io (coming soon)

```bash
cargo install procclean
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
procclean memory                    # Show memory summary
procclean mem                       # Alias for 'memory'
procclean mem -f json               # Memory as JSON
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
| `1`     | Sort by memory          |
| `2`     | Sort by CPU             |
| `3`     | Sort by PID             |
| `4`     | Sort by name            |
| `5`     | Sort by cwd             |
| `!`     | Reverse sort order      |

## Architecture

Procclean 2.0 is written in Rust with Python bindings for PyPI distribution:

**Rust Core:**
- **sysinfo** - Cross-platform system information
- **ratatui** - Terminal UI framework
- **clap** - CLI argument parsing
- **tokio** - Async runtime
- **serde** - Serialization

**Python Bindings:**
- **PyO3** - Rust-Python interop
- **maturin** - Build and publish Python packages with Rust extensions

## Development

### Rust Development

```bash
# Build Rust binary
cargo build --release

# Run tests
cargo test

# Run with debug output
RUST_LOG=debug cargo run

# Format code
cargo fmt

# Lint
cargo clippy
```

### Python Development (with Rust backend)

```bash
# Install maturin
pip install maturin

# Build Python wheel with Rust extension
maturin build --release

# Develop locally (editable install)
maturin develop

# Build and test
maturin develop && python -c "import procclean; print(procclean.get_memory())"
```

### Publishing

**To PyPI:**
```bash
# Build wheel
maturin build --release

# Publish to PyPI
maturin publish

# Or publish to TestPyPI first
maturin publish --repository testpypi
```

**To Crates.io:**
```bash
cargo publish
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Originally written in Python, rewritten in Rust for better performance and lower resource usage.
