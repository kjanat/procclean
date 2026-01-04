"""Process cleanup TUI application."""

from importlib.metadata import version

__version__ = version("procclean")

# Re-export core types for convenience
from .core import ProcessInfo

__all__ = ["ProcessInfo", "__version__"]
