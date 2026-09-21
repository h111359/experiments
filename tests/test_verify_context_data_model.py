"""
test_verify_context_data_model.py: Tests for the managed data-model validator.
Part of the AIB test suite for request R-20260718-0809.
Responsibilities: cover empty/model states, identity, sections, entities, relations,
formatting, missing files, and workspace path safety.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = WORKSPACE_ROOT / ".aib_brain" / "tools" / "verify-context-data-model.py"
RELATIVE_PATH = ".aib_memory/context-data-model.md"
EMPTY_MODEL = "# Context Data Model\n\nNo data models are currently documented.\n"
VALID_MODEL = """\
# Context Data Model

## Customer Domain

### Type

logical

### Location

N/A - conceptual model only

### Description

Defines customer identity and order relationships.

### Entities

#### Customer

- Name: Customer ID
  Type: Integer
  Constraints: Key, Not Null

#### Order

- Name: Order ID
  Type: Integer
  Constraints: Key
- Name: Customer ID
  Type: Integer
  Constraints: Foreign Key(Customer.Customer ID)

### Relations

#### Customer Orders

- Left Side Entity: Order
- Left Side Attribute: Customer ID
- Right Side Entity: Customer
- Right Side Attribute: Customer ID
- Relationship Cardinality: M:1

### Other Objects

#### Customer Count

- Name: Customer Count
- Type: Measure
- Description: Counts customers in the model.
"""


def _run(tmp_path: Path, content: str | None, path: str = RELATIVE_PATH) -> subprocess.CompletedProcess:
    """Write optional content and run the validator against a temporary workspace."""
    if content is not None:
        target = tmp_path / RELATIVE_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--workspace", str(tmp_path), "--path", path],
        capture_output=True,
        text=True,
    )


class TestValidDataModelDocuments:
    """Canonical empty and populated documents pass every check."""

    @pytest.mark.parametrize("content", [EMPTY_MODEL, VALID_MODEL])
    def test_valid_documents_pass(self, tmp_path: Path, content: str) -> None:
        """Both convention branches report 8/8 checks passed."""
        result = _run(tmp_path, content)
        assert result.returncode == 0, result.stdout
        assert "Results: 8/8 checks passed." in result.stdout


class TestDataModelStateAndIdentity:
    """Empty-state exclusivity and composite identity are enforced."""

    def test_mixed_empty_and_model_state_fails(self, tmp_path: Path) -> None:
        """The empty notice cannot coexist with a model H2."""
        content = EMPTY_MODEL + VALID_MODEL.split("# Context Data Model\n", 1)[1]
        result = _run(tmp_path, content)
        assert result.returncode == 1
        assert "[FAIL] check_empty_state_exclusive" in result.stdout

    def test_duplicate_identity_fails(self, tmp_path: Path) -> None:
        """Same business name and Location cannot appear twice."""
        model_body = VALID_MODEL.split("## Customer Domain", 1)[1]
        content = VALID_MODEL + "\n## Customer Domain" + model_body
        result = _run(tmp_path, content)
        assert result.returncode == 1
        assert "[FAIL] check_model_identity_and_order" in result.stdout


class TestDataModelStructure:
    """Required model, entity, relation, and object fields are enforced."""

    @pytest.mark.parametrize(
        ("old", "new", "check_name"),
        [
            ("### Description", "### Notes", "check_heading_hierarchy"),
            ("logical", "conceptual", "check_required_model_sections"),
            ("  Type: Integer\n  Constraints: Key, Not Null", "  Constraints: Key, Not Null", "check_entities_and_attributes"),
            ("Relationship Cardinality: M:1", "Relationship Cardinality: 1:M", "check_relations_and_objects"),
            ("- Description: Counts customers in the model.", "", "check_relations_and_objects"),
        ],
    )
    def test_invalid_model_content_fails(
        self, tmp_path: Path, old: str, new: str, check_name: str
    ) -> None:
        """Each malformed construct fails its responsible check."""
        result = _run(tmp_path, VALID_MODEL.replace(old, new, 1))
        assert result.returncode == 1, result.stdout
        assert f"[FAIL] {check_name}" in result.stdout

    def test_prohibited_html_fails(self, tmp_path: Path) -> None:
        """HTML is rejected by the formatting check."""
        result = _run(tmp_path, VALID_MODEL.replace("Counts customers", "<b>Counts</b> customers"))
        assert result.returncode == 1
        assert "[FAIL] check_formatting_and_duplicates" in result.stdout


class TestDataModelFileSafety:
    """Unreadable and out-of-workspace targets fail safely."""

    def test_missing_file_fails(self, tmp_path: Path) -> None:
        """A missing extension reports failure and non-zero exit."""
        result = _run(tmp_path, None)
        assert result.returncode == 1
        assert "[FAIL] check_file_readable_and_title" in result.stdout

    def test_workspace_escape_fails(self, tmp_path: Path) -> None:
        """Parent traversal outside the workspace is rejected."""
        result = _run(tmp_path, None, "../outside.md")
        assert result.returncode == 1
        assert "escapes the workspace root" in result.stdout
