# 1. Executive Summary

- **Request ID:** R-20260403-0939

- **Request title:** Menu Improvement

- **Iteration ID:** 01

- **High-level purpose:** Clean up the AIB interactive command menu (`menu.py`) by removing erroneous entries (`Reverse Engineer`, `Test_common`), gating prompt-action execution on GitHub Copilot CLI availability with real subprocess execution when detected, removing clutter (displayed command strings), smoothing the UX, and allowing `close-request` to auto-close an active iteration instead of blocking.

- **Scope:** Changes are confined to `menu.py`, `close-request.py`, and supporting documentation (`ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`). No changes to prompt files, other tool scripts, or CI workflows.

- **Previous iterations:** None — this is the first (and only currently active) iteration.

- **Key decisions required:**
  1. How to exclude `reverse-engineer.py` and `test_common.py` from the menu — extend `EXCLUDE_SCRIPTS` constant vs. introduce a separate `TOOL_SCRIPTS` allowlist.
  2. Whether prompt actions when CLI is absent should still appear in the menu body (as read-only rows) or only appear in a separate informational block.
  3. Exact `gh copilot suggest` invocation: interactive terminal pass-through vs. `capture_output=True` with streamed print.
  4. Auto-close iteration on `close-request`: done silently vs. with a printed notice.
  5. Which fields to strip from menu line rendering (`[script]`, `[prompt_file]`, descriptions).

- **Risks:** Risk of breaking test_common.py discovery if the exclusion mechanism is too broad; risk of subprocess pass-through incompatibilities across platforms.

- **Expected outcome if accepted:** A clean, professional menu that surfaces only the four lifecycle tool actions, gates prompt actions on CLI detection, executes prompts via CLI, and allows frictionless request closure.


# 2. Scope Interpretation

- **In scope — explicit:**

  Remove "Reverse Engineer" option from the CLI menu.

  Remove "Test_common" option from the CLI menu.

  Prompt actions list in the menu shall be selectable and lead to actual `gh copilot suggest` execution only when GitHub Copilot CLI is detected.

  When no GitHub Copilot CLI is detected, show all prompt invocation strings informatively; no execution option.

  Remove display of the command string being executed from the script action run flow.

  Remove unnecessary confirmations and verbose text for a smoother UX.

  Closing a request with an active iteration shall succeed and shall automatically close the iteration as a side effect.

- **Out of scope — explicit:** None stated by user.

- **Out of scope — inferred:**

  No changes to prompt `.md` files or their content.

  No changes to other tool scripts (`initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`).

  No changes to CI/release bookkeeping workflow.

- **Implicit in scope:**
  (implicit rule - AIB framework) Documentation must be updated whenever code components are changed: `ARCH-01`, `CMP-01`, and `RQT-02` must reflect revised menu behavior. `KNW-01` glossary may require a new term for "Prompt Action" or update to `TERM-0006`.

  (implicit rule - AIB framework) Tests must be updated to reflect behavioral changes; existing tests that probe the removed menu entries or old `close-request` guard must be revised.


# 3. Domain Knowledge Essentials

- **AI Builder (AIB):** Minimal, model-agnostic framework for specification-driven development. The framework exposes tool scripts via an interactive terminal menu (`menu.py`).

- **AIB Command Menu (CMP-ART-0006):** The primary human-facing entry point into AIB tooling. It presents script actions and prompt actions in a terminal UI. Personas: DEVELOPER (primary), AI_AGENT (indirect).

- **Prompt action:** A menu entry that maps to a `.aib_brain/prompts/aib-*.md` file. The intent is to trigger that prompt in an AI chat interface. With GitHub Copilot CLI present, this can be executed directly.

- **GitHub Copilot CLI (`gh copilot`):** An optional CLI extension to the GitHub CLI that allows invoking GitHub Copilot from the terminal. Availability is environment-dependent (developer machines may or may not have it installed).

- **Impacted roles/personas:** DEVELOPER (daily user of the menu), AI_AGENT (reads the prompt files directly, not affected by menu).

