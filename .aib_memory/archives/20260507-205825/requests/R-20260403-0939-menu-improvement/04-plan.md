# Plan

---

## Overview

This plan implements all five improvement areas for the AIB interactive menu and request-lifecycle workflow identified in R-20260403-0939 and fully specified through iterations 01–03. Iteration 04 analysis confirmed all five improvements remain unimplemented and the specification is immediately actionable.

**What changes:**
- `menu.py`: remove `reverse-engineer.py` and `test_common.py` from Script actions; gate the Prompt section on `copilot` CLI availability with a static informational fallback; replace `run_prompt_action()` body with a real CLI invocation; strip suffix labels and command-echo print lines.
- `close-request.py`: replace the blocking `ValidationError` guard with auto-close-iteration logic.
- `test_common.py`: add `TestCloseRequestAutoClose` test class and an `EXCLUDE_SCRIPTS` membership test.
- Four product-doc updates: ARCH-01, CMP-01, RQT-02, KNW-01.

Inputs: `request.md` §Goal (five improvement areas), §Constraints, §Success criteria; `04-analysis.md` §1 Executive Summary, §2 Scope Interpretation, §4 Technical Knowledge, §6 Impact Assessment, §6.6 Decision Points, §7 Research Plan and Findings. No questionnaire was produced for iteration 04; all decisions are resolved.

---

## Scope of Work

**In Scope**
- Six inline edits to `.aib_brain/tools/menu.py` (Improvements 1–4)
- One import addition and guard replacement in `.aib_brain/tools/close-request.py` (Improvement 5)
- New `TestCloseRequestAutoClose` class and `EXCLUDE_SCRIPTS` membership test in `.aib_brain/tools/test_common.py`
- Product-doc updates: ARCH-01 (AIB Command Menu Description), CMP-01 (CMP-ART-0005 and CMP-ART-0006 `edge_cases_and_validation`), RQT-02 (FR-008), KNW-01 (TERM-0013 addition)

**Out of Scope**
- No changes to `.aib_brain/prompts/*.md` files
- No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, or `common.py`
- No new Python package dependencies
- No changes to CI workflow or release bookkeeping
- No changes to `collect_parameters()`

**Assumptions**
- `copilot` binary on the developer PATH accepts `copilot -p "Execute the prompt defined in <path>"` as an interactive invocation (Assumption A2 from `04-analysis.md` §5; manual pre-test recommended before Task 6)
- Moving `_detect_copilot_cli()` to eager pre-loop introduces no perceptible startup delay (Assumption A3 from `04-analysis.md` §5)
- `COMPLETED`, `format_markdown_table`, `write_text` are importable from `common` without modifying `common.py` (Assumption A4 from `04-analysis.md` §5)

**Constraints**
- Python 3.10+ stdlib only; no third-party packages (NFR-004)
- Cross-platform: Windows (`msvcrt`) and POSIX (`termios`) compatibility must be maintained
- `_COPILOT_CLI_AVAILABLE` global caches detection result; no repeated subprocess calls per render cycle
- Auto-close guard in `close-request.py` MUST run only when `active_iterations` is non-empty; empty list skips silently
- `subprocess.run(["copilot", ...])` MUST NOT use `capture_output`
- All four impacted product docs have `edit_allowed = Y` per `.aib_memory/references.md`

---

## Decision Gates (Blocking Questions & Answers)

**A. Scope & Outcome**

- Question: What is the minimal shippable outcome for this iteration?
- Chosen Answer / Value: All five improvement areas implemented, full pytest suite passing, and four product-doc files updated.
- Rationale: Directly specified in `request.md` §Success criteria items 1–6.
- Evidence / Reference: `request.md` §Success criteria; `04-analysis.md` §1 Executive Summary.
- Impact if changed: Partial delivery fails acceptance criterion 6 (100% test pass).

