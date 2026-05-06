# Implementation Log

Files taken into consideration:
- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/request.md`
- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/iterations.md`
- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/01-analysis.md`
- `.aib_memory/references.md`
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md`
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md`
- `.aib_brain/tools/menu.py`
- `tests/test_menu.py`

Append-only entries. Add a new section for every execution update.

## Implementation Log

### Entry 2026-04-03 18:55 — Iteration 01

#### Scope

Fix `UnicodeDecodeError` in `_stream_pipe` (`menu.py`) caused by `subprocess.Popen` defaulting to `cp1252` on Windows when the Copilot CLI emits non-ASCII UTF-8 bytes. Add exception handling in `_stream_pipe` so thread failures are captured as `[THREAD-ERROR]` entries in the per-action log file. Update OBS-01 and CMP-01 to reflect the new log marker and encoding enforcement. Add automated tests covering the two fixes (aligned with 01-analysis Impact Assessment).

#### Changes

- Modified `.aib_brain/tools/menu.py` `_run_and_tee`: added `encoding="utf-8"` and `errors="replace"` to the `subprocess.Popen` call to prevent `UnicodeDecodeError` on Windows when non-ASCII UTF-8 bytes are emitted by Copilot CLI.
- Modified `.aib_brain/tools/menu.py` `_stream_pipe`: added `except Exception as exc` handler that acquires the existing `lock` and writes `[THREAD-ERROR] <ExceptionType>: <message>` to the log file, then `finally` closes the pipe as before.
- Modified `tests/test_menu.py`: added three new tests in `TestRunAndTee`: `test_utf8_non_ascii_output_logged_correctly`, `test_thread_exception_captured_in_log`, `test_exit_marker_present_when_thread_fails`.
- Modified `.aib_memory/docs/04 Technology/Observability/OBS-01.md`: added `[THREAD-ERROR]` to Log Levels list, Log Event Schema table (new row), and Taxonomy & Categories table; added Change Control entry.
- Modified `.aib_memory/docs/04 Technology/Compute/CMP-01.md`: updated CMP-ART-0006 `edge_cases_and_validation` to note `encoding="utf-8", errors="replace"` on Popen and that streaming thread exceptions are caught and logged as `[THREAD-ERROR]`.

#### Tests

- Unit | `tests/test_menu.py::TestRunAndTee::test_utf8_non_ascii_output_logged_correctly` | spawns real subprocess writing UTF-8 multi-byte char (U+2192, bytes 0xE2 0x86 0x92 — 0x86 undefined in cp1252); asserts `[OUT] arrow →` and `[EXIT] 0` present in log | PASS
- Unit | `tests/test_menu.py::TestRunAndTee::test_thread_exception_captured_in_log` | calls `_stream_pipe` directly with a mock pipe that raises `UnicodeDecodeError`; asserts `[THREAD-ERROR]` and `UnicodeDecodeError` in log | PASS
- Unit | `tests/test_menu.py::TestRunAndTee::test_exit_marker_present_when_thread_fails` | patches `subprocess.Popen` to return a mock with pipes that raise `UnicodeDecodeError`; calls `_run_and_tee`; asserts both `[THREAD-ERROR]` and `[EXIT]` present in log | PASS
- Unit | All 51 pre-existing tests in `tests/test_menu.py` | unchanged; all pass | PASS (54 total, 0 failures)

#### Outcome

Success. Both root causes resolved: subprocess encoding is now UTF-8 with `errors="replace"` resilience, and streaming thread exceptions are captured in the log as `[THREAD-ERROR]` markers. The `[EXIT]` marker is always written after thread joins complete. All 54 tests pass. Documentation updated additively with no breaking changes to existing log format.

#### Evidence

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.0.1
collected 54 items
...
54 passed in 0.75s
```

#### Notes (Optional)

- Assumption A2 from the analysis was partially falsified: `errors="replace"` was added (not just `encoding="utf-8"`) to provide resilience against any malformed byte sequences, consistent with the request scope.
- The `[THREAD-ERROR]` marker is additive; existing `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, `[EXIT]` markers are unchanged.