- **Business process:** BP-0001 and related AIB lifecycle processes (UC-002 through UC-005 in KNW-03) are accessed via the menu. The close-request flow (UC-005 equivalent) is directly affected by the iteration auto-close change.

- **Acceptance impact:** A cleaner menu improves developer experience and reduces errors from selecting inapplicable entries.


# 4. Technical Knowledge & Terms

- **`menu.py`:** Interactive terminal UI launcher at `.aib_brain/tools/menu.py`. Uses `msvcrt` on Windows and `termios` on POSIX for unbuffered key input. Renders two sections: Script actions and Prompt actions.

- **`EXCLUDE_SCRIPTS`:** Constant set in `menu.py` listing script filenames skipped during dynamic discovery in `build_script_actions`. Currently: `{"menu.py", "common.py", "initialize.py"}`.

- **`build_script_actions()`:** Discovers all `.py` files in `tools/` not in `EXCLUDE_SCRIPTS`, appending them after the four hardcoded lifecycle actions. This is why `reverse-engineer.py` and `test_common.py` appear.

- **`discover_prompt_actions()`:** Discovers `aib-*.md` prompt files. Always returns all of them regardless of CLI state.

- **`render_menu()`:** Renders each script action line with `[script_name]` appended, and each prompt action line with `[prompt_file]` appended.

- **`run_action()`:** Collects parameters, prints "Running command:" + the full command string, runs the subprocess with `capture_output=True`, and shows output. This is the source of unnecessary clutter.

- **`run_prompt_action()`:** Currently: always shows a copy/paste suggestion; additionally shows CLI command if CLI detected. Does NOT execute anything.

- **`close-request.py`:** Raises `ValidationError("Cannot close request while an iteration is Active")` if an active iteration exists. The request wants this changed to auto-close the iteration first.

- **`close-iteration.py`:** Deterministically closes the active iteration by updating `iterations.md`. Can be reused as a library function or its logic duplicated.

- **`gh copilot suggest "<prompt>"`:** The CLI invocation. Must be run without `capture_output=True` so the interactive CLI experience passes through to the terminal.

- **Python 3.10+ / stdlib only:** Constraint from RQT-02 / NFR-004. No new dependencies may be introduced.

- **Platform:** Windows (primary based on `.aib_brain/run.bat`) and POSIX (supported via `run.sh`). The fix for `run_prompt_action` must work on both.

- **`subprocess.run` with `capture_output=False`:** To allow interactive pass-through for `gh copilot suggest`, `capture_output` should NOT be set (defaults to False), allowing stdin/stdout/stderr to flow to the terminal.


# 5. Assumptions

- Assumption A1: `test_common.py` is a pytest test file, not a user-facing tool, and its presence in the menu is a defect caused by the overly broad `build_script_actions` discovery.
  - Rationale: File header states "Comprehensive tests for common.py helpers". It uses `unittest` and imports test framework symbols.
  - Risk if false: If it were an intentional tool, removing it from the menu would constitute a feature removal.
  - Falsification method: Confirm with user whether `test_common.py` is ever invoked directly as a tool from the menu.

- Assumption A2: `reverse-engineer.py` should NOT appear in the Script actions section (it is an AI-driven prompt-triggered workflow, not a standalone tool); only the four lifecycle scripts are appropriate as direct menu items.
  - Rationale: `reverse-engineer.py` outputs JSON Lines (workspace file inventory) intended as intermediate input for the `aib-reverse-engineer.md` prompt. It is not a human-invocable standalone action.
  - Risk if false: If users sometimes invoke `reverse-engineer.py` directly from the menu, removing it is a regression.
  - Falsification method: Check if there are any recorded usages of `reverse-engineer` as a menu action; confirm with user.

- Assumption A3: "Real execution" for prompt actions means running `subprocess.run(["gh", "copilot", "suggest", "<chat_prompt>"], ...)` with pass-through I/O (not `capture_output=True`).
  - Rationale: GitHub Copilot CLI has its own interactive output; capturing it would break the experience.
  - Risk if false: If `gh copilot suggest` expects piped non-interactive usage, pass-through may cause terminal rendering issues.
  - Falsification method: Test `gh copilot suggest "..."` locally on a machine with the CLI installed.

