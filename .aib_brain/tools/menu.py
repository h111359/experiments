#!/usr/bin/env python3
"""Interactive launcher for AIB tool scripts."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from common import ACTIVE, parse_markdown_table, read_text

EXCLUDE_SCRIPTS = {"menu.py", "common.py", "initialize.py", "reverse-engineer.py", "test_common.py"}

SCRIPT_CREATE_REQUEST = "create-request.py"
SCRIPT_CLOSE_REQUEST = "close-request.py"
SCRIPT_CREATE_ITERATION = "create-iteration.py"
SCRIPT_CLOSE_ITERATION = "close-iteration.py"



def _sanitize_action_id(raw: str) -> str:
    """Return a filesystem-safe action identifier from *raw*."""
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in raw.lower()).strip("-")[:60]


def _make_log_path(action_id: str, workspace: Path | None = None) -> Path:
    """Return the log file path for an action execution.

    The ``workspace`` parameter is used as the base directory for the ``logs/``
    folder.  When *None*, the current working directory is used.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_id = _sanitize_action_id(action_id)
    log_dir = (workspace or Path.cwd()) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"aib-action-{ts}-{safe_id}.log"


def _stream_pipe(pipe, dest, log_file, prefix, lock):
    """Read *pipe* line-by-line, writing each line to *dest* and *log_file*."""
    try:
        for raw_line in iter(pipe.readline, ""):
            line = raw_line.rstrip("\n").rstrip("\r")
            with lock:
                dest.write(line + "\n")
                dest.flush()
                log_file.write(f"{prefix} {line}\n")
                log_file.flush()
    except Exception as exc:  # noqa: BLE001
        with lock:
            log_file.write(f"[THREAD-ERROR] {type(exc).__name__}: {exc}\n")
            log_file.flush()
    finally:
        pipe.close()


