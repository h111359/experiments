## Overview

This iteration resolves two confirmed defects in `.aib_brain/tools/menu.py`:

1. **UnicodeDecodeError** — `subprocess.Popen` in `_run_and_tee` (line ~130) uses `text=True` without specifying `encoding`, defaulting to the Windows system code page (`cp1252`). When the GitHub Copilot CLI emits UTF-8 multi-byte characters, `cp1252` cannot decode them, raising `UnicodeDecodeError` in the `_stream_pipe` streaming thread, which kills the thread and corrupts the per-action log output.

2. **Silent thread failure** — `_stream_pipe` has a `try/finally` block that closes the pipe but no `except` block. Any exception in the thread is discarded; the per-action log contains only `[START]` and `[CMD]` markers.

The fix is to add `encoding="utf-8", errors="replace"` to the `Popen` call and wrap the `_stream_pipe` loop in an exception handler that writes a `[THREAD-ERROR]` entry to the log file. Automated tests and two product-doc updates (OBS-01, CMP-01) complete the iteration.

Linkage: request.md §Goal, §Scope, §Constraints; 01-analysis.md §Decision Points DP-1 and DP-2; 01-analysis.md §Disambiguation Questionnaire Q1–Q4.

## Scope of Work

**In Scope**
- Modify `_run_and_tee` in `.aib_brain/tools/menu.py`: add `encoding="utf-8"` and `errors="replace"` to the `subprocess.Popen` call.
- Modify `_stream_pipe` in `.aib_brain/tools/menu.py`: add `except Exception as exc` handler that acquires the existing `lock` and writes `[THREAD-ERROR] <ExceptionType>: <message>` to the log file.
- Add three new unit tests to `tests/test_menu.py` covering: (a) non-ASCII UTF-8 subprocess output streamed and logged correctly; (b) thread exception captured in log under `[THREAD-ERROR]`; (c) `[EXIT]` present even when a streaming thread fails.
- Update OBS-01 (`.aib_memory/docs/04 Technology/Observability/OBS-01.md`) to document the `[THREAD-ERROR]` marker in the Log Levels list, Log Event Schema, and Taxonomy & Categories table.
- Update CMP-01 (`.aib_memory/docs/04 Technology/Compute/CMP-01.md`): amend CMP-ART-0006 `edge_cases_and_validation` to note `encoding="utf-8", errors="replace"` on Popen and that streaming thread exceptions are caught and logged as `[THREAD-ERROR]`.

