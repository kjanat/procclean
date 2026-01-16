#!/usr/bin/env -S uv run
"""Generate CLI reference documentation from argparse parser.

Usage:
    ./scripts/generate_cli_docs.py

Exit codes:
    0 - Docs unchanged
    1 - Docs updated
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from procclean.cli.docs import DOCS_CLI_PATH, write_cli_docs

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def main() -> int:
    """Generate CLI docs.

    Returns:
        0 if docs unchanged, 1 if updated.
    """
    updated = write_cli_docs()

    if updated:
        log.info("CLI docs updated: %s", DOCS_CLI_PATH)
        return 1

    log.info("CLI docs unchanged: %s", DOCS_CLI_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
