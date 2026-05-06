# Request

## Goal

1. To be removed iterations of a request. No more prefixed analysis, questionnaire and plan files. Hence the iterations are not needed. Remove from the application menu options, scripts, prompts, conventions, contexts, documentation Readme and Concepts.md.
2. Modify the analysis prompt to apply the answered questions in the request and to remove the answered questions (replace the answered questions with direct instructions following the prefered by the user option)
3. Add notation if the user wants to add/modify something in the request and wants to ask the AI to revise the request accordingly. This could be by adding a special type instruction in the request file and running the analysis prompt again to apply these ammendments.

## Background

## Scope

## Out of scope

## Constraints

## Success criteria

## Assumptions

- A1: `common.py` contains no iteration-exclusive helpers; all iteration-related logic is self-contained within `create-iteration.py` and `close-iteration.py` and their tests.
  - Risk if false: Removing the scripts without updating `common.py` would leave dead exports that may cause import errors in other tool scripts.

- A2: `.aib_memory/context.md` will be regenerated via `aib-context.md` after this change and does not require manual updating.
  - Risk if false: `context.md` would contain stale iteration references visible to any AI agent reading it as context.

- A3: `questionnaire-convention.md` has no active prompt referencing it and no active test relying on it; deletion is safe.
  - Risk if false: A hidden reference would cause a broken link or convention-not-found failure.

## Plan

### Task 1: Update `menu.py` — remove iteration tracking and actions
**Intent:** Eliminate all iteration-related code from the terminal menu launcher.
**Inputs:** `.aib_brain/tools/menu.py` (current)
**Outputs:** Updated `menu.py` without `SCRIPT_CREATE_ITERATION`, `SCRIPT_CLOSE_ITERATION`, `MenuState.active_iteration_id`, `has_active_iteration`, iteration filtering branches, or iteration-specific actions in `build_script_actions()`.
**External Interfaces:** None.
**Environment & Configuration:** Python 3.10+; no external deps.
**Procedure:**
1. Remove `SCRIPT_CREATE_ITERATION = "create-iteration.py"` and `SCRIPT_CLOSE_ITERATION = "close-iteration.py"` constants.
2. Add `"create-iteration.py"` and `"close-iteration.py"` to `EXCLUDE_SCRIPTS`.
3. Remove `active_iteration_id` field and `has_active_iteration` property from `MenuState`.
4. Remove iteration-tracking logic from `resolve_menu_state()` (iterations_path read, it_header/it_rows parse, active_iterations check, iteration_id return).
5. Remove the two hardcoded iteration action dicts (id 3&4) from `build_script_actions()`.
6. Remove the `SCRIPT_CREATE_ITERATION` and `SCRIPT_CLOSE_ITERATION` filtering branches from `filter_visible_actions()`.
**Done Criteria:** `menu.py` imports and runs without reference to iteration concepts; visible action list for an active request shows only Create Request (when no active), Close Request, and any auto-discovered scripts.
**Dependencies:** None.
**Risk Notes:** If other auto-discovered scripts depend on `has_active_iteration`, they would break; verify no such dependency exists first.

### Task 2: Update `create-request.py` — remove `iterations.md` creation
**Intent:** Stop seeding `iterations.md` when a new request is created.
**Inputs:** `.aib_brain/tools/create-request.py` (current)
**Outputs:** Updated `create-request.py` that creates only `request.md` and `implementation.md`; no `iterations.md`.
**External Interfaces:** None.
**Environment & Configuration:** Python 3.10+.
**Procedure:**
1. Remove imports no longer needed after the block is deleted (audit: `format_markdown_table`, `now_iso` — keep if used elsewhere in the file).
2. Delete the `iterations_intro`, `iterations_table`, and `write_text(request_folder / "iterations.md", ...)` block.
3. Verify printed output still reflects the created artifacts accurately.
**Done Criteria:** Running `create-request.py` on a clean workspace creates `request.md` and `implementation.md` but no `iterations.md`.
**Dependencies:** None.
**Risk Notes:** `format_markdown_table` and `now_iso` are also used by other parts of the script; do not remove those imports unless confirmed unused.

