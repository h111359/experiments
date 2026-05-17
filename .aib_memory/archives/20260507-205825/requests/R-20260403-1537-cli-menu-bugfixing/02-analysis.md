# Analysis — Iteration 02

## 1. Executive Summary

- Request ID: R-20260403-1537

- Request title: CLI menu bugfixing

- Iteration ID: 02

- This is a follow-up iteration that incorporates the user's questionnaire answers from iteration 01 and resolves previously open questions through direct Copilot CLI research.

- The primary bug is now confirmed: `run_prompt_action()` in `menu.py` invokes `subprocess.run(["copilot", <bare-string>])` without the required `-p` flag. The Copilot CLI `--help` output confirms that `-p, --prompt <text>` is the correct flag for non-interactive prompt execution.

- The user has decided on: (a) hardcoding the correct `copilot -p` command, (b) using `pytest` as the test framework, (c) placing tests in a separate `tests/` directory at workspace root, and (d) implementing full lifecycle E2E tests.

- Iteration 01 identified the root cause and proposed two solution options. This iteration narrows the scope to the user's chosen approach, resolves the Copilot CLI syntax question through live research, and provides a refined, implementation-ready request rewrite.

- No conflicts between iteration 01 and iteration 02 — iteration 02 complements iteration 01 by resolving all open questions and committing to specific decisions.

## 2. Scope Interpretation

- **In scope:** Fix `run_prompt_action()` in `.aib_brain/tools/menu.py` to use `copilot -p "..."` flag syntax for non-interactive prompt execution.

- **In scope:** Add error handling and user feedback to `run_prompt_action()` consistent with the existing `run_action()` pattern (capture stdout/stderr, display success/failure status, offer detail view on failure).

- **In scope:** Verify `_detect_copilot_cli()` correctness — confirmed working (checks `copilot --version`, which returns exit code 0 when the CLI is installed).

- **In scope:** Create automated test suite using `pytest` in a separate `tests/` directory at workspace root, covering: `menu.py`, `common.py`, `create-request.py`, `close-request.py`, `create-iteration.py`, `close-iteration.py`, `initialize.py`, `reverse-engineer.py`.

- **In scope:** Full lifecycle E2E test: create-request → create-iteration → close-iteration → close-request via subprocess in a temporary workspace.

- **Out of scope:** Making the Copilot CLI command configurable (user chose hardcoded approach per QID-BF-002).

- **Out of scope:** Changes to `.aib_brain/prompts/*.md` prompt content files.

- **Out of scope:** Changes to `.github/workflows/` CI workflows.

- **Out of scope:** Changes to `scripts/release_bookkeeping.py`.

- **Out of scope:** Live Copilot CLI integration tests (all Copilot CLI calls must be mocked).

- **Out of scope:** UI/UX redesign of the CLI menu beyond the bug fix and error handling improvement.

- **Out of scope:** Performance optimization of tool scripts.

- (implicit rule - AIB framework) Documentation updates to CMP-01 for new test suite catalog entry and RQT-02 if test automation acceptance criteria are added.

## 3. Domain Knowledge Essentials

- **AIB (AI Builder):** Minimal, model-agnostic framework for specification-driven development. Organizes work as requests and iterations stored in `.aib_memory/` (TERM-0001).

- **Prompt Action (TERM-0013):** A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file; navigable and executable when Copilot CLI is available; informational-only when CLI is absent.

- **Copilot CLI:** GitHub Copilot CLI binary (`copilot`). Accepts `-p, --prompt <text>` for non-interactive prompt execution. Supports `--allow-all-tools` to bypass confirmation prompts in scripted mode.

- **Personas impacted:** DEVELOPER (runs CLI menu daily as primary interface), AI_AGENT (executes prompt-driven workflows), MAINTAINER (owns `.aib_brain` assets and test infrastructure).

- **Business process impacted:** All lifecycle processes are invoked via the CLI menu (BP-0001 through BP-0003); prompt actions are the AI-driven complement to script actions.

- **Acceptance impact:** The bug renders prompt actions non-functional for all users with Copilot CLI installed, forcing manual invocation.

