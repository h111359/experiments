# Plan - Iteration 01

## Overview

This iteration replaces the buffered `subprocess.run(capture_output=True)` pattern in `run_prompt_action()` and `run_action()` within `.aib_brain/tools/menu.py` with a `subprocess.Popen()`-based tee pattern that streams stdout/stderr line-by-line to both the terminal and a timestamped log file, inherits stdin for interactive user input passthrough, and reports failures with full context (exit code, stdout, stderr) without requiring a secondary opt-in prompt.

The changes address the blank-screen problem, missing persistent logging, no stdin passthrough, and opaque failure reporting described in request.md §Background. The chosen solution is Option A (Popen Tee Pattern with Inherited stdin) from 01-analysis.md §Solution Options, validated by questionnaire answers QID-BF-001 (option A: gitignore execution logs), QID-BF-002 (option A: `logs/` directory), and QID-BF-003 (option A: unbounded retention).

## Scope of Work

**In Scope**
- Implement a tee-pattern helper function in `menu.py` (or `common.py`) using `subprocess.Popen()` with threading for dual-stream (stdout + stderr) reading.
- Refactor `run_prompt_action()` to use the tee helper with `stdin` inherited for user input passthrough.
- Refactor `run_action()` to use the same tee helper for script actions.
- Create per-action log files at `logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log` with timestamped start marker, output lines, and exit code.
- Display a "Running..." banner before subprocess start and a structured result summary after exit.
- Remove the secondary "Show full details? [y/N]" prompt on failure; display full output immediately.
- Add `logs/aib-action-*.log` to `.gitignore`.
- Update tests in `tests/test_menu.py` to cover streaming, log file creation, stdin passthrough, and error reporting.
- Update product documentation: ARCH-01, ARCH-06, CMP-01, OBS-01, RQT-02.

**Out of Scope**
- Modifications to the Copilot CLI binary or `_detect_copilot_cli()`.
- GUI or web-based log viewer.
- Remote/cloud logging or telemetry.
- Log rotation, automatic cleanup, or retention automation.
- Changes to menu keyboard navigation (arrow keys, digit shortcuts, exit command).
- Modifications to GitHub Actions CI workflows or `scripts/release_bookkeeping.py`.

**Assumptions**
- The `copilot` CLI flushes stdout incrementally (assumption A1 from analysis; if false, streaming degrades gracefully to chunk-based display).
- The `copilot` CLI reads from stdin for user prompts (assumption A2 from analysis).

**Constraints**
- Python 3.10+ standard library only — no third-party packages.
- Cross-platform: Windows (cmd.exe, PowerShell, Windows Terminal) and Unix (bash, zsh).
- Log files MUST NOT contain secrets, credentials, tokens, or sensitive PII.
- Copilot CLI detection and gating logic in `menu.py` must remain unchanged.
- Existing menu behavior (action filtering, parameter collection, destructive-action confirmation) must be preserved.

## Decision Gates (Blocking Questions & Answers)

1) **Question:** What is the minimal shippable outcome for this iteration?
   **Chosen Answer / Value:** Real-time output streaming + per-action log file creation + stdin passthrough for both script and prompt actions, with full error reporting on failure.
   **Rationale:** Directly addresses all three stated pain points (no visibility, no error info, no input).
   **Evidence / Reference:** request.md §Goal; 01-analysis.md §Disambiguation Q1.
   **Impact if changed:** Reducing scope leaves at least one pain point unresolved.

2) **Question:** Which user-visible changes must be demonstrable at iteration end?
   **Chosen Answer / Value:** (a) Running a prompt action shows incremental copilot output in terminal. (b) A log file appears in `logs/` after action execution. (c) If copilot asks a question, the user can type a response. (d) On failure, full output is shown without opt-in prompt.
   **Rationale:** Maps to the four request goals.
   **Evidence / Reference:** request.md §Success criteria; 01-analysis.md §Disambiguation Q2.
   **Impact if changed:** Removing any demo criterion fails the corresponding success criterion.

3) **Question:** Should execution log files be excluded from version control?
   **Chosen Answer / Value:** Yes — add `logs/aib-action-*.log` to `.gitignore`.
   **Rationale:** Execution logs are transient operational artifacts; committing them creates PR noise and inflates repo size.
   **Evidence / Reference:** 01-questionnaire.md QID-BF-001, option A selected.
   **Impact if changed:** If committed, a log retention/cleanup mechanism would be needed.

