# Request

## Goal

Fix the `UnicodeDecodeError` in `.aib_brain/tools/menu.py` that crashes the AIB Command Menu's streaming threads (`_stream_pipe`) when the GitHub Copilot CLI subprocess emits non-ASCII UTF-8 characters on Windows. Additionally, fix the logging gap that prevents thread exceptions from being captured in the per-action execution log file (`logs/aib-action-*.log`).

## Background

The AIB Command Menu (CMP-ART-0006, `menu.py`) uses `subprocess.Popen` with `text=True` in the `_run_and_tee` function to spawn Copilot CLI and tee its output to the terminal and a log file. On Windows, `text=True` without an explicit `encoding` parameter defaults to the system code page `cp1252`. When Copilot CLI outputs UTF-8 multi-byte characters (e.g., byte `0x8f`), `cp1252` cannot decode them, causing `UnicodeDecodeError` in the `_stream_pipe` threading target (menu.py line ~104). The exception kills the streaming thread. Because `_stream_pipe` has a `try/finally` block that only closes the pipe but does not catch exceptions, the error is never recorded in the log file.

Evidence from a separate test workspace (`ai-builder-test-07`):
- Terminal output showed `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f in position 2: character maps to <undefined>` in `Thread-7 (_stream_pipe)`.
- The per-action log file contained only `[START]` and `[CMD]` markers with no `[OUT]`, `[ERR]`, or error diagnostic information.

Root cause: `subprocess.Popen(..., text=True)` at menu.py line ~130 lacks `encoding="utf-8"`.
Secondary cause: `_stream_pipe` at menu.py line ~99 has no exception handler to log thread failures.

## Scope

- Modify `_run_and_tee` in `.aib_brain/tools/menu.py`: add `encoding="utf-8"` and `errors="replace"` to the `subprocess.Popen` call.
- Modify `_stream_pipe` in `.aib_brain/tools/menu.py`: add exception handling that catches exceptions, writes a `[THREAD-ERROR]` entry to the log file (thread-safe via the existing `lock`), and terminates the thread gracefully.
- Add automated tests in `tests/test_menu.py`: (a) verify subprocess output containing non-ASCII UTF-8 characters is streamed and logged correctly; (b) verify a simulated thread exception is captured in the log file under a `[THREAD-ERROR]` marker; (c) verify `[EXIT]` is written even when a streaming thread fails.
- Update OBS-01 (`REF-0021`) to document the `[THREAD-ERROR]` log marker in the event schema and taxonomy tables.
- Update CMP-01 (`REF-0007`, CMP-ART-0006) `edge_cases_and_validation` to note UTF-8 encoding enforcement with `errors="replace"` on Popen.

## Out of scope

- Changes to the GitHub Copilot CLI itself or its output encoding behavior.
- Changes to non-menu tool scripts (initialize.py, create-request.py, create-iteration.py, close-iteration.py, close-request.py, common.py).
- Changes to the Python standard library or threading module.
- Platform-specific encoding auto-detection or user-configurable encoding settings.
- Changes to release bookkeeping or CI workflows.

## Constraints

- Python 3.10+ compatibility must be maintained (NFR-004).
- All existing tests in `tests/test_menu.py` must continue to pass unchanged.
- The log file format change (new `[THREAD-ERROR]` marker) must be additive — existing `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, `[EXIT]` markers remain unchanged.
- The `_stream_pipe` exception handler must be thread-safe (acquire the existing `lock` before writing to `log_file`).

## Success criteria

- The AIB Command Menu successfully streams Copilot CLI output containing non-ASCII UTF-8 characters on Windows without raising `UnicodeDecodeError`.
- Thread exceptions in `_stream_pipe` are written to the per-action log file with a `[THREAD-ERROR]` marker containing the exception type and message.
- The `[EXIT]` marker is present in the log file even when one or both streaming threads encounter exceptions.
- All existing tests in `tests/test_menu.py` pass without modification.
- At least 2 new tests verify: (1) non-ASCII UTF-8 subprocess output is correctly streamed and logged; (2) thread exceptions are captured in the log under `[THREAD-ERROR]`.
- OBS-01 documents the `[THREAD-ERROR]` marker in the Log Event Schema and Taxonomy tables.
- CMP-01 CMP-ART-0006 `edge_cases_and_validation` notes `encoding="utf-8", errors="replace"` on Popen.