## 4. Technical Knowledge & Terms

- **menu.py:** Interactive terminal UI (~665 LOC) implementing `choose_action()` loop with cross-platform key input (`msvcrt` on Windows, `termios` on Unix). Dispatches script actions via `run_action()` and prompt actions via `run_prompt_action()`.

- **`run_prompt_action(paction)`:** The buggy function. Currently calls `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` — missing the `-p` flag.

- **`run_action(python_exe, tools_dir, action, workspace_default)`:** Reference implementation for action execution. Captures output via `capture_output=True`, displays success/failure status, offers detail view on error.

- **`_detect_copilot_cli()`:** Lazy-cached detection via `copilot --version`. Confirmed correct — returns `True` when the Copilot CLI binary is on PATH.

- **`discover_prompt_actions(brain_dir)`:** Discovers `aib-*.md` files in `.aib_brain/prompts/`, orders per `_PROMPT_ORDER`, returns list of action dicts with `title`, `description`, `prompt_file` keys.

- **pytest:** User-selected test framework. Supports native discovery of `test_*.py` files, parametrize decorators, fixtures, and can run existing `unittest`-based tests.

- **subprocess.run:** Python stdlib function for running external commands. Key parameters: `capture_output=True`, `text=True`, `timeout`.

- **EXCLUDE_SCRIPTS:** Set in menu.py: `{"menu.py", "common.py", "initialize.py", "reverse-engineer.py", "test_common.py"}`. Prevents non-tool scripts from appearing as menu entries.

## 5. Assumptions

- Assumption A1: The Copilot CLI binary is named `copilot` and is on the system PATH.
  - Rationale: `_detect_copilot_cli()` checks `copilot --version` and the `copilot --help` output was successfully retrieved during this analysis.
  - Risk if false: The fix would invoke a wrong binary.
  - Falsification method: Verified — `copilot --help` returned valid output confirming the binary exists and responds.

- Assumption A2: The correct Copilot CLI invocation for non-interactive prompt execution is `copilot -p "<text>"`.
  - Rationale: The `copilot --help` output explicitly states: `-p, --prompt <text>  Execute a prompt in non-interactive mode (exits after completion)`.
  - Risk if false: N/A — confirmed by live CLI help output.
  - Falsification method: Verified — ran `copilot --help` and confirmed `-p` flag documentation.

- Assumption A3: The `--allow-all-tools` flag (or equivalent) should be included in the non-interactive invocation so the CLI does not hang waiting for tool-use confirmations.
  - Rationale: The `copilot --help` output states `--allow-all-tools` is "required for non-interactive mode". Without it, the Copilot CLI may prompt for confirmation interactively, which would block the subprocess.
  - Risk if false: If the user's Copilot CLI configuration already auto-approves tools, the flag is redundant but harmless.
  - Falsification method: Test with and without the flag in a controlled invocation.

- Assumption A4: Existing `test_common.py` tests will continue to pass when run through `pytest` from the new `tests/` directory.
  - Rationale: `pytest` natively supports `unittest.TestCase` subclasses. The existing tests use `unittest` patterns.
  - Risk if false: Import path issues if `test_common.py` relies on relative imports.
  - Falsification method: Run `pytest` with both old and new test files and verify all pass.

- Assumption A5: E2E lifecycle tests will use `tempfile.TemporaryDirectory()` to create isolated workspace copies and invoke tool scripts as subprocesses.
  - Rationale: This is the pattern already used in the existing `TestCloseRequestAutoClose` test in `test_common.py`.
  - Risk if false: Minimal — this is a well-established pattern.
  - Falsification method: Implement and verify tests pass in temp directories.

## 6. Impact Assessment

### 6.1 Affected Components / Areas

| Component (from ARCH-01) | Change type | Impact |
| --- | --- | --- |
| AIB Command Menu (menu.py) | modify | Fix `run_prompt_action()` to use `copilot -p` flag; add error handling and output capture |
| AIB Tool Scripts (test infrastructure) | add | New `tests/` directory at workspace root with test modules for all tool scripts |
| AIB Tool Scripts (common.py, lifecycle scripts) | none / test-only | No production code changes; new test coverage only |

