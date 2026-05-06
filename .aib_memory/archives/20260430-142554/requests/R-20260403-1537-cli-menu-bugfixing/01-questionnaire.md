# Questionnaire — Iteration 01

## 1. Business & Functional Questions

### QID-BF-001
**Intent:** Determine the exact Copilot CLI binary and invocation syntax available on the developer's system so the bug fix targets the correct command.
**Rationale:** The `run_prompt_action()` function calls `subprocess.run(["copilot", <bare-string>])` but the informational display uses `copilot -p "..."`. The correct CLI syntax must be confirmed before a fix can be implemented. This directly impacts Scope, Requirements, and Architecture.
**Impact Areas:** Scope, Requirements, Architecture
**Answer Type:** single-select
**Options:**
- [ ] A) Standalone `copilot` binary with `-p` flag (e.g., `copilot -p "prompt text"`) (recommended)
- [ ] B) GitHub CLI extension `gh copilot` (e.g., `gh copilot suggest "prompt text"`)
- [ ] C) Standalone `copilot` binary with different flag syntax (describe below)
- [ ] D) Not sure — will provide output of `copilot --help` or `gh copilot --help`
- [x] Other — (describe here): Make research yourself, run "copilot --help", search Internet
**Constraints & Guards:** If D is selected, paste the help output in the Answer Box below. If Other, describe the exact invocation command that works.

### QID-BF-002
**Intent:** Decide whether the Copilot CLI invocation command should be made configurable or hardcoded to a single syntax.
**Rationale:** Different developer environments may have different Copilot CLI installations (standalone vs. GitHub CLI extension). Making the command configurable via an environment variable (e.g., `AIB_COPILOT_CMD`) adds resilience but increases complexity. This affects Architecture and Operations.
**Impact Areas:** Architecture, Operations, User Experience
**Answer Type:** single-select
**Options:**
- [ ] A) Make it configurable via environment variable with a sensible default (recommended)
- [x] B) Hardcode the correct command based on QID-BF-001 answer
- [ ] C) Support auto-detection of both `copilot` and `gh copilot` at runtime
- [ ] Other — (describe here):
**Constraints & Guards:** Option C implies more complex detection logic but maximum portability. Option A is the simplest way to support both.

## 2. Architecture & Technical Questions

### QID-AT-001
**Intent:** Select the test framework for the new automated test suite.
**Rationale:** The existing `test_common.py` uses `unittest` (stdlib). `pytest` offers better test discovery, parametrize, fixtures, and output while being fully compatible with existing unittest-based tests. Choosing the framework affects how tests are structured and invoked. This impacts Architecture and Timeline.
**Impact Areas:** Architecture, Timeline
**Answer Type:** single-select
**Options:**
- [x] A) `pytest` — install as dev dependency; can run existing unittest tests natively (recommended)
- [ ] B) `unittest` only — no additional dependencies; consistent with existing test file
- [ ] Other — (describe here):
**Constraints & Guards:** If A is selected, `pytest` will be listed in a `dev-requirements.txt` or equivalent. Production code remains stdlib-only.

### QID-AT-002
**Intent:** Decide where test files should be located in the repository.
**Rationale:** Test file organization affects discoverability, import paths, and CI configuration. Co-locating tests with source in `.aib_brain/tools/` is consistent with the existing `test_common.py` placement. A separate `tests/` directory provides cleaner separation but requires import path adjustments.
**Impact Areas:** Architecture, Operations
**Answer Type:** single-select
**Options:**
- [ ] A) Co-located with source in `.aib_brain/tools/test_*.py` — consistent with existing layout (recommended)
- [x] B) Separate `tests/` directory at workspace root with subdirectories mirroring source
- [ ] C) Separate `.aib_brain/tests/` directory under the brain folder
- [ ] Other — (describe here):
**Constraints & Guards:** If B or C is selected, import path configuration may be needed (e.g., `conftest.py` or `sys.path` manipulation).

### QID-AT-003
**Intent:** Confirm the desired scope of end-to-end (E2E) tests for the lifecycle workflow.
**Rationale:** The request asks for E2E tests. The fullest E2E test would exercise the entire sequence: create-request → create-iteration → close-iteration → close-request via subprocess calls in a temporary workspace, verifying register and artifact state at each step. This is the most valuable but also the most complex test to maintain.
**Impact Areas:** Scope, Architecture, Timeline
**Answer Type:** single-select
**Options:**
- [x] A) Full lifecycle E2E: create-request → create-iteration → close-iteration → close-request in one test (recommended)
- [ ] B) Partial E2E: test each script independently as subprocess, but not chained
- [ ] C) Skip E2E; focus on unit and integration tests only
- [ ] Other — (describe here):
**Constraints & Guards:** All E2E tests use temporary directories and do not affect actual workspace state.

## 3. Appendix — Answer Encoding Rules

- Checkbox unchecked: `- [ ]`
- Checkbox checked: `- [x]` (lowercase or uppercase X)
- Single-select: exactly one option must be checked; `Other` counts as an option if checked.
- Multi-select: any number of options may be checked; zero checked = unanswered.
- If `Other` is checked, provide a description after the colon.
- `(recommended)` marks the suggested default — selecting a different option is perfectly valid.
