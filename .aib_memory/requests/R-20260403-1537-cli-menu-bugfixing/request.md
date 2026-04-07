## Goal

Fix the confirmed bug in the `run_prompt_action()` function in `.aib_brain/tools/menu.py` where the Copilot CLI is invoked without the required `-p` flag, and create a comprehensive automated test suite using `pytest` in a separate `tests/` directory at the workspace root, covering all Python tool scripts in `.aib_brain/tools/`.

## Background

The AIB Command Menu (`menu.py`, CMP-ART-0006) is the primary human interface for invoking tool scripts and prompt actions (TERM-0013). When the Copilot CLI is detected via `_detect_copilot_cli()`, prompt actions are rendered as navigable/selectable entries.

**Root cause (confirmed via `copilot --help`):** The function `run_prompt_action()` at line ~593 of `menu.py` calls `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])`, passing the prompt text as a bare positional argument. The Copilot CLI requires the `-p, --prompt <text>` flag for non-interactive execution and `--allow-all-tools` to prevent interactive tool-confirmation blocking. The correct invocation is `copilot -p "<text>" --allow-all-tools`. The informational display in `render_menu()` already correctly shows `copilot -p "..."`, confirming the display was correct but execution was not.

**Secondary issue:** `run_prompt_action()` has no error handling, no `capture_output`, and no user feedback — unlike `run_action()` (lines 504-542) which captures stdout/stderr, displays success/failure status, and offers detail view on error.

**Test coverage gap:** The existing `test_common.py` provides unit tests for `common.py` helpers only. No test coverage exists for `menu.py`, lifecycle scripts (`create-request.py`, `close-request.py`, `create-iteration.py`, `close-iteration.py`), `initialize.py`, or `reverse-engineer.py`.

## Scope

- **Bug fix — `run_prompt_action()` in `.aib_brain/tools/menu.py`:**
  - Change the subprocess invocation from `["copilot", <bare-string>]` to `["copilot", "-p", <prompt-text>, "--allow-all-tools"]`.
  - Add `capture_output=True` and `text=True` parameters to the `subprocess.run()` call.
  - Add success/failure display and error detail view mirroring the existing `run_action()` pattern (lines 504-542).
  - No changes to `_detect_copilot_cli()` (confirmed correct — checks `copilot --version`, returns True when binary is on PATH).
  - The Copilot CLI command is hardcoded (not configurable via environment variable).

- **Test suite — new `tests/` directory at workspace root:**
  - Create `tests/conftest.py` with shared fixtures and `sys.path` configuration for importing `.aib_brain/tools/` modules.
  - Create `tests/test_menu.py` — unit tests for:
    - `discover_prompt_actions()` — correct discovery, ordering, and formatting of prompt action dicts.
    - `resolve_menu_state()` — returns correct `MenuState` for active/no-active/closed request scenarios.
    - `filter_visible_actions()` — correct visibility filtering based on `MenuState`.
    - `build_script_actions()` — correct action list construction and renumbering.
    - `validate_param()` — input validation for action parameters.
    - `collect_parameters()` — parameter collection with mocked `input()`.
    - `build_command()` — correct command list construction.
    - `run_prompt_action()` — subprocess called with `["copilot", "-p", ..., "--allow-all-tools"]` (mocked `subprocess.run`).
    - `_detect_copilot_cli()` — returns True/False based on mocked subprocess responses.
  - Create `tests/test_create_request.py` — integration tests: workspace setup, register update, folder creation, iteration seeding, duplicate detection, missing title.
  - Create `tests/test_close_request.py` — integration tests: close active request, auto-close iteration, already-closed request, missing request.
  - Create `tests/test_create_iteration.py` — integration tests: create next iteration, enforce single active, missing request.
  - Create `tests/test_close_iteration.py` — integration tests: close active iteration, explicit ID, no active iteration.
  - Create `tests/test_initialize.py` — integration tests: first run initialization, idempotent rerun, force overwrite.
  - Create `tests/test_reverse_engineer.py` — unit tests: file inventory, exclusion rules, output format.
  - Create `tests/test_lifecycle_e2e.py` — full lifecycle E2E test: create-request → create-iteration → close-iteration → close-request via subprocess calls in a temporary workspace, verifying register and artifact state at each step.
  - Verify existing `test_common.py` tests pass when run via `pytest`.

- (implicit rule - AIB framework) Update CMP-01 with a new test suite catalog entry (CMP-ART-0008).

## Out of scope

- Making the Copilot CLI invocation command configurable (environment variable or config file).
- Changes to `.aib_brain/prompts/*.md` prompt content files.
- Changes to `.github/workflows/` CI workflows.
- Changes to `scripts/release_bookkeeping.py`.
- Live Copilot CLI integration tests (all Copilot CLI calls must be mocked in tests).
- UI/UX redesign of the CLI menu beyond the bug fix and error handling improvement.
- Performance optimization of tool scripts.
- Changes to `_detect_copilot_cli()` detection logic (confirmed correct).

## Constraints

- Python 3.10+ stdlib only for production code in `.aib_brain/tools/menu.py`.
- `pytest` is permitted as a dev-only dependency; it must not be required at runtime.
- Tests must not modify the developer's actual `.aib_memory/` state — all integration and E2E tests must use `tempfile.TemporaryDirectory()` for isolation.
- Tests must not require network access, a live Copilot CLI binary, or GitHub connectivity.
- All Copilot CLI subprocess calls in tests must be mocked via `unittest.mock.patch`.
- Platform-specific key input (`msvcrt` on Windows, `termios` on Unix) in `menu.py` must be mocked at the `get_key()` function level in tests, not at the low-level OS module level.
- Tests must complete in under 60 seconds total on a standard developer workstation.
- The `tests/conftest.py` must handle `sys.path` manipulation so tests can import from `.aib_brain/tools/`.

## Success criteria

- Selecting a prompt action in the CLI menu invokes `copilot -p "<prompt-text>" --allow-all-tools` via subprocess, and the user sees a "Status: Success" or "Status: Failed (exit code N)" message with stdout/stderr output.
- `run_prompt_action()` captures stdout/stderr via `capture_output=True` and displays them to the user, following the same pattern as `run_action()`.
- All new test files in `tests/` execute successfully via `python -m pytest tests/` with 0 failures.
- Existing `.aib_brain/tools/test_common.py` tests continue to pass when run via `pytest` (regression).
- Test coverage spans all target modules: `menu.py`, `common.py`, `create-request.py`, `close-request.py`, `create-iteration.py`, `close-iteration.py`, `initialize.py`, `reverse-engineer.py`.
- At least one test exists in each category: unit, integration, regression, smoke, and E2E.
- The full lifecycle E2E test (create-request → create-iteration → close-iteration → close-request) passes in a temporary workspace.
- CMP-01 is updated with a new catalog entry for the test suite.
