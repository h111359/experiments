## Overview

This plan covers iteration 02 of request R-20260403-1537 (CLI menu bugfixing). The iteration implements two workstreams: (1) fix the confirmed bug in `run_prompt_action()` in `.aib_brain/tools/menu.py` where the Copilot CLI is invoked without the required `-p` flag and lacks error handling, and (2) create a comprehensive `pytest`-based test suite in a new `tests/` directory at workspace root covering all tool scripts. The iteration also updates CMP-01 with a new catalog entry for the test suite.

Linkage: request.md §Goal, §Background, §Scope; 02-analysis.md §2 Scope Interpretation, §4 Technical Knowledge, §6 Impact Assessment; 01-questionnaire.md QID-BF-001 (research Copilot CLI syntax), QID-BF-002 (hardcoded command — option B), QID-AT-001 (pytest — option A), QID-AT-002 (separate tests/ directory — option B), QID-AT-003 (full lifecycle E2E — option A).

## Scope of Work

**In Scope**
- Fix `run_prompt_action()` in `.aib_brain/tools/menu.py` to invoke `copilot -p "<prompt-text>" --allow-all-tools` via subprocess.
- Add `capture_output=True` and `text=True` to the `subprocess.run()` call in `run_prompt_action()`.
- Add success/failure display and error detail view to `run_prompt_action()` mirroring the existing `run_action()` pattern (lines 504–542 of menu.py).
- Create `tests/` directory at workspace root with `conftest.py` and per-module test files.
- Create unit tests for `menu.py` functions: `discover_prompt_actions()`, `resolve_menu_state()`, `filter_visible_actions()`, `build_script_actions()`, `validate_param()`, `collect_parameters()`, `build_command()`, `run_prompt_action()`, `_detect_copilot_cli()`.
- Create integration tests for lifecycle scripts: `create-request.py`, `close-request.py`, `create-iteration.py`, `close-iteration.py`.
- Create integration tests for `initialize.py`.
- Create unit tests for `reverse-engineer.py`.
- Create a full lifecycle E2E test: create-request → create-iteration → close-iteration → close-request via subprocess in a temporary workspace.
- Verify existing `test_common.py` passes when run via `pytest`.
- Update CMP-01 with a new catalog entry (CMP-ART-0008) for the test suite.

**Out of Scope**
- Making the Copilot CLI command configurable via environment variable or config file.
- Changes to `.aib_brain/prompts/*.md` prompt content files.
- Changes to `.github/workflows/` CI workflows.
- Changes to `scripts/release_bookkeeping.py`.
- Live Copilot CLI integration tests (all CLI calls must be mocked).
- UI/UX redesign of the CLI menu beyond the bug fix and error handling.
- Performance optimization of tool scripts.
- Changes to `_detect_copilot_cli()` detection logic.

**Assumptions**
- The Copilot CLI binary is named `copilot` and is on PATH (verified via `copilot --help` — see 02-analysis.md §5 Assumption A1, A2).
- `--allow-all-tools` is required for non-interactive mode per CLI documentation (02-analysis.md §5 Assumption A3).
- `pytest` natively discovers and runs existing `unittest.TestCase`-based tests (02-analysis.md §5 Assumption A4).

**Constraints**
- Python 3.10+ stdlib only for production code in `.aib_brain/tools/menu.py`.
- `pytest` is a dev-only dependency; not required at runtime.
- All integration and E2E tests must use `tempfile.TemporaryDirectory()` for isolation — no modification to the developer's `.aib_memory/` state.
- No network access, live Copilot CLI binary, or GitHub connectivity required in tests.
- Platform-specific key input (`msvcrt`/`termios`) must be mocked at `get_key()` level, not low-level OS modules.
- All Copilot CLI subprocess calls in tests must be mocked via `unittest.mock.patch`.
- Full test suite must complete in under 60 seconds.

## Decision Gates (Blocking Questions & Answers)