### Task 3: Update `analysis-convention.md` and `request-convention.md` — rename analysis file
**Intent:** Replace `<ITERATION_ID>-analysis.md` with `analysis.md` in both normative convention files.
**Inputs:** `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`
**Outputs:** Updated conventions with `analysis.md` as the canonical output file name.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. In `analysis-convention.md`: update Section 3 (File Naming) — replace all occurrences of `<ITERATION_ID>-analysis.md` with `analysis.md`; remove `ITERATION_ID` definition; update Section 8 (Creation Workflow) Seed step.
2. In `analysis-convention.md`: update Section 2 Scope statement; remove iteration ID references from Section 4.1 Executive Summary requirements.
3. In `request-convention.md`: update optional sections list to reference `analysis.md`; remove iteration-resolution requirement.
**Done Criteria:** Both convention files reference `analysis.md` exclusively with no remaining `ITERATION_ID` patterns.
**Dependencies:** None.
**Risk Notes:** None.

### Task 4: Update `aib-analysis.md` prompt — rename output, apply Q&D, add amendment detection
**Intent:** Rework the analysis prompt to (a) output `analysis.md`, (b) consume answered Q&D questions instead of preserving them, and (c) detect and apply `## Amend Request` amendments before analysis.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (current)
**Outputs:** Updated `aib-analysis.md` with three behaviour changes.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Change Goal line: replace `<ITERATION_ID>-analysis.md` with `analysis.md`.
2. Remove iteration ID resolution from Mandatory preflight (steps 1 "Resolve active request and active iteration" → change to "Resolve active request").
3. Add new preflight step (before analysis drafting): detect `## Amend Request` section in `request.md`; if present, apply its instructions to the relevant mandatory sections (Goal, Background, Scope, Out of scope, Constraints, Success criteria), then remove the `## Amend Request` section from `request.md`.
4. In "Re-run behaviour — `## Questions & Decisions`": replace the "answered questions MUST be preserved verbatim" rule with: "answered questions MUST be applied as embedded instructions to the relevant sections of `request.md`, then removed from `## Questions & Decisions`." Define "answered" as: checkbox `[x]` checked OR `> Answer:` has non-empty text.
5. Update "Re-run behaviour summary" bullet for `## Questions & Decisions` to reflect: apply-and-remove instead of merge/preserve.
6. Update Section 8 output path reference.
**Done Criteria:** The prompt specifies `analysis.md` as output; Q&D answered questions are consumed; amendment detection is described; no iteration ID reference remains.
**Dependencies:** Task 3 (convention must be consistent with prompt).
**Risk Notes:** The apply-and-remove logic requires the AI to reason about which section an answer applies to; include an explicit mapping hint in the prompt.

### Task 5: Update `request-convention.md` — define `## Amend Request` transient section
**Intent:** Document the `## Amend Request` section as a user-facing transient amendment mechanism in the normative convention.
**Inputs:** `.aib_brain/conventions/request-convention.md`
**Outputs:** Updated convention with definition of the `## Amend Request` section.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Add a new entry after Optional Section 11 (`## Questions & Decisions`) describing `## Amend Request`: purpose (user-written inline amendment), format (free text), lifecycle (created by user, consumed and cleared by `create-analysis`), and rule (never preserved across analysis runs).
2. Note that the section must NOT appear in the seed template.
**Done Criteria:** `request-convention.md` contains a normative definition for `## Amend Request` as a transient section.
**Dependencies:** Task 4 (prompt references the mechanism).
**Risk Notes:** None.

### Task 6: Update `aib-implement.md` prompt — remove iteration resolution
**Intent:** Remove the step that resolves active iteration from `iterations.md`.
**Inputs:** `.aib_brain/prompts/aib-implement.md`
**Outputs:** Updated `aib-implement.md` without iteration resolution.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Remove the "Resolve active iteration from request `iterations.md`" line from Input resolution section.
2. Verify no other reference to `<ITERATION_ID>` or `iterations.md` remains.
**Done Criteria:** `aib-implement.md` contains no iteration ID or `iterations.md` references.
**Dependencies:** None.
**Risk Notes:** None.

