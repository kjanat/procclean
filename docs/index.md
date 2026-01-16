---
title: procclean
hide:
    - toc
---

<figure markdown="span">
  <img src="assets/images/logo.svg" alt="procclean" class="hero-logo">
</figure>

Interactive TUI for exploring and cleaning up processes - find orphans, memory hogs, and kill them.

**Version 3.0** - Complete rewrite in Rust for maximum performance, with Python bindings for seamless installation.

## Features

- **Memory overview** - Real-time total/used/free/swap display
- **Multiple views** - All processes, Orphaned, Killable, High Memory (>500MB)
- **Orphan detection** - Finds processes whose parent died (PPID=1)
- **Tmux awareness** - Won't flag tmux processes as orphan candidates
- **Batch operations** - Select multiple processes and kill them at once
- **Process grouping** - Find duplicate/similar processes consuming resources
- **CLI mode** - Scriptable commands with JSON/CSV/Markdown output
- **Fast & Lightweight** - Written in Rust for maximum performance

## Quick Start

_Install via pip (easiest):_

```bash
pip install procclean
```

_Or using uv (recommended):_

```bash
# Install
uv tool install procclean

# Run without installing
uvx procclean
```

_Or using pipx:_

```bash
pipx install procclean
# or run directly
pipx run procclean
```

### Usage examples

_Launch TUI_

```bash
procclean
```

_CLI usage_

```bash
procclean list -o         # Show orphans
procclean list -m         # High memory processes
procclean kill -k -y      # Kill all killable orphans
procclean groups          # Show process groups
procclean memory          # Memory summary
```

## Requirements

- **Python users**: Python 3.14+ (for `pip install`)
- **Rust users**: Rust 1.70+ (for `cargo build`)
- **Platform**: Linux (uses `/proc` filesystem)

## Architecture

Version 3.0 brings major improvements:

- **Core**: Written in Rust (sysinfo, ratatui, clap, tokio)
- **Python Bindings**: PyO3 for seamless Python integration
- **Performance**: Up to 10x faster than Python implementation
- **Memory**: 50% lower memory footprint
- **Distribution**: Available via both PyPI and Crates.io
