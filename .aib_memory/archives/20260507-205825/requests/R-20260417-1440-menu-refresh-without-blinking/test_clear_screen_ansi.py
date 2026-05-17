"""
test_clear_screen_ansi.py: Tests for the blink-free clear_screen() implementation.
Part of request R-20260417-1440 (Menu refresh without blinking).
Responsibilities: T1 — assert os.system is not called; T2 — assert ANSI sequences written.
"""

from __future__ import annotations

import io
import sys
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Ensure menu module is importable from the tools directory.
# ---------------------------------------------------------------------------

import importlib
import os
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".aib_brain" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import menu


# ---------------------------------------------------------------------------
# T1 — clear_screen does NOT call os.system
# ---------------------------------------------------------------------------

class TestClearScreenNoSubprocess:
    """T1: clear_screen() must not spawn a subprocess via os.system."""

    def test_os_system_not_called(self):
        """Patch os.system and verify clear_screen() never invokes it."""
        with patch("os.system") as mock_sys, \
             patch("sys.stdout", new_callable=io.StringIO):
            menu.clear_screen()
        assert mock_sys.call_count == 0, (
            "clear_screen() must not call os.system(); "
            f"it was called {mock_sys.call_count} time(s)"
        )


# ---------------------------------------------------------------------------
# T2 — clear_screen writes ANSI escape sequences to stdout
# ---------------------------------------------------------------------------

class TestClearScreenAnsiOutput:
    """T2: clear_screen() must write ESC[H and ESC[J to stdout."""

    def test_ansi_cursor_home_written(self):
        """The cursor-home sequence ESC[H must be present in the captured output."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            menu.clear_screen()
        written = buf.getvalue()
        assert "\033[H" in written, (
            "clear_screen() must write the cursor-home ANSI sequence ESC[H; "
            f"got: {repr(written)}"
        )

    def test_ansi_erase_screen_written(self):
        """The erase-to-end-of-screen sequence ESC[J must be present in the captured output."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            menu.clear_screen()
        written = buf.getvalue()
        assert "\033[J" in written, (
            "clear_screen() must write the erase-screen ANSI sequence ESC[J; "
            f"got: {repr(written)}"
        )

    def test_both_ansi_sequences_present(self):
        """Both ESC[H and ESC[J must appear together in a single clear_screen() call."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            menu.clear_screen()
        written = buf.getvalue()
        assert "\033[H" in written and "\033[J" in written, (
            "clear_screen() must write both ESC[H and ESC[J; "
            f"got: {repr(written)}"
        )
