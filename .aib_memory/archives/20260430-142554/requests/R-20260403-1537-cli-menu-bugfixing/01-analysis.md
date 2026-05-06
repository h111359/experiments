# Analysis

## 1. Executive Summary

- Request ID: R-20260403-1537

- Request title: CLI menu bugfixing

- Iteration ID: 01

- The user reports that choosing a prompt action in the AIB interactive CLI menu does not perform the expected action, even when the Copilot CLI is detected as available.

- The request also asks for comprehensive automated tests (unit, integration, regression, smoke, end-to-end) covering the entire workspace codebase.

- This is the first iteration; no prior iterations or conflicting decisions exist.

- The scope spans two distinct workstreams: (1) diagnosing and fixing bugs in the menu/prompt-action execution path, and (2) designing and implementing a test suite for all AIB Python scripts.

- Primary artifacts under investigation: `.aib_brain/tools/menu.py`, `.aib_brain/tools/common.py`, `.aib_brain/run.bat`, `.aib_brain/run.sh`, and all tool scripts in `.aib_brain/tools/`.

- Existing test file: `.aib_brain/tools/test_common.py` covers `common.py` helpers but does not cover `menu.py`, lifecycle scripts, or prompt action execution.

## 2. Scope Interpretation

- **In scope:** Diagnose and fix the bug where selecting a prompt action in the CLI menu does not execute the intended Copilot CLI invocation.

- **In scope:** Investigate additional bugs across all tool scripts (menu.py, common.py, create-request.py, close-request.py, create-iteration.py, close-iteration.py, initialize.py, reverse-engineer.py).

- **In scope:** Create automated tests covering unit, integration, regression, smoke, and end-to-end layers for the entire workspace Python codebase.

- **In scope:** Ensure tests can be executed automatically (e.g., via `python -m pytest` or `python -m unittest`).

- (implicit rule - AIB framework) Documentation updates to product-docs referencing test strategy (CMP-01, CMP-02, RQT-02) if test infrastructure is added as a new component.

- **Out of scope (implicit):** Changes to `.aib_brain/prompts/*.md` prompt content itself — those are AI-driven artifacts, not executable code.

- **Out of scope (implicit):** Changes to CI/CD workflows (`.github/workflows/`) unless directly required to run the new test suite.

## 3. Domain Knowledge Essentials

- **AIB (AI Builder):** A minimal, model-agnostic framework for specification-driven development. Organizes work as requests and iterations stored in `.aib_memory/`.

- **Prompt Action:** A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file; navigable and executable when Copilot CLI is available; informational-only when CLI is absent (see TERM-0013, KNW-01).

- **Copilot CLI:** An external command-line tool (`copilot`) used to execute prompt files. Detection is performed by running `copilot --version` (see `_detect_copilot_cli()` in menu.py).

- **Personas impacted:** DEVELOPER (runs CLI menu daily), AI_AGENT (executes prompt-driven workflows), MAINTAINER (owns `.aib_brain` assets).

- **Business process impacted:** BP-0001 (Initialize), indirectly all lifecycle processes since the menu is the primary entry point for tool scripts.

- **Acceptance impact:** If prompt actions silently fail, the DEVELOPER persona loses confidence in the AIB workflow and must fall back to manual Copilot invocations.

## 4. Technical Knowledge & Terms

- **menu.py:** Interactive terminal UI (~650 LOC) that discovers tool scripts and prompt files, renders a navigable menu, and dispatches execution via `subprocess.run`.

- **common.py:** Shared helpers (~370 LOC) for Markdown table parsing, workspace validation, request/iteration resolution, file I/O.

- **run.bat / run.sh:** Shell wrappers that invoke `menu.py --workspace <parent-dir>`.

- **EXCLUDE_SCRIPTS:** Set in menu.py containing script filenames that should not appear as menu entries: `{"menu.py", "common.py", "initialize.py", "reverse-engineer.py", "test_common.py"}`.

- **`_detect_copilot_cli()`:** Lazy-cached function that runs `copilot --version` via subprocess. Returns `True` if exit code is 0.

- **`run_prompt_action()`:** Calls `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` — this is the function invoked when a user selects a prompt action.

- **`choose_action()`:** Main menu loop. Handles UP/DOWN/ENTER/DIGIT/QUIT key events. For prompt actions selected via ENTER, it calls `run_prompt_action()` and then `continue` (returns to menu loop). For prompt actions selected via DIGIT, it also calls `run_prompt_action()` and then `continue`.

