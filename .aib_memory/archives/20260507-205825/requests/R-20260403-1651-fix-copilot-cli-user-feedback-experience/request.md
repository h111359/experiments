# Request

## Goal

Improve the AIB Command Menu (`menu.py`) so that when the DEVELOPER executes a script action or a prompt action (Copilot CLI invocation), the terminal displays subprocess output in real time, a persistent log file is written for every action execution, the subprocess can receive user keyboard input when the Copilot CLI prompts for it, and failures are reported with full context (exit code, stdout, stderr) without requiring a secondary opt-in prompt.

## Background

The AIB Command Menu (`.aib_brain/tools/menu.py`, component CMP-ART-0006) currently invokes both Python tool scripts and the Copilot CLI using `subprocess.run()` with `capture_output=True`. This causes:
- **Blank-screen problem**: The user sees no output while the subprocess runs. For long-running AI prompt actions this can last minutes with zero feedback.
- **Accidental keystroke risk**: Keystrokes entered during the silent wait are buffered and consumed by subsequent `input()` calls, potentially skipping result display or navigating the menu unintentionally.
- **Opaque failure reporting**: On non-zero exit code, only the first line of stderr/stdout is shown; full details require a follow-up `[y/N]` prompt.
- **No stdin passthrough**: The Copilot CLI cannot ask the user clarifying questions because stdin is not connected to the subprocess.
- **No persistent logging**: There is no file-based record of action executions. Once terminal output scrolls away, it is lost.

These issues are referenced in ARCH-01 (AIB Command Menu component), CMP-01 (CMP-ART-0006), and OBS-01 (currently a stub). The DEVELOPER persona (KNW-03) lists "manual documentation is error-prone" and "large diffs are hard to review" as pain points; missing execution logs exacerbate both.

## Scope

- Modify `run_prompt_action()` in `.aib_brain/tools/menu.py` to replace `subprocess.run(..., capture_output=True)` with a `subprocess.Popen()`-based tee pattern that streams stdout/stderr line-by-line to both the terminal and a timestamped log file, and inherits stdin for user input passthrough.
- Apply the same tee-pattern modification to `run_action()` in `.aib_brain/tools/menu.py` for Python script actions.
- Introduce a log-file helper (within `menu.py` or `common.py`) that creates per-action log files at `logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log` with timestamped start/output/exit entries.
- Display a clear "Running..." banner before subprocess start and a structured result summary (exit code, log file path) after subprocess exit.
- Update tests in `tests/test_menu.py` to cover real-time streaming, log file creation, stdin passthrough, and error-reporting scenarios.
- Update product documentation: ARCH-01, ARCH-06, CMP-01, OBS-01, RQT-02.

## Out of scope

- Modifications to the Copilot CLI binary or its installation/detection logic (`_detect_copilot_cli()`).
- GUI or web-based log viewer.
- Remote/cloud logging or telemetry.
- Modifications to GitHub Actions CI workflows or `scripts/release_bookkeeping.py`.
- Log rotation, automatic cleanup, or retention automation (deferred to a future request if needed).
- Changes to the menu's keyboard navigation (arrow keys, digit shortcuts, exit command).

## Constraints

- Python 3.10+ standard library only — no third-party packages.
- Cross-platform: must work on Windows (cmd.exe, PowerShell, Windows Terminal) and Unix (bash, zsh).
- Log files MUST NOT contain secrets, credentials, tokens, or sensitive PII.
- The Copilot CLI detection and gating logic in `menu.py` must remain unchanged.
- Existing menu behavior (action filtering, parameter collection, destructive-action confirmation) must be preserved.
- All changes must be covered by automated tests.

## Success criteria

1. When a prompt action is executed, the DEVELOPER sees copilot output appearing incrementally in the terminal within 2 seconds of the subprocess producing its first output line.
2. When a script action is executed, the DEVELOPER sees script stdout/stderr in real time in the terminal.
3. After every action execution (success or failure), a log file exists at `logs/aib-action-<timestamp>-<action-id>.log` containing timestamped start marker, all stdout/stderr lines, and the exit code.
4. When the Copilot CLI prompts for user input during a prompt action, the DEVELOPER can type a response and it is received by the subprocess.
5. On subprocess failure, the terminal displays the full exit code and output without requiring a secondary opt-in prompt.
6. All existing tests in `tests/test_menu.py` continue to pass, and new tests cover: (a) real-time output streaming, (b) log file creation and content, (c) stdin passthrough, (d) failure reporting.
7. Product documentation (ARCH-01, ARCH-06, CMP-01, OBS-01, RQT-02) is updated to reflect the new logging and interaction model.
