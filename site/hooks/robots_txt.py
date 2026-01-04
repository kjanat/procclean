"""MkDocs hook to generate robots.txt based on privacy settings."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger("mkdocs.hooks.robots_txt")

# Robots.txt content that blocks all crawlers
_ROBOTS_BLOCK_ALL = """\
User-agent: *
Disallow: /
"""


def on_post_build(config: MkDocsConfig) -> None:
    """Generate robots.txt after build if private mode is enabled.

    Controlled via `extra.private` in mkdocs.yml:
        extra:
          private: true  # Blocks all search engine indexing

    Args:
        config: MkDocs configuration.
    """
    private = config.extra.get("private", False)

    if not private:
        log.debug("Site is public, skipping robots.txt generation")
        return

    site_dir = Path(config.site_dir)
    robots_path = site_dir / "robots.txt"

    robots_path.write_text(_ROBOTS_BLOCK_ALL)
    log.info("Generated robots.txt to block indexing: %s", robots_path)