- **test_common.py:** Existing unittest suite (~900 LOC) covering common.py helpers. No coverage for menu.py or lifecycle scripts beyond one integration test for close-request auto-closing iterations.

- **Python 3.10+** is the runtime requirement. Tests use `unittest` and `tempfile`.

## 5. Assumptions

- Assumption A1: The Copilot CLI binary is named `copilot` and is on the system PATH when the user reports the bug.
  - Rationale: The `_detect_copilot_cli()` function checks `copilot --version`; if this succeeds, the CLI is considered available.
  - Risk if false: The detection itself may be the bug — if `copilot` resolves to something else or has changed its CLI interface.
  - Falsification method: Run `copilot --version` manually in the same terminal and verify output.

- Assumption A2: The `copilot` CLI accepts a bare string argument as a prompt instruction (i.e., `copilot "Execute the prompt defined in ..."`).
  - Rationale: `run_prompt_action()` calls `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` with no flags.
  - Risk if false: The `copilot` CLI may require specific flags such as `copilot -p "..."` or `copilot chat "..."` or `gh copilot suggest "..."`. This is the most likely root cause of the reported bug.
  - Falsification method: Check the Copilot CLI documentation or run `copilot --help` to verify accepted invocation syntax.

- Assumption A3: The prompt_file path in the action dict is correctly resolved relative to the workspace (e.g., `.aib_brain/prompts/aib-create-analysis.md`).
  - Rationale: `discover_prompt_actions()` constructs the path as `str(Path(".aib_brain") / "prompts" / path.name).replace("\\", "/")`.
  - Risk if false: An incorrect relative path would cause Copilot CLI to fail silently or with an error the user doesn't see.
  - Falsification method: Print or log the constructed path and verify it matches an actual file.

- Assumption A4: The test framework to be used is `pytest` (standard for Python projects) or `unittest` (already used in test_common.py).
  - Rationale: Existing tests use `unittest`. `pytest` can run `unittest`-based tests natively.
  - Risk if false: User may prefer a different framework.
  - Falsification method: Ask user for preference.

- Assumption A5: End-to-end tests will exercise the tool scripts as subprocesses (same pattern as `TestCloseRequestAutoClose`) rather than requiring a live Copilot CLI or GitHub connection.
  - Rationale: Copilot CLI is an external dependency that cannot be assumed available in CI.
  - Risk if false: True E2E coverage of prompt actions requires mocking or a real Copilot CLI.
  - Falsification method: Clarify with user whether prompt-action E2E tests should mock the CLI or require it.

## 6. Impact Assessment

### 6.1 Affected Components / Areas

| Component (from ARCH-01) | Change type | Impact |
| --- | --- | --- |
| AIB Command Menu (menu.py) | modify | Fix prompt action invocation; add testability hooks |
| AIB Tool Scripts (common.py) | modify | Possible minor refactors to improve testability |
| AIB Tool Scripts (create-request.py, close-request.py, create-iteration.py, close-iteration.py) | none / test-only | New tests wrapping existing functionality |
| AIB Tool Scripts (initialize.py) | none / test-only | New tests wrapping existing functionality |
| AIB Tool Scripts (reverse-engineer.py) | none / test-only | New tests wrapping inventory functionality |
| AIB Tool Scripts (test_common.py) | modify | Extend with new test modules or add to existing file |

### 6.2 Change Type and Dependencies

- **menu.py → `run_prompt_action()`**: Modify the Copilot CLI invocation to use correct command syntax. Depends on verifying actual Copilot CLI interface.
- **menu.py → `_detect_copilot_cli()`**: Potential fix if detection logic is also incorrect (e.g., wrong binary name).
- **New test files → all tool scripts**: Add test modules; depends on all tool scripts being importable or testable as subprocesses.

### 6.3 Domain Impacts

- DOMAIN (ARCH): Minor impact — test infrastructure may warrant a new row in ARCH-01 component inventory if a dedicated test runner or configuration is introduced.
  - Relevant: ARCH-01

- DOMAIN (CMP): Impact — CMP-01 script catalog needs a new entry for the test suite.
  - Relevant: CMP-01

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): No impact detected.

- DOMAIN (RQT): Impact — RQT-02 acceptance criteria should reference automated test execution.
  - Relevant: RQT-02

- DOMAIN (OBS): No impact detected.

- DOMAIN (SEC): No impact detected.

### 6.4 Constraints