**Out of Scope**
- Changes to the GitHub Copilot CLI itself or its output encoding behavior.
- Changes to non-menu tool scripts (`initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `close-request.py`, `common.py`).
- Platform-specific encoding auto-detection or user-configurable encoding settings.
- Changes to CI workflows or release bookkeeping.
- Any changes to `.aib_brain/prompts/*.md` prompt content files.

**Assumptions**
- The GitHub Copilot CLI outputs UTF-8 encoded text on all platforms (01-analysis.md §Assumptions A1).
- The `log_file` handle remains open for the full lifetime of the streaming threads — it is opened in a `with` block in `_run_and_tee` that covers both thread `.start()` and `.join()` calls (01-analysis.md §Assumptions A3).
- Python 3.10+ is available (NFR-004 from request.md §Constraints).

**Constraints**
- Python 3.10+ compatibility must be maintained (NFR-004).
- All existing tests in `tests/test_menu.py` must continue to pass without modification.
- The `_stream_pipe` exception handler must be thread-safe — acquire the existing `lock` before writing to `log_file`.
- The log file format change (new `[THREAD-ERROR]` marker) must be additive; existing `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, `[EXIT]` markers remain unchanged.
- OBS-01 and CMP-01 have `edit_allowed = Y` per `.aib_memory/references.md`.

## Decision Gates

1) **Question:** Should `errors="replace"` be added alongside `encoding="utf-8"`, or should strict mode (`errors="strict"`) be used?
   **Chosen Answer / Value:** `errors="replace"` (Option B from 01-analysis.md §Decision Points DP-1)
   **Rationale:** The menu is a user-facing tool. Replacing an undecodable byte with U+FFFD `▒` is preferable to crashing the streaming thread. The replacement character is visually obvious in terminal and log output.
   **Evidence / Reference:** 01-analysis.md §Decision Points DP-1; request.md §Scope.
   **Impact if changed:** Reverting to strict mode would re-expose the crash risk for any future malformed byte sequences; the fix's resilience guarantee would be lost.

2) **Question:** Should thread exceptions be logged under the existing `[ERR]` prefix or a new `[THREAD-ERROR]` marker?
   **Chosen Answer / Value:** New `[THREAD-ERROR]` marker (Option A from 01-analysis.md §Decision Points DP-2)
   **Rationale:** `[ERR]` is already defined as subprocess stderr content (OBS-01). Thread infrastructure failures are a distinct category and should not be conflated with subprocess output.
   **Evidence / Reference:** 01-analysis.md §Decision Points DP-2; OBS-01 Taxonomy table.
   **Impact if changed:** Using `[ERR]` would require no OBS-01 schema update but would conflate infrastructure failures with subprocess stderr, making log analysis ambiguous.

3) **Question:** Should the streaming thread log the exception and terminate gracefully, or attempt recovery (e.g., skip the bad line and continue)?
   **Chosen Answer / Value:** Log and terminate gracefully — no recovery attempt.
   **Rationale:** Once a decoding error occurs mid-stream, the pipe state is unreliable. Attempting partial recovery risks producing corrupt or incomplete output in the log. (01-analysis.md §Disambiguation Questionnaire Q2)
   **Evidence / Reference:** 01-analysis.md §Disambiguation Questionnaire Q2; Python threading documentation.
   **Impact if changed:** Recovery would require per-line error handling and potentially undefined partial-log state.

4) **Question:** Should `errors="backslashreplace"` be used instead of `errors="replace"`?
   **Chosen Answer / Value:** `errors="replace"` — produces U+FFFD visible in terminal.
   **Rationale:** `backslashreplace` generates escape sequences (`\x8f`) that are less readable in a terminal output context. (01-analysis.md §Disambiguation Questionnaire Q4)
   **Evidence / Reference:** 01-analysis.md §Disambiguation Questionnaire Q4; Python codecs documentation.
   **Impact if changed:** Output would show `\x8f` instead of `▒`; more diagnostic but less user-friendly.

## Work Breakdown Structure (WBS)

### Task 1: Fix subprocess encoding in `_run_and_tee`

**Intent:** Add `encoding="utf-8"` and `errors="replace"` to the `subprocess.Popen` call in `_run_and_tee` to prevent `UnicodeDecodeError` when the Copilot CLI emits non-ASCII UTF-8 bytes on Windows.

**Inputs:**
- `.aib_brain/tools/menu.py` (current state — `_run_and_tee` at line ~119, `Popen` call at line ~130)
- request.md §Scope (primary fix), §Constraints (Python 3.10+)
- 01-analysis.md §Decision Points DP-1, §Technical Knowledge & Terms

**Outputs:**
- `.aib_brain/tools/menu.py` — `_run_and_tee` function updated with `encoding="utf-8", errors="replace"` on the `Popen` call.

**Procedure:**
1. Open `.aib_brain/tools/menu.py`.
2. Locate `def _run_and_tee` (line ~119) and the `subprocess.Popen` call within it.
3. Add `encoding="utf-8"` and `errors="replace"` keyword arguments to the `Popen` call.
4. Verify that no other `Popen` or `subprocess.run` calls in the file use `text=True` without an explicit `encoding` argument. If found, apply the same fix.
5. Save the file.

**Done Criteria:**
- The `subprocess.Popen` call in `_run_and_tee` contains `encoding="utf-8"` and `errors="replace"`.
- All pre-existing tests in `tests/test_menu.py` pass (`pytest tests/test_menu.py`).
- No `SyntaxError` or `ImportError` when importing `menu.py`.

**Dependencies:** None (first task).

**Risk Notes:** R1 — if Copilot CLI uses a non-UTF-8 encoding on some systems, `errors="replace"` prevents crashes but produces replacement characters. Probability: Low; accepted per DP-1.

---

### Task 2: Add exception handling in `_stream_pipe`

**Intent:** Wrap the `_stream_pipe` loop in an `except Exception` handler that writes a `[THREAD-ERROR]` entry to the log file, making streaming thread failures observable in the per-action log.

**Inputs:**
- `.aib_brain/tools/menu.py` (output of Task 1)
- request.md §Scope (secondary fix), §Constraints (thread-safe log writes)
- 01-analysis.md §Decision Points DP-2, §Disambiguation Questionnaire Q2–Q3
- OBS-01 §Log Levels (marker format: `[THREAD-ERROR] <ExceptionType>: <message>`)

**Outputs:**
- `.aib_brain/tools/menu.py` — `_stream_pipe` function updated with `except Exception as exc` block that acquires `lock` and writes `[THREAD-ERROR] <type>: <message>` to `log_file`.

**Procedure:**
1. Open `.aib_brain/tools/menu.py`.
2. Locate `def _stream_pipe` (line ~101).
3. Wrap the `for raw_line in iter(pipe.readline, ""):` loop in a `try` block.
4. Add `except Exception as exc:` after the loop body.
5. Inside the `except` block: acquire `lock` via `with lock:`, then write `log_file.write(f"[THREAD-ERROR] {type(exc).__name__}: {exc}\n")` and call `log_file.flush()`.
6. Retain the existing `finally: pipe.close()` block.
7. Save the file.

**Done Criteria:**
- `_stream_pipe` has a `try/except Exception/finally` structure; the `except` block acquires `lock` and writes `[THREAD-ERROR]` to `log_file`.
- All pre-existing tests in `tests/test_menu.py` pass.
- A `UnicodeDecodeError` raised inside `_stream_pipe` no longer propagates to `Thread._bootstrap_inner` uncaught.

**Dependencies:** Task 1 (FS — menu.py must be in a consistent state).

**Risk Notes:** R3 — acquiring the lock inside the `except` block is thread-safe because each thread has its own `exc` scope and the lock is reentrant-safe for this pattern.

---

### Task 3: Add automated tests in `tests/test_menu.py`

**Intent:** Add three unit tests to `TestRunAndTee` in `tests/test_menu.py` verifying: (a) non-ASCII UTF-8 subprocess output is streamed and logged correctly; (b) a thread exception is captured as `[THREAD-ERROR]` in the log; (c) `[EXIT]` is written even when a streaming thread fails.

**Inputs:**
- `.aib_brain/tools/menu.py` (output of Tasks 1 and 2 — functions under test)
- `tests/test_menu.py` (existing `TestRunAndTee` class and fixtures)
- request.md §Scope (test requirements), §Success criteria (≥ 2 new tests)
- 01-analysis.md §Research Plan and Findings (test gaps identified), §Disambiguation Q2–Q3

**Outputs:**
- `tests/test_menu.py` — three new test methods added to `TestRunAndTee`:
  - `test_utf8_non_ascii_output_logged_correctly`
  - `test_thread_exception_captured_in_log`
  - `test_exit_marker_present_when_thread_fails`

**Procedure:**
1. Open `tests/test_menu.py`.
2. Locate `class TestRunAndTee`.
3. Add `test_utf8_non_ascii_output_logged_correctly`: spawn a real subprocess that prints a UTF-8 character outside cp1252 range (e.g., U+2192 `→`, bytes `0xE2 0x86 0x92`); call `_run_and_tee`; assert log contains `[OUT]` with the character and `[EXIT] 0`.
4. Add `test_thread_exception_captured_in_log`: call `_stream_pipe` directly with a mock pipe whose `readline` raises `UnicodeDecodeError`; assert log contains `[THREAD-ERROR]` and `UnicodeDecodeError`.
5. Add `test_exit_marker_present_when_thread_fails`: patch `subprocess.Popen` to return a mock with pipes that raise `UnicodeDecodeError`; call `_run_and_tee`; assert log contains both `[THREAD-ERROR]` and `[EXIT]`.
6. Run `pytest tests/test_menu.py` and confirm all tests pass (including pre-existing ones).

**Done Criteria:**
- Three new test methods exist in `TestRunAndTee`.
- `pytest tests/test_menu.py` exits with code 0; count of passing tests is ≥ `(previous count + 3)`.
- No test uses live Copilot CLI binary; all subprocess calls that would invoke real external tools are mocked.

**Dependencies:** Task 1 (FS), Task 2 (FS).

**Risk Notes:** None beyond standard mock complexity.

---

### Task 4: Update OBS-01 documentation

**Intent:** Add the `[THREAD-ERROR]` marker to OBS-01's Log Levels list, Log Event Schema table, Taxonomy & Categories table, and Change Control section to reflect the new logging behavior.

**Inputs:**
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` (current state)
- request.md §Scope (OBS-01 update required)
- 01-analysis.md §Affected Documentation, §Decision Points DP-2
- `.aib_memory/references.md` REF-0021 (`edit_allowed = Y`)
- `.aib_brain/conventions/obs-01-convention.md` (OBS-01 editing convention)

**Outputs:**
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — updated with `[THREAD-ERROR]` marker in Log Levels, Log Event Schema, Taxonomy & Categories, and Change Control.

**Procedure:**
1. Open `.aib_memory/docs/04 Technology/Observability/OBS-01.md`.
2. In the **Log Levels** section: add `- [THREAD-ERROR] — an exception raised inside a streaming thread, capturing type and message.` after the `[ERR]` bullet.
3. In the **Log Event Schema** table: add a row for `THREAD-ERROR lines` with format `[THREAD-ERROR] <ExceptionType>: <message>`, Required `N`, Description `Exception raised in a streaming thread; zero or more per execution`.
4. In the **Taxonomy & Categories** table: add a row with Category `Thread error`, Marker prefix `[THREAD-ERROR]`, Description `Exception caught inside a streaming thread`.
5. In the **Change Control** section: append an entry documenting the addition of `[THREAD-ERROR]` marker referencing R-20260403-1844 / Iteration 01.
6. Confirm all changes are additive — no existing rows or bullets are removed.

**Done Criteria:**
- OBS-01 contains `[THREAD-ERROR]` in the Log Levels list, Log Event Schema table, and Taxonomy table.
- Change Control section has a new entry referencing R-20260403-1844.
- No pre-existing content in OBS-01 is altered or removed.

**Dependencies:** Task 2 (FS — the marker definition is driven by the implementation).

**Risk Notes:** None. `edit_allowed = Y` confirmed.

---

### Task 5: Update CMP-01 documentation

**Intent:** Update CMP-ART-0006 row in CMP-01 to document `encoding="utf-8", errors="replace"` on Popen and streaming thread exception logging as `[THREAD-ERROR]`.

**Inputs:**
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` (current state)
- request.md §Scope (CMP-01 update required)
- 01-analysis.md §Affected Documentation, §Impact Assessment DOMAIN (CMP)
- `.aib_memory/references.md` REF-0007 (`edit_allowed = Y`)
- `.aib_brain/conventions/cmp-01-convention.md` (CMP-01 editing convention)

**Outputs:**
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — CMP-ART-0006 `edge_cases_and_validation` field updated.

**Procedure:**
1. Open `.aib_memory/docs/04 Technology/Compute/CMP-01.md`.
2. Locate the CMP-ART-0006 row in the Catalog table.
3. In the `edge_cases_and_validation` cell: append `; streams stdout/stderr via Popen tee pattern with encoding="utf-8", errors="replace" to handle non-ASCII output on Windows; streaming thread exceptions caught and logged as [THREAD-ERROR]`.
4. Confirm no other cells in CMP-ART-0006 are inadvertently modified.
5. Save the file.

**Done Criteria:**
- CMP-ART-0006 `edge_cases_and_validation` contains `encoding="utf-8", errors="replace"` and `[THREAD-ERROR]`.
- Column order in the CMP-01 Catalog table is unchanged.
- No other CMP-ART rows are modified.

**Dependencies:** Task 2 (FS — the behavior to document must be implemented first).

**Risk Notes:** None. `edit_allowed = Y` confirmed.

## Dependencies & Interfaces

- From Task: 1 | To Task: 2 | Dependency Type: FS | Critical: Y | Notes: Task 2 modifies the same function block; menu.py must be in a consistent state after Task 1 before Task 2 edits begin.
- From Task: 1 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: Tests in Task 3 exercise the `_run_and_tee` encoding fix; the fix must be in place before tests are written/validated.
- From Task: 2 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: Tests in Task 3 exercise the `_stream_pipe` exception handling; it must be in place before tests are written/validated.
- From Task: 2 | To Task: 4 | Dependency Type: FS | Critical: N | Notes: OBS-01 documents the `[THREAD-ERROR]` marker introduced by Task 2. Can be done in parallel but should not be published before the implementation is confirmed.
- From Task: 2 | To Task: 5 | Dependency Type: FS | Critical: N | Notes: CMP-01 documents behavior implemented in Task 2. Can be done in parallel with Task 4.

- Interface: `.aib_brain/tools/menu.py` | Direction: Out | Protocol/Contract: Python module; `_stream_pipe(pipe, dest, log_file, prefix, lock)` and `_run_and_tee(command, log_path, title, inherit_stdin) -> int` | Version: current (Python 3.10+) | Notes: Function signatures must remain unchanged; no new public API introduced.
- Interface: `tests/test_menu.py` | Direction: Out | Protocol/Contract: pytest test module; new methods appended to `TestRunAndTee` class | Version: current pytest version | Notes: Must not break existing test discovery or parameterization.
- Interface: `subprocess.Popen` | Direction: In | Protocol/Contract: Python stdlib `subprocess.Popen(... encoding="utf-8", errors="replace")` | Version: Python 3.10+ | Notes: The `encoding` and `errors` parameters are available since Python 3.6.

## Environment & Configuration

**Environments:** Developer workstation (local-only; no stage/prod).

**Config Keys:**
- Key: N/A | Scope: N/A | Default: N/A | Allowed Range/Values: N/A | Source: N/A | Change Control: N/A

No environment-variable or config-file changes are required by this iteration.

**Secrets Handling:** Not applicable. No secrets are involved. Log files MUST NOT contain credentials per OBS-01 §Privacy & Security.

## Testing Strategy (This Iteration)

- **Test Types:** Unit
- **Coverage Targets:** At minimum 2 new tests verifying the encoding fix and exception-logging fix (request.md §Success criteria); 3 new tests planned per WBS Task 3.
- **Data/Fixtures:** Test fixtures use `tmp_path` (pytest built-in) for log files; real subprocess spawned with a Python one-liner for UTF-8 non-ASCII output; mock pipes constructed with `io.StringIO` or mock objects raising `UnicodeDecodeError` for exception-path tests.
- **Test Execution:** `pytest tests/test_menu.py -v` from the workspace root.
- **Acceptance Evidence:** Pytest console output showing all N tests passed (N = pre-existing count + 3); no failures or errors.

## Observability & Quality Gates

- **Key Metrics/Logs:** Per-action log file (`logs/aib-action-*.log`) must contain `[THREAD-ERROR] <ExceptionType>: <message>` when a streaming thread raises an exception, and `[EXIT] <code>` must always be present after thread joins.
- **Quality Gates:**
  - All pre-existing tests in `tests/test_menu.py` continue to pass (zero regressions).
  - Three new tests in `TestRunAndTee` pass with exit code 0.
  - Manual smoke: launch menu and invoke a prompt action; verify no `UnicodeDecodeError` in terminal and `[EXIT]` is present in the generated log file.
  - OBS-01 and CMP-01 contain the required additions (verified by reading the files post-update).

## Documentation Touchpoints

- Doc Path: `.aib_memory/docs/04 Technology/Observability/OBS-01.md` | Change Type: update | Update Trigger: Task 4 | Edit Allowed: Y | Notes: Add `[THREAD-ERROR]` to Log Levels, Log Event Schema, Taxonomy, and Change Control. Changes are additive only.
- Doc Path: `.aib_memory/docs/04 Technology/Compute/CMP-01.md` | Change Type: update | Update Trigger: Task 5 | Edit Allowed: Y | Notes: Amend CMP-ART-0006 `edge_cases_and_validation` to note encoding and thread-exception behavior.

## Milestones

- Planned Start: 2026-04-03
- Planned End: 2026-04-03

- Milestone: M1 | Description: menu.py fixes complete (encoding + exception handling) | Due: After Tasks 1 and 2 | Depends On: Task 1, Task 2 | Exit Criteria: `_run_and_tee` has `encoding="utf-8", errors="replace"`; `_stream_pipe` has `except Exception` block writing `[THREAD-ERROR]`; no pre-existing test failures.
- Milestone: M2 | Description: Test suite extended | Due: After Task 3 | Depends On: Task 3 | Exit Criteria: `pytest tests/test_menu.py` passes with ≥ (previous count + 3) tests.
- Milestone: M3 | Description: Documentation updated | Due: After Tasks 4 and 5 | Depends On: Task 4, Task 5 | Exit Criteria: OBS-01 and CMP-01 contain required additions; no pre-existing content removed.
- Milestone: M4 | Description: Iteration complete | Due: After M1, M2, M3 | Depends On: M1, M2, M3 | Exit Criteria: All acceptance criteria satisfied; iteration ready to close.

## Risks & Mitigations

- R1: Copilot CLI uses a non-UTF-8 encoding on some Windows configurations — P: Low, I: Medium — Mitigation: `errors="replace"` prevents crashes; replacement characters (`▒`) are visible. If frequent, a follow-up can add encoding auto-detection. (01-analysis.md §Risks R1)
- R2: `[THREAD-ERROR]` marker breaks any external log-parsing tooling — P: Low, I: Low — Mitigation: Change is additive; marker documented in OBS-01; no known external parsers. (01-analysis.md §Risks R2)
- R3: `errors="replace"` silently masks genuine encoding problems — P: Low, I: Low — Mitigation: U+FFFD `▒` is visually obvious in terminal and log output; developers can inspect for `▒` characters. (01-analysis.md §Risks R3)
- R4: Lock acquisition inside `except` block could cause deadlock if `lock` was held by the crashing thread — P: Very Low, I: High — Mitigation: The `lock` in `_stream_pipe` is acquired/released inside the `for` loop's `with lock:` block; it is never held across a `readline` call, so it cannot be held when the exception fires. (01-analysis.md §Constraints)

## Acceptance & Handover

- **Iteration Acceptance Criteria:**
  - Task 1 Done Criteria satisfied: `Popen` in `_run_and_tee` has `encoding="utf-8", errors="replace"`.
  - Task 2 Done Criteria satisfied: `_stream_pipe` has `except Exception as exc` block writing `[THREAD-ERROR]` to log.
  - Task 3 Done Criteria satisfied: `pytest tests/test_menu.py` passes with ≥ (previous count + 3) tests.
  - Task 4 Done Criteria satisfied: OBS-01 updated with `[THREAD-ERROR]` marker.
  - Task 5 Done Criteria satisfied: CMP-01 CMP-ART-0006 `edge_cases_and_validation` updated.
  - All Quality Gates in §Observability & Quality Gates passed.

- **Handover Artifacts:**
  - Modified source: `.aib_brain/tools/menu.py`
  - Extended test file: `tests/test_menu.py`
  - Updated product docs: `.aib_memory/docs/04 Technology/Observability/OBS-01.md`, `.aib_memory/docs/04 Technology/Compute/CMP-01.md`

- **Post-Iteration Follow-ups:**
  - None identified. All decision points are resolved and all scope items are covered within this iteration.