- Assumption A4: "Remove unnecessary text/confirmation" refers specifically to: (a) the `[script]` suffix in menu lines, (b) the `[prompt_file]` suffix in menu lines, (c) the "Running command:" + command line in `run_action`, and (d) possibly the `Parameter input / ----` banner and hint lines.
  - Rationale: These are the most verbose non-essential elements visible to the user during normal operation.
  - Risk if false: Some users may rely on seeing the script name in the menu for disambiguation.
  - Falsification method: Ask user to enumerate which specific texts they consider unnecessary.

- Assumption A5: The informational prompt list when CLI is absent should be rendered as a static block in the menu (non-navigable, non-selectable), showing only the prompt title and the `gh copilot suggest "Execute the prompt defined in <path>"` invocation string.
  - Rationale: The request says "list in minimalistic way the invocation strings for all possible prompts, without giving option for execution from the menu (just informative)". A static printed block at the bottom of the menu satisfies this.
  - Risk if false: User might want a navigable informational list; or might want it as a separate sub-menu.
  - Falsification method: Confirm with user how the informational list should look when CLI is absent.

- Assumption A6: Auto-closing the iteration during `close-request` should print a notice (e.g., "Auto-closed iteration 01") but not require user confirmation.
  - Rationale: The request says "shall be allowed" and "shall result in closing the iteration" — implies automatic side effect, not interactive.
  - Risk if false: Silent auto-close could surprise users who did not intend to abandon the iteration.
  - Falsification method: Confirm with user whether a printed notice is sufficient or a confirmation prompt is needed.

- Assumption A7: The `collect_parameters` and `build_command` flows for the four lifecycle actions should remain structurally intact — only the cosmetic "Running command:" print should be removed.
  - Rationale: The request says "remove unnecessary information like showing the command to be executed" — this targets the display, not the underlying execution.
  - Risk if false: If users also want to simplify or auto-fill parameters (e.g., workspace), further refactoring is needed.
  - Falsification method: User acceptance test on the revised menu.


# 6. Impact Assessment

## 6.1 Affected Components / Areas

- `.aib_brain/tools/menu.py` — Primary change target: exclusion of `reverse-engineer.py` and `test_common.py`, prompt-action CLI gating, run display cleanup, UX text reduction.

- `.aib_brain/tools/close-request.py` — Change close-request guard: remove `ValidationError` on active iteration; add auto-close logic.

- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Update CMP-ART-0006 (AIB command menu) notes to reflect new behavior.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Update component inventory note for AIB Command Menu.

- `.aib_memory/docs/03 Requirements/RQT-02.md` — Update FR-008 (interactive menu) to reflect prompt-action gating behavior.

- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Potentially add/update term for "Prompt Action" if not present.

- `.aib_brain/tools/test_common.py` — May require new test cases for: (a) exclusion of discovered non-tool scripts, (b) revised `close-request` auto-close behavior.

## 6.2 Change Type and Dependencies

| Area | Change type | Dependencies | Sequencing |
| --- | --- | --- | --- |
| `menu.py` — EXCLUDE_SCRIPTS | modify | none | Independent; implement first |
| `menu.py` — prompt action gating | modify | `_detect_copilot_cli()` already exists | After exclusion fix |
| `menu.py` — `run_prompt_action` execution | modify | `_detect_copilot_cli()` | After gating change |
| `menu.py` — remove menu line suffixes | modify | `render_menu()` | Independent |
| `menu.py` — remove "Running command:" | modify | `run_action()` | Independent |
| `close-request.py` — auto-close iteration | modify | Reuses close-iteration logic from `close-iteration.py` or `common.py` | After menu changes |
| `test_common.py` — new tests | modify | All above code changes | Last |
| Documentation updates | modify | Code changes completed | Final step |

## 6.3 Domain Impacts

- DOMAIN (ARCH): Minor impact. AIB Command Menu component description must be updated in ARCH-01 to reflect prompt-action gating and exclusion of non-tool scripts. No new components introduced.
  - Relevant: ARCH-01 Component Inventory row for "AIB Command Menu"