- Tests must run with Python 3.10+ and only stdlib + `pytest` (or `unittest`).
- Tests must not require a live Copilot CLI, GitHub connection, or network access.
- Tests must be non-destructive to the developer's actual `.aib_memory/` state — use temporary directories.
- Tests must be runnable via a single command (e.g., `python -m pytest .aib_brain/tools/`).

### 6.5 Required Documentation Updates

- CMP-01 - Notebook/Script Catalog
  Required update? YES
  Reason: New test suite entry (CMP-ART-0008 or similar) for the test runner.

- RQT-02 - Requirements Document
  Required update? POSSIBLY
  Reason: Add test automation as an acceptance criterion.

- ARCH-01 - High-level Architecture
  Required update? POSSIBLY
  Reason: Only if test infrastructure introduces a new component.

### 6.6 Decision Points

- **DP-1: Copilot CLI invocation syntax**
  - Option A: Fix `run_prompt_action()` to use `copilot -p "..."` flag syntax.
  - Option B: Fix to use `gh copilot suggest "..."` (GitHub CLI extension form).
  - Option C: Make the invocation command configurable.
  - Implication: Option A is simplest if the standalone `copilot` binary supports `-p`. Option B requires `gh` CLI. Option C is most flexible.
  - Recommendation: Verify the actual CLI syntax first (see Open Questions), then implement the correct one. Option C is the safest long-term choice.

- **DP-2: Test framework**
  - Option A: Continue with `unittest` only (consistent with existing test_common.py).
  - Option B: Adopt `pytest` as the test runner (can still run unittest-based tests).
  - Recommendation: Option B — `pytest` provides better discovery, output, and fixture support while remaining compatible with existing tests.

- **DP-3: Test file organization**
  - Option A: Single large test file (`test_common.py` expanded).
  - Option B: Multiple test files per module (e.g., `test_menu.py`, `test_create_request.py`, etc.) in `.aib_brain/tools/`.
  - Option C: Separate `tests/` directory at workspace root.
  - Recommendation: Option B — keeps tests co-located with source, enables granular execution.

## 7. Research Plan and Findings

### Methodology
- Internal docs scan: Read all 27 product-doc references plus Concepts.md.
- Repository scan: Read all Python scripts in `.aib_brain/tools/`, shell wrappers, and existing test file.
- Pattern scan: Analyzed menu.py control flow for prompt action dispatch and Copilot CLI invocation.

### Evidence Summary

**Bug diagnosis — `run_prompt_action()`:**

The function at line ~593 of menu.py:

```python
def run_prompt_action(paction: dict[str, str]) -> None:
    subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])
```

This passes a free-form text string as the sole argument to `copilot`. The GitHub Copilot CLI likely does not accept a bare positional argument as a prompt. Typical invocation patterns for Copilot CLI are:
- `gh copilot suggest "..."` (via GitHub CLI extension)
- `copilot -p "..."` (hypothetical standalone flag)

The informational-only display in `render_menu()` (line ~582) shows: `copilot -p "Execute the prompt defined in ..."` — note the `-p` flag. But `run_prompt_action()` does **not** use `-p`. This discrepancy is the most probable bug.

**Additional findings:**

1. **`choose_action()` return semantics**: When a prompt action is selected, `run_prompt_action()` is called and then `continue` is used — meaning the function returns to the menu loop. The menu does not wait for or display results of the copilot command. The `subprocess.run()` call in `run_prompt_action()` does block, but stdout/stderr are not captured or displayed. If the command fails, the user sees nothing.

2. **No error handling in `run_prompt_action()`**: Unlike `run_action()` (which captures output and displays Status: Success/Failed), `run_prompt_action()` has no error handling, no output capture, and no user feedback.

3. **`_detect_copilot_cli()` uses `copilot --version`**: If the actual CLI binary is `gh` (with `copilot` as a subcommand extension), then `copilot --version` may succeed for a different `copilot` binary (or fail entirely), leading to incorrect detection.

4. **Existing test coverage gap**: `test_common.py` has no tests for `menu.py` functions (discover_prompt_actions, resolve_menu_state, filter_visible_actions, run_prompt_action, choose_action, build_command, collect_parameters, validate_param, etc.).

### Gaps and Unknowns
- Exact Copilot CLI invocation syntax is unverified from documentation.
- Whether the user has `copilot` or `gh copilot` on their PATH.
- Whether `_detect_copilot_cli()` returns True or False in the user's environment.