- Question: Which user-visible changes must be demonstrable at iteration end?
- Chosen Answer / Value: (1) Menu shows neither Reverse Engineer nor Test Common entries. (2) Prompt section behaviour varies by CLI availability. (3) No command-echo text in terminal. (4) `close-request` succeeds with an Active iteration.
- Rationale: Maps directly to `request.md` §Success criteria items 1–5.
- Evidence / Reference: `request.md` §Success criteria.
- Impact if changed: N/A.

- Question: Non-functional targets applicable to this iteration?
- Chosen Answer / Value: Menu startup latency ≤ 1 s with eager CLI detection; cross-platform compatibility maintained; stdlib only (no new packages).
- Rationale: Assumption A3 and NFR-004; `04-analysis.md` §5 and §6.4.
- Evidence / Reference: `04-analysis.md` §5 Assumption A3; `04-analysis.md` §6.4 Constraints.
- Impact if changed: Slower startup on edge-case machine configurations.

**B. CLI Binary Identity**

- Question: Which binary and argument pattern are used for Copilot CLI detection and invocation?
- Chosen Answer / Value: Detection: `["copilot", "--version"]`. Invocation: `["copilot", "-p", f"Execute the prompt defined in {path}"]`.
- Rationale: Resolved by QID-BF-001 in `02-questionnaire.md` (option B + freeform: "If copilot is installed, the cmd command for running it is `copilot`"). Reconfirmed in `03-analysis.md` and `04-analysis.md`.
- Evidence / Reference: `02-questionnaire.md` §QID-BF-001; `04-analysis.md` §6.6 Decision 1.
- Impact if changed: If binary name differs per environment, detection falls back gracefully to static informational mode.

**C. Eager vs Lazy CLI Detection**

- Question: Should `_detect_copilot_cli()` be called eagerly (pre-loop) or lazily (on first prompt action)?
- Chosen Answer / Value: Eager — call once before the `while True` loop in `choose_action()`; cache result in `_COPILOT_CLI_AVAILABLE` global.
- Rationale: Required so `render_menu()` can gate the Prompt section on the very first render. `04-analysis.md` §6.6 Decision 3.
- Evidence / Reference: `04-analysis.md` §6.6 Decision 3; `04-analysis.md` §4 `choose_action()` description.
- Impact if changed: Lazy detection would produce inconsistent first-render UX.

**D. Static Block Format When CLI Is Absent**

- Question: What header and line format should the static informational block use when CLI is not detected?
- Chosen Answer / Value: Header `--- Prompt actions (Copilot CLI not detected — informational only) ---`; lines `  • <Title>  →  copilot -p "Execute the prompt defined in <relative_path>"`.
- Rationale: `04-analysis.md` §6.6 Decision 2.
- Evidence / Reference: `04-analysis.md` §6.6 Decision 2.
- Impact if changed: Inconsistent UX terminology.

**E. Data, Compute, Security, Observability (Q4–Q11)**

- Questions: Data schemas, external APIs, secrets, metrics/alerts — all canonical questions.
- Chosen Answer / Value: N/A for all.
- Rationale: Changes are purely local Python file edits and Markdown product-doc updates. No data schemas, external APIs, secrets, or runtime metrics are involved.
- Evidence / Reference: `04-analysis.md` §2 Out of Scope; `04-analysis.md` §6.3 Domain Impacts.
- Impact if changed: N/A.

**F. Documentation Updates**

- Question: Which product docs must be created or updated?
- Chosen Answer / Value: ARCH-01 (AIB Command Menu row Description), CMP-01 (CMP-ART-0005 and CMP-ART-0006 `edge_cases_and_validation`), RQT-02 (FR-008), KNW-01 (add TERM-0013).
- Rationale: `04-analysis.md` §6.5 Required Documentation Updates — all four confirmed still pending as of iteration 04.
- Evidence / Reference: `04-analysis.md` §6.5; `04-analysis.md` §7 Evidence summary.
- Impact if changed: Stale product-docs fail AIB documentation governance check.

---

## Work Breakdown Structure (WBS)

### Task 1: Extend EXCLUDE_SCRIPTS in menu.py

**Intent:** Add `"reverse-engineer.py"` and `"test_common.py"` to the `EXCLUDE_SCRIPTS` set so they no longer appear as Script actions in the menu.