4) **Question:** What is the preferred directory location for execution log files?
   **Chosen Answer / Value:** `logs/` — same top-level directory as release logs, differentiated by filename prefix `aib-action-*` vs `version_*`.
   **Rationale:** Simple; reuses existing directory; no new path conventions needed.
   **Evidence / Reference:** 01-questionnaire.md QID-BF-002, option A selected.
   **Impact if changed:** A different location would require new directory creation logic.

5) **Question:** What log retention policy applies?
   **Chosen Answer / Value:** Unbounded — no automatic cleanup; developer manages manually.
   **Rationale:** Simplest approach; appropriate for typical usage patterns; cleanup can be added in a future request.
   **Evidence / Reference:** 01-questionnaire.md QID-BF-003, option A selected.
   **Impact if changed:** Adding cleanup logic would increase scope.

6) **Question:** Which algorithm/specification variant is in scope?
   **Chosen Answer / Value:** Popen tee pattern (Option A). Line-by-line stdout/stderr reading with concurrent dual-stream output via `threading`.
   **Rationale:** Cross-platform, stdlib-only, full control over formatting and logging.
   **Evidence / Reference:** 01-analysis.md §Solution Options, Option A recommended.
   **Impact if changed:** Shell-level tee (Option B) would require platform-specific branching.

7) **Question:** How is stdin handled for the copilot subprocess?
   **Chosen Answer / Value:** Direct stdin inheritance (`stdin=None` or `stdin=sys.stdin` in Popen). No logging of user input.
   **Rationale:** Simplest and most reliable approach; logging user input raises privacy concerns.
   **Evidence / Reference:** 01-analysis.md §Decision D2, Option A recommended.
   **Impact if changed:** Proxying stdin adds complexity and privacy risk.

8) **Question:** Which input data schemas are authoritative?
   **Chosen Answer / Value:** N/A — no new data sources, schemas, or ingestion pipelines. Log files are plain text with no schema contract.
   **Rationale:** This is a UI/observability enhancement within an existing CLI tool.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q4-Q6.
   **Impact if changed:** N/A.

9) **Question:** Which interfaces or integration contracts change?
   **Chosen Answer / Value:** N/A — no new API endpoints or inter-service contracts. The only interface change is the subprocess invocation pattern within menu.py.
   **Rationale:** Internal refactor of subprocess handling only.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q10-Q11.
   **Impact if changed:** N/A.

10) **Question:** What security/privacy considerations apply?
    **Chosen Answer / Value:** Log files MUST NOT contain secrets or PII. No new identities or secrets introduced.
    **Rationale:** Logging terminal output does not change security posture if sensitive content is excluded.
    **Evidence / Reference:** 01-analysis.md §Disambiguation Q12-Q14; request.md §Constraints.
    **Impact if changed:** If copilot output contains sensitive data, log sanitization would be required.

11) **Question:** Which metrics/logs/traces prove the change is healthy?
    **Chosen Answer / Value:** (a) Log file created with non-zero size after each action. (b) Log contains timestamped start, output lines, exit code. (c) No Python exceptions during normal operation.
    **Rationale:** Minimum indicators that streaming and logging function correctly.
    **Evidence / Reference:** 01-analysis.md §Disambiguation Q15.
    **Impact if changed:** Additional metrics would require beyond-scope instrumentation.

12) **Question:** Which product docs must be updated?
    **Chosen Answer / Value:** ARCH-01 (update component), ARCH-06 (add sequence), CMP-01 (update CMP-ART-0006), OBS-01 (populate stub), RQT-02 (refine FR-008). All `edit_allowed=Y`.
    **Rationale:** These are the docs directly impacted by code changes per impact assessment.
    **Evidence / Reference:** 01-analysis.md §Affected Documentation; references.md.
    **Impact if changed:** Omitting updates leaves documentation inconsistent with implementation.

13) **Question:** What acceptance evidence will be recorded?
    **Chosen Answer / Value:** Test results from `tests/test_menu.py` and implementation log entry in `implementation.md`.
    **Rationale:** Aligns with existing AIB practice.
    **Evidence / Reference:** Concepts.md §Holistic workflow; 01-analysis.md §Disambiguation Q19.
    **Impact if changed:** Reduced test coverage weakens confidence.

