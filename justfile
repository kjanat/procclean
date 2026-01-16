# https://just.systems
# Run `just` to see available recipes

set quiet

# Show available recipes
[group('meta')]
default:
    @just --list --unsorted

# Development

# Build the project
[group('dev')]
build:
    cargo build

# Build release version
[group('dev')]
build-release:
    cargo build --release

# Run the TUI app
[group('dev')]
run *ARGS:
    cargo run -- {{ ARGS }}

# Run release version
[group('dev')]
run-release *ARGS:
    cargo run --release -- {{ ARGS }}

# Quality Checks

# Run all checks (fmt + clippy + test)
[group('quality')]
check: fmt-check clippy test

# Format code
[group('quality')]
fmt:
    cargo fmt

# Check formatting
[group('quality')]
fmt-check:
    cargo fmt -- --check

# Lint with clippy
[group('quality')]
clippy:
    cargo clippy -- -D warnings

# Run all tests
[group('quality')]
test:
    cargo test

# Run tests with verbose output
[group('quality')]
test-v:
    cargo test -- --nocapture

# Build & Release

# Install locally
[group('release')]
install:
    cargo install --path .

# Show current version
[group('release')]
version:
    @grep '^version' Cargo.toml | head -1

# Create a signed release tag (NEVER delete tags, use -f to update)
[group('release')]
tag VERSION MESSAGE:
    git tag -s v{{ VERSION }} -m "v{{ VERSION }} - {{ MESSAGE }}"

# Utilities

# Remove build artifacts and caches
[group('util')]
clean:
    cargo clean
    rm -rf target/

# Check for outdated dependencies
[group('util')]
outdated:
    cargo outdated

# Update dependencies
[group('util')]
update:
    cargo update

# Full CI check
[group('quality')]
ci: check

# Python Legacy (for reference)

# Run Python version (if needed for comparison)
[group('legacy')]
python-setup:
    uv sync
    uv run pre-commit install --install-hooks

[group('legacy')]
python-run:
    uv run procclean