- DOMAIN (CMP): Moderate impact. CMP-ART-0006 (AIB Command Menu) edge cases and description must reflect the new gating behavior and excluded scripts.
  - Relevant: CMP-01 row CMP-ART-0006

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): Low impact. Tool script behavior changed for `close-request.py`.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (KNW): Low impact. Glossary may benefit from a "Prompt Action" term definition if not already present.
  - Relevant: KNW-01

- DOMAIN (RQT): Low impact. FR-008 in RQT-02 describes the interactive menu; must be updated to specify CLI-gated prompt actions.
  - Relevant: RQT-02 FR-008

- DOMAIN (OBS): No impact detected.

- DOMAIN (OPR): No impact detected.

- DOMAIN (SEC): No impact detected. The subprocess execution of `gh copilot suggest` does not introduce new secrets or auth concerns beyond what `gh` already manages.

## 6.4 Constraints

- Python 3.10+ / stdlib only (NFR-004 from RQT-02). No new packages.

- Script must remain cross-platform (Windows `msvcrt` + POSIX `termios`). The `subprocess.run` call for `gh copilot suggest` must not pass `capture_output=True` so the interactive CLI renders correctly on both platforms.

- Exactly one active iteration per request lifecycle rule must be maintained. Auto-close in `close-request.py` must handle the case where no active iteration exists (i.e., it must be optional, not fail on absence).

- AIB framework rule: `.aib_brain/` scripts must not be modified by AIB tool scripts themselves (only humans). This constraint is about runtime behavior, not about this change request.

## 6.5 Required Documentation Updates

- ARCH-01 — AIB Command Menu component description
  Required update? YES
  Reason: Component behavior changes (prompt-action gating, excluded scripts)

- CMP-01 — CMP-ART-0006 row (AIB Command Menu)
  Required update? YES
  Reason: edge_cases_and_validation field must reflect new CLI-gating behavior and excluded scripts

- RQT-02 — Functional Requirements FR-008
  Required update? YES
  Reason: Must specify that prompt actions require CLI and that non-tool scripts are excluded

- KNW-01 — Glossary
  Required update? CONDITIONAL
  Reason: Add "Prompt Action" term if not present; update existing "Tool Script" term to clarify distinction from prompt-triggered scripts

## 6.6 Decision Points

**Decision 1 — Exclusion mechanism for non-tool scripts**

- Option 1A: Extend `EXCLUDE_SCRIPTS` constant with `reverse-engineer.py` and `test_common.py`.
  - Implication: Simple. Must be maintained manually when new non-tool `.py` files are added.
  - Recommended: YES — simplest, minimal change, matches existing pattern.

- Option 1B: Replace `EXCLUDE_SCRIPTS` with an explicit `INCLUDED_SCRIPTS` allowlist containing only the four lifecycle scripts.
  - Implication: Any new legitimate tool is invisible until added to allowlist. Safer but more maintenance.

- Option 1C: Add a filename pattern rule (e.g., exclude files matching `test_*.py`).
  - Implication: Automatically excludes future test files, but may accidentally exclude legitimate scripts named `test-*.py`.

**Decision 2 — Prompt action display when CLI absent**

- Option 2A: Remove prompt action rows from the navigable menu entirely; show a static informational block above the "Exit" line.
  - Implication: Clean separation. Menu navigation indices stay consistent.
  - Recommended: YES — matches "list in minimalistic way ... without giving option for execution".

- Option 2B: Keep prompt action rows in the navigable menu but disable selection (display `(requires Copilot CLI)` suffix).
  - Implication: User can highlight rows but pressing Enter produces an error or notice.

**Decision 3 — gh copilot suggest invocation style**

- Option 3A: `subprocess.run(["gh", "copilot", "suggest", chat_prompt])` without `capture_output` — interactive pass-through.
  - Implication: Full interactive experience. Terminal may need to restore state after.
  - Recommended: YES.