14) **Question:** What is the rollback strategy?
    **Chosen Answer / Value:** `git revert` of commit(s) modifying `menu.py`, tests, docs, and `.gitignore`. Delete any log files created during testing.
    **Rationale:** All changes are file-based and version-controlled.
    **Evidence / Reference:** 01-analysis.md §Disambiguation Q20.
    **Impact if changed:** N/A.

## Work Breakdown Structure (WBS)

### Task 1: Implement Tee-Pattern Helper

**Intent:** Create a reusable helper function that runs a subprocess with real-time output streaming to both terminal and a log file.
**Inputs:**
- `.aib_brain/tools/menu.py` (current source)
- `.aib_brain/tools/common.py` (shared helpers)
- Python `subprocess`, `threading`, `pathlib`, `datetime` stdlib modules
**Outputs:**
- Modified `.aib_brain/tools/menu.py` with new helper function (e.g., `_run_and_tee()`)
**Procedure:**
1. Add `import threading` and `from datetime import datetime` to `menu.py` imports.
2. Implement `_run_and_tee(command: list[str], log_path: Path, title: str, inherit_stdin: bool = False) -> int` that:
   - Opens the log file for writing with a timestamped start marker.
   - Creates a `subprocess.Popen` with `stdout=PIPE, stderr=PIPE` and `stdin=None` (inherit) when `inherit_stdin=True`, else `stdin=PIPE`.
   - Spawns daemon threads to read stdout and stderr line-by-line, writing each line to both the terminal (`sys.stdout`/`sys.stderr`) and the log file with timestamps.
   - Waits for the subprocess to complete.
   - Writes exit code to the log file.
   - Returns the exit code.
3. Ensure the log directory (`logs/`) is created if it doesn't exist (`os.makedirs(log_dir, exist_ok=True)`).
4. Generate log file name as `aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log` where `<action-id>` is sanitized from the action title/script name.
**Done Criteria:**
- `_run_and_tee()` exists in `menu.py` and can be called with a command list, log path, and title.
- Function creates a log file at the specified path with timestamped start, output lines, and exit code.
- Function streams stdout/stderr to terminal in real time.
- Function returns the subprocess exit code.
**Dependencies:** None (first task).
**Risk Notes:** Threading for dual-stream reading could introduce interleaving of stdout/stderr lines in the log file; acceptable since line-level ordering is sufficient. See risk R2 in analysis.

### Task 2: Refactor run_prompt_action()

**Intent:** Replace `subprocess.run(capture_output=True)` with the tee helper and remove the "Show full details?" opt-in prompt.
**Inputs:**
- `.aib_brain/tools/menu.py` — current `run_prompt_action()` function
- `_run_and_tee()` helper from Task 1
**Outputs:**
- Modified `run_prompt_action()` in `.aib_brain/tools/menu.py`
**Procedure:**
1. Replace the `subprocess.run(...)` call with a call to `_run_and_tee()`, passing `inherit_stdin=True` to enable user input passthrough to the copilot CLI.
2. Before the subprocess call, print a "Running..." banner: `print("\n▶ Running copilot CLI... (output appears below)\n")`.
3. After the subprocess completes, print a structured summary: exit code and log file path.
4. On success: print "Status: Success" and the log file path, then `input("Press Enter to return to menu...")`.
5. On failure: print "Status: Failed (exit code N)" and the log file path — do NOT prompt "Show full details?" since full output was already streamed.
6. Then `input("Press Enter to return to menu...")`.
**Done Criteria:**
- `run_prompt_action()` no longer uses `subprocess.run(capture_output=True)`.
- Copilot output appears incrementally in the terminal during execution.
- User can type responses when copilot CLI prompts for input.
- On failure, full exit code is displayed without secondary opt-in.
- A log file is created at `logs/aib-action-<timestamp>-<action-id>.log`.
**Dependencies:** Task 1 (FS — `_run_and_tee()` must exist).
**Risk Notes:** If copilot CLI does not flush stdout, streaming appears delayed — this is a CLI limitation, not a code defect.

### Task 3: Refactor run_action()

