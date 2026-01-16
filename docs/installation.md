# Installation

## Python Package (Recommended)

Procclean 3.0 is written in Rust with Python bindings for easy installation via pip.

### Using pip

```bash
pip install procclean
```

### Using uv (recommended)

Install as a tool:

```bash
uv tool install procclean
# then run `procclean`
```

Or run directly without installing:

```bash
uvx procclean
```

### Using pipx

```bash
pipx install procclean
# or run directly
pipx run procclean
```

## Rust Binary

For Rust developers or if you want the standalone binary:

### From source

```bash
git clone https://github.com/kjanat/procclean
cd procclean
cargo build --release
sudo cp target/release/procclean /usr/local/bin/
```

### Using cargo install

```bash
cargo install --path .
```

### From Crates.io (coming soon)

```bash
cargo install procclean
```

## Requirements

- **Python users**: Python 3.14+ (for `pip install`)
- **Rust users**: Rust 1.70+ (for `cargo build`)
- **Platform**: Linux (uses `/proc` filesystem)

## Architecture

Version 3.0 is a complete rewrite in Rust for maximum performance:

- **Core**: Written in Rust (sysinfo, ratatui, clap, tokio)
- **Python Bindings**: PyO3 for seamless Python integration
- **Distribution**: Available via both PyPI (pip) and Crates.io (cargo)

## Migration from 2.x

Version 3.0 maintains full CLI and TUI compatibility with 2.x. The main changes:

- **Performance**: Significantly faster due to Rust implementation
- **Memory**: Lower memory footprint
- **Dependencies**: No Python dependencies required (bundled Rust binary)
- **Installation**: Same commands work (`pip install procclean`)
