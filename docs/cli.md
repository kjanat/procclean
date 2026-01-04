# CLI Reference

## Commands

### list

List processes with optional filters.

```bash
procclean list                          # All processes (table)
procclean list -f json|csv|md           # Different output formats
procclean list -s mem|cpu|pid|name|cwd  # Sort by field
procclean list -o                       # Orphans only
procclean list -m                       # High memory only (>500MB)
procclean list -k                       # Killable orphans only
procclean list --cwd                    # Filter by current directory
procclean list --cwd /path/to/dir       # Filter by specific cwd
```

### kill

Kill one or more processes.

```bash
procclean kill <PID> [PID...]   # Kill by PID(s)
procclean kill -f <PID>         # Force kill (SIGKILL)
procclean kill --cwd /path -y   # Kill all in cwd (skip confirm)
procclean kill -k -y            # Kill all killable orphans
procclean kill -k --preview     # Preview what would be killed
procclean kill -k --dry-run     # Alias for --preview
```

### groups

Show process groups (similar processes grouped together).

```bash
procclean groups
```

### mem

Show memory summary.

```bash
procclean mem
```

## Output Formats

The `-f` flag supports:

| Format  | Description                    |
| ------- | ------------------------------ |
| `table` | Human-readable table (default) |
| `json`  | JSON array for scripting       |
| `csv`   | CSV for spreadsheets           |
| `md`    | Markdown table                 |

## Sort Options

The `-s` flag supports:

| Field  | Description       |
| ------ | ----------------- |
| `mem`  | Memory usage      |
| `cpu`  | CPU usage         |
| `pid`  | Process ID        |
| `name` | Process name      |
| `cwd`  | Working directory |
