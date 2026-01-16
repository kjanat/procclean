# https://just.systems
# Run `just` to see available recipes

set quiet

# Show available recipes
[group('meta')]
default:
    @just --list --unsorted

# ─────────────────────────────────────────────────────────────────────────────
# Development
# ─────────────────────────────────────────────────────────────────────────────

# Session setup: sync deps and install pre-commit hooks
[group('dev')]
setup:
    uv sync
    uv run pre-commit install --install-hooks

# Run the TUI app
[group('dev')]
run:
    uv run procclean

# Run CLI with arguments
[group('dev')]
cli *ARGS:
    uv run procclean {{ ARGS }}

# ─────────────────────────────────────────────────────────────────────────────
# Quality Checks
# ─────────────────────────────────────────────────────────────────────────────

# Run all checks (lint + type + test)
[group('quality')]
check: lint type test

# Lint with ruff
[group('quality')]
lint:
    uv run ruff check src/
    uv run ruff format --check src/

# Auto-fix lint issues
[group('quality')]
fix:
    uv run ruff check --fix src/
    uv run ruff format src/

# Type check with ty
[group('quality')]
type:
    uv run ty check

# Run all tests
[group('quality')]
test:
    uv run pytest

# Run tests with verbose output
[group('quality')]
test-v:
    uv run pytest -vv

# Run tests with coverage
[group('quality')]
test-cov:
    uv run pytest --cov -vv

# Run a single test file or pattern
[group('quality')]
test-one PATTERN:
    uv run pytest {{ PATTERN }} -v

# Run all pre-commit hooks
[group('quality')]
hooks:
    uv run pre-commit run --all-files

# ─────────────────────────────────────────────────────────────────────────────
# Build & Release
# ─────────────────────────────────────────────────────────────────────────────

# Build the package
[group('release')]
build:
    uv build

# Show current version
[group('release')]
version:
    @uv version

# Bump patch version (0.0.X)
[group('release')]
bump-patch:
    uv version --bump patch

# Bump minor version (0.X.0)
[group('release')]
bump-minor:
    uv version --bump minor

# Bump major version (X.0.0)
[group('release')]
bump-major:
    uv version --bump major

# Create a signed release tag (NEVER delete tags, use -f to update)
[group('release')]
tag VERSION MESSAGE:
    git tag -s v{{ VERSION }} -m "v{{ VERSION }} - {{ MESSAGE }}"

# ─────────────────────────────────────────────────────────────────────────────
# Documentation
# ─────────────────────────────────────────────────────────────────────────────

# Serve docs locally with live reload
[group('docs')]
docs:
    uv run mkdocs serve

# Build static docs
[group('docs')]
docs-build:
    uv run mkdocs build

# Regenerate CLI docs (docs/cli.md)
[group('docs')]
gen-cli-docs:
    uv run scripts/generate_cli_docs.py

# Regenerate TUI screenshots
[group('docs')]
gen-screenshots:
    uv run scripts/generate_screenshots.py

# ─────────────────────────────────────────────────────────────────────────────
# TUI Development
# ─────────────────────────────────────────────────────────────────────────────

# Run TUI with Textual dev console
[group('dev')]
tui-dev:
    uv run textual run --dev src/procclean/tui/app.py:ProcessCleanerApp

# Open Textual dev console (run in separate terminal)
[group('dev')]
tui-console:
    uv run textual console

# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

# Remove build artifacts and caches
[group('util')]
clean:
    rm -rf dist/ build/ .pytest_cache/ .ruff_cache/ .mypy_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Check for outdated dependencies
[group('util')]
outdated:
    uv pip list --outdated

# Full CI check (mirrors GitHub Actions)
[group('quality')]
ci: hooks check