- Option 3B: `subprocess.run(["gh", "copilot", "suggest", chat_prompt], capture_output=True)` — captured output printed after.
  - Implication: Loses interactivity; `gh copilot suggest` is interactive by nature.

**Decision 4 — Auto-close notice in close-request**

- Option 4A: Print notice `"Auto-closed iteration <id> before closing request."` then proceed.
  - Recommended: YES — transparent side effect without requiring confirmation.

- Option 4B: Silently close iteration before closing request.
  - Implication: Could confuse user who notices iteration state changed unexpectedly.


# 7. Research Plan and Findings

**Methodology:** Internal docs scan + repository scan of specific files.

**Evidence summary:**

- `menu.py` `build_script_actions()` uses `discover_tool_scripts()` which returns all `.py` files in `tools/` not in `EXCLUDE_SCRIPTS`. `reverse-engineer.py` and `test_common.py` are not in `EXCLUDE_SCRIPTS` → they appear in the menu. This confirms the defect.

- `render_menu()` always appends `[script]` and `[prompt_file]` to menu lines. The request says to remove these.

- `run_action()` contains `print("\nRunning command:")` + `print(" ".join(command))` which shows the raw command. The request says to remove this.

- `run_prompt_action()` always shows copy/paste text; CLI detection only adds an extra line. It never executes the CLI. The request says real execution should happen when CLI is present.

- `close-request.py` raises `ValidationError("Cannot close request while an iteration is Active")`. The request says closing should auto-close the iteration. The existing `close-iteration.py` logic can be referenced for the filesystem write.

- `discover_prompt_actions()` always returns all prompt actions regardless of CLI state. The gating must be applied in `choose_action()` or `render_menu()`.

- No existing tests in `test_common.py` explicitly test the menu behavior (the tests focus on `common.py` helpers). New tests for menu behavior changes may need to be added, or it is acceptable to rely on manual testing for the UX changes.

**Gaps and unknowns:**

- It is not confirmed whether any user has intentionally invoked `reverse-engineer.py` as a standalone menu action.

- The exact desired UX for the informational prompt list (when CLI absent) is not fully specified — assumed to be a static print block.

- Whether descriptions should be removed from menu lines or only the `[script]` / `[prompt_file]` suffix is ambiguous.

**Proposed validation:**

- Run the updated menu on a machine with and without `gh copilot` installed to validate both branches.

- Run `python -m pytest .aib_brain/tools/test_common.py` to confirm no regressions in `common.py` helpers.

**Files Read:**