**Inputs:** `.aib_brain/tools/menu.py` — `EXCLUDE_SCRIPTS` constant (line ~16); current value: `{"menu.py", "common.py", "initialize.py"}`

**Outputs:** `.aib_brain/tools/menu.py` — `EXCLUDE_SCRIPTS` updated to `{"menu.py", "common.py", "initialize.py", "reverse-engineer.py", "test_common.py"}`

**Procedure:**
1. Read `.aib_brain/tools/menu.py` lines 1–30 to locate `EXCLUDE_SCRIPTS` exactly.
2. Add `"reverse-engineer.py"` and `"test_common.py"` to the set literal.
3. Save the file.

**Done Criteria:** `EXCLUDE_SCRIPTS` in `menu.py` contains all five strings: `"menu.py"`, `"common.py"`, `"initialize.py"`, `"reverse-engineer.py"`, `"test_common.py"`.

**Dependencies:** None.

**Risk Notes:** None.

---

### Task 2: Update _detect_copilot_cli() binary string

**Intent:** Change the CLI detection subprocess command from `["gh", "copilot", "--version"]` to `["copilot", "--version"]` to match the actual installed binary.

**Inputs:** `.aib_brain/tools/menu.py` — `_detect_copilot_cli()` function (lines ~57–79); currently calls `["gh", "copilot", "--version"]`

**Outputs:** `.aib_brain/tools/menu.py` — `_detect_copilot_cli()` uses `["copilot", "--version"]`; all references to `["gh", "copilot", ...]` removed

**Procedure:**
1. Read `.aib_brain/tools/menu.py` lines 55–80 to locate the subprocess call inside `_detect_copilot_cli()`.
2. Replace `["gh", "copilot", "--version"]` with `["copilot", "--version"]`.
3. Save the file.

**Done Criteria:** `_detect_copilot_cli()` body contains `["copilot", "--version"]`; no `["gh", "copilot", ...]` string remains in the function.

**Dependencies:** None.

**Risk Notes:** Assumption A1 — binary name confirmed as `copilot` by QID-BF-001 in `02-questionnaire.md`.

---

### Task 3: Update render_menu() — suffix removal and CLI gating

**Intent:** Remove `[script]` and `[prompt_file]` suffixes from menu line strings; add `cli_available: bool` parameter; render a static non-navigable informational block for Prompt actions when CLI is absent.

**Inputs:** `.aib_brain/tools/menu.py` — `render_menu()` function (lines ~549–590); updated `_detect_copilot_cli()` binary from Task 2

**Outputs:** `.aib_brain/tools/menu.py` — `render_menu()` signature gains `cli_available: bool`; Script loop no longer appends `[script]` suffix; Prompt section is conditional on `cli_available`; static informational block rendered when `cli_available = False`

**Procedure:**
1. Read `.aib_brain/tools/menu.py` lines 545–595 to confirm exact current code.
2. Add `cli_available: bool` parameter to `render_menu()` signature.
3. Remove the `if script: line += f" [{script}]"` line from the Script actions loop.
4. Remove the `line += f" [{paction['prompt_file']}]"` line from the Prompt actions loop.
5. Wrap the navigable Prompt actions rendering in `if cli_available:`.
6. Add an `else:` branch that renders: header `--- Prompt actions (Copilot CLI not detected — informational only) ---` followed by one line per prompt action formatted as `  • <title>  →  copilot -p "Execute the prompt defined in <path>"` (non-navigable, not counted in `total_items`).
7. Save the file.

**Done Criteria:**
- `render_menu()` signature contains `cli_available: bool` parameter.
- No `[script]` suffix appears on Script action lines.
- No `[prompt_file]` suffix appears on Prompt action lines.
- With `cli_available=False`: static informational block renders; no navigable indices for prompts.
- With `cli_available=True`: navigable Prompt entries render as before.

**Dependencies:** Task 2 (binary update establishes the detection contract before gating is wired up).

**Risk Notes:** None.

