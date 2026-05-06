#!/usr/bin/env python3
"""Interactive launcher for AIB tool scripts."""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from common import ACTIVE, get_semver, parse_markdown_table, read_text

# Lifecycle scripts are excluded from dynamic discovery to prevent them from
# reappearing in the menu; they are managed by the AI prompts directly.
EXCLUDE_SCRIPTS = {
    "menu.py",
    "common.py",
    "initialize.py",
    "test_common.py",
    "create-iteration.py",
    "close-iteration.py",
    "create-request.py",
    "close-request.py",
    "reverse-engineer.py",
}

# Auto-refresh interval used by choose_action() when no key is pressed.
_REFRESH_TIMEOUT_S: float = 3.0

# Sentinel action that re-reads workspace state and re-renders the menu without
# executing any tool script.
_REFRESH_ACTION: dict[str, Any] = {
    "id": "refresh",
    "title": "Refresh",
    "description": "Re-read workspace state and refresh the menu.",
    "type": "refresh",
    "script": None,
    "parameters": [],
    "destructive": False,
}

# Conditional action for closing the active request; injected by
# filter_visible_actions only when state.has_active_request is True.
_CLOSE_REQUEST_ACTION: dict[str, Any] = {
    "id": "close",
    "title": "Close current request",
    "description": "Close the active request and mark it as Closed in the register.",
    "script": "close-request.py",
    "destructive": False,
    "parameters": [
        {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": ".", "prompt": "Workspace path", "hint": "Root folder containing .aib_brain"},
    ],
}



def _enable_ansi_windows() -> None:
    """Enable ANSI/VT escape sequence processing on Windows consoles.

    Uses the Windows Console API via ctypes to set ENABLE_VIRTUAL_TERMINAL_PROCESSING
    on the standard output handle. Must be called once at startup before any ANSI
    escape sequences are written to stdout. On non-Windows platforms this is a no-op.
    Failures (e.g., restricted ctypes access or legacy console) are silently ignored
    so the program continues with gracefully degraded terminal output.
    """
    if os.name != "nt":
        return
    try:
        import ctypes
        import ctypes.wintypes

        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        STD_OUTPUT_HANDLE = -11
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.wintypes.DWORD()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:  # noqa: BLE001
        # Graceful degradation: ANSI sequences may appear as literal text on
        # unsupported consoles; blink elimination goal is not met in that case.
        pass


def _sanitize_action_id(raw: str) -> str:
    """Return a filesystem-safe action identifier from *raw*."""
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in raw.lower()).strip("-")[:60]