### Proposed Validation Actions
- User to confirm: what does `copilot --version` output in their terminal?
- User to confirm: what does `copilot --help` show as valid invocation syntax?
- Alternatively: check if `gh copilot` is the intended invocation path.

### Files Read

- `.aib_brain/tools/menu.py` — Main menu logic; identified `run_prompt_action()` bug and missing error handling.
- `.aib_brain/tools/common.py` — Shared helpers; no bugs found; good testability.
- `.aib_brain/tools/create-request.py` — Request creation script; no bugs found.
- `.aib_brain/tools/close-request.py` — Request closing script with auto-close iteration; no bugs found.
- `.aib_brain/tools/create-iteration.py` — Iteration creation script; no bugs found.
- `.aib_brain/tools/close-iteration.py` — Iteration closing script; no bugs found.
- `.aib_brain/tools/initialize.py` — Memory initialization script; no bugs found.
- `.aib_brain/tools/reverse-engineer.py` — File inventory helper; no bugs found.
- `.aib_brain/tools/test_common.py` — Existing test suite (~900 LOC); covers common.py only.
- `.aib_brain/run.bat` — Windows launcher; correct invocation pattern.
- `.aib_brain/run.sh` — Unix launcher; correct invocation pattern.
- `.aib_brain/prompts/aib-create-analysis.md` — Prompt file; read for context.
- `.aib_memory/requests_register.md` — Active request confirmed as R-20260403-1537.
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/iterations.md` — Active iteration confirmed as 01.
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/request.md` — Request content read.
- `.aib_memory/references.md` — All 28 references enumerated; 27 product-docs identified.
- `.aib_brain/Concepts.md` — AIB concepts and action contract read.
- `.aib_brain/conventions/analysis-convention.md` — Analysis format convention read.
- `.aib_brain/conventions/request-convention.md` — Request format convention read.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Architecture; confirmed AIB Command Menu component description.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — Topology; stub only.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — Capacity; stub only.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — ADRs; no bug-related content.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — Runtime sequences; useful context for menu flow.
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — Resource catalog; no bug-related content.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Script catalog; CMP-ART-0006 describes menu.py.
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — Algorithm register; ALG-0002 describes resolution logic.
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — Source catalog; no bug-related content.
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — Data models; useful for register parsing tests.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — Data lineage; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — Storage strategy; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — Consumption patterns; no bug-related content.
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — Metrics; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — Data quality; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — Archiving policy; no bug-related content.
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — Dashboard inventory; empty.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Glossary; TERM-0013 defines Prompt Action.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — Business processes; BP-0001 to BP-0003.
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — Personas and use cases.
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — Logging; stub only.
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — Product charter; stub only.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — Requirements; FR-008 describes menu prompt action gating.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — Access; stub only.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — Data protection; stub only.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — Secrets; stub only.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — Network security; stub only.

## 8. Rewrite Proposal of the Request

See the updated `request.md` file written alongside this analysis.

## 9. Solution Options

### Option A: Minimal Bug Fix + Focused Test Suite