### 6.2 Change Type and Dependencies

- **menu.py → `run_prompt_action()`**: Modify to pass `-p` flag and `--allow-all-tools`. Add `capture_output=True`, `text=True`. Add success/failure display mirroring `run_action()`. No upstream dependencies.

- **New `tests/` directory**: Add `conftest.py` for shared fixtures, plus per-module test files. Depends on `pytest` being installed as a dev dependency.

- **Sequencing**: Bug fix (menu.py) is independent of test suite creation. Both can proceed in parallel, but the test for `run_prompt_action()` depends on the fix being in place.

### 6.3 Domain Impacts

- DOMAIN (ARCH): Minor impact — test infrastructure is a new logical component but does not change the architecture diagram.
  - Relevant: ARCH-01

- DOMAIN (CMP): Impact — CMP-01 needs a new catalog entry for the test suite.
  - Relevant: CMP-01

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): No impact detected.

- DOMAIN (RQT): Possible impact — RQT-02 could reference test automation as an acceptance criterion.
  - Relevant: RQT-02

- DOMAIN (OBS): No impact detected.

- DOMAIN (SEC): No impact detected.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (DEV): No impact detected.

- DOMAIN (OPR): No impact detected.

### 6.4 Constraints

- Python 3.10+ stdlib only for production code (`menu.py` fix).
- `pytest` is permitted as a dev-only dependency for the test suite.
- Tests must not modify the developer's actual `.aib_memory/` state — use `tempfile.TemporaryDirectory()`.
- Tests must not require network access, live Copilot CLI, or GitHub connectivity.
- Platform-specific key input (`msvcrt` on Windows, `termios` on Unix) must be mocked in tests.
- All Copilot CLI subprocess calls in tests must be mocked.

### 6.5 Required Documentation Updates

- CMP-01 - Notebook/Script Catalog
  Required update? YES
  Reason: New test suite catalog entry (e.g., CMP-ART-0008) for the pytest-based test runner.

- RQT-02 - Requirements Document
  Required update? POSSIBLY
  Reason: Add test automation as an acceptance criterion if deemed necessary.

- ARCH-01 - High-level Architecture
  Required update? NO
  Reason: Test infrastructure is a development concern, not an architectural component.

### 6.6 Decision Points

- **DP-1: Copilot CLI invocation syntax** — RESOLVED
  - Decision: Use `copilot -p "..." --allow-all-tools` (hardcoded).
  - Rationale: Confirmed via `copilot --help` that `-p` is the correct flag. User chose hardcoded approach (QID-BF-002 = B). `--allow-all-tools` is required for non-interactive mode per CLI documentation.

- **DP-2: Test framework** — RESOLVED
  - Decision: Use `pytest` (QID-AT-001 = A).
  - Rationale: Better discovery, parametrize, fixtures, compatible with existing unittest tests.

- **DP-3: Test file organization** — RESOLVED
  - Decision: Separate `tests/` directory at workspace root (QID-AT-002 = B).
  - Rationale: Cleaner separation from production code. Requires `conftest.py` for import path configuration.

- **DP-4: E2E test scope** — RESOLVED
  - Decision: Full lifecycle E2E: create-request → create-iteration → close-iteration → close-request in one test (QID-AT-003 = A).
  - Rationale: Most valuable test for verifying the entire workflow. Uses temporary workspace directories.

## 7. Research Plan and Findings

### Methodology
- Live CLI research: Ran `copilot --help` in the developer's terminal to confirm the exact invocation syntax.
- Internal docs scan: Read request.md, iterations.md, 01-analysis.md, 01-questionnaire.md (with user answers), implementation.md.
- Repository scan: Read menu.py (focus on `run_prompt_action()`, `run_action()`, `_detect_copilot_cli()`, `choose_action()`), common.py, all product-doc references.
- Pattern scan: Compared `run_action()` error handling pattern with `run_prompt_action()` gap.

### Evidence Summary

**Bug root cause — confirmed:**

The `copilot --help` output states:
```
-p, --prompt <text>  Execute a prompt in non-interactive mode (exits after completion)
```