### Task 7: Update `Concepts.md` — remove iteration concept
**Intent:** Remove all iteration-related definitions, actions, constraints, and file examples from `Concepts.md`.
**Inputs:** `.aib_brain/Concepts.md`
**Outputs:** Updated `Concepts.md` without iteration lifecycle actions, conventions, or file naming references.
**External Interfaces:** None.
**Environment & Configuration:** Text editor.
**Procedure:**
1. Remove `create-iteration` and `close-iteration` from Supported actions list.
2. Remove both rows from Action contract matrix.
3. Remove iteration-related rules from "Common input resolution rules" (iteration_id resolution logic and failure condition).
4. Remove `create-iteration` and `close-iteration` from Holistic workflow steps 5–6; renumber remaining steps.
5. Remove iteration lifecycle states, allowed transitions, and concurrency rule for iterations from the Lifecycle section.
6. Remove "Iteration files naming (normative)" section.
7. Update folder structure example under "Content of request folder" — remove `iterations.md` and rename `01-analysis.md` to `analysis.md`.
8. Remove `iterations.md` description from "What each file means" list.
9. Update `<ITERATION_ID>-analysis.md` description to `analysis.md`.
10. Remove `iterations-template.md` from "Minimal list of templates".
11. Remove `create-iteration.py` and `close-iteration.py` from "Minimal tools to be defined".
**Done Criteria:** `Concepts.md` contains no reference to iteration ID, iteration files, `iterations.md`, or the two removed scripts.
**Dependencies:** None.
**Risk Notes:** `Concepts.md` has `edit_allowed=N` in `references.md`; this is an explicit user-requested modification to brain assets and is permitted.

### Task 8: Update `README.md` (root) and `.aib_brain/README.md`
**Intent:** Remove iteration-related commands and workflow steps from both README files.
**Inputs:** `README.md` (root), `.aib_brain/README.md`
**Outputs:** Updated README files without iteration command examples or workflow steps.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Root `README.md`: remove any iteration command references if present.
2. `.aib_brain/README.md`: remove `create-iteration.py` and `close-iteration.py` from "Common Commands" (Windows and Linux examples); remove "Add progress steps: `create-iteration.py`" and "Finish current step: `close-iteration.py`" from "Typical Daily Flow"; remove `aib-questionnaire.md` and `aib-plan.md` from "Available prompt files" list; remove steps 2–3 from "Recommended order per iteration"; update the Scenario 1 workflow description; rename analysis output to `analysis.md` throughout.
**Done Criteria:** Neither README file contains `create-iteration`, `close-iteration`, `aib-questionnaire`, `aib-plan`, or `<ITERATION_ID>` mentions.
**Dependencies:** None.
**Risk Notes:** None.

### Task 9: Update product documentation — RQT-02, KNW-01, KNW-02, ARCH-01
**Intent:** Keep product docs consistent with the removed iteration behaviour.
**Inputs:** RQT-02, KNW-01, KNW-02, ARCH-01
**Outputs:** Updated docs with iteration references removed.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. `RQT-02`: Remove FR-003 ("manages exactly one Active iteration per request"); update FR-004 to read "generates `analysis.md` per request" (no ITERATION_ID prefix); update acceptance criteria item 2 to remove "creates iteration 01 as Active".
2. `KNW-01`: Remove the TERM-0006 row ("Iteration") and add a change log entry recording the removal.
3. `KNW-02`: Update BP-0002 description — remove "including default iteration 01"; update outputs list to remove `iterations.md`; update steps to remove iteration seed step.
4. `ARCH-01`: Update AIB Tool Scripts component description to remove `create-iteration.py` and `close-iteration.py` references.
**Done Criteria:** All four product docs contain no iteration lifecycle references.
**Dependencies:** None.
**Risk Notes:** None.

### Task 10: Delete iteration scripts, conventions, and template
**Intent:** Remove the now-obsolete files from the workspace.
**Inputs:** `.aib_brain/tools/create-iteration.py`, `.aib_brain/tools/close-iteration.py`, `.aib_brain/conventions/iterations-convention.md`, `.aib_brain/conventions/questionnaire-convention.md`, `.aib_brain/templates/iterations-template.md`
**Outputs:** Files deleted.
**External Interfaces:** None.
**Environment & Configuration:** File system.
**Procedure:**
1. Confirm `common.py` has no iteration-exclusive exports consumed only by the two scripts (Assumption A1 validation).
2. Delete `create-iteration.py`.
3. Delete `close-iteration.py`.
4. Delete `iterations-convention.md`.
5. Delete `questionnaire-convention.md`.
6. Delete `iterations-template.md`.
**Done Criteria:** None of the five files exist; no import errors in remaining tool scripts.
**Dependencies:** Tasks 1, 2, 7 (all references removed before file deletion).
**Risk Notes:** Deletion is irreversible via file system; VCS (git) is the recovery path if needed.