**Intent:** Apply the same tee pattern to script action execution for consistency.
**Inputs:**
- `.aib_brain/tools/menu.py` — current `run_action()` function
- `_run_and_tee()` helper from Task 1
**Outputs:**
- Modified `run_action()` in `.aib_brain/tools/menu.py`
**Procedure:**
1. Replace the `subprocess.run(command, text=True, capture_output=True)` call with a call to `_run_and_tee()`, passing `inherit_stdin=False` (script actions do not need interactive input).
2. Before the subprocess call, print a "Running..." banner: `print(f"\n▶ Running {title}... (output appears below)\n")`.
3. After the subprocess completes, print a structured summary: exit code and log file path.
4. On success: print "Status: Success" and the log file path, then `input("Press Enter to return to menu...")`.
5. On failure: print "Status: Failed (exit code N)" and the log file path — no secondary opt-in prompt.
6. Then `input("Press Enter to return to menu...")`.
**Done Criteria:**
- `run_action()` no longer uses `subprocess.run(capture_output=True)`.
- Script output appears incrementally in the terminal during execution.
- On failure, full exit code is displayed without secondary opt-in.
- A log file is created at `logs/aib-action-<timestamp>-<action-id>.log`.
**Dependencies:** Task 1 (FS — `_run_and_tee()` must exist).
**Risk Notes:** None beyond shared Task 1 risks.

### Task 4: Update .gitignore

**Intent:** Exclude execution log files from version control per questionnaire decision QID-BF-001.
**Inputs:**
- `.gitignore` (current content, if exists)
- Questionnaire answer QID-BF-001 option A
**Outputs:**
- Updated `.gitignore` with `logs/aib-action-*.log` pattern
**Procedure:**
1. Open `.gitignore` at workspace root (create if missing).
2. Append a comment `# AIB execution logs (transient)` and the pattern `logs/aib-action-*.log`.
3. Verify that existing `logs/version_*.md` files are NOT affected by the new pattern.
**Done Criteria:**
- `.gitignore` contains the `logs/aib-action-*.log` pattern.
- `git status` does not show execution log files as untracked after an action is run.
- Existing `logs/version_*.md` files remain tracked.
**Dependencies:** None (independent of code tasks).
**Risk Notes:** None.

### Task 5: Update Tests

**Intent:** Cover new streaming, logging, stdin passthrough, and error-reporting behavior in the test suite.
**Inputs:**
- `tests/test_menu.py` (current tests)
- `tests/conftest.py` (shared fixtures)
- Modified `menu.py` from Tasks 1-3
**Outputs:**
- Updated `tests/test_menu.py` with new test cases
**Procedure:**
1. Add test for real-time output streaming: mock a subprocess that writes lines with delays; verify lines appear in captured output.
2. Add test for log file creation: run an action; verify a `logs/aib-action-*.log` file exists with expected content (start marker, output lines, exit code).
3. Add test for stdin passthrough in prompt actions: mock a subprocess that reads from stdin; verify it receives input (or verify `stdin=None` is passed to Popen).
4. Add test for failure reporting: mock a subprocess that exits with non-zero; verify full output is displayed and no "Show full details?" prompt appears.
5. Ensure all existing tests in `tests/test_menu.py` continue to pass (refactor mocks as needed to accommodate the Popen-based implementation).
6. Run the full test suite: `python -m pytest tests/test_menu.py -v`.
**Done Criteria:**
- All existing tests pass.
- New tests cover: streaming output, log file creation and content, stdin passthrough, failure reporting without opt-in.
- Test suite exits with zero failures.
**Dependencies:** Tasks 1, 2, 3 (FS — code changes must be finalized before tests can validate them).
**Risk Notes:** Mocking `Popen` with threading is more complex than mocking `subprocess.run`; may need `unittest.mock` patches on both Popen and thread targets.

### Task 6: Update Product Documentation