1) **Question:** What is the correct Copilot CLI invocation syntax for non-interactive prompt execution?
   **Chosen Answer / Value:** `copilot -p "<prompt-text>" --allow-all-tools`
   **Rationale:** Confirmed via `copilot --help` output; `-p, --prompt <text>` is the documented flag; `--allow-all-tools` is required for non-interactive mode.
   **Evidence / Reference:** 02-analysis.md §5 Assumption A2, A3; 01-questionnaire.md QID-BF-001.
   **Impact if changed:** Subprocess command construction in `run_prompt_action()` and its test assertions would need updating.

2) **Question:** Should the Copilot CLI command be configurable or hardcoded?
   **Chosen Answer / Value:** Hardcoded.
   **Rationale:** User selected option B in QID-BF-002; simplest approach matching current codebase style.
   **Evidence / Reference:** 01-questionnaire.md QID-BF-002 = B.
   **Impact if changed:** Would require adding environment variable parsing and a configuration fallback path.

3) **Question:** Which test framework to use?
   **Chosen Answer / Value:** `pytest`.
   **Rationale:** Better discovery, parametrize, fixtures, and compatibility with existing unittest tests.
   **Evidence / Reference:** 01-questionnaire.md QID-AT-001 = A.
   **Impact if changed:** Test file structure, fixtures, and invocation commands would change.

4) **Question:** Where should test files be placed?
   **Chosen Answer / Value:** Separate `tests/` directory at workspace root.
   **Rationale:** Cleaner separation from production code; requires `conftest.py` for import path config.
   **Evidence / Reference:** 01-questionnaire.md QID-AT-002 = B.
   **Impact if changed:** Import path configuration and CI commands would change.

5) **Question:** What is the E2E test scope?
   **Chosen Answer / Value:** Full lifecycle: create-request → create-iteration → close-iteration → close-request in one test.
   **Rationale:** Most valuable test for verifying entire workflow integrity.
   **Evidence / Reference:** 01-questionnaire.md QID-AT-003 = A.
   **Impact if changed:** Would reduce E2E coverage and miss cross-script integration issues.

## Work Breakdown Structure (WBS)

### Task 1: Fix `run_prompt_action()` subprocess invocation

**Intent:** Correct the Copilot CLI invocation to use the required `-p` flag and `--allow-all-tools`.
**Inputs:** `.aib_brain/tools/menu.py` (current buggy function at ~line 593); `copilot --help` syntax reference (02-analysis.md §4).
**Outputs:** Modified `.aib_brain/tools/menu.py` — `run_prompt_action()` function.
**Procedure:**
1. Open `.aib_brain/tools/menu.py` and locate `run_prompt_action()`.
2. Replace `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` with `subprocess.run(["copilot", "-p", f"Execute the prompt defined in {paction['prompt_file']}", "--allow-all-tools"], capture_output=True, text=True)`.
3. Add success/failure status display after the subprocess call, following the `run_action()` pattern: check `result.returncode`, print "Status: Success" or "Status: Failed (exit code N)", display stdout/stderr, and offer detail view on error.
4. Verify the edited function compiles without syntax errors.
**Done Criteria:** `run_prompt_action()` constructs the command as `["copilot", "-p", <prompt-text>, "--allow-all-tools"]` with `capture_output=True` and `text=True`; success/failure display logic is present; no syntax errors.
**Dependencies:** None.
**Risk Notes:** None — confirmed syntax via live CLI help.

### Task 2: Create `tests/conftest.py` with shared fixtures

**Intent:** Establish test infrastructure with `sys.path` configuration for importing `.aib_brain/tools/` modules.
**Inputs:** Workspace root path; `.aib_brain/tools/` module structure.
**Outputs:** `tests/conftest.py`.
**Procedure:**
1. Create `tests/` directory at workspace root.
2. Create `tests/conftest.py` with `sys.path` manipulation to add `.aib_brain/tools/` to the import path.
3. Add shared fixtures: `workspace_dir` (creates a `tempfile.TemporaryDirectory` with minimal AIB structure), `brain_dir`, `tools_dir`.
4. Add a fixture for mocking `get_key()` to avoid platform-specific key input issues.
**Done Criteria:** `conftest.py` exists; `import menu`, `import common` work from test files; shared fixtures are importable.
**Dependencies:** None.
**Risk Notes:** Import path manipulation must handle the hyphenated script names (e.g., `create-request.py`) which cannot be imported as Python modules directly — use `importlib.util` for those.

