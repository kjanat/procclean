# Installation

## Using uv (recommended)

Install as a tool:

```bash
uv tool install git+https://github.com/kjanat/procclean
```

Or run directly without installing:

```bash
uvx git+https://github.com/kjanat/procclean
```

## From source

```bash
git clone https://github.com/kjanat/procclean
cd procclean
uv sync
uv run procclean
```

## Requirements

- Python 3.14+
- Linux (uses `/proc` filesystem)

## Dependencies

- [psutil](https://github.com/giampaolo/psutil) - Process utilities
- [textual](https://github.com/Textualize/textual) - TUI framework
- [tabulate](https://github.com/astanin/python-tabulate) - Table formatting
