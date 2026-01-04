"""MkDocs hook to ensure CLI docs are up-to-date before build."""

from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig

# Add src to path for imports
_src_path = str(Path(__file__).parent.parent.parent / "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

log = logging.getLogger("mkdocs.hooks.ensure_cli_docs")


def on_pre_build(config: MkDocsConfig) -> None:
    """Regenerate CLI docs before build to ensure they're fresh.

    Args:
        config: MkDocs configuration (unused, required by hook signature).
    """
    del config  # Unused but required by MkDocs hook signature

    # Import dynamically to ensure sys.path is set up first
    docs_module = importlib.import_module("procclean.cli.docs")
    docs_cli_path = docs_module.DOCS_CLI_PATH
    write_cli_docs = docs_module.write_cli_docs

    updated = write_cli_docs()

    if updated:
        log.info("CLI docs regenerated: %s", docs_cli_path)
    else:
        log.debug("CLI docs unchanged: %s", docs_cli_path)