### Task 3: Create `tests/test_menu.py`

**Intent:** Unit-test all public functions in `menu.py` with subprocess mocking.
**Inputs:** `.aib_brain/tools/menu.py` source; `tests/conftest.py` fixtures.
**Outputs:** `tests/test_menu.py`.
**Procedure:**
1. Write tests for `discover_prompt_actions()` — verify correct discovery, ordering, and dict structure from a mock prompts directory.
2. Write tests for `resolve_menu_state()` — verify correct `MenuState` for active/no-active/closed request scenarios using mock register files.
3. Write tests for `filter_visible_actions()` — verify visibility filtering based on different `MenuState` values.
4. Write tests for `build_script_actions()` — verify action list construction and renumbering.
5. Write tests for `validate_param()` — input validation for action parameters.
6. Write tests for `collect_parameters()` — parameter collection with mocked `input()`.
7. Write tests for `build_command()` — correct command list construction.
8. Write test for `run_prompt_action()` — verify subprocess is called with `["copilot", "-p", <text>, "--allow-all-tools"]` using `unittest.mock.patch("subprocess.run")`.
9. Write tests for `_detect_copilot_cli()` — verify True/False based on mocked subprocess responses.
**Done Criteria:** All tests in `test_menu.py` pass via `python -m pytest tests/test_menu.py`; `run_prompt_action()` test asserts correct subprocess arguments.
**Dependencies:** Task 1 (fixed function), Task 2 (conftest).
**Risk Notes:** Menu functions may have internal dependencies on global state or terminal dimensions; may need selective mocking.

### Task 4: Create `tests/test_create_request.py`

**Intent:** Integration-test the create-request lifecycle script in isolated temp workspaces.
**Inputs:** `.aib_brain/tools/create-request.py` source; temp workspace fixture from conftest.
**Outputs:** `tests/test_create_request.py`.
**Procedure:**
1. Write test for successful request creation: verify folder, request.md, iterations.md, and register row.
2. Write test for duplicate detection: attempt to create a second Active request and verify failure.
3. Write test for missing title: verify appropriate error.
4. Write test for workspace setup: verify register is properly seeded before request creation.
**Done Criteria:** All tests pass; each test uses `tempfile.TemporaryDirectory()`; no writes to actual `.aib_memory/`.
**Dependencies:** Task 2 (conftest).
**Risk Notes:** None.

### Task 5: Create `tests/test_close_request.py`

**Intent:** Integration-test the close-request lifecycle script.
**Inputs:** `.aib_brain/tools/close-request.py` source; temp workspace fixture.
**Outputs:** `tests/test_close_request.py`.
**Procedure:**
1. Write test for closing an Active request: verify state transitions to Closed with `closed_at` timestamp.
2. Write test for auto-close iteration: verify active iteration is auto-closed before the request.
3. Write test for already-closed request: verify appropriate error message.
4. Write test for missing request: verify failure on empty register.
**Done Criteria:** All tests pass in temp workspaces; state transitions verified.
**Dependencies:** Task 2 (conftest), Task 4 (create-request test provides workspace setup patterns).
**Risk Notes:** None.

### Task 6: Create `tests/test_create_iteration.py`

**Intent:** Integration-test the create-iteration lifecycle script.
**Inputs:** `.aib_brain/tools/create-iteration.py` source; temp workspace fixture.
**Outputs:** `tests/test_create_iteration.py`.
**Procedure:**
1. Write test for creating next iteration: verify iteration ID is strictly ascending and state is Active.
2. Write test for enforcing single Active: verify failure when an Active iteration already exists.
3. Write test for missing request: verify failure when no Active request exists.
**Done Criteria:** All tests pass; iteration ID sequencing verified.
**Dependencies:** Task 2 (conftest).
**Risk Notes:** None.

### Task 7: Create `tests/test_close_iteration.py`

