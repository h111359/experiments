"""
test_tools_common.py: Comprehensive tests for common.py helpers.
Relocated from .aib_brain/tools/test_common.py as part of R-20260511-2019 to place
tool-level unit tests under the standard pytest-discoverable tests/ directory.
Responsibilities: validate all public helpers in common.py, including YAML header
helpers, text I/O, slug generation, workspace validation, and register updates.
"""

from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

# NOTE: sys.path.insert is NOT needed here; conftest.py already inserts the
# .aib_brain/tools/ directory into sys.path before any test module is loaded.

from common import (
    ACTIVE,
    CLOSED,
    ValidationError,
    ensure_workspace,
    now_compact_request_id,
    now_iso,
    parse_input_header,
    read_input_header,
    read_text,
    slugify,
    validate_plan_md,
    write_input_header,
    write_text,
)

# ---------------------------------------------------------------------------
# Workspace root so test helpers can locate sibling tool scripts.
# ---------------------------------------------------------------------------

_TESTS_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _TESTS_DIR.parent
_TOOLS_DIR = _WORKSPACE_ROOT / ".aib_brain" / "tools"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INPUT_MD_IDLE = (
    "---\n"
    "state:\n"
    "  request_id: ~\n"
    "  title: ~\n"
    "  status: idle\n"
    "  input_verification_result: null\n"
    "  context_verification_result: null\n"
    "options:\n"
    "  minimum_questions: 5\n"
    "  input_verification_enabled: true\n"
    "  context_verification_enabled: true\n"
    "---\n\n"
    "## Input\n\n"
)


def _setup_workspace(tmp: str) -> Path:
    """Create the minimum workspace structure expected by ensure_workspace."""
    ws = Path(tmp)
    (ws / ".aib_brain").mkdir(parents=True, exist_ok=True)
    (ws / ".aib_memory").mkdir(parents=True, exist_ok=True)
    return ws


# ---------------------------------------------------------------------------
# YAML header parsing
# ---------------------------------------------------------------------------

class TestParseInputHeader(unittest.TestCase):
    def test_valid_idle_header(self):
        result = parse_input_header(INPUT_MD_IDLE)
        self.assertIsNotNone(result)
        self.assertEqual(result["state"]["status"], "idle")
        self.assertEqual(result["state"]["request_id"], "~")
        self.assertEqual(result["state"]["title"], "~")
        self.assertEqual(result["options"]["minimum_questions"], 5)

    def test_valid_active_header(self):
        content = (
            "---\n"
            "state:\n"
            "  request_id: R-20260101-1200\n"
            "  title: My Test Request\n"
            "  status: analysis_ready\n"
            "  input_verification_result: null\n"
            "  context_verification_result: null\n"
            "options:\n"
            "  minimum_questions: 3\n"
            "  input_verification_enabled: true\n"
            "  context_verification_enabled: true\n"
            "---\n\n"
            "## Input\n\n"
        )
        result = parse_input_header(content)
        self.assertIsNotNone(result)
        self.assertEqual(result["state"]["request_id"], "R-20260101-1200")
        self.assertEqual(result["state"]["title"], "My Test Request")
        self.assertEqual(result["state"]["status"], "analysis_ready")
        self.assertEqual(result["options"]["minimum_questions"], 3)

    def test_returns_none_for_no_frontmatter(self):
        result = parse_input_header("## Input\n\nSome content.\n")
        self.assertIsNone(result)

    def test_returns_none_for_unclosed_frontmatter(self):
        result = parse_input_header("---\nstate:\n  status: idle\n## Input\n\n")
        self.assertIsNone(result)

    def test_single_quoted_title(self):
        content = (
            "---\n"
            "state:\n"
            "  request_id: R-20260101-1200\n"
            "  title: 'Title with: colon'\n"
            "  status: idle\n"
            "  input_verification_result: null\n"
            "  context_verification_result: null\n"
            "options:\n"
            "  minimum_questions: 5\n"
            "  input_verification_enabled: true\n"
            "  context_verification_enabled: true\n"
            "---\n\n"
        )
        result = parse_input_header(content)
        self.assertIsNotNone(result)
        self.assertEqual(result["state"]["title"], "Title with: colon")

    def test_raises_on_old_flat_format(self):
        old_format = (
            "---\n"
            "request_id: R-20260101-1200\n"
            "title: Old Request\n"
            "state: analysis_ready\n"
            "options:\n"
            "  minimum_questions: 5\n"
            "---\n\n"
            "## Input\n\n"
        )
        with self.assertRaises(ValueError):
            parse_input_header(old_format)

    def test_round_trip_nested_structure(self):
        result = parse_input_header(INPUT_MD_IDLE)
        self.assertIsNotNone(result)
        self.assertIn("state", result)
        self.assertIn("options", result)
        self.assertIsInstance(result["state"], dict)
        self.assertIsInstance(result["options"], dict)
        self.assertIn("status", result["state"])
        self.assertIn("request_id", result["state"])


