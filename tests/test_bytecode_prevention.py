"""Validate bytecode prevention in launchers, prompts, and menu child tools.
Part of AIB request R-20260819-1437 automated coverage.
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

from menu import _CHILD_ENV, build_command


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
BRAIN_DIR = WORKSPACE_ROOT / ".aib_brain"
PROMPTS_DIR = BRAIN_DIR / "prompts"
WRITING_PROMPTS = (
    "aib-analyze.md",
    "aib-clarify.md",
    "aib-context-migration.md",
    "aib-create-request.md",
    "aib-execute.md",
    "aib-implement.md",
    "aib-input-from-context.md",
    "aib-modify.md",
    "aib-refresh-context-data-model.md",
    "aib-refresh-context.md",
    "aib-sync-spec.md",
    "aib-update-adr-requirements.md",
)
UNSAFE_AIB_COMMAND = re.compile(
    r"\bpython3?\s+(?!-B\b)(?=[^`\r\n]*\.aib_brain[\\/]+tools[\\/]+)"
)


def test_launchers_disable_bytecode_before_path_setup() -> None:
    """Windows and POSIX launchers must set the environment and invoke with -B."""
    batch = (BRAIN_DIR / "run.bat").read_text(encoding="utf-8")
    shell = (BRAIN_DIR / "run.sh").read_text(encoding="utf-8")

    assert batch.index("set PYTHONDONTWRITEBYTECODE=1") < batch.index("set SCRIPT_DIR=")
    assert 'python -B "%SCRIPT_DIR%tools\\menu.py"' in batch
    assert shell.index("export PYTHONDONTWRITEBYTECODE=1") < shell.index("SCRIPT_DIR=")
    assert 'python3 -B "$SCRIPT_DIR/tools/menu.py"' in shell


def test_every_prompt_prescribed_aib_python_command_uses_dash_b() -> None:
    """Writing prompts must contain no direct AIB tool command lacking -B."""
    for prompt_name in WRITING_PROMPTS:
        content = (PROMPTS_DIR / prompt_name).read_text(encoding="utf-8")
        assert UNSAFE_AIB_COMMAND.search(content) is None, prompt_name


def test_menu_builds_dash_b_commands_with_copied_environment(tmp_path: Path) -> None:
    """Menu action commands must use -B and a non-mutating child environment copy."""
    action = {"script": "sample.py", "parameters": []}
    command = build_command(sys.executable, tmp_path, action, {})

    assert command[:2] == [sys.executable, "-B"]
    assert _CHILD_ENV is not os.environ
    assert _CHILD_ENV["PYTHONDONTWRITEBYTECODE"] == "1"


def test_every_menu_subprocess_receives_the_bytecode_environment() -> None:
    """All menu Popen/run child sites must pass the shared child environment."""
    menu_path = BRAIN_DIR / "tools" / "menu.py"
    tree = ast.parse(menu_path.read_text(encoding="utf-8"))
    child_calls: list[ast.Call] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "subprocess":
            continue
        if node.func.attr in {"Popen", "run"}:
            child_calls.append(node)

    assert child_calls
    for call in child_calls:
        env_keywords = [keyword for keyword in call.keywords if keyword.arg == "env"]
        assert len(env_keywords) == 1
        assert isinstance(env_keywords[0].value, ast.Name)
        assert env_keywords[0].value.id == "_CHILD_ENV"