The current `run_prompt_action()` code:
```python
subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])
```

This passes the prompt text as a bare positional argument. The correct invocation is:
```python
subprocess.run(["copilot", "-p", f"Execute the prompt defined in {paction['prompt_file']}", "--allow-all-tools"])
```

Evidence → Implication mapping:
- `copilot --help` shows `-p` flag → `run_prompt_action()` must include `-p` as a separate argument.
- `copilot --help` shows `--allow-all-tools` is "required for non-interactive mode" → should be included to prevent the CLI from hanging on tool-use prompts.
- `run_action()` uses `capture_output=True`, `text=True`, and displays status → `run_prompt_action()` should mirror this pattern.
- The informational display in `render_menu()` already shows `copilot -p "..."` — confirming the display was correct but the execution was not.

**Additional finding — `--allow-all-tools` flag:**

The `copilot --help` output includes:
```
--allow-all-tools  Allow all tools to run automatically without confirmation; required for non-interactive mode
```

Without this flag, `copilot -p "..."` may attempt to prompt interactively for tool-use confirmations, which would block the subprocess or cause unexpected behavior.

### Gaps and Unknowns
- None remaining. All open questions from iteration 01 have been resolved.

### Proposed Validation Actions
- No further research needed. Implementation can proceed directly.

### Files Read

- `.aib_brain/tools/menu.py` — Confirmed bug in `run_prompt_action()` (line ~593); confirmed `run_action()` pattern (lines 504-542); confirmed `_detect_copilot_cli()` is correct (lines 57-82).
- `.aib_brain/tools/common.py` — Reviewed shared helpers; no changes needed.
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/request.md` — Current request scope read.
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/iterations.md` — Iteration 01 Completed, Iteration 02 Active.
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/01-analysis.md` — Previous analysis reviewed; all findings still valid.
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/01-questionnaire.md` — User answers incorporated (QID-BF-001: research CLI yourself; QID-BF-002: hardcode; QID-AT-001: pytest; QID-AT-002: tests/ directory; QID-AT-003: full lifecycle E2E).
- `.aib_memory/requests/R-20260403-1537-cli-menu-bugfixing/implementation.md` — Empty (append-only header only).
- `.aib_memory/references.md` — All 28 references enumerated; 27 product-docs identified.
- `.aib_brain/Concepts.md` — AIB concepts and action contract reviewed.
- `.aib_brain/conventions/analysis-convention.md` — Analysis format convention reviewed.
- `.aib_brain/conventions/request-convention.md` — Request format convention reviewed.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Architecture; confirmed AIB Command Menu component; no change needed.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — [SKIPPED — domain out of scope] Topology; stub only.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — [SKIPPED — domain out of scope] Capacity; stub only.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — [SKIPPED — domain out of scope] ADRs; no bug-related content.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — Runtime sequences; reviewed SEQ-001 and SEQ-002 for menu flow context.
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — [SKIPPED — domain out of scope] Resource catalog.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Script catalog; CMP-ART-0006 describes menu.py; needs new entry for test suite.
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — Algorithm register; ALG-0002 describes resolution logic; no changes needed.
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — [SKIPPED — domain out of scope] Source catalog.
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — Data models; reviewed for register parsing context.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — [SKIPPED — domain out of scope] Data lineage; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — [SKIPPED — domain out of scope] Storage strategy; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — [SKIPPED — domain out of scope] Consumption patterns.
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — [SKIPPED — domain out of scope] Metrics; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — [SKIPPED — domain out of scope] Data quality; stub only.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — [SKIPPED — domain out of scope] Archiving policy.
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — [SKIPPED — domain out of scope] Dashboard inventory; empty.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Glossary; TERM-0013 defines Prompt Action.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — Business processes; BP-0001 to BP-0003 reviewed.
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — Personas (DEVELOPER, AI_AGENT, MAINTAINER) and use cases reviewed.
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — Logging; stub only; no changes needed.
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — [SKIPPED — domain out of scope] Product charter; stub only.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — Requirements; FR-008 describes menu prompt action gating; possible update for test acceptance criteria.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — [SKIPPED — domain out of scope] Access; stub only.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — [SKIPPED — domain out of scope] Data protection; stub only.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — [SKIPPED — domain out of scope] Secrets; stub only.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — [SKIPPED — domain out of scope] Network security; stub only.
- Terminal output of `copilot --help` — Confirmed `-p, --prompt <text>` flag and `--allow-all-tools` requirement for non-interactive mode.

