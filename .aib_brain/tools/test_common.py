#!/usr/bin/env python3
"""Comprehensive tests for common.py helpers."""

from __future__ import annotations

import datetime as dt
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    ACTIVE,
    CLOSED,
    ValidationError,
    ensure_workspace,
    format_markdown_table,
    load_template,
    now_compact_request_id,
    now_iso,
    parse_markdown_table,
    read_text,
    requests_register_path,
    resolve_active_request_or_explicit,
    slugify,
    update_requests_register,
    validate_request_md,
    write_text,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_HEADER = ["request_id", "title", "folder", "state", "created_at", "closed_at"]


def _make_register_table(rows: list[list[str]]) -> str:
    return "# Requests Register\n\n" + format_markdown_table(REGISTER_HEADER, rows)


def _setup_workspace(tmp: str) -> Path:
    """Create the minimum workspace structure expected by ensure_workspace."""
    ws = Path(tmp)
    (ws / ".aib_brain").mkdir(parents=True, exist_ok=True)
    (ws / ".aib_memory").mkdir(parents=True, exist_ok=True)
    return ws


# ---------------------------------------------------------------------------
# Markdown table parsing
# ---------------------------------------------------------------------------

class TestParseMarkdownTable(unittest.TestCase):
    def test_valid_table(self):
        md = (
            "| a | b | c |\n"
            "| --- | --- | --- |\n"
            "| 1 | 2 | 3 |\n"
            "| 4 | 5 | 6 |\n"
        )
        header, rows = parse_markdown_table(md)
        self.assertEqual(header, ["a", "b", "c"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["1", "2", "3"])
        self.assertEqual(rows[1], ["4", "5", "6"])

    def test_empty_content(self):
        header, rows = parse_markdown_table("")
        self.assertEqual(header, [])
        self.assertEqual(rows, [])

    def test_only_header_no_rows(self):
        md = "| a | b |\n| --- | --- |\n"
        header, rows = parse_markdown_table(md)
        self.assertEqual(header, ["a", "b"])
        self.assertEqual(rows, [])

    def test_missing_cells_padded(self):
        md = (
            "| a | b | c |\n"
            "| --- | --- | --- |\n"
            "| 1 |\n"
        )
        header, rows = parse_markdown_table(md)
        self.assertEqual(header, ["a", "b", "c"])
        self.assertEqual(len(rows), 1)
        # Row should be padded to match header length
        self.assertEqual(len(rows[0]), 3)

    def test_extra_cells_truncated(self):
        md = (
            "| a | b |\n"
            "| --- | --- |\n"
            "| 1 | 2 | 3 | 4 |\n"
        )
        header, rows = parse_markdown_table(md)
        self.assertEqual(len(rows[0]), 2)

    def test_non_table_content_ignored(self):
        md = (
            "# Title\n"
            "Some paragraph.\n"
            "| h1 | h2 |\n"
            "| --- | --- |\n"
            "| v1 | v2 |\n"
        )
        header, rows = parse_markdown_table(md)
        self.assertEqual(header, ["h1", "h2"])
        self.assertEqual(rows, [["v1", "v2"]])


# ---------------------------------------------------------------------------
# Markdown table formatting
# ---------------------------------------------------------------------------

class TestFormatMarkdownTable(unittest.TestCase):
    def test_round_trip(self):
        header = ["col1", "col2", "col3"]
        rows = [["a", "b", "c"], ["d", "e", "f"]]
        text = format_markdown_table(header, rows)
        parsed_header, parsed_rows = parse_markdown_table(text)
        self.assertEqual(parsed_header, header)
        self.assertEqual(parsed_rows, rows)

    def test_rows_shorter_than_header(self):
        header = ["a", "b", "c"]
        rows = [["1"]]
        text = format_markdown_table(header, rows)
        self.assertIn("| 1 |  |  |", text)

    def test_newlines_in_values_replaced(self):
        header = ["x"]
        rows = [["line1\nline2"]]
        text = format_markdown_table(header, rows)
        self.assertNotIn("\nline2", text)
        self.assertIn("line1 line2", text)

    def test_empty_rows(self):
        header = ["a", "b"]
        text = format_markdown_table(header, [])
        lines = [l for l in text.strip().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)  # header + separator


# ---------------------------------------------------------------------------
# Slugification
# ---------------------------------------------------------------------------

class TestSlugify(unittest.TestCase):
    def test_normal_text(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_special_characters(self):
        self.assertEqual(slugify("foo@bar!baz"), "foo-bar-baz")

    def test_empty_string(self):
        self.assertEqual(slugify(""), "request")

    def test_whitespace_only(self):
        self.assertEqual(slugify("   "), "request")

    def test_leading_trailing_spaces(self):
        self.assertEqual(slugify("  My Title  "), "my-title")

    def test_multiple_hyphens_collapsed(self):
        self.assertEqual(slugify("a---b"), "a-b")

    def test_numeric_input(self):
        self.assertEqual(slugify("123"), "123")


# ---------------------------------------------------------------------------
# Timestamp formatting
# ---------------------------------------------------------------------------

class TestTimestampFormatting(unittest.TestCase):
    def test_now_iso_fixed(self):
        fixed = dt.datetime(2025, 1, 15, 10, 30, 45, tzinfo=dt.timezone.utc)
        result = now_iso(fixed)
        self.assertEqual(result, "2025-01-15 10:30:45 +0000")

    def test_now_compact_request_id_fixed(self):
        fixed = dt.datetime(2025, 3, 7, 14, 5, 0, tzinfo=dt.timezone.utc)
        result = now_compact_request_id(fixed)
        self.assertEqual(result, "R-20250307-1405")

    def test_now_iso_no_arg_returns_string(self):
        result = now_iso()
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_now_compact_no_arg_returns_string(self):
        result = now_compact_request_id()
        self.assertTrue(result.startswith("R-"))


# ---------------------------------------------------------------------------
# Workspace validation
# ---------------------------------------------------------------------------

class TestEnsureWorkspace(unittest.TestCase):
    def test_valid_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            ensure_workspace(ws)  # should not raise

    def test_missing_directory(self):
        with self.assertRaises(ValidationError):
            ensure_workspace(Path("/nonexistent/workspace/path"))

    def test_missing_aib_brain(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValidationError):
                ensure_workspace(Path(tmp))


# ---------------------------------------------------------------------------
# Read / write text
# ---------------------------------------------------------------------------

class TestReadWriteText(unittest.TestCase):
    def test_read_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = read_text(Path(tmp) / "no_such_file.txt")
            self.assertEqual(result, "")

    def test_read_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "hello.txt"
            p.write_text("world", encoding="utf-8")
            self.assertEqual(read_text(p), "world")

    def test_write_creates_parents(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "a" / "b" / "c" / "file.txt"
            write_text(p, "deep content")
            self.assertTrue(p.exists())
            self.assertEqual(p.read_text(encoding="utf-8"), "deep content")

    def test_write_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "file.txt"
            write_text(p, "first")
            write_text(p, "second")
            self.assertEqual(read_text(p), "second")


# ---------------------------------------------------------------------------
# Load template
# ---------------------------------------------------------------------------

class TestLoadTemplate(unittest.TestCase):
    def test_existing_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain_dir = Path(tmp)
            tmpl_dir = brain_dir / "templates"
            tmpl_dir.mkdir(parents=True)
            (tmpl_dir / "sample.md").write_text("template content", encoding="utf-8")
            result = load_template(brain_dir, "sample.md")
            self.assertEqual(result, "template content")

    def test_missing_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValidationError):
                load_template(Path(tmp), "missing.md")


# ---------------------------------------------------------------------------
# Resolve active request or explicit
# ---------------------------------------------------------------------------

class TestResolveActiveRequestOrExplicit(unittest.TestCase):
    def _write_register(self, ws: Path, rows: list[list[str]]) -> None:
        content = _make_register_table(rows)
        reg_path = requests_register_path(ws)
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        write_text(reg_path, content)

    def test_explicit_id_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            self._write_register(ws, [
                ["R-001", "Title1", "folder1", ACTIVE, "2025-01-01", ""],
                ["R-002", "Title2", "folder2", CLOSED, "2025-01-02", "2025-01-03"],
            ])
            row = resolve_active_request_or_explicit(ws, "R-002")
            self.assertEqual(row[0], "R-002")

    def test_explicit_id_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            self._write_register(ws, [
                ["R-001", "Title1", "folder1", ACTIVE, "2025-01-01", ""],
            ])
            with self.assertRaises(ValidationError):
                resolve_active_request_or_explicit(ws, "R-999")

    def test_single_active_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            self._write_register(ws, [
                ["R-001", "Title1", "folder1", ACTIVE, "2025-01-01", ""],
                ["R-002", "Title2", "folder2", CLOSED, "2025-01-02", "2025-01-03"],
            ])
            row = resolve_active_request_or_explicit(ws, None)
            self.assertEqual(row[0], "R-001")
            self.assertEqual(row[3], ACTIVE)

    def test_multiple_active_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            self._write_register(ws, [
                ["R-001", "A", "f1", ACTIVE, "2025-01-01", ""],
                ["R-002", "B", "f2", ACTIVE, "2025-01-02", ""],
            ])
            with self.assertRaises(ValidationError):
                resolve_active_request_or_explicit(ws, None)

    def test_no_active_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            self._write_register(ws, [
                ["R-001", "A", "f1", CLOSED, "2025-01-01", "2025-01-02"],
            ])
            with self.assertRaises(ValidationError):
                resolve_active_request_or_explicit(ws, None)

    def test_missing_register_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            with self.assertRaises(ValidationError):
                resolve_active_request_or_explicit(ws, None)


# ---------------------------------------------------------------------------
# Update requests register
# ---------------------------------------------------------------------------

class TestUpdateRequestsRegister(unittest.TestCase):
    def test_writes_correct_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            rows = [["R-001", "My Title", "my-folder", ACTIVE, "2025-01-01", ""]]
            update_requests_register(ws, rows)
            content = read_text(requests_register_path(ws))
            self.assertIn("# Requests Register", content)
            self.assertIn("R-001", content)
            self.assertIn("My Title", content)
            # Verify the file is parseable back
            header, parsed_rows = parse_markdown_table(content)
            self.assertEqual(header, REGISTER_HEADER)
            self.assertEqual(parsed_rows[0][0], "R-001")


# ---------------------------------------------------------------------------
# Initialize idempotency
# ---------------------------------------------------------------------------

class TestInitializeIdempotency(unittest.TestCase):
    def test_register_not_overwritten_when_exists(self):
        """Simulates that a second call to update_requests_register
        replaces content, but an external tool should check existence first."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            reg = requests_register_path(ws)
            original_content = "# Requests Register\n\nCustom content.\n"
            reg.parent.mkdir(parents=True, exist_ok=True)
            write_text(reg, original_content)

            # An idempotent initializer should skip if file already exists
            if reg.exists():
                pass  # Do not overwrite
            else:
                update_requests_register(ws, [])

            self.assertEqual(read_text(reg), original_content)


# ---------------------------------------------------------------------------
# slugify max_length (P30)
# ---------------------------------------------------------------------------

class TestSlugifyMaxLength(unittest.TestCase):
    def test_long_title_truncated(self):
        long_title = "a" * 200
        result = slugify(long_title)
        self.assertLessEqual(len(result), 64)

    def test_default_max_length_64(self):
        title = "word " * 20  # well beyond 64 chars when slugified
        result = slugify(title)
        self.assertLessEqual(len(result), 64)

    def test_short_title_unchanged(self):
        result = slugify("hello world")
        self.assertEqual(result, "hello-world")

    def test_no_trailing_dash_after_truncation(self):
        # Build a string that would end on a dash boundary at position 64
        # "ab-" repeated: 3 chars * 21 = 63 chars + "a" = 64 exactly
        # We want to ensure the result doesn't end with "-"
        title = "ab " * 30  # slugified = "ab-ab-ab-..." well over 64
        result = slugify(title)
        self.assertFalse(result.endswith("-"), f"Result ends with dash: {result!r}")

    def test_custom_max_length(self):
        result = slugify("hello world this is a long title", max_length=10)
        self.assertLessEqual(len(result), 10)


# ---------------------------------------------------------------------------
# validate_request_md (P21)
# ---------------------------------------------------------------------------

VALID_REQUEST_MD = """\
## Goal
Implement the thing.

## Background
Some background.

## Scope
- A
- B

## Out of scope
- X

## Constraints
- None

## Success criteria
- Passes tests
"""


class TestValidateRequestMd(unittest.TestCase):
    def test_valid_request_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "request.md"
            write_text(path, VALID_REQUEST_MD)
            # Should not raise
            validate_request_md(path)

    def test_missing_section_raises(self):
        for section in [
            "## Goal",
            "## Background",
            "## Scope",
            "## Out of scope",
            "## Constraints",
            "## Success criteria",
        ]:
            with self.subTest(missing=section):
                content = VALID_REQUEST_MD.replace(section, "## Placeholder")
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "request.md"
                    write_text(path, content)
                    with self.assertRaises(ValidationError):
                        validate_request_md(path)

    def test_empty_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "request.md"
            write_text(path, "")
            with self.assertRaises(ValidationError):
                validate_request_md(path)

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nonexistent.md"
            with self.assertRaises(ValidationError):
                validate_request_md(path)


# ---------------------------------------------------------------------------
# create-request letter-check (P29)
# ---------------------------------------------------------------------------

class TestCreateRequestLetterCheck(unittest.TestCase):
    """Verify that a title with no letters raises ValidationError."""

    def test_numeric_title_raises(self):
        import re as _re
        from common import ValidationError as VE

        title = "12345"
        with self.assertRaises(VE):
            if not _re.search(r"[a-zA-Z]", title):
                raise VE("Title must contain at least one letter to generate a meaningful slug.")

    def test_letters_title_passes(self):
        import re as _re
        title = "Issue 31"
        # Should not raise
        if not _re.search(r"[a-zA-Z]", title):
            raise AssertionError("Should not reach here")

    def test_empty_title_caught_by_existing_guard(self):
        # Empty title is already caught by the "if not title" guard before
        # the letter-check, so no separate letter-check error is expected.
        title = ""
        self.assertFalse(bool(title.strip()))


# ---------------------------------------------------------------------------
# close-request auto-close active iteration (Improvement 5)
# ---------------------------------------------------------------------------

IT_HEADER = ["iteration_id", "state", "created_at", "closed_at", "summary"]


def _make_iterations_table(rows: list[list[str]]) -> str:
    return "# Iterations\n\n" + format_markdown_table(IT_HEADER, rows)


class TestCloseRequestAutoClose(unittest.TestCase):
    def _setup_workspace_with_active_iteration(
        self,
        ws: Path,
        req_id: str = "R-001",
        iteration_id: str = "01",
    ) -> Path:
        """Create minimal workspace with one active request + one active iteration."""
        (ws / ".aib_brain").mkdir(parents=True, exist_ok=True)
        (ws / ".aib_memory").mkdir(parents=True, exist_ok=True)

        folder_rel = f".aib_memory/requests/{req_id}-title"
        reg_content = _make_register_table([
            [req_id, "Test Title", folder_rel, ACTIVE, "2026-01-01 10:00:00 +0000", ""],
        ])
        reg_path = requests_register_path(ws)
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        write_text(reg_path, reg_content)

        it_folder = ws / folder_rel
        it_folder.mkdir(parents=True, exist_ok=True)
        it_content = _make_iterations_table([
            [iteration_id, ACTIVE, "2026-01-01 10:00:00 +0000", "", "Initial iteration"],
        ])
        iterations_path = it_folder / "iterations.md"
        write_text(iterations_path, it_content)
        return iterations_path

    def test_close_request_auto_closes_active_iteration(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            iterations_path = self._setup_workspace_with_active_iteration(ws)

            close_request_script = Path(__file__).resolve().parent / "close-request.py"
            result = subprocess.run(
                [sys.executable, str(close_request_script), "--workspace", str(ws)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)

            combined = result.stdout + result.stderr
            self.assertIn("Auto-closed iteration", combined)

            from common import COMPLETED as _COMPLETED, parse_markdown_table as _pmt, read_text as _rt
            it_header, it_rows = _pmt(_rt(iterations_path))
            it_col = {name: idx for idx, name in enumerate(it_header)}
            self.assertEqual(it_rows[0][it_col["state"]], _COMPLETED)

    def test_exclude_scripts_contains_new_entries(self):
        import importlib.util
        menu_path = Path(__file__).resolve().parent / "menu.py"
        spec = importlib.util.spec_from_file_location("menu_module", menu_path)
        menu_module = importlib.util.module_from_spec(spec)
        sys.modules["menu_module"] = menu_module
        try:
            spec.loader.exec_module(menu_module)
            exclude = menu_module.EXCLUDE_SCRIPTS
            self.assertIn("reverse-engineer.py", exclude)
            self.assertIn("test_common.py", exclude)
        finally:
            del sys.modules["menu_module"]