### Task 11: Update and remove iteration test files
**Intent:** Remove tests for deleted scripts and update integration tests that assert iteration presence.
**Inputs:** `tests/test_create_iteration.py`, `tests/test_close_iteration.py`, `tests/conftest.py`, `tests/test_lifecycle_e2e.py`, `tests/test_create_request.py`
**Outputs:** Two test files deleted; remaining test files updated.
**External Interfaces:** `pytest` test runner.
**Environment & Configuration:** Python 3.10+; `pytest`.
**Procedure:**
1. Read `conftest.py` and `test_lifecycle_e2e.py` and `test_create_request.py` fully; identify all assertions related to `iterations.md`, `iteration_id`, or iteration-prefixed files.
2. Delete `test_create_iteration.py` and `test_close_iteration.py`.
3. Update `test_create_request.py` to assert `iterations.md` is NOT created.
4. Update `test_lifecycle_e2e.py` and `conftest.py` to remove iteration-dependent fixtures and assertions.
5. Run `pytest` and confirm all remaining tests pass.
**Done Criteria:** No test file references iteration scripts or `iterations.md`; `pytest` exits with code 0.
**Dependencies:** Tasks 1, 2, 10 (scripts deleted before test suite is cleaned up).
**Risk Notes:** Removing assertions from `test_lifecycle_e2e.py` may decrease coverage of the request open/close flow; ensure the `implementation.md` creation and `request.md` creation are still asserted.

## Testing

- T1 — analysis file created without iteration prefix: Run `create-analysis` (aib-analysis.md) on the active request. Expected outcome: `analysis.md` is created in the request folder; no file named `<nn>-analysis.md` is created.

- T2 — menu shows no iteration actions: Launch the menu with an active request. Expected outcome: "Create iteration" and "Close iteration" are absent from the displayed action list.

- T3 — create-request produces no iterations.md: Run `python create-request.py --workspace . --title "Test"`. Expected outcome: `request.md` and `implementation.md` exist in the new request folder; `iterations.md` does not exist.

- T4 — answered Q&D applied and removed: Place an answered `**Q001**` block (checkbox checked) in `## Questions & Decisions` of `request.md`. Re-run `aib-analysis.md`. Expected outcome: the Q001 block no longer exists in `## Questions & Decisions`; the answer has been applied as appropriate text in the relevant mandatory section of `request.md`.

- T5 — amendment applied and cleared: Add `## Amend Request\n\nAdd testing details to Scope.` to `request.md`. Run `aib-analysis.md`. Expected outcome: `## Scope` is updated to include the referenced testing details; `## Amend Request` section no longer exists in `request.md`.

- T6 — amendment re-run idempotency: Re-run `aib-analysis.md` on a `request.md` that has no `## Amend Request` section. Expected outcome: no error; `request.md` unchanged with respect to the Amend section; analysis regenerates normally.

- T7 — test suite passes after deletions: Run `pytest` from workspace root after all Task 10–11 changes. Expected outcome: all tests pass; exit code 0; no import errors for deleted scripts.

- T8 — no residual iteration references: Run a full-workspace grep for `iteration_id|ITERATION_ID|iterations\.md|create-iteration|close-iteration` excluding `.aib_memory/requests/` (historical data). Expected outcome: zero matches.

- T9 — product docs updated: Check `RQT-02`, `KNW-01`, `KNW-02`, `ARCH-01` directly. Expected outcome: no occurrence of FR-003, TERM-0006, "iteration 01", or `create-iteration.py` / `close-iteration.py` script names.

## Documentation

- `.aib_brain/conventions/analysis-convention.md` (ref_id: N/A) — Normative convention updated: file naming changed from `<ITERATION_ID>-analysis.md` to `analysis.md`.

- `.aib_brain/conventions/request-convention.md` (ref_id: N/A) — Normative convention updated: analysis path reference updated; `## Amend Request` transient section defined.

- `.aib_brain/prompts/aib-analysis.md` (ref_id: N/A) — Prompt reworked: output path, Q&D consumption behaviour, amendment detection.

- `.aib_brain/prompts/aib-implement.md` (ref_id: N/A) — Iteration resolution step removed.

- `.aib_brain/Concepts.md` (ref_id: REF-0028) — Brain asset updated: iteration actions, contract matrix, workflow, file naming removed.

- `README.md` (ref_id: N/A) — Root README updated: iteration references removed.

- `.aib_brain/README.md` (ref_id: N/A) — User guide updated: iteration commands and workflow steps removed.

- `.aib_memory/docs/03 Requirements/RQT-02.md` (ref_id: REF-0023) — FR-003 removed; FR-004 updated to `analysis.md` naming; acceptance criteria updated.

- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` (ref_id: REF-0018) — TERM-0006 (Iteration) removed; change log updated.

- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` (ref_id: REF-0019) — BP-0002 updated to remove iteration seeding.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` (ref_id: REF-0001) — AIB Tool Scripts component description updated.
