"""Tests for formatters module."""

import csv
import io
import json
import math

from procclean.formatters import (
    COLUMNS,
    DEFAULT_COLUMNS,
    ColumnSpec,
    clip_left,
    clip_right,
    fmt_float1,
    fmt_status,
    format_csv,
    format_json,
    format_markdown,
    format_output,
    format_table,
    get_available_columns,
    get_rows,
)


class TestClipRight:
    """Tests for clip_right function."""

    def test_no_truncation_when_short(self):
        """Should return unchanged string when shorter than max."""
        assert clip_right("hello", 10) == "hello"

    def test_truncates_from_right(self):
        """Should truncate keeping left portion."""
        assert clip_right("hello world", 5) == "hello"

    def test_exact_length(self):
        """Should return unchanged when exactly max length."""
        assert clip_right("hello", 5) == "hello"


class TestClipLeft:
    """Tests for clip_left function."""

    def test_no_truncation_when_short(self):
        """Should return unchanged string when shorter than max."""
        assert clip_left("hello", 10) == "hello"

    def test_truncates_from_left_with_ellipsis(self):
        """Should truncate keeping right portion with ellipsis."""
        result = clip_left("/very/long/path/to/file", 15)
        assert result == "...path/to/file"
        assert len(result) == 15

    def test_exact_length(self):
        """Should return unchanged when exactly max length."""
        assert clip_left("hello", 5) == "hello"


class TestFmtFloat1:
    """Tests for fmt_float1 function."""

    def test_formats_with_one_decimal(self):
        """Should format float with 1 decimal place."""
        assert fmt_float1(math.pi) == "3.1"
        assert fmt_float1(100.0) == "100.0"
        assert fmt_float1(0.04) == "0.0"  # rounds down

    def test_handles_integers(self):
        """Should handle integer input."""
        assert fmt_float1(42) == "42.0"


class TestFmtStatus:
    """Tests for fmt_status function."""

    def test_plain_status(self, make_process):
        """Should return plain status when no markers."""
        proc = make_process(status="running", is_orphan=False, in_tmux=False)
        assert fmt_status(proc) == "running"

    def test_orphan_marker(self, make_process):
        """Should add orphan marker when is_orphan is True."""
        proc = make_process(status="running", is_orphan=True, in_tmux=False)
        assert fmt_status(proc) == "running [orphan]"

    def test_tmux_marker(self, make_process):
        """Should add tmux marker when in_tmux is True."""
        proc = make_process(status="running", is_orphan=False, in_tmux=True)
        assert fmt_status(proc) == "running [tmux]"

    def test_both_markers(self, make_process):
        """Should add both markers when both are True."""
        proc = make_process(status="running", is_orphan=True, in_tmux=True)
        assert fmt_status(proc) == "running [orphan] [tmux]"


class TestColumnSpec:
    """Tests for ColumnSpec dataclass."""

    def test_extract_simple_value(self, make_process):
        """Should extract raw value from process."""
        spec = ColumnSpec("pid", "PID", lambda p: p.pid)
        proc = make_process(pid=1234)
        assert spec.extract(proc) == "1234"

    def test_extract_with_formatter(self, make_process):
        """Should apply formatter to value."""
        spec = ColumnSpec("rss_mb", "RAM", lambda p: p.rss_mb, fmt_float1)
        proc = make_process(rss_mb=123.456)
        assert spec.extract(proc) == "123.5"

    def test_extract_with_max_width_clips_right(self, make_process):
        """Should clip non-cwd values from right."""
        spec = ColumnSpec("name", "Name", lambda p: p.name, max_width=5)
        proc = make_process(name="very_long_name")
        assert spec.extract(proc) == "very_"

    def test_extract_cwd_clips_left(self, make_process):
        """Should clip cwd values from left with ellipsis."""
        spec = ColumnSpec("cwd", "CWD", lambda p: p.cwd, max_width=15)
        proc = make_process(cwd="/very/long/path/to/dir")
        result = spec.extract(proc)
        assert result.startswith("...")
        assert len(result) == 15


class TestGetRows:
    """Tests for get_rows function."""

    def test_default_columns(self, sample_processes):
        """Should use DEFAULT_COLUMNS when none specified."""
        headers, _rows = get_rows(sample_processes)
        assert len(headers) == len(DEFAULT_COLUMNS)
        assert "PID" in headers
        assert "Name" in headers

    def test_custom_columns(self, sample_processes):
        """Should use specified columns."""
        headers, rows = get_rows(sample_processes, columns=["pid", "name", "rss_mb"])
        assert headers == ["PID", "Name", "RAM (MB)"]
        assert len(rows) == len(sample_processes)
        assert len(rows[0]) == 3

    def test_ignores_invalid_columns(self, sample_processes):
        """Should ignore columns not in COLUMNS."""
        headers, _rows = get_rows(
            sample_processes, columns=["pid", "invalid_col", "name"]
        )
        assert headers == ["PID", "Name"]