**Intent:** Integration-test the close-iteration lifecycle script.
**Inputs:** `.aib_brain/tools/close-iteration.py` source; temp workspace fixture.
**Outputs:** `tests/test_close_iteration.py`.
**Procedure:**
1. Write test for closing Active iteration: verify state becomes Completed with `closed_at`.
2. Write test for explicit iteration ID close.
3. Write test for no Active iteration: verify appropriate error.
**Done Criteria:** All tests pass; state transitions verified.
**Dependencies:** Task 2 (conftest).
**Risk Notes:** None.

### Task 8: Create `tests/test_initialize.py`

**Intent:** Integration-test the initialize script for first-run and idempotent rerun scenarios.
**Inputs:** `.aib_brain/tools/initialize.py` source; temp workspace fixture.
**Outputs:** `tests/test_initialize.py`.
**Procedure:**
1. Write test for first-run initialization: verify `.aib_memory/` structure, registers, and doc stubs are created.
2. Write test for idempotent rerun: verify running initialize twice produces consistent state.
3. Write test for force overwrite behavior (if applicable).
**Done Criteria:** All tests pass; `.aib_memory/` structure verified in temp workspaces.
**Dependencies:** Task 2 (conftest).
**Risk Notes:** None.

### Task 9: Create `tests/test_reverse_engineer.py`

**Intent:** Unit-test the reverse-engineer script's file inventory and output format logic.
**Inputs:** `.aib_brain/tools/reverse-engineer.py` source.
**Outputs:** `tests/test_reverse_engineer.py`.
**Procedure:**
1. Write tests for file inventory: verify correct file listing from a mock workspace.
2. Write tests for exclusion rules: verify excluded paths/patterns are respected.
3. Write tests for output format: verify generated output matches expected Markdown structure.
**Done Criteria:** All tests pass; inventory and exclusion logic verified.
**Dependencies:** Task 2 (conftest).
**Risk Notes:** None.

### Task 10: Create `tests/test_lifecycle_e2e.py`

**Intent:** Full lifecycle E2E test exercising create-request → create-iteration → close-iteration → close-request via subprocess in a temporary workspace.
**Inputs:** All lifecycle scripts; temp workspace with initialized `.aib_memory/`.
**Outputs:** `tests/test_lifecycle_e2e.py`.
**Procedure:**
1. Create temp workspace and run initialize to seed `.aib_memory/`.
2. Run `create-request.py` via subprocess; verify register row and folder.
3. Run `create-iteration.py` via subprocess; verify iteration register.
4. Run `close-iteration.py` via subprocess; verify iteration state.
5. Run `close-request.py` via subprocess; verify request state.
6. Assert register and artifact state at each step.
**Done Criteria:** E2E test passes end-to-end in a temp workspace; all register states verified at each step.
**Dependencies:** Task 2 (conftest), Tasks 4–8 (patterns established).
**Risk Notes:** Subprocess invocations must use the correct Python executable and pass the workspace path; ensure `sys.executable` is used.

### Task 11: Verify existing `test_common.py` regression

**Intent:** Confirm existing tests still pass when run through `pytest`.
**Inputs:** `.aib_brain/tools/test_common.py`.
**Outputs:** Pass/fail result from `python -m pytest .aib_brain/tools/test_common.py`.
**Procedure:**
1. Run `python -m pytest .aib_brain/tools/test_common.py` from workspace root.
2. Verify all existing tests pass with 0 failures.
**Done Criteria:** All existing tests in `test_common.py` pass with 0 failures; no regressions.
**Dependencies:** None.
**Risk Notes:** Import path issues if `test_common.py` uses relative imports — may need minor conftest or path adjustments.

### Task 12: Update CMP-01 with test suite catalog entry