---

### Task 4: Remove command-echo prints from run_action()

**Intent:** Delete the two `print()` calls that display `Running command:` and the raw Python command string to the terminal.

**Inputs:** `.aib_brain/tools/menu.py` — `run_action()` function (lines ~504–543); `print("\nRunning command:")` and `print(" ".join(command))` calls

**Outputs:** `.aib_brain/tools/menu.py` — `run_action()` no longer emits command-echo lines before execution

**Procedure:**
1. Read `.aib_brain/tools/menu.py` lines 503–545 to locate both print calls.
2. Remove `print("\nRunning command:")`.
3. Remove `print(" ".join(command))`.
4. Save the file.

**Done Criteria:** `run_action()` body contains neither `print("\nRunning command:")` nor `print(" ".join(command))`.

**Dependencies:** None.

**Risk Notes:** None.

---

### Task 5: Update choose_action() — eager detection and navigation gating

**Intent:** Call `_detect_copilot_cli()` once before the `while True` loop; pass the result to `render_menu()` as `cli_available`; exclude Prompt action indices from `total_items` when CLI is absent.

**Inputs:** `.aib_brain/tools/menu.py` — `choose_action()` function (lines ~622–661); updated `render_menu()` signature from Task 3

**Outputs:** `.aib_brain/tools/menu.py` — `_detect_copilot_cli()` called exactly once before `while True`; result passed as `cli_available` on every `render_menu()` call; `total_items` is `len(script_actions)` when CLI is absent

**Procedure:**
1. Read `.aib_brain/tools/menu.py` lines 620–665 to confirm exact current structure of `choose_action()`.
2. Add `cli_available = _detect_copilot_cli()` immediately before the `while True:` loop.
3. Pass `cli_available=cli_available` to every `render_menu()` call inside the loop.
4. When `not cli_available`, set `total_items = len(script_actions)` so Prompt action indices are non-navigable.
5. Confirm no call to `_detect_copilot_cli()` remains inside `run_prompt_action()` (to be removed in Task 6 if present).
6. Save the file.

**Done Criteria:**
- Exactly one `_detect_copilot_cli()` call exists before the `while True` loop.
- All `render_menu()` calls inside the loop receive `cli_available` argument.
- When `cli_available = False`, keyboard navigation cannot reach a Prompt action entry.

**Dependencies:** Task 3 (updated `render_menu()` signature must exist before it can be called with `cli_available`).

**Risk Notes:** Assumption A3 — eager detection adds negligible latency (< 1 s) under normal PATH conditions.

---

### Task 6: Replace run_prompt_action() body with real CLI invocation

**Intent:** Replace the entire body of `run_prompt_action()` with a direct `subprocess.run` call that launches `copilot` interactively; remove all copy/paste guidance text.

**Inputs:** `.aib_brain/tools/menu.py` — `run_prompt_action()` function (lines ~595–620); `choose_action()` gating from Task 5 (ensures this function is only called when CLI is available)

**Outputs:** `.aib_brain/tools/menu.py` — `run_prompt_action()` body is `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])`; no copy/paste text; no lazy `_detect_copilot_cli()` call inside

**Procedure:**
1. Read `.aib_brain/tools/menu.py` lines 593–625 to confirm exact current body.
2. Delete the entire body of `run_prompt_action()`.
3. Replace with exactly: `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` — no `capture_output` argument.
4. Verify `subprocess` is already imported at the top of `menu.py` (confirm by reading import block).
5. Save the file.

**Done Criteria:**
- `run_prompt_action()` body contains only the `subprocess.run` call.
- No copy/paste text (`print(...)` referencing manual CLI invocation) remains.
- No lazy `_detect_copilot_cli()` call remains inside `run_prompt_action()`.
- No `capture_output` argument is passed to `subprocess.run`.

**Dependencies:** Task 5 (gating ensures this function is only reachable when CLI is available).

**Risk Notes:** Assumption A2 — `copilot` accepts bare prompt string without subcommand. Recommended: manually run `copilot -p "Execute the prompt defined in .aib_brain/prompts/aib-create-analysis.md"` on the target machine before executing this task.