**Intent:** Update all affected product-doc files to reflect the new logging and streaming capabilities.
**Inputs:**
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` (current)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` (current)
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` (current)
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` (current stub)
- `.aib_memory/docs/03 Requirements/RQT-02.md` (current)
- Per-document conventions: `arch-01-convention.md`, `arch-06-convention.md`, `cmp-01-convention.md`, `obs-01-convention.md`, `rqt-02-convention.md`
**Outputs:**
- Updated ARCH-01: AIB Command Menu component description includes real-time streaming, per-action log files, stdin passthrough.
- Updated ARCH-06: New scenario SEQ-004 for prompt/script action execution with real-time streaming and logging.
- Updated CMP-01: CMP-ART-0006 entry updated with outputs (log file path pattern), edge cases (streaming, stdin), and dependencies.
- Updated OBS-01: Populated with execution logging specification — log format, location, naming, retention, content rules.
- Updated RQT-02: FR-008 refined to specify real-time feedback, per-action logging, and stdin passthrough.
**Procedure:**
1. Read each convention file to ensure updates conform to the required format.
2. Update ARCH-01 Component Inventory row for "AIB Command Menu" to include: "streams subprocess stdout/stderr to terminal in real time via Popen tee pattern; writes per-action log files to `logs/aib-action-<timestamp>-<action-id>.log`; inherits stdin for interactive copilot CLI sessions".
3. Update ARCH-06 to add scenario SEQ-004 with Mermaid sequence diagram showing Developer → Menu → Popen → Terminal + Log File flow.
4. Update CMP-01 CMP-ART-0006 row: add `file:logs/aib-action-*.log` to outputs; add streaming and stdin notes to edge_cases_and_validation.
5. Populate OBS-01 with: log location (`logs/`), naming convention, log file content format (timestamped start/output/exit), retention policy (unbounded/manual), content exclusion rules (no secrets/PII).
6. Update RQT-02 FR-008 to: "The system supports launching tool scripts via an interactive menu with real-time output streaming to terminal, per-action execution log files, and stdin passthrough for copilot CLI prompts; prompt actions require copilot CLI availability and display as informational only when CLI is absent."
7. Add change log entries to each updated document referencing R-20260403-1651 / Iteration 01.
**Done Criteria:**
- All five product-doc files are updated with accurate descriptions matching the implemented behavior.
- Each update conforms to its per-document convention.
- Change log entries are appended.
- No references to stubs or placeholder content remain in updated sections.
**Dependencies:** Tasks 1, 2, 3 (FS — implementation must be finalized so documentation reflects actual behavior).
**Risk Notes:** Documentation updates depend on final implementation details; if implementation changes during Task 1-3, documentation must be adjusted accordingly.

## Dependencies & Interfaces

- From Task: 1 | To Task: 2 | Dependency Type: FS | Critical: Y | Notes: `_run_and_tee()` helper must be implemented before `run_prompt_action()` can be refactored.
- From Task: 1 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: `_run_and_tee()` helper must be implemented before `run_action()` can be refactored.
- From Task: 2 | To Task: 5 | Dependency Type: FS | Critical: Y | Notes: Prompt action refactoring must be complete before tests can validate streaming/log behavior.
- From Task: 3 | To Task: 5 | Dependency Type: FS | Critical: Y | Notes: Script action refactoring must be complete before tests can validate.
- From Task: 1 | To Task: 6 | Dependency Type: FS | Critical: N | Notes: Documentation should reflect final implementation; can start drafting in parallel.
- From Task: 5 | To Task: 6 | Dependency Type: FS | Critical: N | Notes: Test results inform documentation accuracy; final doc updates after tests pass.

- Interface: copilot CLI | Direction: Out | Protocol/Contract: stdin/stdout/stderr via OS process | Version: current installed | Notes: Invoked as `copilot -p "<prompt>" --allow-all-tools`; output streaming depends on CLI flushing behavior.
- Interface: OS filesystem | Direction: Out | Protocol/Contract: file write | Version: N/A | Notes: Log files written to `logs/` directory.

## Environment & Configuration

- **Environments:** Local development workstation only (no staging/production).
- Key: LOG_DIR | Scope: Global | Default: logs/ | Allowed Range/Values: any valid directory path | Source: hardcoded in menu.py | Change Control: code change in menu.py
- Key: LOG_FILE_PREFIX | Scope: Global | Default: aib-action- | Allowed Range/Values: any valid filename prefix | Source: hardcoded in menu.py | Change Control: code change in menu.py

**Secrets Handling:** No secrets involved. Log files MUST NOT capture secrets, credentials, tokens, or PII. The tee helper writes only subprocess stdout/stderr content; no environment variables or system secrets are logged.

## Testing Strategy (This Iteration)

- **Test Types:** Unit tests (mocked subprocess), Integration-style tests (verify file creation)
- **Coverage Targets:** All new code paths in `_run_and_tee()`, refactored `run_prompt_action()`, and refactored `run_action()` must have at least one test. All existing tests must continue to pass.
- **Data/Fixtures:** Use `tmp_path` pytest fixture for log file directory isolation. Mock subprocess via `unittest.mock.patch` on `subprocess.Popen`.
- **Test Execution:** `python -m pytest tests/test_menu.py -v` from workspace root with virtual environment activated.
- **Acceptance Evidence:** Full pytest output showing all tests pass (zero failures). Log file content assertions within tests. Implementation log entry in `implementation.md`.

