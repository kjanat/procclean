"""MkDocs hook to ensure TUI screenshots are up-to-date before build."""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

    from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger("mkdocs.hooks.ensure_screenshots")

# Path to the generate_screenshots.py script
_SCRIPT_PATH = (
    Path(__file__).parent.parent.parent / "scripts" / "generate_screenshots.py"
)


def _load_screenshots_module() -> types.ModuleType:
    """Load the generate_screenshots module from file path.

    Returns:
        The loaded generate_screenshots module.

    Raises:
        ImportError: If the module cannot be loaded from the script path.
    """
    # Add src to path for procclean imports
    src_path = str(Path(__file__).parent.parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    spec = importlib.util.spec_from_file_location("generate_screenshots", _SCRIPT_PATH)
    if spec is None or spec.loader is None:
        msg = f"Cannot load module from {_SCRIPT_PATH}"
        raise ImportError(msg)

    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_screenshots"] = module
    spec.loader.exec_module(module)
    return module


def on_pre_build(config: MkDocsConfig) -> None:
    """Regenerate TUI screenshots before build to ensure they're fresh.

    Args:
        config: MkDocs configuration (unused, required by hook signature).
    """
    del config  # Unused but required by MkDocs hook signature

    screenshots_module = _load_screenshots_module()
    screenshots_dir = screenshots_module.SCREENSHOTS_DIR
    write_screenshots = screenshots_module.write_screenshots

    updated = write_screenshots()

    if updated:
        log.info("TUI screenshots regenerated: %s", screenshots_dir)
    else:
        log.debug("TUI screenshots unchanged: %s", screenshots_dir)
