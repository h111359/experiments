"""
test_quit_option.py: Tests for the restored quit option in menu.py.
Part of request R-20260417-1534 (Add quit option to menu).
Responsibilities: T1 — QUIT key returns None; T2 — DIGIT:0 returns None; T3 — render shows 0) Quit.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".aib_brain" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import menu
from menu import MenuState


# ---------------------------------------------------------------------------
# T1 — QUIT key causes choose_action to return None
# ---------------------------------------------------------------------------

class TestQuitKeyReturnsNone:
    """T1: Pressing q/Q (QUIT) must cause choose_action() to return None."""

    def test_quit_key_returns_none(self, tmp_path: Path):
        """get_key returning 'QUIT' must make choose_action return None."""
        tools_dir = TOOLS_DIR

        with patch("menu.resolve_menu_state", return_value=MenuState(None, None, None)), \
             patch("menu.build_script_actions", return_value=[]), \
             patch("menu.render_menu"), \
             patch("menu.get_key", return_value="QUIT"):
            result = menu.choose_action(tools_dir, tmp_path)

        assert result is None, f"Expected None on QUIT, got {result!r}"


# ---------------------------------------------------------------------------
# T2 — DIGIT:0 key causes choose_action to return None
# ---------------------------------------------------------------------------

class TestDigit0ReturnsNone:
    """T2: Pressing 0 (DIGIT:0) must cause choose_action() to return None."""

    def test_digit0_returns_none(self, tmp_path: Path):
        """get_key returning 'DIGIT:0' must make choose_action return None."""
        tools_dir = TOOLS_DIR

        with patch("menu.resolve_menu_state", return_value=MenuState(None, None, None)), \
             patch("menu.build_script_actions", return_value=[]), \
             patch("menu.render_menu"), \
             patch("menu.get_key", return_value="DIGIT:0"):
            result = menu.choose_action(tools_dir, tmp_path)

        assert result is None, f"Expected None on DIGIT:0, got {result!r}"


# ---------------------------------------------------------------------------
# T3 — render_menu output contains '0) Quit'
# ---------------------------------------------------------------------------

class TestRenderMenuShowsQuit:
    """T3: render_menu() must write a line containing '0) Quit' to stdout."""

    def test_render_menu_contains_quit_line(self):
        """The rendered menu buffer must include the fixed 0) Quit footer."""
        state = MenuState(None, None, None)
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            menu.render_menu(state, [], 0)
        output = buf.getvalue()
        assert "0) Quit" in output, (
            "render_menu() must include '0) Quit' in its output; "
            f"got: {repr(output)}"
        )