---

### Task 7: Update close-request.py — auto-close iteration guard and imports

**Intent:** Add `COMPLETED`, `format_markdown_table`, `write_text` to imports; replace the guard that raises `ValidationError` when an active iteration exists with logic that auto-closes each active iteration and prints a notice.

**Inputs:**
- `.aib_brain/tools/close-request.py` — full file; import block (lines ~1–15); guard at lines ~55–57: `raise ValidationError("Cannot close request while an iteration is Active")`
- `.aib_brain/tools/close-iteration.py` — reference pattern for the iteration table write operation

**Outputs:** `.aib_brain/tools/close-request.py` — imports extended; guard replaced with auto-close loop

**Procedure:**
1. Read `.aib_brain/tools/close-request.py` fully to confirm exact import block, variable names, and guard context.
2. Read `.aib_brain/tools/close-iteration.py` to confirm the iteration write pattern (`write_text`, `format_markdown_table`, header names, row structure).
3. In the `from common import ...` statement of `close-request.py`, add `COMPLETED`, `format_markdown_table`, `write_text`.
4. Locate the guard block `if active_iterations: raise ValidationError(...)`.
5. Replace it with:
   ```
   if active_iterations:
       for it_id in active_iterations:
           # update the iterations table row to COMPLETED
           <mirror close-iteration.py write pattern using confirmed variable names>
           print(f"Auto-closed iteration {it_id} before closing request.")
   ```
   Use the exact variable names (`iterations_path`, `header`, `rows`, etc.) found by reading the file in step 1.
6. Save the file.

**Done Criteria:**
- `close-request.py` imports include `COMPLETED`, `format_markdown_table`, `write_text`.
- Running `python .aib_brain/tools/close-request.py --workspace .` with an Active iteration exits code 0.
- Terminal prints `"Auto-closed iteration <id> before closing request."` for each auto-closed iteration.
- Terminal then prints `"Closed request: R-..."`.
- Running with an already-closed request still raises `ValidationError("Request already closed")`.

**Dependencies:** None — independent of `menu.py` changes.

**Risk Notes:** Assumption A4 — all three names importable from `common`. Read full import block before modifying; confirm no collision with existing aliases.

---

### Task 8: Add tests to test_common.py

**Intent:** Add `TestCloseRequestAutoClose` test class testing the auto-close path, and a test asserting `EXCLUDE_SCRIPTS` membership of `"reverse-engineer.py"` and `"test_common.py"`.

**Inputs:**
- `.aib_brain/tools/test_common.py` — full existing test file; note existing fixture and helper patterns
- Completed code changes from Task 1 (`EXCLUDE_SCRIPTS` updated) and Task 7 (`close-request.py` auto-close implemented)

**Outputs:** `.aib_brain/tools/test_common.py` — new `TestCloseRequestAutoClose` class with (a) auto-close path test and (b) `EXCLUDE_SCRIPTS` membership test

**Procedure:**
1. Read `.aib_brain/tools/test_common.py` fully to understand existing fixture conventions, import style, and helper patterns.
2. Add a new test class `TestCloseRequestAutoClose` at the end of the file.
3. Add test `test_close_request_auto_closes_active_iteration`: set up a minimal temporary workspace with an Active iteration; invoke `close-request.py` programmatically (import and call the relevant entry function, or run via subprocess); assert that the iteration row is now `Completed`; assert output contains `"Auto-closed iteration"`.
4. Add test `test_exclude_scripts_contains_new_entries`: import `EXCLUDE_SCRIPTS` from `menu`; assert `"reverse-engineer.py" in EXCLUDE_SCRIPTS` and `"test_common.py" in EXCLUDE_SCRIPTS`.
5. Run `pytest .aib_brain/tools/test_common.py` and confirm all tests pass.
6. Save the file.