**Overview:** Fix the `run_prompt_action()` invocation to use the correct Copilot CLI command syntax (matching the informational display's `-p` flag). Add error handling and user feedback. Create targeted test modules for each tool script.

**Benefits:**
- Directly addresses the reported bug with minimal change surface.
- Tests focus on areas with known gaps (menu.py, lifecycle scripts).
- Low risk of regressions.

**Trade-offs:**
- Does not address potential issues with the CLI detection mechanism.
- Does not make the copilot command configurable.

**Constraints:**
- Requires confirmation of the correct Copilot CLI syntax.

**Risks:**
- If the CLI syntax varies by installation, the fix may not be universal.

**Expected effort:** Small (bug fix: hours; tests: 1-2 days).

**High-level acceptance-test ideas:**
- Unit test: `run_prompt_action()` constructs the correct subprocess command (mocked).
- Integration test: menu renders prompt actions correctly with/without CLI.
- Regression test: existing test_common.py tests still pass.

### Option B: Comprehensive Fix + Configurable CLI + Full Test Suite

**Overview:** Fix `run_prompt_action()`, make the Copilot CLI command configurable (environment variable or config file), improve `_detect_copilot_cli()` to support both `copilot` and `gh copilot`, add comprehensive error handling with captured output. Create a full test suite organized per-module.

**Benefits:**
- Addresses root cause and future-proofs against CLI variations.
- Error handling gives users actionable feedback.
- Full test suite provides long-term confidence.

**Trade-offs:**
- Larger scope of change.
- Configuration adds complexity.

**Constraints:**
- Still requires knowing at least one valid CLI invocation to set as default.

**Risks:**
- Over-engineering if the CLI interface is stable.

**Expected effort:** Medium (fix + config: 1 day; tests: 2-3 days).

**High-level acceptance-test ideas:**
- All tests from Option A.
- Unit test: configurable CLI command is respected.
- Unit test: detection works for both `copilot` and `gh copilot`.
- Smoke test: menu launches, navigates, and exits cleanly.
- E2E test: full lifecycle (create-request → create-iteration → close-iteration → close-request) via subprocess.

### Recommendation

**Option B** is recommended. The configurability provides resilience against Copilot CLI interface changes, and the comprehensive test suite addresses the user's explicit request for "all kind of tests." The additional effort is proportionate to the value of long-term maintainability.

## 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | May need new test-infrastructure component row |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | New test suite catalog entry |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | Test automation acceptance criterion |

## 11. Operational & Documentation Implications

- **Runbooks:** No change needed; tests are developer-local.
- **SLAs/SLOs:** No change.
- **Monitoring/Observability:** No change; test results are local console output.
- **Data quality rules:** No change.
- **Product documentation:** CMP-01 needs a new artifact entry for the test suite. RQT-02 may need a new functional requirement for test automation (e.g., FR-010).

## 12. Risks

- Risk R1: Copilot CLI invocation syntax is unknown without documentation verification.
  - Probability: Medium
  - Impact: High
  - Mitigation: Ask user to verify `copilot --help` or `gh copilot --help` output before implementing the fix.
  - Owner (role): DEVELOPER

- Risk R2: Tests that mock `subprocess.run` may not catch real invocation failures.
  - Probability: Low
  - Impact: Medium
  - Mitigation: Include at least one integration test that exercises the actual subprocess call with a known-good script.
  - Owner (role): DEVELOPER

- Risk R3: Adding a test framework dependency (pytest) may conflict with the "stdlib only" constraint for tool scripts.
  - Probability: Low
  - Impact: Low
  - Mitigation: pytest is a dev-only dependency, not required at runtime. Document in a `dev-requirements.txt` or use unittest only.
  - Owner (role): MAINTAINER

- Risk R4: Menu.py uses platform-specific key input (msvcrt on Windows, termios on Unix) which is hard to test.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Extract key input behind an abstraction that can be mocked in tests.
  - Owner (role): DEVELOPER

## 13. Disambiguation Questionnaire

- **Q1: What is the exact Copilot CLI invocation that works in the user's environment?**
  - Chosen Answer: Unknown — needs user verification.
  - Rationale: `run_prompt_action()` uses `subprocess.run(["copilot", <string>])` but the informational display shows `copilot -p "..."`. The correct syntax must be verified.
  - Evidence: menu.py lines ~582 (informational display with `-p`) vs ~593 (`run_prompt_action()` without `-p`).
  - Impact if changed: Correct CLI syntax is essential for the fix.

- **Q2: Should the test suite use `pytest` or `unittest`?**
  - Chosen Answer: `pytest` (recommended) — but user preference is needed.
  - Rationale: pytest runs unittest tests natively and adds better discovery, parametrize, and fixture support.
  - Evidence: Existing test_common.py uses unittest.
  - Impact if changed: If unittest-only, some test patterns become more verbose.

- **Q3: Should prompt-action E2E tests require a live Copilot CLI?**
  - Chosen Answer: No — mock the CLI call.
  - Rationale: CI environments typically lack Copilot CLI. Mocking is safer and more portable.
  - Evidence: No CI config for Copilot CLI in `.github/workflows/`.
  - Impact if changed: If live CLI is required, tests cannot run in CI.

## 14. Open Questions & Next Actions

1. **What is the correct Copilot CLI invocation command?**
   - Owner: User (DEVELOPER)
   - Due: Before implementation begins
   - Resolution path: Run `copilot --help` or `gh copilot --help` and share the output. Alternatively, verify which binary (`copilot` standalone or `gh copilot` extension) is installed.

2. **Does the user want `pytest` or `unittest` as the test framework?**
   - Owner: User (DEVELOPER)
   - Due: Before test implementation
   - Resolution path: State preference. Default recommendation is `pytest`.

3. **Should tests be co-located with source (`.aib_brain/tools/test_*.py`) or in a separate `tests/` directory?**
   - Owner: User (DEVELOPER)
   - Due: Before test implementation
   - Resolution path: State preference. Default recommendation is co-located.