class TestFormatTable:
    """Tests for format_table function."""

    def test_empty_processes(self):
        """Should return message when no processes."""
        assert format_table([]) == "No processes found."

    def test_returns_table_format(self, sample_processes):
        """Should return ASCII table format."""
        result = format_table(sample_processes)
        assert "PID" in result
        assert "Name" in result
        # simple_outline format uses box chars
        assert "─" in result or "-" in result


class TestFormatMarkdown:
    """Tests for format_markdown function."""

    def test_empty_processes(self):
        """Should return message when no processes."""
        assert format_markdown([]) == "No processes found."

    def test_returns_markdown_table(self, sample_processes):
        """Should return pipe-delimited table."""
        result = format_markdown(sample_processes)
        assert "|" in result
        assert "PID" in result
        # Should have header separator row
        lines = result.strip().split("\n")
        assert len(lines) >= 3  # header + separator + at least 1 row


class TestFormatJson:
    """Tests for format_json function."""

    def test_returns_valid_json(self, sample_processes):
        """Should return valid JSON."""
        result = format_json(sample_processes)
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == len(sample_processes)

    def test_contains_all_fields(self, make_process):
        """Should include all expected fields."""
        proc = make_process(
            pid=42,
            name="test",
            cmdline="test cmd",
            cwd="/tmp",
            is_orphan=True,
            in_tmux=True,
        )
        result = format_json([proc])
        data = json.loads(result)[0]
        assert data["pid"] == 42
        assert data["name"] == "test"
        assert data["cmdline"] == "test cmd"
        assert data["cwd"] == "/tmp"
        assert data["is_orphan"] is True
        assert data["in_tmux"] is True
        assert "rss_mb" in data
        assert "cpu_percent" in data
        assert "status" in data


class TestFormatCsv:
    """Tests for format_csv function."""

    def test_empty_processes(self):
        """Should return empty string when no processes."""
        assert not format_csv([])

    def test_returns_csv_with_headers(self, sample_processes):
        """Should return CSV with header row."""
        result = format_csv(sample_processes)
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert rows[0][0] == "pid"
        assert "name" in rows[0]
        assert len(rows) == len(sample_processes) + 1  # header + data rows

    def test_csv_values_correct(self, make_process):
        """Should have correct values in CSV."""
        proc = make_process(pid=123, name="myproc", rss_mb=45.67)
        result = format_csv([proc])
        reader = csv.DictReader(io.StringIO(result))
        row = next(reader)
        assert row["pid"] == "123"
        assert row["name"] == "myproc"
        assert row["rss_mb"] == "45.67"


class TestFormatOutput:
    """Tests for format_output routing function."""

    def test_routes_to_json(self, sample_processes):
        """Should return JSON when fmt='json'."""
        result = format_output(sample_processes, "json")
        data = json.loads(result)
        assert isinstance(data, list)

    def test_routes_to_csv(self, sample_processes):
        """Should return CSV when fmt='csv'."""
        result = format_output(sample_processes, "csv")
        assert "pid" in result
        assert "," in result

    def test_routes_to_md(self, sample_processes):
        """Should return markdown when fmt='md'."""
        result = format_output(sample_processes, "md")
        assert "|" in result

    def test_routes_to_markdown(self, sample_processes):
        """Should return markdown when fmt='markdown'."""
        result = format_output(sample_processes, "markdown")
        assert "|" in result

    def test_routes_to_table(self, sample_processes):
        """Should return table by default."""
        result = format_output(sample_processes, "table")
        assert "PID" in result

    def test_default_is_table(self, sample_processes):
        """Should return table for unknown format."""
        result = format_output(sample_processes, "unknown")
        assert "PID" in result


class TestGetAvailableColumns:
    """Tests for get_available_columns function."""

    def test_returns_all_column_keys(self):
        """Should return list of all column keys."""
        cols = get_available_columns()
        assert set(cols) == set(COLUMNS.keys())
        assert "pid" in cols
        assert "name" in cols
        assert "rss_mb" in cols
        assert "cwd" in cols


class TestColumnsDefinitions:
    """Tests for COLUMNS dict and DEFAULT_COLUMNS."""

    def test_all_default_columns_exist(self):
        """All DEFAULT_COLUMNS should exist in COLUMNS."""
        for col in DEFAULT_COLUMNS:
            assert col in COLUMNS, f"Default column '{col}' not in COLUMNS"

    def test_column_specs_have_required_fields(self):
        """Each ColumnSpec should have key, header, and get."""
        for key, spec in COLUMNS.items():
            assert spec.key == key
            assert spec.header
            assert callable(spec.get)
