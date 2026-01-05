---
title: procclean
hide:
  - toc
---

<figure markdown="span">
  <img src="assets/images/logo.svg" alt="procclean" class="hero-logo">
</figure>

Interactive TUI for exploring and cleaning up processes - find orphans, memory
hogs, and kill them. :procclean-icon:

## Features

- **Memory overview** - Real-time total/used/free/swap display
- **Multiple views** - All processes, Orphaned, Process Groups, High Memory
  (>500MB)
- **Orphan detection** - Finds processes whose parent died (PPID=1)
- **Tmux awareness** - Won't flag tmux processes as orphan candidates
- **Batch operations** - Select multiple processes and kill them at once
- **Process grouping** - Find duplicate/similar processes consuming resources
- **CLI mode** - Scriptable commands with JSON/CSV/Markdown output

## Quick Start

```bash
# Install
uv tool install git+https://github.com/kjanat/procclean

# Or run directly
uvx git+https://github.com/kjanat/procclean

# Launch TUI
procclean

# CLI usage
procclean list -o  # Show orphans
procclean kill -k -y  # Kill all killable orphans
```

## Requirements

- Python 3.14+
- Linux (uses `/proc` filesystem)