- `.aib_memory/requests/R-20260403-0939-menu-improvement/request.md` — Active request goal and success criteria confirmed.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/iterations.md` — Iteration 01 is Active.
- `.aib_memory/references.md` — Required-read set identified (all 27 product-doc entries).
- `.aib_brain/prompts/aib-create-analysis.md` — Prompt being executed; used for preflight rules.
- `.aib_brain/conventions/analysis-convention.md` — Full convention read for structural compliance.
- `.aib_brain/conventions/request-convention.md` — Request format convention read.
- `.aib_brain/Concepts.md` — AIB invocation contract and lifecycle rules confirmed.
- `.aib_brain/tools/menu.py` — Full file read; all current behavior confirmed.
- `.aib_brain/tools/close-request.py` — Current validation guard confirmed.
- `.aib_brain/tools/close-iteration.py` — Close iteration logic read for reuse reference.
- `.aib_brain/tools/test_common.py` — Confirmed as pytest test file, not a tool.
- `.aib_brain/tools/reverse-engineer.py` — Confirmed as JSON inventory emitter for prompt support, not a standalone tool.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-008 confirmed (interactive menu); NFR-004 (Python 3.10+).
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Component inventory confirms AIB Command Menu entry.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — CMP-ART-0006 entry confirmed; edge cases field identified for update.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Glossary reviewed; no "Prompt Action" term currently exists.
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — DEVELOPER persona confirmed as primary menu user.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — Business processes reviewed; no directly affected process entries.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — Reviewed; no menu-specific sequence scenarios defined.
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — STUB; no relevant content.
- All remaining product-doc entries (ARCH-02, ARCH-03, ARCH-04, ARCH-05, ARCH-07, DATA-01 through DATA-09, SEC-01 through SEC-04, OBS-01, CMP-02, KNW-04, KNW-05, FNL-01, FNL-02, DSR-01 through DSR-03, DEV-01 through DEV-06, OPR-01 through OPR-05, RQT-04) — Either STUB (no content) or domain out of scope for this UX/CLI menu request. `[SKIPPED — domain out of scope]` for DATA, SEC, DSR, FNL, OPR, DEV stubs.


# 8. Rewrite Proposal of the Request

## Goal

Update the AIB interactive command menu (`menu.py`) and the `close-request.py` tool script to address five distinct improvement areas:

1. **Remove non-tool script entries from the menu.** The menu currently shows "Reverse Engineer" and "Test Common" as interactive options because `reverse-engineer.py` and `test_common.py` are auto-discovered by `build_script_actions()`. Add both filenames to the `EXCLUDE_SCRIPTS` constant so they no longer appear in the Script actions section. Accepted measure: neither entry appears when the menu renders.

2. **Gate prompt actions on GitHub Copilot CLI availability.** When `gh copilot --version` exits with code 0 (CLI detected), render prompt actions as navigable menu entries. When CLI is not detected, replace the navigable prompt-actions section with a static informational block listing each prompt's title and its corresponding `gh copilot suggest "Execute the prompt defined in <path>"` invocation string. No selection or execution is possible in the absence of CLI. Accepted measure: running the menu on a machine without `gh copilot` shows the static block only; on a machine with `gh copilot`, prompt actions are selectable.

3. **Execute prompt actions via Copilot CLI when CLI is present.** When the user selects a prompt action and CLI is available, call `subprocess.run(["gh", "copilot", "suggest", "Execute the prompt defined in <path>"])` without `capture_output` so the interactive CLI session renders in the terminal. After `gh copilot suggest` exits, return to the menu. Remove the existing copy/paste text from `run_prompt_action()`. Accepted measure: the CLI invocation is actually launched rather than just printed.

4. **Remove clutter from menu rendering and action execution.** In `render_menu()`, remove the `[script]` suffix from script action lines and the `[prompt_file]` suffix from prompt action lines. In `run_action()`, remove the `print("\nRunning command:")` and the `print(" ".join(command))` lines. Accepted measure: a script action run no longer shows the raw Python command in the terminal.

5. **Allow close-request to succeed even when an active iteration exists.** In `close-request.py`, replace the `ValidationError("Cannot close request while an iteration is Active")` guard with logic that: (a) detects the active iteration, (b) closes it by writing `Completed` state and the current timestamp to `iterations.md`, and (c) prints `"Auto-closed iteration <id> before closing request."` before proceeding to close the request. Accepted measure: running `close-request` with an active iteration closes both the iteration and the request in a single operation without error.

## Background

The AIB interactive menu is the primary developer access point for AIB lifecycle tools. Unnecessary entries, verbose output, and blocked workflows degrade developer experience and introduce errors.

## Scope

- `menu.py`: EXCLUDE_SCRIPTS extension; `render_menu()` suffix removal; `run_action()` command-line removal; `choose_action()` and `render_menu()` prompt-action gating; `run_prompt_action()` real CLI execution.
- `close-request.py`: Guard replacement with auto-close logic.
- Documentation: `ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`.
- Tests: `test_common.py` — add/update test cases for close-request auto-close behavior; verify menu exclusion logic if unit-testable.

## Out of scope

- No changes to prompt `.md` files.
- No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`.
- No new Python dependencies.
- No changes to CI workflow or release bookkeeping.

## Functional expectations

- Menu renders without `[script]` / `[prompt_file]` suffixes.
- When CLI absent: prompt section replaced by static informational text; indices [1..n] map only to script actions.
- When CLI present: all prompt actions are navigable and execute `gh copilot suggest` on selection.
- `close-request` with active iteration: succeeds, auto-closes iteration, prints notice for each closed iteration.
- `close-request` with no active iteration: behavior unchanged.

## Non-functional expectations