## Observability & Quality Gates

- **Key Metrics/Logs:**
  - Log file exists at `logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log` after each action execution.
  - Log file contains: `[START]` timestamp marker, output lines prefixed with `[OUT]` or `[ERR]`, `[EXIT]` line with return code.
  - No unhandled Python exceptions in stderr during normal menu operation.
- **Quality Gates:**
  - All unit tests pass (`pytest` exit code 0).
  - No regressions in existing test suite.
  - Manual smoke test: run a prompt action and a script action; verify terminal shows real-time output and log file is created.
  - Documentation review: all five product-doc files updated and internally consistent.

## Documentation Touchpoints

- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Update AIB Command Menu component description with streaming, logging, stdin passthrough.
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Add SEQ-004 scenario for action execution with real-time streaming.
- Doc Path: .aib_memory/docs/04 Technology/Compute/CMP-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Update CMP-ART-0006 outputs and edge cases.
- Doc Path: .aib_memory/docs/04 Technology/Observability/OBS-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Populate from stub with execution logging specification.
- Doc Path: .aib_memory/docs/03 Requirements/RQT-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Refine FR-008 with real-time feedback and logging requirements.

## Milestones

- Milestone: M1 | Description: Core tee helper implemented and unit-tested in isolation | Due: After Task 1 completes | Depends On: Task 1 | Exit Criteria: `_run_and_tee()` exists, creates log files, streams output; basic unit test passes.
- Milestone: M2 | Description: Both action functions refactored and manually verified | Due: After Tasks 2 and 3 complete | Depends On: Task 1, Task 2, Task 3 | Exit Criteria: Running a script action and a prompt action from the menu shows real-time output and creates log files.
- Milestone: M3 | Description: Full test suite passes with new coverage | Due: After Task 5 completes | Depends On: Task 2, Task 3, Task 5 | Exit Criteria: `pytest tests/test_menu.py -v` exits with zero failures; new tests for streaming, logging, stdin, error reporting are present.
- Milestone: M4 | Description: Documentation and .gitignore finalized | Due: After Tasks 4 and 6 complete | Depends On: Task 4, Task 5, Task 6 | Exit Criteria: Five product-doc files updated; `.gitignore` updated; all changes reviewed for consistency.

## Risks & Mitigations

- R1: Copilot CLI does not flush stdout incrementally — P: Low, I: Medium — Mitigation: streaming degrades gracefully to chunk-based display; document limitation. Test manually before implementation.
- R2: Threading for dual-stream reading introduces race conditions or interleaving — P: Low, I: High — Mitigation: use daemon threads with simple line-by-line reads; write to log under a shared lock if needed. Contingency: fall back to sequential read (stdout first, then stderr).
- R3: Log files accumulate unbounded disk usage — P: Medium, I: Low — Mitigation: individual files are small (KB range); document manual cleanup in OBS-01; defer automated retention to a future request per QID-BF-003.
- R4: Accidental keystroke during subprocess — P: Medium, I: Low — Mitigation: display clear "Running..." banner; keystrokes go to subprocess stdin (harmless if copilot ignores unexpected input).
- R5: Existing tests break due to mock changes (Popen vs subprocess.run) — P: Medium, I: Medium — Mitigation: carefully update mocks in Task 5; run full suite before marking task complete.

## Acceptance & Handover

- **Iteration Acceptance Criteria:**
  - All Done Criteria for Tasks 1–6 are satisfied.
  - All Quality Gates pass (test suite green, docs updated, manual smoke test successful).
  - Success criteria from request.md §Success criteria items 1–7 are met.

- **Handover Artifacts:**
  - Modified source: `.aib_brain/tools/menu.py`
  - Updated tests: `tests/test_menu.py`
  - Updated gitignore: `.gitignore`
  - Updated product docs: ARCH-01, ARCH-06, CMP-01, OBS-01, RQT-02
  - Implementation log entry: `.aib_memory/requests/R-20260403-1651-fix-copilot-cli-user-feedback-experience/implementation.md`

- **Post-Iteration Follow-ups:**
  - Monitor copilot CLI flushing behavior in production usage; if buffering is confirmed, consider filing a copilot CLI feature request.
  - If log file accumulation becomes a concern, create a new request for automated retention/cleanup.
  - Consider extending the log format with structured JSON output in a future iteration if machine-readable logs are needed.
