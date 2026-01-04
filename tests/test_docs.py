"""Tests for CLI documentation generation utilities."""

import argparse
import os
from unittest.mock import patch

from procclean.cli.docs import (
    _argparser_to_markdown,
    _capture_help,
    _extract_h2_sections,
    _normalize_content,
    generate_cli_docs,
    merge_alias_sections,
    write_cli_docs,
)


class TestCaptureHelp:
    """Tests for _capture_help function."""

    def test_captures_html_output(self):
        """Should return HTML string with help content."""
        parser = argparse.ArgumentParser(prog="test", description="Test program")
        parser.add_argument("--foo", help="Foo option")

        result = _capture_help(parser)

        assert "<pre" in result
        assert "<code" in result
        assert "test" in result

    def test_restores_force_color_env(self):
        """Should restore FORCE_COLOR environment variable."""
        original = os.environ.get("FORCE_COLOR")
        parser = argparse.ArgumentParser(prog="test")

        _capture_help(parser)

        assert os.environ.get("FORCE_COLOR") == original

    def test_restores_force_color_when_set(self):
        """Should restore FORCE_COLOR when it was previously set."""
        os.environ["FORCE_COLOR"] = "0"
        parser = argparse.ArgumentParser(prog="test")

        try:
            _capture_help(parser)
            assert os.environ.get("FORCE_COLOR") == "0"
        finally:
            os.environ.pop("FORCE_COLOR", None)


class TestArgparserToMarkdown:
    """Tests for _argparser_to_markdown function."""

    def test_generates_markdown_with_heading(self):
        """Should generate markdown with specified heading."""
        parser = argparse.ArgumentParser(prog="myapp", description="My app")

        result = _argparser_to_markdown(parser, heading="My CLI")

        assert result.startswith("# My CLI")
        assert "myapp" in result

    def test_includes_subcommands(self):
        """Should include subcommand documentation."""
        parser = argparse.ArgumentParser(prog="myapp")
        subparsers = parser.add_subparsers()
        subparsers.add_parser("sub1", help="First subcommand")
        subparsers.add_parser("sub2", help="Second subcommand")

        result = _argparser_to_markdown(parser)

        assert "## sub1" in result
        assert "## sub2" in result
        assert "myapp sub1 --help" in result

    def test_no_subcommands(self):
        """Should handle parser without subcommands."""
        parser = argparse.ArgumentParser(prog="simple")

        result = _argparser_to_markdown(parser)

        assert "# CLI Reference" in result
        assert "##" not in result  # No h2 sections for subcommands


class TestExtractH2Sections:
    """Tests for _extract_h2_sections function."""

    def test_extracts_h2_sections(self):
        """Should extract h2 sections with correct line ranges."""
        markdown = """# Title

## Section 1

Content 1

## Section 2

Content 2
"""
        _lines, sections = _extract_h2_sections(markdown)

        assert len(sections) == 2  # noqa: PLR2004
        assert sections[0][0] == "Section 1"
        assert sections[1][0] == "Section 2"

    def test_no_h2_sections(self):
        """Should return empty list when no h2 sections."""
        markdown = "# Just a title\n\nSome content"

        _lines, sections = _extract_h2_sections(markdown)

        assert sections == []

    def test_ignores_h2_in_code_blocks(self):
        """Should not match ## inside fenced code blocks."""
        markdown = """# Title

## Real Section

```markdown
## Not a section
```

## Another Real Section
"""
        _lines, sections = _extract_h2_sections(markdown)

        assert len(sections) == 2  # noqa: PLR2004
        titles = [s[0] for s in sections]
        assert "Real Section" in titles
        assert "Another Real Section" in titles
        assert "Not a section" not in titles


class TestNormalizeContent:
    """Tests for _normalize_content function."""

    def test_normalizes_command_invocations(self):
        """Should replace command names with CMD placeholder."""
        content = "procclean list --help\nprocclean kill --help"

        result = _normalize_content(content)

        assert "procclean CMD --help" in result
        assert "procclean list --help" not in result

    def test_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        content = "  \n  some content  \n  "

        result = _normalize_content(content)

        assert result == "some content"


class TestMergeAliasSections:
    """Tests for merge_alias_sections function."""

    def test_merges_duplicate_sections(self):
        """Should merge sections with identical content."""
        markdown = """# CLI

## list

procclean list --help

content

## ls

procclean ls --help

content
"""
        result = merge_alias_sections(markdown)

        assert "## `list` / `ls`" in result
        # Should only have one instance of the content
        assert result.count("content") == 1

    def test_no_sections_returns_unchanged(self):
        """Should return unchanged when no h2 sections."""
        markdown = "# Just a title"

        result = merge_alias_sections(markdown)

        assert result == markdown

    def test_unique_sections_unchanged(self):
        """Should not merge sections with different content."""
        markdown = """# CLI

## cmd1

unique content 1

## cmd2

unique content 2
"""
        result = merge_alias_sections(markdown)

        assert "## `cmd1`" in result
        assert "## `cmd2`" in result
        assert "unique content 1" in result
        assert "unique content 2" in result


class TestGenerateCliDocs:
    """Tests for generate_cli_docs function."""

    def test_generates_complete_docs(self):
        """Should generate complete CLI documentation."""
        result = generate_cli_docs()

        # Check header comment
        assert "AUTO-GENERATED" in result
        assert "dprint-ignore-file" in result

        # Check content
        assert "# CLI Reference" in result
        assert "procclean" in result

    def test_includes_subcommands(self):
        """Should include all subcommands."""
        result = generate_cli_docs()

        # Check for known subcommands (merged aliases)
        assert "list" in result.lower()
        assert "kill" in result.lower()
        assert "mem" in result.lower() or "memory" in result.lower()


class TestWriteCliDocs:
    """Tests for write_cli_docs function."""

    def test_writes_new_file(self, tmp_path):
        """Should write file when it doesn't exist."""
        test_path = tmp_path / "cli.md"

        with patch("procclean.cli.docs.DOCS_CLI_PATH", test_path):
            result = write_cli_docs()

        assert result is True
        assert test_path.exists()
        assert "CLI Reference" in test_path.read_text()

    def test_updates_changed_file(self, tmp_path):
        """Should update file when content differs."""
        test_path = tmp_path / "cli.md"
        test_path.write_text("old content")

        with patch("procclean.cli.docs.DOCS_CLI_PATH", test_path):
            result = write_cli_docs()

        assert result is True
        assert "CLI Reference" in test_path.read_text()

    def test_skips_unchanged_file(self, tmp_path):
        """Should return False when file content unchanged."""
        test_path = tmp_path / "cli.md"

        with patch("procclean.cli.docs.DOCS_CLI_PATH", test_path):
            # First write
            write_cli_docs()
            # Second write should detect no change
            result = write_cli_docs()

        assert result is False