- No new Python package dependencies.
- Cross-platform (Windows + POSIX).
- Idempotent: running `close-request` twice (second time on already-closed request) still returns `ValidationError`; auto-close only occurs once.

## Measurable acceptance criteria

1. Launching the menu: neither "Reverse Engineer" nor "Test Common" appears in any section.
2. On a machine without `gh copilot`: no prompt action rows are selectable; a static invocation string list is shown.
3. On a machine with `gh copilot`: selecting a prompt action launches `gh copilot suggest "..."` interactively.
4. Running any script action: the terminal no longer displays `Running command:` or the raw Python command string.
5. `python close-request.py --workspace .` while an iteration is Active: exits code 0, prints `"Auto-closed iteration 01 before closing request."` and `"Closed request: R-..."`.
6. Running `pytest .aib_brain/tools/test_common.py` passes at 100%.


# 9. Solution Options

## Option A — Targeted Direct Code Changes (Recommended)

**Overview:** Make the smallest set of direct modifications to `menu.py` and `close-request.py` that satisfy all five improvement areas. No new modules or configuration files.

**Benefits:**
- Minimal diff, easy to review.
- Follows existing code patterns (extends `EXCLUDE_SCRIPTS`, modifies `render_menu`, modifies `close-request`).
- No new files or abstractions.

**Trade-offs:**
- `EXCLUDE_SCRIPTS` remains an inline constant; any new non-tool `.py` file in `tools/` requires manual addition.
- `run_prompt_action` and `choose_action` logic becomes slightly more branchy (CLI-present vs absent paths).

**Constraints:** Python 3.10+ stdlib only; cross-platform.

**Risks:**
- If `gh copilot suggest` interactive behavior differs across OS or `gh` versions, the pass-through call may not render cleanly. Mitigated by testing on target platform.
- Forgetting to add future test files to `EXCLUDE_SCRIPTS`.

**Expected effort:** Low — approximately 60–80 lines changed across two files.

**Acceptance test ideas:**
- Visual inspection of menu output (no `[script]`/`[prompt_file]` suffixes; no "Reverse Engineer"/"Test Common").
- `close-request.py` integration test with active iteration.
- `pytest test_common.py` 100% pass.

---

## Option B — Config-Driven Menu with Allowlist

**Overview:** Replace `EXCLUDE_SCRIPTS` with a JSON or inline data structure defining an explicit allowlist of tool scripts (`create-request.py`, `close-request.py`, `create-iteration.py`, `close-iteration.py`). Any `.py` file not in the allowlist is never shown. Prompt gating and execution changes remain the same as Option A.

**Benefits:**
- Safer long-term: new scripts are invisible until explicitly added.
- Reduces the risk of test files leaking into the menu as the tool grows.

**Trade-offs:**
- Slightly more code change (replace discover logic).
- Allowlist needs to stay in sync with intended tools.

**Constraints:** Same as Option A.

**Risks:**
- Allowlist diverging from actual tools if additions are made to `tools/` without updating the allowlist.

**Expected effort:** Low-Medium — ~80–100 lines changed.

**Acceptance test ideas:** Same as Option A.

---

## Recommendation

**Option A** is recommended for this iteration. It satisfies all five improvement areas with a minimal, focused change. The `EXCLUDE_SCRIPTS` approach is already established in the codebase and extending it with two entries is the lowest-risk choice. If the tool directory grows significantly with non-tool scripts in future, an allowlist approach (Option B) can be adopted in a future request.


# 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | AIB Command Menu component description must reflect prompt-action gating and excluded scripts |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0006 (AIB Command Menu) edge_cases_and_validation field must be updated |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | FR-008 must be updated to specify CLI-gated prompt actions |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Add "Prompt Action" term to distinguish from "Tool Script" |


# 11. Operational & Documentation Implications

- **Runbooks:** No runbook changes required. The menu is an interactive developer tool, not a CI-driven process.

- **SLAs/SLOs:** Not applicable for this change.

- **Monitoring/observability:** No changes to logging. The `close-request.py` auto-close prints a human-readable notice to stdout; no structured log entry is required.