def _make_log_path(action_id: str, workspace: Path | None = None) -> Path:
    """Return the log file path for an action execution.

    The ``workspace`` parameter is used as the base directory for the
    ``.aib_memory/logs/`` folder.  When *None*, the current working directory
    is used.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_id = _sanitize_action_id(action_id)
    log_dir = (workspace or Path.cwd()) / ".aib_memory" / "logs"
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
    """Clear the terminal using ANSI escape sequences to avoid blank-screen blink.

    Writes cursor-home (ESC[H) followed by erase-to-end-of-screen (ESC[J) directly
    to stdout, avoiding subprocess spawning and the associated blank-window flash.
    The function name and signature are preserved for backward compatibility.
    """
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


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
    active_request_title: str | None = None

    @property
    def has_active_request(self) -> bool:
        return bool(self.active_request_id)


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

    return MenuState(active_request_id, active_request_folder, active_request_title)


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

    All discovered ``.py`` files in ``tools_dir`` that are not in
    ``EXCLUDE_SCRIPTS`` are listed with a minimal workspace parameter.
    Lifecycle scripts (create-request, close-request) are excluded and
    managed by the AI prompts directly.
    """
    actions: list[dict[str, Any]] = []

    next_id = 1
    for script in discover_tool_scripts(tools_dir):
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
    """Return visible actions, appending close-request when an active request exists.

    Lifecycle scripts are fully excluded via EXCLUDE_SCRIPTS so there is
    nothing to conditionally hide from the dynamically discovered set.
    The close-request action is injected at the end of the list when
    state.has_active_request is True, disappearing automatically after
    the request is closed on the next menu refresh.
    """
    visible = list(actions)
    if state.has_active_request:
        # Append a copy so the module-level constant is not mutated.
        close_action = dict(_CLOSE_REQUEST_ACTION)
        close_action["id"] = str(len(visible) + 1)
        visible.append(close_action)
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


def get_key(timeout: float | None = None) -> str:
    """Read a single keypress from the terminal and return a normalised key name.

    Args:
        timeout: Maximum seconds to wait for a keypress. When ``None`` the
            function blocks until a key is pressed. When a float is supplied
            the function returns ``"TIMEOUT"`` if no key arrives within that
            many seconds.

    Returns:
        A normalised key name: ``"UP"``, ``"DOWN"``, ``"ENTER"``, ``"QUIT"``,
        ``"DIGIT:<n>"``, ``"TIMEOUT"`` (only when *timeout* is set and the
        deadline expires), or ``"OTHER"`` for any unrecognised key.
    """
    if os.name == "nt":
        import msvcrt

        if timeout is None:
            # Blocking: wait indefinitely for the next keypress.
            first = msvcrt.getwch()
        else:
            # Polling loop: check for available input every 50 ms until deadline.
            deadline = time.monotonic() + timeout
            while not msvcrt.kbhit():
                if time.monotonic() >= deadline:
                    return "TIMEOUT"
                time.sleep(0.05)
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

    if timeout is not None:
        # Check whether input is ready before entering raw mode; avoids blocking.
        import select

        readable, _, _ = select.select([sys.stdin], [], [], timeout)
        if not readable:
            return "TIMEOUT"

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


def print_prompt_reference() -> None:
    """Print copy-paste-ready prompt invocations for the three core AIB prompts."""
    print("")
    print("  ── AIB Prompts (copy-paste into your AI coding interface) ──")
    print("  Execute `.aib_brain/prompts/aib-analysis.md`")
    print("  Execute `.aib_brain/prompts/aib-implement.md`")
    print("  Execute `.aib_brain/prompts/aib-context.md`")
    print("")


def render_menu(
    state: MenuState,
    script_actions: list[dict[str, Any]],
    selected_index: int,
) -> None:
    """Render the interactive menu with active-request status and prompt reference.

    Accumulates the entire menu string into an in-memory buffer and flushes it to
    stdout in a single write, minimising the blank-window between clear and redraw.
    No print() or clear_screen() calls are made inside this function.
    """
    buf = io.StringIO()

    # Move cursor to top-left and erase to end of screen (blink-free clear).
    buf.write("\033[H\033[J")

    buf.write(ascii_banner() + "\n")

    req_id = state.active_request_id or "No active request"
    req_title = state.active_request_title
    if state.active_request_id and req_title:
        req_text = f"{req_id} — {req_title}"
    else:
        req_text = req_id
    buf.write(f"Active request: {req_text}\n")

    # Inline prompt reference block (previously delegated to print_prompt_reference()).
    buf.write("\n")
    buf.write("  ── AIB Prompts (copy-paste into your AI coding interface) ──\n")
    buf.write("  Execute `.aib_brain/prompts/aib-analysis.md`\n")
    buf.write("  Execute `.aib_brain/prompts/aib-implement.md`\n")
    buf.write("  Execute `.aib_brain/prompts/aib-context.md`\n")
    buf.write("\n")

    for idx, action in enumerate(script_actions, start=1):
        marker = ">" if idx - 1 == selected_index else " "
        number = str(idx)
        line = f"{marker} {number}) {action.get('title', 'Untitled action')}"
        description = str(action.get("description", "")).strip()
        if description:
            line += f" - {description}"
        buf.write(line + "\n")

    # Fixed quit footer — non-navigable; displayed below all numbered items.
    buf.write("  0) Quit\n")

    # Erase any stale content remaining below the rendered menu (handles menu shrinkage).
    buf.write("\033[J")

    sys.stdout.write(buf.getvalue())
    sys.stdout.flush()


def choose_action(tools_dir: Path, workspace: Path) -> dict[str, Any] | None:
    all_script_actions = build_script_actions(tools_dir)

    selected = 0

    while True:
        state = resolve_menu_state(workspace)
        script_actions = filter_visible_actions(all_script_actions, state) + [_REFRESH_ACTION]
        total_items = len(script_actions)
        render_menu(state, script_actions, selected)
        key = get_key(timeout=_REFRESH_TIMEOUT_S)

        if key == "TIMEOUT":
            # No keypress within the idle window; re-render to pick up state changes.
            continue
        if key == "QUIT":
            # q/Q pressed; signal the caller to exit the menu loop.
            return None
        if key == "DIGIT:0":
            # 0 pressed; same exit intent as q/Q.
            return None
        if key == "UP":
            selected = (selected - 1) % total_items
            continue
        if key == "DOWN":
            selected = (selected + 1) % total_items
            continue
        if key == "ENTER":
            if selected < len(script_actions):
                action = script_actions[selected]
                if action.get("type") == "refresh":
                    selected = 0
                    continue
                return action
        if key.startswith("DIGIT:"):
            digit = key.split(":", 1)[1]
            numeric = int(digit)
            if 1 <= numeric <= len(script_actions):
                action = script_actions[numeric - 1]
                if action.get("type") == "refresh":
                    selected = 0
                    continue
                return action


def check_version_compatibility(workspace: Path, python_exe: str, tools_dir: Path) -> bool:
    """Check whether .aib_brain/ and .aib_memory/ semver markers match.

    When a mismatch (or missing memory semver) is detected, an upgrade prompt
    is shown. The user can choose to upgrade or skip. If the user upgrades,
    ``initialize.py --upgrade`` is invoked and this function returns True so
    the caller continues to the normal menu without requiring a relaunch.
    When the upgrade fails, the function returns False so the caller exits.
    When the user skips, or when versions are in sync, the function returns True.

    Args:
        workspace: Resolved workspace root path.
        python_exe: Path to the Python interpreter.
        tools_dir: Path to the .aib_brain/tools/ directory.

    Returns:
        True when the caller should continue to the normal menu; False when
        the caller should exit (upgrade failed or user chose to exit).
    """
    brain_dir = workspace / ".aib_brain"
    memory_dir = workspace / ".aib_memory"

    brain_semver = get_semver(brain_dir)
    memory_semver = get_semver(memory_dir)

    # Unknown brain version: cannot compare; warn but do not block.
    if brain_semver is None:
        print("WARNING: No semver marker found in .aib_brain/; version check skipped.")
        return True

    # Versions match — no prompt needed.
    if brain_semver == memory_semver:
        return True

    # Display a version mismatch banner.
    brain_label = brain_semver
    memory_label = memory_semver or "unknown (no marker)"
    print("\n" + "=" * 60)
    print("  AIB VERSION MISMATCH DETECTED")
    print(f"  .aib_brain/  version : {brain_label}")
    print(f"  .aib_memory/ version : {memory_label}")
    print("=" * 60)
    print(
        "\n  Your .aib_memory/ was created with a different AIB version.\n"
        "  Upgrading will archive the current .aib_memory/ and re-seed\n"
        "  it from the new brain templates while preserving your curated\n"
        "  files (context.md, instructions.md, and optionally requests/).\n"
    )

    # Present options and loop until a valid choice is made.
    while True:
        print("  [1] Upgrade .aib_memory/ now  (recommended)")
        print("  [2] Skip for this session")
        choice = input("\n  Enter choice [1/2]: ").strip()
        if choice == "1":
            init_script = (tools_dir / "initialize.py").resolve()
            result = subprocess.run(
                [python_exe, str(init_script), "--workspace", str(workspace), "--upgrade"],
                # Inherit stdin/stdout so the upgrade output is visible.
                stdin=None,
                text=True,
            )
            if result.returncode != 0:
                print("\nERROR: Upgrade failed. Re-launch menu to try again.")
                return False
            else:
                print("\nUpgrade complete. Continuing to menu...")
                return True
        if choice == "2":
            print("  Skipping upgrade for this session.\n")
            return True
        print("  Invalid choice — please enter 1 or 2.")


def main() -> None:
    """Main entry point: parse arguments, ensure memory is initialized, then run the menu.

    Performs a version-compatibility check before showing the interactive menu.
    When .aib_brain/ and .aib_memory/ semver markers differ, the user is
    offered an upgrade option before the menu is shown.
    """
    args = parse_cli_args()
    workspace = Path(args.workspace).resolve()

    tools_dir = Path(__file__).resolve().parent
    python_exe = sys.executable

    ensure_memory_initialized_if_missing(workspace, python_exe, tools_dir)

    # Version-compatibility check: prompt for upgrade if semver markers differ.
    should_continue = check_version_compatibility(workspace, python_exe, tools_dir)
    if not should_continue:
        # Upgrade failed; exit so the user can retry after resolving the issue.
        return

    # Enable ANSI VT processing on Windows once before the first render.
    _enable_ansi_windows()

    try:
        while True:
            action = choose_action(tools_dir, workspace)
            if action is None:
                # None signals a quit intent (q/Q/0); exit the menu loop cleanly.
                break
            run_action(python_exe, tools_dir, action, str(workspace))
    except KeyboardInterrupt:
        # Ctrl+C pressed during menu navigation or key polling; exit cleanly.
        sys.stdout.write("\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