## 8. Rewrite Proposal of the Request

See the updated `request.md` file written alongside this analysis.

## 9. Solution Options

### Option A: Hardcoded `-p` Fix + Error Handling + Test Suite in `tests/`

**Overview:** Fix `run_prompt_action()` to invoke `copilot -p "<prompt-text>" --allow-all-tools`. Add `capture_output=True`, `text=True`, and success/failure display mirroring `run_action()`. Create a `tests/` directory at workspace root with `conftest.py` and per-module test files using `pytest`.

**Benefits:**
- Directly addresses the confirmed root cause with the verified correct syntax.
- Error handling gives users immediate feedback on prompt action success/failure.
- `tests/` directory provides clean separation and scalable test organization.
- Full lifecycle E2E test validates the entire AIB workflow.
- `pytest` provides better output, discovery, and fixture support.

**Trade-offs:**
- Hardcoded command means future Copilot CLI interface changes require a code change.
- `tests/` directory at root requires `conftest.py` with `sys.path` manipulation for imports.

**Constraints:**
- `pytest` is dev-only (not required at runtime).
- All CLI calls mocked in tests.

**Risks:**
- Minor: If Copilot CLI changes its flag syntax in a future version, the hardcoded command will break. Mitigated by the fact that `-p` is a fundamental flag documented in the CLI help.

**Expected effort:** Small-to-medium (bug fix: hours; test suite: 1-2 days).

**High-level acceptance-test ideas:**
- Unit: `run_prompt_action()` constructs `["copilot", "-p", "...", "--allow-all-tools"]` (mocked subprocess).
- Unit: `_detect_copilot_cli()` returns True/False based on mocked subprocess responses.
- Unit: `discover_prompt_actions()` returns correctly ordered and formatted action dicts.
- Integration: Each lifecycle script (create-request, close-request, create-iteration, close-iteration, initialize) works correctly in a temp workspace.
- Regression: Existing test_common.py tests pass under pytest.
- Smoke: Menu launches and exits without error (mocked key input).
- E2E: Full lifecycle create-request → create-iteration → close-iteration → close-request via subprocess in temp workspace.

### Option B: Configurable CLI Command + Detection Enhancement + Test Suite

**Overview:** Same as Option A but additionally make the Copilot CLI command configurable via an environment variable (e.g., `AIB_COPILOT_CMD`) and enhance `_detect_copilot_cli()` to detect both `copilot` and `gh copilot`.

**Benefits:**
- Future-proof against CLI interface changes.
- Supports diverse developer environments.

**Trade-offs:**
- Additional complexity beyond what the user requested.
- User explicitly chose hardcoded approach (QID-BF-002 = B).

**Constraints:**
- Same as Option A.

**Risks:**
- Over-engineering given the user's explicit choice.

**Expected effort:** Medium (1-2 additional hours for configuration logic).

### Recommendation

**Option A** is recommended. It directly implements the user's choices from the questionnaire (hardcoded command, pytest, tests/ directory, full E2E), addresses the confirmed root cause with verified syntax, and avoids over-engineering. All open questions are resolved.

## 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | New test suite catalog entry needed (e.g., CMP-ART-0008) |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | Possible addition of test automation acceptance criterion |

## 11. Operational & Documentation Implications

- **Runbooks:** No change needed; tests are developer-local and CI-compatible.

- **SLAs/SLOs:** No change.

- **Monitoring/Observability:** No change; test results are local console output via `pytest`.

- **Data quality rules:** No change.

- **Product documentation:** CMP-01 needs a new artifact entry (CMP-ART-0008) for the pytest-based test suite. RQT-02 may optionally reference automated test execution as an acceptance criterion.

## 12. Risks