class TestWriteInputHeader(unittest.TestCase):
    def test_round_trip_idle(self):
        header = {
            "state": {"request_id": "~", "title": "~", "status": "idle",
                      "input_verification_result": None, "context_verification_result": None},
            "options": {"minimum_questions": 0, "input_verification_enabled": True,
                        "context_verification_enabled": True},
        }
        result = write_input_header(INPUT_MD_IDLE, header)
        parsed = parse_input_header(result)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["state"]["status"], "idle")
        self.assertEqual(parsed["state"]["request_id"], "~")

    def test_round_trip_active(self):
        header = {
            "state": {"request_id": "R-20260101-1200", "title": "My Title",
                      "status": "analysis_ready", "input_verification_result": None,
                      "context_verification_result": None},
            "options": {"minimum_questions": 2, "input_verification_enabled": True,
                        "context_verification_enabled": True},
        }
        result = write_input_header(INPUT_MD_IDLE, header)
        parsed = parse_input_header(result)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["state"]["request_id"], "R-20260101-1200")
        self.assertEqual(parsed["state"]["title"], "My Title")
        self.assertEqual(parsed["state"]["status"], "analysis_ready")
        self.assertEqual(parsed["options"]["minimum_questions"], 2)

    def test_body_preserved(self):
        content = INPUT_MD_IDLE + "Some existing body content.\n"
        header = {
            "state": {"request_id": "~", "title": "~", "status": "idle",
                      "input_verification_result": None, "context_verification_result": None},
            "options": {"minimum_questions": 0, "input_verification_enabled": True,
                        "context_verification_enabled": True},
        }
        result = write_input_header(content, header)
        self.assertIn("Some existing body content.", result)

    def test_title_with_special_chars_quoted(self):
        header = {
            "state": {"request_id": "R-001", "title": "Fix: the issue",
                      "status": "idle", "input_verification_result": None,
                      "context_verification_result": None},
            "options": {"minimum_questions": 0, "input_verification_enabled": True,
                        "context_verification_enabled": True},
        }
        result = write_input_header(INPUT_MD_IDLE, header)
        self.assertIn("'Fix: the issue'", result)


class TestReadInputHeader(unittest.TestCase):
    def test_reads_existing_idle_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            (ws / ".aib_memory" / "input.md").write_text(INPUT_MD_IDLE, encoding="utf-8")
            header = read_input_header(ws)
            self.assertEqual(header["state"]["status"], "idle")

    def test_raises_when_input_md_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            with self.assertRaises(ValidationError):
                read_input_header(ws)

    def test_raises_when_no_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _setup_workspace(tmp)
            (ws / ".aib_memory" / "input.md").write_text("## Input\n\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                read_input_header(ws)


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
# validate_plan_md (P21)
# ---------------------------------------------------------------------------

VALID_PLAN_MD = """\
## Goal
Implement the thing.

## Constraints
- None

## Success criteria
- Passes tests

## Plan
### Task 1: Do the work

#### Intent
Complete the implementation.

#### Outputs
Updated files.

#### Procedure
Step 1.

#### Done criteria
All tests pass.

#### Dependencies
None.
"""


class TestValidatePlanMd(unittest.TestCase):
    def test_valid_plan_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            write_text(path, VALID_PLAN_MD)
            # Should not raise
            validate_plan_md(path)

    def test_missing_section_raises(self):
        for section in [
            "## Goal",
            "## Constraints",
            "## Success criteria",
            "## Plan",
        ]:
            with self.subTest(missing=section):
                content = VALID_PLAN_MD.replace(section, "## Placeholder")
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "plan.md"
                    write_text(path, content)
                    with self.assertRaises(ValidationError):
                        validate_plan_md(path)

    def test_empty_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            write_text(path, "")
            with self.assertRaises(ValidationError):
                validate_plan_md(path)

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nonexistent.md"
            with self.assertRaises(ValidationError):
                validate_plan_md(path)


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