- **Data quality rules:** Not applicable.

- **Product documentation artifacts:**
  - `RQT-02` FR-008: Update description to specify that prompt actions are gated on `gh copilot` CLI availability and execute `gh copilot suggest` when available.
  - `ARCH-01` Component Inventory: Update AIB Command Menu description to mention CLI gating and excluded scripts.
  - `CMP-01` CMP-ART-0006: Update `edge_cases_and_validation` to include "Prompt actions require gh copilot CLI; non-tool scripts excluded from discovery."
  - `KNW-01`: Add term TERM-0013 "Prompt Action" — a menu entry that triggers a `.aib_brain/prompts/aib-*.md` file via GitHub Copilot CLI when available.


# 12. Risks

- Risk R1: `gh copilot suggest` interactive behavior incompatible with the subprocess call on some platforms.
  - Probability: Low
  - Impact: Medium — prompt actions would appear to hang or fail silently.
  - Mitigation: Test on Windows and POSIX before merge. Restore fallback copy/paste output if `subprocess.run` returns non-zero.
  - Owner (role): DEVELOPER

- Risk R2: Auto-closing an active iteration in `close-request.py` silently corrupts `iterations.md` if the file write fails midway.
  - Probability: Low
  - Impact: High — iteration state becomes inconsistent.
  - Mitigation: Reuse proven write pattern from `close-iteration.py`; ensure atomic write via temp file or at minimum write-then-validate pattern already used in `common.py`.
  - Owner (role): AIB Maintainers

- Risk R3: Extending `EXCLUDE_SCRIPTS` does not prevent future test or helper files from appearing in the menu.
  - Probability: Medium (as codebase grows)
  - Impact: Low — cosmetic defect (extra menu entries).
  - Mitigation: Document that all non-tool `.py` files in `tools/` must be added to `EXCLUDE_SCRIPTS`. Consider adopting Option B (allowlist) in a follow-up request.
  - Owner (role): AIB Maintainers

- Risk R4: CLI detection caching (`_COPILOT_CLI_AVAILABLE`) keeps a stale `False` value if the user installs `gh copilot` during a menu session.
  - Probability: Very Low
  - Impact: Low — user must restart the menu.
  - Mitigation: Acceptable as-is; current behavior is already lazy-cached. No change needed unless user reports issue.
  - Owner (role): DEVELOPER

- Risk R5: Removing the "Running command:" display may reduce debuggability when a script action fails unexpectedly.
  - Probability: Low
  - Impact: Low — the exit code and error summary are still displayed.
  - Mitigation: Keep the "Show full details? [y/N]" prompt in `run_action` so the full stderr/stdout is still accessible on failure.
  - Owner (role): DEVELOPER


# 13. Open Questions & Next Actions

1. **Confirm `reverse-engineer.py` exclusion intent.**
   - Owner: User
   - Trigger: Before implementation begins.
   - Resolution path: User confirms that `reverse-engineer.py` should never appear as a standalone menu entry (Assumption A2). If confirmed, extend `EXCLUDE_SCRIPTS`. If not, define the correct menu behavior for it.

2. **Confirm which texts are "unnecessary" in the menu.**
   - Owner: User
   - Trigger: Before implementation begins.
   - Resolution path: User confirms whether descriptions should also be removed from menu item lines, or only the `[script]`/`[prompt_file]` suffixes (Assumption A4). Also confirm whether the `Parameter input / ------` banner and hint lines in `collect_parameters()` should be simplified.

3. **Confirm informational prompt list format when CLI absent.**
   - Owner: User
   - Trigger: Before implementation begins.
   - Resolution path: User confirms whether the static informational block should appear within the menu screen (preferred per Assumption A5) or as a separate sub-menu or separate command. Confirm whether prompt descriptions should appear alongside invocation strings.

4. **Confirm auto-close behavior: silent vs. printed notice.**
   - Owner: User
   - Trigger: Before implementation begins.
   - Resolution path: User confirms whether printing `"Auto-closed iteration <id> before closing request."` is sufficient (Assumption A6), or whether a confirmation prompt is required.
