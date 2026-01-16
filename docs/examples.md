# Examples

Common usage patterns for the CLI.

## Listing Processes

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

## Killing Processes

```bash
procclean kill <PID> [PID...]   # Kill by PID(s)
procclean kill -f <PID>         # Force kill (SIGKILL)
procclean kill --cwd /path -y   # Kill all in cwd (skip confirm)
procclean kill -k -y            # Kill all killable orphans
procclean kill -k --preview     # Preview what would be killed
procclean kill -k --dry-run     # Alias for --preview
```

## Process Groups

```bash
procclean groups                # Show similar processes grouped
procclean groups -f json        # JSON output
```

## Memory Summary

```bash
procclean mem                   # Show memory summary
procclean mem -f json           # JSON output
```

<div class="grid cards" markdown>

- :material-clock-fast:{ .lg .middle } **Output Formats**

    ***

    The `-f` flag supports:

    | Format  | Description                    |
    | ------- | ------------------------------ |
    | `table` | Human-readable table (default) |
    | `json`  | JSON array for scripting       |
    | `csv`   | CSV for spreadsheets           |
    | `md`    | Markdown table                 |

- :fontawesome-brands-markdown:{ .lg .middle } **Sort Options**

    ***

    The `-s` flag supports:

    | Field  | Description       |
    | ------ | ----------------- |
    | `mem`  | Memory usage      |
    | `cpu`  | CPU usage         |
    | `pid`  | Process ID        |
    | `name` | Process name      |
    | `cwd`  | Working directory |

</div>

## Common Workflows

### Clean up orphaned dev processes

```bash
# Preview what would be killed
procclean kill -k --preview

# Kill all killable orphans (with confirmation)
procclean kill -k

# Kill without confirmation
procclean kill -k -y
```

### Find memory hogs in a project directory

```bash
# List high-memory processes in current directory
procclean list -m --cwd

# Kill all processes in a specific directory
procclean kill --cwd /path/to/project -y
```

### Export process list for analysis

```bash
# JSON for scripting
procclean list -f json > processes.json

# CSV for spreadsheets
procclean list -f csv > processes.csv
```
