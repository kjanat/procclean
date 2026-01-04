"""Process cleanup TUI application."""

from importlib.metadata import version

__version__ = version("procclean")

# Re-export main entry point and core types
from procclean.__main__ import main
from procclean.core import ProcessInfo

__all__ = ["ProcessInfo", "__version__", "main"]
