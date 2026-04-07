"""Shared pytest fixtures and path configuration for the AIB test suite."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Import-path configuration – must run before any AIB module import
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"
TEMPLATES_DIR = WORKSPACE_ROOT / ".aib_brain" / "templates"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


# ---------------------------------------------------------------------------
# Minimal AIB workspace builder
# ---------------------------------------------------------------------------

REGISTER_CONTENT = (
    "# Requests Register\n\n"
    "| request_id | title | folder | state | created_at | closed_at |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)


def _seed_workspace(root: Path) -> None:
    """Create the minimum workspace structure required by AIB tool scripts."""
    (root / ".aib_brain" / "templates").mkdir(parents=True, exist_ok=True)
    (root / ".aib_memory" / "requests").mkdir(parents=True, exist_ok=True)
    (root / ".aib_memory" / "docs").mkdir(parents=True, exist_ok=True)

    # Copy real templates so scripts can load them
    for tmpl in TEMPLATES_DIR.glob("*.md"):
        shutil.copy(tmpl, root / ".aib_brain" / "templates" / tmpl.name)

    # Seed empty requests register
    register = root / ".aib_memory" / "requests_register.md"
    register.write_text(REGISTER_CONTENT, encoding="utf-8")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def workspace_dir():
    """Yield a temp workspace Path with minimal AIB structure; clean up after."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_workspace(root)
        yield root


@pytest.fixture()
def brain_dir(workspace_dir: Path) -> Path:
    return workspace_dir / ".aib_brain"


@pytest.fixture()
def tools_dir() -> Path:
    return TOOLS_DIR


@pytest.fixture()
def mock_get_key():
    """Fixture that patches menu.get_key; call mock_get_key.side_effect to set returns."""
    with patch("menu.get_key") as m:
        yield m