- Risk R1: Copilot CLI `--allow-all-tools` flag may grant broader permissions than expected during prompt execution.
  - Probability: Low
  - Impact: Medium
  - Mitigation: The `--allow-all-tools` flag is documented as "required for non-interactive mode" by the Copilot CLI. The prompt actions are user-initiated and workspace-scoped. Document this behavior in the menu's informational display.
  - Owner (role): DEVELOPER

- Risk R2: Tests that mock `subprocess.run` may not catch real CLI invocation failures (e.g., wrong PATH, permission issues).
  - Probability: Low
  - Impact: Medium
  - Mitigation: Include at least one integration test that exercises actual subprocess calls with known-good tool scripts (not Copilot CLI). Copilot CLI tests remain mocked per constraints.
  - Owner (role): DEVELOPER

- Risk R3: Moving from co-located tests to a separate `tests/` directory may break import paths for the existing `test_common.py`.
  - Probability: Medium
  - Impact: Low
  - Mitigation: Create a `conftest.py` that adds `.aib_brain/tools/` to `sys.path`. Verify existing tests pass from the new location.
  - Owner (role): DEVELOPER

- Risk R4: Platform-specific key input (`msvcrt`/`termios`) in `menu.py` requires careful mocking to avoid test failures on different OS.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Mock `get_key()` at the function level rather than mocking low-level OS modules. Test both Windows and Unix code paths with separate parametrized test cases.
  - Owner (role): DEVELOPER

## 13. Disambiguation Questionnaire

- **Q1: What is the exact Copilot CLI invocation for prompt execution?**
  - Chosen Answer: `copilot -p "<text>" --allow-all-tools`
  - Rationale: Confirmed via `copilot --help` output. `-p, --prompt <text>` executes in non-interactive mode. `--allow-all-tools` is required for non-interactive mode.
  - Evidence: Terminal output of `copilot --help` (live research during this iteration).
  - Impact if changed: Core fix would need different flags.

- **Q2: Should the CLI command be hardcoded or configurable?**
  - Chosen Answer: Hardcoded (QID-BF-002 = B).
  - Rationale: User explicitly selected this option. Simpler implementation.
  - Evidence: 01-questionnaire.md answer.
  - Impact if changed: Would require environment variable handling and default fallback logic.

- **Q3: Which test framework?**
  - Chosen Answer: `pytest` (QID-AT-001 = A).
  - Rationale: User explicitly selected this option. Better discovery, fixtures, parametrize.
  - Evidence: 01-questionnaire.md answer.
  - Impact if changed: Test patterns would need to use `unittest` conventions exclusively.

- **Q4: Where should tests live?**
  - Chosen Answer: Separate `tests/` directory at workspace root (QID-AT-002 = B).
  - Rationale: User explicitly selected this option. Cleaner separation.
  - Evidence: 01-questionnaire.md answer.
  - Impact if changed: Would affect import paths and project structure.

- **Q5: E2E test scope?**
  - Chosen Answer: Full lifecycle E2E (QID-AT-003 = A).
  - Rationale: User explicitly selected this option. Most comprehensive validation.
  - Evidence: 01-questionnaire.md answer.
  - Impact if changed: Would reduce test coverage of the complete workflow.

- **Q6, Q7, Q8: Live Copilot CLI in tests? Prompt-action E2E mocked?**
  - Chosen Answer: All Copilot CLI calls mocked.
  - Rationale: CI environments lack Copilot CLI. Tests must be portable, offline, and deterministic.
  - Evidence: Request constraints section, iteration 01 analysis assumption A5.
  - Impact if changed: Tests would require Copilot CLI installed and authenticated.

## 13. Open Questions & Next Actions

No open questions remain. All items from iteration 01 have been resolved:

1. ~~Copilot CLI invocation syntax~~ — Resolved via live `copilot --help` research. Answer: `copilot -p "<text>" --allow-all-tools`.

2. ~~Test framework preference~~ — Resolved via questionnaire. Answer: `pytest`.

3. ~~Test file location~~ — Resolved via questionnaire. Answer: `tests/` at workspace root.

4. ~~E2E scope~~ — Resolved via questionnaire. Answer: Full lifecycle.

Implementation can proceed directly without further clarification.