**Intent:** Add a new catalog entry CMP-ART-0008 for the pytest-based test suite.
**Inputs:** `.aib_memory/docs/04 Technology/Compute/CMP-01.md` (current catalog); `.aib_brain/conventions/cmp-01-convention.md` (governing convention).
**Outputs:** Updated `.aib_memory/docs/04 Technology/Compute/CMP-01.md` with CMP-ART-0008 row.
**Procedure:**
1. Read the CMP-01 convention to verify required column schema.
2. Append a new row to the Catalog table: `CMP-ART-0008 | AIB test suite | script | Automated pytest test suite for all AIB tool scripts | repo:tests/*.py | param:workspace=.|N/A | test results (stdout) | pytest; CMP-ART-0001..CMP-ART-0006; .aib_brain/tools/common.py | Python 3.10+; pytest | tests/ | Verify all test files pass; temp dirs for isolation | schedule=ad-hoc; timeout=60s | AIB Maintainers | active`.
3. Validate the updated table conforms to CMP-01 convention column order and allowed enumerations.
**Done Criteria:** CMP-01 contains CMP-ART-0008 row; table structure is valid per convention.
**Dependencies:** Task 2 (test directory exists).
**Risk Notes:** None.

## Dependencies & Interfaces

- From Task: 1 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: Task 3 test for `run_prompt_action()` asserts the fixed subprocess arguments from Task 1.
- From Task: 2 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures and import path config required by all test files.
- From Task: 2 | To Task: 4 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures required.
- From Task: 2 | To Task: 5 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures required.
- From Task: 2 | To Task: 6 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures required.
- From Task: 2 | To Task: 7 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures required.
- From Task: 2 | To Task: 8 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures required.
- From Task: 2 | To Task: 9 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures required.
- From Task: 2 | To Task: 10 | Dependency Type: FS | Critical: Y | Notes: conftest.py fixtures and E2E patterns required.
- From Task: 4 | To Task: 10 | Dependency Type: SS | Critical: N | Notes: E2E test reuses workspace setup patterns from create-request tests.

- Interface: Copilot CLI (`copilot` binary) | Direction: Out | Protocol/Contract: subprocess invocation with `-p` and `--allow-all-tools` flags | Version: current installed | Notes: All test invocations MUST be mocked; no live CLI calls.
- Interface: Python subprocess module | Direction: Out | Protocol/Contract: `subprocess.run()` with `capture_output=True`, `text=True` | Version: Python 3.10+ | Notes: Used by both production code and tests.

## Environment & Configuration

- **Environments:** Dev (local developer workstation only).

- Key: PYTHON_VERSION | Scope: Global | Default: 3.10+ | Allowed Range/Values: 3.10, 3.11, 3.12, 3.13 | Source: system Python or venv | Change Control: developer discretion.

**Secrets Handling:** No secrets involved. Copilot CLI authentication is handled externally by the CLI binary; not managed by AIB.

## Testing Strategy (This Iteration)

- **Test Types:** Unit (menu.py functions, reverse-engineer.py), Integration (lifecycle scripts in temp workspaces), Regression (existing test_common.py), E2E (full lifecycle in temp workspace).
- **Coverage Targets:** All public functions in menu.py; all lifecycle scripts; all tool scripts.
- **Data/Fixtures:** `conftest.py` provides temp workspace fixtures via `tempfile.TemporaryDirectory()`. Fixtures seed minimal `.aib_brain/` and `.aib_memory/` structures for test isolation.
- **Test Execution:** `python -m pytest tests/` from workspace root. Additionally: `python -m pytest .aib_brain/tools/test_common.py` for regression.
- **Acceptance Evidence:** `pytest` terminal output showing all tests passed with 0 failures. Full test suite completes in under 60 seconds.

## Observability & Quality Gates

- **Key Metrics:** Test pass rate = 100%. Test execution time < 60 seconds.
- **Quality Gates:**
  - All tests pass: `python -m pytest tests/` exits with code 0.
  - Existing tests pass: `python -m pytest .aib_brain/tools/test_common.py` exits with code 0.
  - No `.aib_memory/` state modifications outside temp directories during any test run.
  - `run_prompt_action()` subprocess call includes `-p` flag and `--allow-all-tools` (verified by unit test assertion).

## Documentation Touchpoints