def _run_and_tee(
    command: list[str],
    log_path: Path,
    title: str,
    inherit_stdin: bool = False,
) -> int:
    """Run *command* while streaming stdout/stderr to terminal and *log_path*.

    Returns the subprocess exit code.
    """
    lock = threading.Lock()
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"[START] {datetime.now().isoformat()} — {title}\n")
        log_file.write(f"[CMD] {' '.join(command)}\n")
        log_file.flush()

        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=None if inherit_stdin else subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        stdout_thread = threading.Thread(
            target=_stream_pipe,
            args=(proc.stdout, sys.stdout, log_file, "[OUT]", lock),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_stream_pipe,
            args=(proc.stderr, sys.stderr, log_file, "[ERR]", lock),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        proc.wait()
        stdout_thread.join()
        stderr_thread.join()

        log_file.write(f"[EXIT] {proc.returncode}\n")
        log_file.flush()

    return proc.returncode


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def ascii_banner() -> str:
    return "\n".join(
        [
            r"   ___    ___    ____   _   _   ___   _      ____    _____   ____    ",
            r"  / _ \  |_ _|  | __ ) | | | | |_ _| | |    |  _ \  | ____| |  _ \   ",
            r" / /_\ \  | |   |  _ \ | |_| |  | |  | |__  | |_| | |  _|   | |_) |  ",
            r"/_/   \_\|___|  |____/  \___/  |___| |____| |____/  |_____| |_| \_\  ",
            "",
        ]
    )


@dataclass(frozen=True)
class MenuState:
    active_request_id: str | None
    active_request_folder: str | None
    active_iteration_id: str | None
    active_request_title: str | None = None

    @property
    def has_active_request(self) -> bool:
        return bool(self.active_request_id)

    @property
    def has_active_iteration(self) -> bool:
        return bool(self.active_iteration_id)


def _safe_table(path: Path) -> tuple[list[str], list[list[str]]]:
    if not path.exists():
        return [], []
    header, rows = parse_markdown_table(read_text(path))
    return header, rows


def resolve_menu_state(workspace: Path) -> MenuState:
    register_path = workspace / ".aib_memory" / "requests_register.md"
    header, rows = _safe_table(register_path)
    if not header or not rows:
        return MenuState(None, None, None)

    col = {name: idx for idx, name in enumerate(header)}
    required_cols = {"request_id", "folder", "state"}
    if not required_cols.issubset(col.keys()):
        return MenuState(None, None, None)

    active_rows = [r for r in rows if r[col["state"]] == ACTIVE]
    if len(active_rows) != 1:
        return MenuState(None, None, None)

    active_request_id = active_rows[0][col["request_id"]].strip() or None
    active_request_folder = active_rows[0][col["folder"]].strip() or None
    active_request_title = active_rows[0][col["title"]].strip() if "title" in col else None
    if not active_request_id or not active_request_folder:
        return MenuState(None, None, None)

    iterations_path = workspace / Path(active_request_folder) / "iterations.md"
    it_header, it_rows = _safe_table(iterations_path)
    if not it_header or not it_rows:
        return MenuState(active_request_id, active_request_folder, None, active_request_title)

    it_col = {name: idx for idx, name in enumerate(it_header)}
    if "iteration_id" not in it_col or "state" not in it_col:
        return MenuState(active_request_id, active_request_folder, None, active_request_title)

    active_iterations = [r for r in it_rows if r[it_col["state"]] == ACTIVE]
    if len(active_iterations) != 1:
        return MenuState(active_request_id, active_request_folder, None, active_request_title)

    iteration_id = active_iterations[0][it_col["iteration_id"]].strip() or None
    return MenuState(active_request_id, active_request_folder, iteration_id, active_request_title)


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AIB interactive command menu")
    parser.add_argument("--workspace", default=".", help="Workspace root path")
    return parser.parse_args()


def discover_tool_scripts(tools_dir: Path) -> list[str]:
    scripts: list[str] = []
    for path in sorted(tools_dir.glob("*.py")):
        if path.name in EXCLUDE_SCRIPTS:
            continue
        scripts.append(path.name)
    return scripts


def build_script_actions(tools_dir: Path) -> list[dict[str, Any]]:
    """Build the full list of script actions dynamically.

    The four core lifecycle scripts always appear first with their full
    parameter definitions.  Any additional ``.py`` files discovered in
    ``tools_dir`` are appended with a minimal workspace parameter.
    """
    actions: list[dict[str, Any]] = [
        {
            "id": "1",
            "title": "Create request",
            "description": "Create a new active request with initial iteration",
            "script": SCRIPT_CREATE_REQUEST,
            "destructive": True,
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": ".", "prompt": "Workspace path", "hint": "Root folder containing .aib_brain"},
                {"name": "title", "flag": "--title", "type": "string", "required": True, "prompt": "Request title", "hint": "Human-friendly title of the request"},
                {"name": "request_id", "flag": "--request-id", "type": "string", "required": False, "prompt": "Request ID (optional)", "hint": "Leave blank for auto-generated ID"},
                {"name": "summary", "flag": "--summary", "type": "string", "required": False, "prompt": "Initial summary (optional)", "hint": "Shown in iterations.md row 01"},
            ],
        },
        {
            "id": "2",
            "title": "Close request",
            "description": "Close active request or explicit request ID",
            "script": SCRIPT_CLOSE_REQUEST,
            "destructive": True,
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": ".", "prompt": "Workspace path", "hint": "Root folder containing .aib_brain"},
                {"name": "request_id", "flag": "--request-id", "type": "string", "required": False, "prompt": "Request ID (optional)", "hint": "Leave blank to close the single active request"},
            ],
        },
        {
            "id": "3",
            "title": "Create iteration",
            "description": "Create next active iteration for a request",
            "script": SCRIPT_CREATE_ITERATION,
            "destructive": True,
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": ".", "prompt": "Workspace path", "hint": "Root folder containing .aib_brain"},
                {"name": "request_id", "flag": "--request-id", "type": "string", "required": False, "prompt": "Request ID (optional)", "hint": "Leave blank to use active request"},
                {"name": "summary", "flag": "--summary", "type": "string", "required": False, "prompt": "Iteration summary (optional)", "hint": "Defaults to Follow-up iteration"},
            ],
        },
        {
            "id": "4",
            "title": "Close iteration",
            "description": "Close active iteration or explicit iteration ID",
            "script": SCRIPT_CLOSE_ITERATION,
            "destructive": True,
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": ".", "prompt": "Workspace path", "hint": "Root folder containing .aib_brain"},
                {"name": "request_id", "flag": "--request-id", "type": "string", "required": False, "prompt": "Request ID (optional)", "hint": "Leave blank to use active request"},
                {"name": "iteration_id", "flag": "--iteration-id", "type": "string", "required": False, "prompt": "Iteration ID (optional)", "hint": "Two digits, e.g. 01; blank closes active iteration"},
            ],
        },
    ]

    known_scripts = {str(a["script"]) for a in actions}
    next_id = len(actions) + 1
    for script in discover_tool_scripts(tools_dir):
        if script in known_scripts:
            continue
        stem = Path(script).stem
        title = " ".join(part.capitalize() for part in stem.split("-"))
        actions.append(
            {
                "id": str(next_id),
                "title": title,
                "description": "Auto-discovered tool script.",
                "script": script,
                "destructive": False,
                "parameters": [
                    {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": ".", "prompt": "Workspace path", "hint": "Root folder containing .aib_brain"},
                ],
            }
        )
        next_id += 1

    # Renumber IDs sequentially so numeric keyboard shortcuts are deterministic.
    for idx, action in enumerate(actions, start=1):
        action["id"] = str(idx)

    return actions


def filter_visible_actions(actions: list[dict[str, Any]], state: MenuState) -> list[dict[str, Any]]:
    visible: list[dict[str, Any]] = []
    for action in actions:
        script = str(action.get("script", "")).strip()

        if script == SCRIPT_CREATE_REQUEST:
            if not state.has_active_request:
                visible.append(action)
            continue

        if script == SCRIPT_CLOSE_REQUEST:
            if state.has_active_request:
                visible.append(action)
            continue

        if script == SCRIPT_CREATE_ITERATION:
            if state.has_active_request and not state.has_active_iteration:
                visible.append(action)
            continue

        if script == SCRIPT_CLOSE_ITERATION:
            if state.has_active_request and state.has_active_iteration:
                visible.append(action)
            continue

        visible.append(action)

    return visible


def ensure_memory_initialized_if_missing(workspace: Path, python_exe: str, tools_dir: Path) -> None:
    memory_root = workspace / ".aib_memory"
    if memory_root.exists():
        return

    init_script = (tools_dir / "initialize.py").resolve()
    result = subprocess.run(
        [python_exe, str(init_script), "--workspace", str(workspace)],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        summary = (stderr or stdout).splitlines()[0] if (stderr or stdout) else "Initialization failed"
        raise SystemExit(f"ERROR: Auto-initialization failed: {summary}")


def get_key() -> str:
    if os.name == "nt":
        import msvcrt

        first = msvcrt.getwch()
        if first in ("\x00", "\xe0"):
            second = msvcrt.getwch()
            if second == "H":
                return "UP"
            if second == "P":
                return "DOWN"
            return "OTHER"
        if first in ("\r", "\n"):
            return "ENTER"
        if first in ("q", "Q"):
            return "QUIT"
        if first.isdigit():
            return f"DIGIT:{first}"
        return "OTHER"

    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            if ch2 == "[" and ch3 == "A":
                return "UP"
            if ch2 == "[" and ch3 == "B":
                return "DOWN"
            return "OTHER"
        if ch1 in ("\r", "\n"):
            return "ENTER"
        if ch1 in ("q", "Q"):
            return "QUIT"
        if ch1.isdigit():
            return f"DIGIT:{ch1}"
        return "OTHER"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def prompt_yes_no(question: str, default_yes: bool = False) -> bool:
    suffix = "[Y/n]" if default_yes else "[y/N]"
    while True:
        answer = input(f"{question} {suffix}: ").strip().lower()
        if not answer:
            return default_yes
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")


def validate_param(raw_value: str, schema: dict[str, Any]) -> tuple[bool, str]:
    param_type = str(schema.get("type", "string")).lower()
    required = bool(schema.get("required", False))

    value = raw_value.strip()
    if required and not value:
        return False, "This field is required."

    if not value:
        return True, ""

    if param_type == "int":
        try:
            int(value)
        except ValueError:
            return False, "Expected an integer value."

    if param_type == "choice":
        choices = [str(c) for c in schema.get("choices", [])]
        if choices and value not in choices:
            return False, f"Expected one of: {', '.join(choices)}"

    return True, ""


def collect_parameters(action: dict[str, Any], workspace_default: str) -> dict[str, str]:
    print("\nParameter input")
    print("---------------")
    values: dict[str, str] = {}

    for param in action.get("parameters", []):
        name = str(param.get("name", "")).strip()
        if not name:
            continue

        prompt = str(param.get("prompt", name))
        hint = str(param.get("hint", "")).strip()
        required = bool(param.get("required", False))

        default_value = param.get("default")
        if name == "workspace" and (default_value is None or str(default_value).strip() == "."):
            default_value = workspace_default

        if name == "workspace":
            values[name] = str(default_value) if default_value not in (None, "") else workspace_default
            continue

        if name in {"request_id", "iteration_id"} and not required:
            if default_value not in (None, ""):
                values[name] = str(default_value)
            continue

        while True:
            label = prompt
            if default_value not in (None, ""):
                label += f" [{default_value}]"
            label += ": "

            if hint:
                print(f"Hint: {hint}")
            raw = input(label).strip()
            value = raw if raw else ("" if default_value is None else str(default_value))

            ok, reason = validate_param(value, param)
            if not ok:
                print(f"Invalid value: {reason}")
                continue

            if value:
                values[name] = value
            elif required:
                print("Invalid value: This field is required.")
                continue
            break

    return values


def build_command(python_exe: str, tools_dir: Path, action: dict[str, Any], values: dict[str, str]) -> list[str]:
    script_name = str(action.get("script", "")).strip()
    command = [python_exe, str((tools_dir / script_name).resolve())]

    for param in action.get("parameters", []):
        name = str(param.get("name", "")).strip()
        flag = str(param.get("flag", "")).strip()
        if not name or not flag:
            continue

        if name not in values:
            continue

        command.extend([flag, values[name]])

    return command


def run_action(python_exe: str, tools_dir: Path, action: dict[str, Any], workspace_default: str) -> None:
    clear_screen()
    title = str(action.get("title", action.get("script", "Action")))
    print(ascii_banner())
    print(f"Selected: {title}")
    print(str(action.get("description", "")))

    values = collect_parameters(action, workspace_default)

    command = build_command(python_exe, tools_dir, action, values)

    workspace = Path(workspace_default)
    log_path = _make_log_path(action.get("script", title), workspace)

    print(f"\n\u25b6 Running {title}... (output appears below)\n")

    exit_code = _run_and_tee(command, log_path, title, inherit_stdin=False)

    if exit_code == 0:
        print(f"\nStatus: Success")
    else:
        print(f"\nStatus: Failed (exit code {exit_code})")
    print(f"Log: {log_path}")
    input("Press Enter to return to menu...")


def render_menu(
    state: MenuState,
    script_actions: list[dict[str, Any]],
    selected_index: int,
) -> None:
    clear_screen()
    print(ascii_banner())

    req_id = state.active_request_id or "No active request"
    req_title = state.active_request_title
    if state.active_request_id and req_title:
        req_text = f"{req_id} — {req_title}"
    else:
        req_text = req_id
    iter_text = state.active_iteration_id or "No active iteration"
    print(f"Active request: {req_text}")
    print(f"Active iteration: {iter_text}")
    print("")

    for idx, action in enumerate(script_actions, start=1):
        marker = ">" if idx - 1 == selected_index else " "
        number = str(idx)
        line = f"{marker} {number}) {action.get('title', 'Untitled action')}"
        description = str(action.get("description", "")).strip()
        if description:
            line += f" - {description}"
        print(line)

    print("  0) Exit")


def choose_action(tools_dir: Path, workspace: Path) -> dict[str, Any] | None:
    all_script_actions = build_script_actions(tools_dir)

    selected = 0

    while True:
        state = resolve_menu_state(workspace)
        script_actions = filter_visible_actions(all_script_actions, state)
        total_items = len(script_actions)
        if total_items == 0:
            raise SystemExit("ERROR: No actions available")
        render_menu(state, script_actions, selected)
        key = get_key()

        if key == "UP":
            selected = (selected - 1) % total_items
            continue
        if key == "DOWN":
            selected = (selected + 1) % total_items
            continue
        if key == "ENTER":
            if selected < len(script_actions):
                return script_actions[selected]
        if key == "QUIT":
            return None
        if key.startswith("DIGIT:"):
            digit = key.split(":", 1)[1]
            if digit == "0":
                return None
            numeric = int(digit)
            if 1 <= numeric <= len(script_actions):
                return script_actions[numeric - 1]


def main() -> None:
    args = parse_cli_args()
    workspace = Path(args.workspace).resolve()

    tools_dir = Path(__file__).resolve().parent
    python_exe = sys.executable

    ensure_memory_initialized_if_missing(workspace, python_exe, tools_dir)

    while True:
        action = choose_action(tools_dir, workspace)
        if action is None:
            clear_screen()
            print("Goodbye from AI Builder menu.")
            return
        run_action(python_exe, tools_dir, action, str(workspace))


if __name__ == "__main__":
    main()
