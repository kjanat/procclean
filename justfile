# https://just.systems
# Run `just` to see available recipes

set quiet

# Show available recipes
default:
    @just --list --unsorted

# ─────────────────────────────────────────────────────────────────────────────
# Development
# ─────────────────────────────────────────────────────────────────────────────

# Session setup: sync deps and install pre-commit hooks
setup:
    uv sync
    uv run pre-commit install --install-hooks

# Run the TUI app
run:
    uv run procclean

# Run CLI with arguments
cli *ARGS:
    uv run procclean {{ ARGS }}

# ─────────────────────────────────────────────────────────────────────────────
# Quality Checks
# ─────────────────────────────────────────────────────────────────────────────

# Run all checks (lint + type + test)
check: lint type test

# Lint with ruff
lint:
    uv run ruff check src/
    uv run ruff format --check src/

# Auto-fix lint issues
fix:
    uv run ruff check --fix src/
    uv run ruff format src/

# Type check with ty
type:
    uv run ty check

# Run all tests
test:
    uv run pytest

# Run tests with verbose output
test-v:
    uv run pytest -vv

# Run tests with coverage
test-cov:
    uv run pytest --cov -vv

# Run a single test file or pattern
test-one PATTERN:
    uv run pytest {{ PATTERN }} -v

# Run all pre-commit hooks
hooks:
    uv run pre-commit run --all-files

# ─────────────────────────────────────────────────────────────────────────────
# Build & Release
# ─────────────────────────────────────────────────────────────────────────────

# Build the package
build:
    uv build

# Show current version
version:
    @uv version

# Bump patch version (0.0.X)
bump-patch:
    uv version --bump patch

# Bump minor version (0.X.0)
bump-minor:
    uv version --bump minor

# Bump major version (X.0.0)
bump-major:
    uv version --bump major

# Create a signed release tag (NEVER delete tags, use -f to update)
tag VERSION MESSAGE:
    git tag -s v{{ VERSION }} -m "v{{ VERSION }} - {{ MESSAGE }}"

# ─────────────────────────────────────────────────────────────────────────────
# Documentation
# ─────────────────────────────────────────────────────────────────────────────

# Serve docs locally with live reload
docs:
    uv run mkdocs serve

# Build static docs
docs-build:
    uv run mkdocs build

# Regenerate CLI docs (docs/cli.md)
gen-cli-docs:
    uv run scripts/generate_cli_docs.py

# Regenerate TUI screenshots
gen-screenshots:
    uv run scripts/generate_screenshots.py

# ─────────────────────────────────────────────────────────────────────────────
# TUI Development
# ─────────────────────────────────────────────────────────────────────────────

# Run TUI with Textual dev console
tui-dev:
    uv run textual run --dev src/procclean/tui/app.py:ProcessCleanerApp

# Open Textual dev console (run in separate terminal)
tui-console:
    uv run textual console

# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

# Remove build artifacts and caches
clean:
    rm -rf dist/ build/ .pytest_cache/ .ruff_cache/ .mypy_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Check for outdated dependencies
outdated:
    uv pip list --outdated

# Full CI check (mirrors GitHub Actions)
ci: hooks check