- Doc Path: .aib_memory/docs/04 Technology/Compute/CMP-01.md | Change Type: update | Update Trigger: Task 12 | Edit Allowed: Y | Notes: Add CMP-ART-0008 row for test suite.
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Change Type: no-change | Update Trigger: N/A | Edit Allowed: Y | Notes: Test infrastructure is a dev concern; no architectural change needed (per 02-analysis.md §6.5).
- Doc Path: .aib_memory/docs/03 Requirements/RQT-02.md | Change Type: no-change | Update Trigger: N/A | Edit Allowed: Y | Notes: Possibly add test automation acceptance criteria in a future iteration if deemed necessary (per 02-analysis.md §6.5).

## Milestones

- Milestone: M1 | Description: Bug fix complete and verified | Due: After Task 1 completion | Depends On: Task 1 | Exit Criteria: `run_prompt_action()` uses corrected subprocess command; no syntax errors.
- Milestone: M2 | Description: Test infrastructure established | Due: After Task 2 completion | Depends On: Task 2 | Exit Criteria: `conftest.py` exists; imports work from test files.
- Milestone: M3 | Description: All unit and integration tests pass | Due: After Tasks 3–9 completion | Depends On: Tasks 3, 4, 5, 6, 7, 8, 9 | Exit Criteria: `python -m pytest tests/` exits with code 0 for all non-E2E tests.
- Milestone: M4 | Description: E2E lifecycle test passes | Due: After Task 10 completion | Depends On: Task 10 | Exit Criteria: Full lifecycle E2E test passes in temp workspace.
- Milestone: M5 | Description: Regression verified and docs updated | Due: After Tasks 11–12 completion | Depends On: Tasks 11, 12 | Exit Criteria: Existing tests pass; CMP-01 updated with CMP-ART-0008.

## Risks & Mitigations

- R1: Hyphenated script names (e.g., `create-request.py`) cannot be imported as standard Python modules. — P: High, I: Medium — Mitigation: Use `importlib.util.spec_from_file_location()` and `module_from_spec()` in conftest.py to handle non-standard module names.
- R2: Platform-specific `get_key()` implementation (`msvcrt` on Windows, `termios` on Unix) complicates cross-platform test execution. — P: Medium, I: Medium — Mitigation: Mock `get_key()` at function level in tests, not at OS module level; test only the logic above the key input layer.
- R3: `menu.py` global state or terminal dimension dependencies could cause flaky tests. — P: Low, I: Low — Mitigation: Mock `shutil.get_terminal_size()` and any global state in test setup.
- R4: `test_common.py` import path issues when run from `tests/` directory. — P: Low, I: Low — Mitigation: Run existing tests with their own path (`python -m pytest .aib_brain/tools/test_common.py`) separately from the new test suite.

## Acceptance & Handover

- Acceptance Criteria:
  - Selecting a prompt action in the CLI menu invokes `copilot -p "<prompt-text>" --allow-all-tools` via subprocess and displays success/failure status with stdout/stderr output.
  - `run_prompt_action()` captures output via `capture_output=True` and follows the `run_action()` display pattern.
  - All new tests in `tests/` execute via `python -m pytest tests/` with 0 failures.
  - Existing `test_common.py` passes via `pytest` (regression).
  - Test coverage spans: menu.py, common.py, create-request.py, close-request.py, create-iteration.py, close-iteration.py, initialize.py, reverse-engineer.py.
  - At least one test in each category: unit, integration, regression, E2E.
  - Full lifecycle E2E test passes in a temporary workspace.
  - CMP-01 contains CMP-ART-0008 entry for the test suite.

- Handover Artifacts:
  - Modified file: `.aib_brain/tools/menu.py` (bug fix in `run_prompt_action()`).
  - New directory: `tests/` with `conftest.py`, `test_menu.py`, `test_create_request.py`, `test_close_request.py`, `test_create_iteration.py`, `test_close_iteration.py`, `test_initialize.py`, `test_reverse_engineer.py`, `test_lifecycle_e2e.py`.
  - Updated doc: `.aib_memory/docs/04 Technology/Compute/CMP-01.md` (CMP-ART-0008 row).

- Post-Iteration Follow-ups:
  - Consider adding test automation as a formal acceptance criterion in RQT-02 in a future iteration.
  - Consider making the Copilot CLI command configurable via environment variable if portability needs arise.
  - Consider CI integration for running `pytest` on PR events.
