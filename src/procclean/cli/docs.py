"""CLI documentation generation utilities."""

from __future__ import annotations

import argparse
import io
import os
import re
from collections import defaultdict
from pathlib import Path

from markdown_it import MarkdownIt
from rich.console import Console
from rich.text import Text
from rich_argparse import RichHelpFormatter

from .parser import create_parser

DOCS_CLI_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "cli.md"
HEADER_COMMENT = (
    "<!-- AUTO-GENERATED - DO NOT EDIT -->\n"
    "<!-- Run: ./scripts/generate_cli_docs.py -->\n"
    "<!-- dprint-ignore-file -->\n"
    "<!-- markdownlint-disable-file -->\n\n"
)

# Apply custom styles for CLI help output (once at module load)
_HELP_STYLES = {
    "prog": "#98f641",
    "args": "#54ebdd",
    "groups": "#98f641",
    "metavar": "#7af0e5",
    "syntax": "#98f641",
    "help": "white",
    "text": "white",
    "default": "#888888",
}
for _key, _value in _HELP_STYLES.items():
    RichHelpFormatter.styles[f"argparse.{_key}"] = _value

_PRE_STYLE = "font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"
_CODE_FORMAT = (
    f'<pre style="{_PRE_STYLE}">\n'
    '<code style="font-family:inherit" class="nohighlight">{code}</code>\n'
    "</pre>\n"
)


def _capture_help(parser: argparse.ArgumentParser) -> str:
    """Capture the help text of an argparse parser as colored HTML.

    Returns:
        HTML string with colored help output.
    """
    # Force colored output even when not in a TTY
    old_force_color = os.environ.get("FORCE_COLOR")
    os.environ["FORCE_COLOR"] = "1"
    try:
        parser.formatter_class = RichHelpFormatter
        text = Text.from_ansi(parser.format_help())
    finally:
        if old_force_color is None:
            os.environ.pop("FORCE_COLOR", None)
        else:
            os.environ["FORCE_COLOR"] = old_force_color

    # force_terminal=True ensures colored output even when not in a TTY
    console = Console(file=io.StringIO(), record=True, force_terminal=True)
    console.print(text, crop=False)

    return console.export_html(code_format=_CODE_FORMAT, inline_styles=True)


def _argparser_to_markdown(
    parser: argparse.ArgumentParser,
    heading: str = "CLI Reference",
) -> str:
    """Convert an argparse parser to markdown documentation with colored output.

    Args:
        parser: The argparse parser to document.
        heading: The main heading for the documentation.

    Returns:
        Markdown string with colored HTML help blocks.
    """
    prog = parser.prog
    main_help = _capture_help(parser).rstrip()

    lines = [
        f"# {heading}",
        "",
        f"Documentation for the `{prog}` script.",
        "",
        "```console",
        f"{prog} --help",
        "```",
        "",
        main_help,
    ]

    # Find subparsers
    subparsers_actions = [
        action
        for action in parser._actions  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction)  # noqa: SLF001
    ]

    if subparsers_actions:
        current_subparsers_action = subparsers_actions[0]
        for sub_cmd_name, sub_cmd_parser in current_subparsers_action.choices.items():
            sub_cmd_help_text = _capture_help(sub_cmd_parser).rstrip()
            lines.extend([
                "",
                f"## {sub_cmd_name}",
                "",
                "```console",
                f"{prog} {sub_cmd_name} --help",
                "```",
                "",
                sub_cmd_help_text,
            ])

    return "\n".join(lines)


def _extract_h2_sections(
    markdown: str,
) -> tuple[list[str], list[tuple[str, int, int]]]:
    """Extract h2 sections from markdown using AST.

    Uses markdown-it parser to reliably detect headings
    (won't match ## inside fenced code blocks).

    Returns:
        Tuple of (lines, sections) where sections is list of (title, start, end).
    """
    md = MarkdownIt()
    tokens = md.parse(markdown)
    lines = markdown.split("\n")

    h2_starts: list[tuple[str, int]] = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            title = tokens[i + 1].content
            start_line = token.map[0]  # type: ignore[index]
            h2_starts.append((title, start_line))

    h2_sections: list[tuple[str, int, int]] = []
    for i, (title, start) in enumerate(h2_starts):
        end = h2_starts[i + 1][1] if i + 1 < len(h2_starts) else len(lines)
        h2_sections.append((title, start, end))

    return lines, h2_sections


def _normalize_content(content: str) -> str:
    """Normalize content for comparison by removing command-specific parts.

    Returns:
        Content with command invocations normalized and whitespace stripped.
    """
    normalized = re.sub(r"procclean \w+ --help", "procclean CMD --help", content)
    return normalized.strip()


def merge_alias_sections(markdown: str) -> str:
    """Merge duplicate argparse alias sections in CLI markdown.

    Detects sections with identical help content (modulo command name)
    and merges their headers, e.g., `## list` + `## ls` -> `## list / ls`.

    Returns:
        Markdown with merged alias sections.
    """
    lines, h2_sections = _extract_h2_sections(markdown)
    if not h2_sections:
        return markdown

    # Group by normalized content
    content_to_titles: dict[str, list[str]] = defaultdict(list)
    for title, start, end in h2_sections:
        content = "\n".join(lines[start + 1 : end])
        normalized = _normalize_content(content)
        content_to_titles[normalized].append(title)

    # Rebuild with merged headers
    result = lines[: h2_sections[0][1]][:]
    seen: set[str] = set()

    for _title, start, end in h2_sections:
        content = "\n".join(lines[start + 1 : end])
        normalized = _normalize_content(content)

        if normalized in seen:
            continue
        seen.add(normalized)

        aliases = content_to_titles[normalized]
        header = " / ".join(f"`{a}`" for a in aliases)

        result.append(f"## {header}")
        result.extend(lines[start + 1 : end])

    return "\n".join(result)


def generate_cli_docs() -> str:
    """Generate merged CLI documentation from argparse parser.

    Returns:
        Complete CLI reference markdown with header comment.
    """
    parser = create_parser()
    markdown = _argparser_to_markdown(parser, heading="CLI Reference")
    merged = merge_alias_sections(markdown)
    return HEADER_COMMENT + merged


def write_cli_docs() -> bool:
    """Generate and write CLI docs to docs/cli.md.

    Returns:
        True if file was updated, False if unchanged.
    """
    new_content = generate_cli_docs()

    if DOCS_CLI_PATH.exists():
        existing = DOCS_CLI_PATH.read_text()
        if existing == new_content:
            return False

    DOCS_CLI_PATH.write_text(new_content)
    return True