**Done Criteria:**
- `TestCloseRequestAutoClose` class exists in `test_common.py`.
- `test_close_request_auto_closes_active_iteration` passes without error.
- `test_exclude_scripts_contains_new_entries` passes without error.
- `pytest .aib_brain/tools/test_common.py` exits code 0 with 100% pass rate.

**Dependencies:** Task 1 (EXCLUDE_SCRIPTS updated), Task 7 (auto-close logic implemented).

**Risk Notes:** Mirror existing test fixture conventions strictly to avoid test isolation issues.

---

### Task 9: Update product documentation

**Intent:** Update ARCH-01, CMP-01, RQT-02, and KNW-01 to accurately reflect all implemented changes.

**Inputs:**
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Component Inventory row: AIB Command Menu Description
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Catalog rows CMP-ART-0005 and CMP-ART-0006 (`edge_cases_and_validation` cells)
- `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-008
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Term Entries table (TERM-0012 is last existing entry)
- `.aib_brain/conventions/arch-01-convention.md`, `.aib_brain/conventions/cmp-01-convention.md`, `.aib_brain/conventions/rqt-02-convention.md`, `.aib_brain/conventions/knw-01-convention.md` — governing conventions

**Outputs:**
- ARCH-01.md: AIB Command Menu Description updated to reference `copilot --version` detection, `EXCLUDE_SCRIPTS` non-tool exclusion mechanism, and static informational block when CLI is absent
- CMP-01.md: CMP-ART-0005 `edge_cases_and_validation` — appended: `; auto-closes active iteration(s) before closing request and prints a notice per iteration`; CMP-ART-0006 `edge_cases_and_validation` — appended: `; prompt actions gated on copilot CLI detection; when CLI absent, renders static informational block; EXCLUDE_SCRIPTS prevents non-tool scripts from appearing`
- RQT-02.md: FR-008 extended to: `The system supports launching tool scripts via an interactive menu; prompt actions require copilot CLI availability and display as informational only when CLI is absent`
- KNW-01.md: TERM-0013 row added: `TERM-0013 | Prompt Action | A menu entry mapping to a .aib_brain/prompts/aib-*.md file; navigable and executable when copilot CLI is available; informational-only display when CLI is absent. | aib-create-analysis.md | AIB Maintainers | — | menu, tooling | Proposed | 1`

**Procedure:**
1. Read each target doc to confirm current state matches `04-analysis.md` §7 Evidence summary.
2. Read governing convention for each doc to confirm required field format before editing.
3. Update ARCH-01.md AIB Command Menu Description cell — append the CLI-gating, EXCLUDE_SCRIPTS, and static fallback context.
4. Update CMP-01.md CMP-ART-0005 `edge_cases_and_validation` cell — append auto-close side effect text.
5. Update CMP-01.md CMP-ART-0006 `edge_cases_and_validation` cell — append CLI-gating and EXCLUDE_SCRIPTS text.
6. Update RQT-02.md FR-008 line — extend with CLI-gated navigation language.
7. Update KNW-01.md Term Entries table — add TERM-0013 row after TERM-0012 with the values above.
8. Verify each updated file still conforms to its convention (column order, field format, no extra tables added).

**Done Criteria:**
- ARCH-01.md AIB Command Menu Description references `copilot --version` detection, `EXCLUDE_SCRIPTS`, and static informational block.
- CMP-ART-0005 `edge_cases_and_validation` includes auto-close-iteration side effect.
- CMP-ART-0006 `edge_cases_and_validation` includes CLI-gating and EXCLUDE_SCRIPTS reference.
- FR-008 in RQT-02.md includes CLI-gated prompt navigation language.
- KNW-01.md contains TERM-0013 "Prompt Action" row.

**Dependencies:** Tasks 1–8 (all code changes and tests complete and verified before docs are finalized).

**Risk Notes:** All four docs have `edit_allowed = Y` per `.aib_memory/references.md`. No follow-up required for permissions.

---

## Dependencies & Interfaces

- From Task: 2 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: `render_menu()` CLI-gating relies on the updated detection binary being set correctly first.
- From Task: 3 | To Task: 5 | Dependency Type: FS | Critical: Y | Notes: `choose_action()` calls `render_menu()` with `cli_available`; signature must exist before wiring.
- From Task: 5 | To Task: 6 | Dependency Type: FS | Critical: Y | Notes: `run_prompt_action()` is only reachable when CLI is available; gating must be in place before replacing the body.
- From Task: 1 | To Task: 8 | Dependency Type: FS | Critical: Y | Notes: `EXCLUDE_SCRIPTS` membership test reads the updated constant.
- From Task: 7 | To Task: 8 | Dependency Type: FS | Critical: Y | Notes: Auto-close test exercises the implemented guard replacement.
- From Task: 1 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect the implemented state of `EXCLUDE_SCRIPTS`.
- From Task: 2 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect the `copilot --version` detection binary.
- From Task: 3 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect CLI-gated Prompt section behaviour.
- From Task: 4 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect removal of command-echo output.
- From Task: 5 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect eager navigation gating in `choose_action()`.
- From Task: 6 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect real `copilot` CLI invocation in `run_prompt_action()`.
- From Task: 7 | To Task: 9 | Dependency Type: FS | Critical: N | Notes: Docs must reflect auto-close side effect in `close-request.py`.
- From Task: 8 | To Task: 9 | Dependency Type: FS | Critical: Y | Notes: Tests must pass (100%) before docs are finalised.

- Interface: `.aib_brain/tools/common.py` | Direction: In | Protocol/Contract: Python module import | Version: current (no changes) | Notes: `COMPLETED`, `format_markdown_table`, `write_text` imported by `close-request.py`; already exported by `common.py`.
- Interface: `copilot` binary | Direction: Out | Protocol/Contract: subprocess call; first positional arg is prompt string | Version: installed version on developer PATH | Notes: Detection: `copilot --version`; invocation: `copilot -p "Execute the prompt defined in <path>"`.

---

## Environment & Configuration

**Environments:** Dev (local developer workstation only; no Stage/Prod pipeline)

- Key: WORKSPACE_ROOT | Scope: Global | Default: `.` | Allowed Range/Values: Any valid workspace root path | Source: CLI parameter `--workspace` | Change Control: CLI argument; no configuration file

**Secrets Handling:** N/A. No secrets involved in this change set.

---

## Testing Strategy (This Iteration)

- Test Types: Unit
- Coverage Targets: 100% pass rate for full `pytest .aib_brain/tools/test_common.py` run (existing tests plus two new tests)
- Data/Fixtures: Minimal in-memory or temporary-directory fixtures; mirror existing test helper and fixture conventions found in `test_common.py`
- Test Execution: `pytest .aib_brain/tools/test_common.py` from workspace root
- Acceptance Evidence: pytest terminal output showing exit code 0 and all tests PASSED

---

## Observability & Quality Gates

- Metrics: Test pass count must equal total test count (zero failures)
- Logs: pytest terminal output; no persistent logs required for this iteration
- Alerts: None (local dev only)
- Quality Gates:
  - `pytest .aib_brain/tools/test_common.py` exits code 0 with 100% pass rate
  - No `[script]` or `[prompt_file]` suffixes visible in any rendered menu section (visual verification)
  - `python .aib_brain/tools/close-request.py --workspace .` with an Active iteration exits code 0 (manual verification)
  - All four product docs pass a structural review against their respective conventions

---

## Documentation Touchpoints

- Doc Path: `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` | Change Type: update | Update Trigger: Task 9 | Edit Allowed: Y | Notes: AIB Command Menu Description cell; REF-0001 in references.md
- Doc Path: `.aib_memory/docs/04 Technology/Compute/CMP-01.md` | Change Type: update | Update Trigger: Task 9 | Edit Allowed: Y | Notes: CMP-ART-0005 and CMP-ART-0006 `edge_cases_and_validation` cells; REF-0007 in references.md
- Doc Path: `.aib_memory/docs/03 Requirements/RQT-02.md` | Change Type: update | Update Trigger: Task 9 | Edit Allowed: Y | Notes: FR-008 text extension; REF-0023 in references.md
- Doc Path: `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` | Change Type: update | Update Trigger: Task 9 | Edit Allowed: Y | Notes: Add TERM-0013 Prompt Action row; REF-0018 in references.md

---

## Milestones

- Planned Start: 2026-04-03 11:35 +0300
- Planned End: End of current implementation session

- Milestone: M1 | Description: All six menu.py inline edits complete | Due: before Task 8 | Depends On: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6 | Exit Criteria: All six changes verified in source; no `[script]`/`[prompt_file]` suffixes; no command-echo prints; `choose_action()` uses eager detection.
- Milestone: M2 | Description: close-request.py auto-close implemented and full test suite passes | Due: before Task 9 | Depends On: Task 7, Task 8 | Exit Criteria: `pytest .aib_brain/tools/test_common.py` exits code 0.
- Milestone: M3 | Description: All four product docs updated | Due: iteration close | Depends On: Task 9 (after M2) | Exit Criteria: ARCH-01, CMP-01, RQT-02, KNW-01 Done Criteria all satisfied.

---

## Risks & Mitigations

- R1: Assumption A2 false — `copilot` requires a subcommand rather than a bare string — P: Low, I: Med — Mitigation: Manually run `copilot -p "Execute the prompt defined in .aib_brain/prompts/aib-create-analysis.md"` on the target machine before executing Task 6; if wrong, determine correct invocation form and update accordingly.
- R2: Line-number drift in menu.py — analysis references line numbers (~16, ~57, ~504, ~549, ~595, ~622) that may shift if the file was modified — P: Low, I: Low — Mitigation: Always re-read the target function by name before editing; never rely solely on line numbers.
- R3: test_common.py fixture incompatibility — new tests must match existing fixture and helper style — P: Low, I: Low — Mitigation: Read full `test_common.py` before writing new tests; mirror existing patterns.
- R4: Import collision in close-request.py — `write_text` or `format_markdown_table` may already be imported under a different alias — P: Very Low, I: Low — Mitigation: Read full import block of `close-request.py` before modifying; resolve any alias conflicts.
- R5: Partial render_menu() rewrite breaks existing navigable Script section — P: Low, I: Med — Mitigation: Run the menu interactively after Task 3 to verify Script section still renders correctly before proceeding to Task 5.

---

## Acceptance & Handover

- Acceptance Criteria:
  - Task 1 Done Criteria satisfied: `EXCLUDE_SCRIPTS` contains all five entries
  - Task 2 Done Criteria satisfied: `_detect_copilot_cli()` uses `["copilot", "--version"]`
  - Task 3 Done Criteria satisfied: `render_menu()` has `cli_available` parameter; no suffixes on menu lines; static block branch present
  - Task 4 Done Criteria satisfied: no command-echo prints in `run_action()`
  - Task 5 Done Criteria satisfied: `choose_action()` uses eager detection; `cli_available` passed to every `render_menu()` call
  - Task 6 Done Criteria satisfied: `run_prompt_action()` body is single `subprocess.run` call; no copy/paste text
  - Task 7 Done Criteria satisfied: `close-request.py` auto-closes active iterations and exits code 0
  - Task 8 Done Criteria satisfied: `pytest .aib_brain/tools/test_common.py` exits code 0 (100% pass)
  - Task 9 Done Criteria satisfied: all four product docs updated per Done Criteria

- Handover Artifacts:
  - Modified source: `.aib_brain/tools/menu.py`
  - Modified source: `.aib_brain/tools/close-request.py`
  - Modified tests: `.aib_brain/tools/test_common.py`
  - Updated docs: `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md`, `.aib_memory/docs/04 Technology/Compute/CMP-01.md`, `.aib_memory/docs/03 Requirements/RQT-02.md`, `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md`

- Post-Iteration Follow-ups:
  - Validate Assumption A2 (`copilot` bare-string invocation) manually before executing Task 6 if not already confirmed
  - Consider promoting KNW-01 terms from `Proposed` → `Approved` status in a follow-up request
