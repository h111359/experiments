## Goal

Evolve the AIB framework workflow by introducing seven coordinated improvements: (1) establish `.aib_memory/input.md` as the ephemeral primary user-agent communication channel; (2) automate request creation from `aib-analysis.md` when no active request exists and automate request closing from `aib-implement.md` upon successful implementation; (3) make `request.md` AI-generated from `input.md` content and make `implementation.md` generated on-demand by `aib-implement.md`, removing all template seeding; (4) reshape the CLI menu to display copy-paste-ready prompt invocations and remove lifecycle commands and exit option; (5) restructure the analysis and request section conventions by moving code/asset scan and internal review into `request.md`, adding a multi-perspective stakeholder review, and making external benchmarking and spike-testing mandatory standalone sections in `analysis.md`; (6) bump the product version to v1.2.0; (7) create a `versions/` folder in the workspace root and archive `.aib_brain` as a versioned zip per version bump, updating installation instructions accordingly.

## Background

The current AIB workflow requires an explicit "Create request" CLI command before any AI-driven work can begin. The interactive menu seeds `request.md` and `implementation.md` from templates in `.aib_brain/templates/` via `create-request.py`. This multi-step ceremony adds friction and diverges from the conversational, iterative interaction model that AIB targets.

The analysis convention currently places "Code and asset scan for impacted components" and "Internal review" inside `analysis.md`, which is a reasoning-only artifact not intended as an implementation driver. Moving these sections to `request.md` makes specifications more actionable and brings stakeholder-relevant review closer to the request definition.

Installation currently requires manually copying the `.aib_brain/` folder from the repository. A versioned zip archive in a `versions/` folder would simplify installation and provide reproducible upgrade paths.

## Scope

- Introduce `.aib_memory/input.md` as the primary user-agent communication channel (ephemeral; overwrite-friendly; cleared to seed template after processing; archived per-request for audit).

- Update `initialize.py` to create `input.md` with a seed template on workspace initialization.

- Update `aib-analysis.md` prompt: when no active request exists, read `input.md`, auto-create a new request with AI-generated `request.md` (following `request-convention.md`), archive `input.md` content to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`, and reset `input.md` to seed template. **Amendment:** For file operations use python scripts 

- Update `aib-implement.md` prompt: auto-run analysis if no active request exists before implementing; generate `implementation.md` from scratch during execution (not pre-seeded); auto-close the request upon successful completion by invoking `close-request.py`.

- Update `create-request.py`: retain folder creation and register update; remove template-based seeding of `request.md` and `implementation.md`.

- Update `menu.py`: remove "Create request" and "Close request" menu items; add display of copy-paste-ready prompt invocations (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`); remove exit option; retain interactive functionality for remaining non-lifecycle scripts (e.g., `reverse-engineer.py`).

- Update `analysis-convention.md`: remove "Code and asset scan for impacted components" and "Internal review of request.md" from `analysis.md` sections; promote "External benchmarking" and "Result of minimal spikes/experiments" to mandatory standalone sections with required depth and detail.

- Update `request-convention.md`: add new mandatory sections for code/asset scan of impacted components, internal review of request and product docs, and multi-perspective stakeholder review (senior solution architect, product owner, user, security officer, data governance officer); update section numbering and validation rules.

- Bump SemVer marker in `.aib_brain/` from `v1.1.2` to `v1.2.0`.

- Create `versions/` folder in workspace root.

- Update `release_bookkeeping.py` to zip `.aib_brain/` and store the archive in `versions/aib_brain_vX.Y.Z.zip` on each version bump.

- Update README installation instructions to reference the `versions/` folder for `.aib_brain` download.


 **Amendment:** Revise the convention of request.md creation. All sections should become mandatory. Amendment section should be excluded - input.md will serve this purpose

  **Amendment:** In input.md should be added a checklist option which if checked - no changes in the request.md is made but the answer is provided accordingly the instructions in input.md or if nothing said - as a timestamped answer.md file in the reqeust folder

  **Amendment:** In input.md should be added a checklist option which if checked - no analysis.md should be generated (this part in the aib-analysis.md prompt should be skipped)  

## Out of scope

- No changes to `initialize.py` beyond adding `input.md` seeding.

- No changes to `close-request.py` core logic (it is still invoked internally by `aib-implement.md`).

- No changes to `reverse-engineer.py`.

- No changes to the GitHub Actions workflow beyond the release bookkeeping zip step.

- No cloud infrastructure provisioning.

- No changes to the core analysis or implement logic beyond what is specified in this request.

## Constraints

- All tool scripts must remain Python 3.10+ standard library only; no third-party packages.

- The framework must remain model-agnostic and vendor-agnostic.

- `input.md` archives stored in request folders MUST NOT be read by `aib-implement.md` or any other prompt.

- Version MUST be set exactly to v1.2.0.

- `.aib_brain/` must never be modified by tool scripts; zip creation is a CI/bookkeeping step only.

- All changes must maintain the single-Active-request invariant.

- `aib-implement.md` auto-close behavior must reuse `close-request.py` and not duplicate its logic.

- `.aib_brain` zip archives in `versions/` MUST be committed to VCS; `.gitignore` MUST NOT exclude `versions/*.zip`.

## Success criteria

- Running `aib-analysis.md` with no active request and non-empty `input.md` creates a new request folder with AI-generated `request.md`, archives the original `input.md` content to the request folder, and resets `input.md` to the seed template.

- Running `aib-analysis.md` with one active request generates `analysis.md` and updates `request.md` optional sections without creating a new request.  **Amendment:** unless the option for not changing the request to be ON

- Executing `create-request.py --workspace . --title "test"` creates a request folder and register entry but does NOT write `request.md` or `implementation.md` in the folder.

- Running `aib-implement.md` with an active request creates `implementation.md` from scratch (not pre-seeded) and sets the request state to Closed upon completion.

- Running `aib-implement.md` with no active request auto-triggers analysis then immediately proceeds with implementation.

- The CLI menu does not show "Create request", "Close request", or "Exit" options; copy-paste-ready prompts are displayed.

- `versions/` folder exists in workspace root; each version bump produces an `aib_brain_vX.Y.Z.zip` inside it.

- README installation instructions reference the `versions/` folder for obtaining `.aib_brain`.

- Exactly one SemVer marker `v1.2.0` exists in `.aib_brain/`; `v1.1.2` does not exist.

- All existing tests pass after test suite updates for removed template seeding behavior.

## Assumptions

- A1: `create-request.py` will continue to handle request folder creation and register update; `aib-analysis.md` invokes it for those operations rather than duplicating the logic.
  - Risk if false: The prompt would need to manage folder creation and register writes directly, increasing prompt complexity and bypassing validation in `create-request.py`.

- A2: Input archives are named `input-archive-<YYYY-MM-DD_HH-MI-SS>.md` and stored in an `inputs/` subfolder within the request folder (Q001 answer). Multiple archives may accumulate if analysis is run multiple times with no active request. The implement prompt and all other prompts MUST NOT read these archives.
  - Risk if false: Loss of audit trail or accidental inclusion of archive content in agent context.

- A3: `create-request.py` and `close-request.py` must also be added to `EXCLUDE_SCRIPTS` in `menu.py` after their menu entries are removed, to prevent them from reappearing via dynamic script discovery.
  - Risk if false: The scripts would be auto-discovered and shown in the menu under generic names, re-exposing lifecycle commands.

- A4: The `versions/` zip files are committed to VCS (Q003 answer). `.gitignore` MUST NOT exclude `versions/*.zip`.
  - Risk if false: Users cannot download archives from GitHub; a separate release mechanism would be needed.

- A5: The MINOR version bump to v1.2.0 (not a PATCH) is justified because this request removes existing behaviors (template seeding, CLI lifecycle commands) that are breaking changes for existing workflows.
  - Risk if false: If PATCH is expected, the version would be v1.1.3, but this understates the impact of the workflow changes.

- A6: The multi-perspective stakeholder review in `request.md` is generated by the AI during analysis (as part of `create-analysis`), not written manually by the user.
  - Risk if false: If user-authored, a convention for when and how the user fills it would be needed.

- A7: `test_lifecycle_e2e.py` and `test_close_request.py` may contain assertions that assume `create-request.py` seeds `request.md` and `implementation.md`. These tests must be reviewed as part of Task 11 before the full suite run.
  - Risk if false: Post-change test suite reports false failures masking real issues.

## Plan

### Task 1: Introduce `input.md` in `initialize.py`
**Intent:** Seed `.aib_memory/input.md` with a structured template on workspace initialization.
**Inputs:** `.aib_brain/tools/initialize.py`; seed template content from Goal 1 spec.
**Outputs:** Modified `initialize.py`; `.aib_memory/input.md` created on each fresh initialize.
**External Interfaces:** None.
**Environment & Configuration:** Python 3.10+; standard library only.
**Procedure:**
1. Open `initialize.py`.
2. After the `context.md` seeding block, add a new block: if `.aib_memory/input.md` does not exist, write it with the seed template content.
3. Seed template content: `## Active request\nNo active request\n\n## Options\n- [ ] No changes — provide answer only\n- [ ] Skip analysis document generation\n\n## Input\n\n`.
4. Update `tests/test_initialize.py` to assert `input.md` is created with the seed sections.
5. Run `pytest tests/test_initialize.py` and confirm all tests pass.
**Done Criteria:** Running `initialize.py` on a fresh workspace creates `.aib_memory/input.md` with the seed template; test passes.
**Dependencies:** None.
**Risk Notes:** If the seed template format changes in future, the hardcoded string in `initialize.py` must be updated manually.

### Task 2: Update `create-request.py` to remove template artifact seeding
**Intent:** Remove `request.md` and `implementation.md` creation from `create-request.py`; retain folder and register logic.
**Inputs:** `.aib_brain/tools/create-request.py`; `tests/test_create_request.py`.
**Outputs:** Modified `create-request.py`; updated `tests/test_create_request.py`.
**External Interfaces:** None.
**Environment & Configuration:** Python 3.10+; standard library only.
**Procedure:**
1. Remove the `load_template` call and `write_text(request_folder / "request.md", ...)` block.
2. Remove the `validate_request_md` call.
3. Remove the `implementation_content` variable and `write_text(request_folder / "implementation.md", ...)` block.
4. Remove unused imports (`load_template`, `validate_request_md`) from the import block.
5. Update `test_create_request.py`: remove assertions that check for `request.md` and `implementation.md` in the request folder.
6. Run `pytest tests/test_create_request.py` and confirm all tests pass.
**Done Criteria:** `create-request.py` creates folder and register row; no `request.md` or `implementation.md` in the folder; tests pass.
**Dependencies:** None.
**Risk Notes:** Any other caller that expects `request.md` to exist post-creation must be updated.

### Task 3: Update `aib-analysis.md` for auto-request creation from `input.md`
**Intent:** Add an execution branch to `aib-analysis.md` that auto-creates a request from `input.md` when no active request exists; add no-changes and no-analysis toggle processing; update archive naming.
**Inputs:** `.aib_brain/prompts/aib-analysis.md`; `input.md` spec; `request-convention.md`.
**Outputs:** Modified `aib-analysis.md` prompt; new `request.md` AI-generated in the request folder; `input.md` content archived to `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`; `input.md` reset.
**External Interfaces:** `create-request.py` (invoked via python script for folder + register); `request-convention.md` (governs `request.md` format).
**Environment & Configuration:** AI coding interface; model-agnostic.
**Procedure:**
1. Add a new "no active request" branch immediately after the preflight step.
2. In this branch: read `input.md`; invoke `create-request.py` via python script for folder + register (derive title from `input.md` content); generate `request.md` following `request-convention.md`.
3. Archive `input.md` content to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`.
4. Reset `input.md` to the seed template.
5. Add no-changes mode toggle: if checked, write a timestamped `answer.md` to the request folder root and exit without modifying `request.md` or generating `analysis.md`.
6. Add no-analysis mode toggle: if checked, skip `analysis.md` generation after updating `request.md` optional sections.
**Done Criteria:** Running `aib-analysis.md` with no active request and non-empty `input.md` creates the request folder with AI-generated `request.md`, archives `input.md` to `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`, and resets `input.md`.
**Dependencies:** Task 2 (create-request.py no longer creates artifacts).
**Risk Notes:** The title derivation from `input.md` must be deterministic; ambiguous content may produce poor slugs.

### Task 4: Update `aib-implement.md` for auto-analyze path, on-demand `implementation.md`, and auto-close
**Intent:** Update `aib-implement.md` to auto-run analysis when no active request exists, generate `implementation.md` from scratch, and auto-close the request upon completion.
**Inputs:** `.aib_brain/prompts/aib-implement.md`; Goals 2–3 spec; implementation-convention.md.
**Outputs:** Modified `aib-implement.md` prompt; `implementation.md` created on-demand; request closed.
**External Interfaces:** `close-request.py` (invoked for auto-close); `aib-analysis.md` (behavior triggered if no active request).
**Environment & Configuration:** AI coding interface; model-agnostic.
**Procedure:**
1. Add a pre-flight branch: if no active request exists, trigger `aib-analysis.md` flow, then proceed with implementation.
2. Remove any reference to pre-existing `implementation.md`; generate it fresh following the implementation convention.
3. After writing the implementation log entry, invoke `close-request.py` to close the request.
4. Ensure `inputs/input-archive-*.md` files in request folders' `inputs/` subfolder are excluded from the prompt's input resolution (MUST NOT be read).
**Done Criteria:** `aib-implement.md` on an active request creates `implementation.md` and closes the request; no pre-seeded file is required.
**Dependencies:** Task 2; Task 3.
**Risk Notes:** Auto-close must only trigger after confirmed successful implementation to prevent premature closure.

### Task 5: Update `menu.py` to display prompts and remove lifecycle actions
**Intent:** Remove "Create request" and "Close request" from the menu; add copy-paste prompt display; remove exit option; exclude lifecycle scripts from dynamic discovery.
**Inputs:** `.aib_brain/tools/menu.py`; `tests/test_menu.py`; README (for prompt list).
**Outputs:** Modified `menu.py`; updated `tests/test_menu.py`.
**External Interfaces:** None.
**Environment & Configuration:** Python 3.10+; standard library only.
**Procedure:**
1. Remove the `SCRIPT_CREATE_REQUEST` and `SCRIPT_CLOSE_REQUEST` constants and their hardcoded entries from `build_script_actions()`.
2. Add `create-request.py` and `close-request.py` to `EXCLUDE_SCRIPTS` to prevent dynamic re-discovery.
3. Add a `print_prompt_reference()` function that displays the three copy-paste prompts (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) with usage instructions.
4. Call `print_prompt_reference()` from the main menu render loop.
5. Remove the exit/quit option from the menu display and input handling.
6. Update `test_menu.py` to reflect removed lifecycle entries and removed exit option.
**Done Criteria:** Menu launched → no Create/Close items; no exit option; prompts displayed; tests pass.
**Dependencies:** None.
**Risk Notes:** Verify the full `menu.py` render loop before editing to identify all exit option references.

### Task 6: Restructure `analysis-convention.md`
**Intent:** Remove "Code and asset scan" and "Internal review" from analysis; promote "External benchmarking" and "Spikes/experiments" to mandatory standalone sections.
**Inputs:** `.aib_brain/conventions/analysis-convention.md`.
**Outputs:** Modified `analysis-convention.md` with updated section structure.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Remove "Code and asset scan for impacted components" from the Research Results sub-list in section 4.4.
2. Remove "Internal-first review of request.md" subsection from section 4.4.
3. Add "External Benchmarking" as a new mandatory standalone section (section 5) with instructions for depth, breadth, and mandatory content.
4. Add "Minimal Spikes and Experiments" as a new mandatory standalone section (section 6) with instructions for structured spike reporting.
5. Renumber subsequent sections; update the mandatory structure list in section 4.
**Done Criteria:** `analysis-convention.md` lists 6 mandatory sections; no code scan or internal review in analysis structure.
**Dependencies:** Task 7 (request-convention must gain what analysis loses).
**Risk Notes:** Existing `analysis.md` files will not conform to the new structure; this is acceptable (closed requests are read-only).

### Task 7: Update `request-convention.md` with new sections
**Intent:** Add code/asset scan, internal review, and multi-perspective stakeholder review as new separate AI-generated sections in `request-convention.md`; remove `## Amends` section.
**Inputs:** `.aib_brain/conventions/request-convention.md`; Goal 5 spec; Q002 answer (separate sections).
**Outputs:** Modified `request-convention.md` with updated section definitions and numbering.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Add a new section definition: "Code and Asset Scan for Impacted Components" — AI-generated table of impacted files with change type and reason.
2. Add a new section definition: "Internal Review of Request and Product Docs" — AI-generated review findings from reading `request.md` and product docs. Keep as a SEPARATE section from Multi-Perspective Stakeholder Review (Q002 answer: internal review = factual findings; multi-perspective = opinion-based evaluation).
3. Add a new section definition: "Multi-Perspective Stakeholder Review" — AI-generated evaluation from five viewpoints: senior solution architect, product owner, user, security officer, data governance officer. Keep as a SEPARATE section from Internal Review.
4. Remove section 12 (`## Amends`) entirely — replaced by `input.md` as the amendment channel.
5. Make all remaining sections mandatory (no optional sections).
6. Update section numbering, validation rules, and the example valid structure.
**Done Criteria:** `request-convention.md` defines the three new separate sections; `## Amends` is removed; all sections are mandatory; validation rules are updated.
**Dependencies:** Task 6.
**Risk Notes:** None.

### Task 8: Bump version to v1.2.0
**Intent:** Rotate the SemVer marker file from `v1.1.2` to `v1.2.0` in `.aib_brain/`.
**Inputs:** `.aib_brain/v1.1.2` (current marker).
**Outputs:** `.aib_brain/v1.2.0` (new marker); `v1.1.2` deleted.
**External Interfaces:** None.
**Environment & Configuration:** Git workspace.
**Procedure:**
1. Create new empty file `.aib_brain/v1.2.0`.
2. Delete `.aib_brain/v1.1.2`.
3. Verify exactly one SemVer marker exists in `.aib_brain/`.
**Done Criteria:** Exactly one file `v1.2.0` exists in `.aib_brain/`; `v1.1.2` is absent.
**Dependencies:** None.
**Risk Notes:** CI release bookkeeping detects the marker; ensure this task is committed before CI runs.

### Task 9: Update `release_bookkeeping.py` and confirm `versions/` folder
**Intent:** Extend `release_bookkeeping.py` to zip `.aib_brain` per version bump; confirm `versions/` folder exists and is tracked in VCS.
**Inputs:** `scripts/release_bookkeeping.py`; workspace root.
**Outputs:** Modified `release_bookkeeping.py`; `versions/` folder confirmed present with `.gitkeep` if empty; `.gitignore` verified not to exclude `versions/*.zip`.
**External Interfaces:** `zipfile` standard library module.
**Environment & Configuration:** Python 3.10+; CI environment; Git on PATH.
**Procedure:**
1. Verify `versions/` folder exists in workspace root (already created per scope amendment).
2. Add a `.gitkeep` placeholder file in `versions/` if the folder is empty, to ensure VCS tracking.
3. In `release_bookkeeping.py`, after marker rotation, add a zip step: create `versions/aib_brain_vX.Y.Z.zip` from `.aib_brain/` using `zipfile.ZipFile`.
4. Add idempotency check: if zip for target version already exists, skip creation.
5. Verify `.gitignore` does not exclude `versions/*.zip` (Q003 answer: zip files committed to VCS).
**Done Criteria:** `versions/` folder exists; running the release script produces `aib_brain_vX.Y.Z.zip` in `versions/`; idempotent on rerun; zip files not gitignored.
**Dependencies:** Task 8.
**Risk Notes:** Zip files can be large; committing to VCS increases repository size if sizes are not bounded.

### Task 10: Update README installation instructions
**Intent:** Replace manual `.aib_brain/` copy instructions with download-from-`versions/` instructions.
**Inputs:** `README.md`.
**Outputs:** Modified `README.md`.
**External Interfaces:** None.
**Environment & Configuration:** Markdown editor.
**Procedure:**
1. Locate the installation section in `README.md`.
2. Replace the manual folder copy step with: download `aib_brain_vX.Y.Z.zip` from the `versions/` folder, unzip it into the workspace root, and rename/place the extracted content as `.aib_brain/`.
3. Reference the current version (v1.2.0) in the instruction.
**Done Criteria:** README installation section references `versions/`; no manual copy instruction remains.
**Dependencies:** Task 9.
**Risk Notes:** None.

### Task 11: Update test suite for changed behaviors
**Intent:** Update all affected tests to pass with the new behaviors.
**Inputs:** `tests/test_create_request.py`; `tests/test_initialize.py`; `tests/test_menu.py`.
**Outputs:** Updated test files; passing test suite.
**External Interfaces:** `pytest`.
**Environment & Configuration:** Python 3.10+; `pytest` installed.
**Procedure:**
1. `test_create_request.py`: remove assertions checking for `request.md` and `implementation.md` in the request folder after creation.
2. `test_initialize.py`: add assertion that `input.md` is created with the expected seed sections.
3. `test_menu.py`: update `build_script_actions` tests to reflect removed create/close entries; update menu display tests for removed exit option.
4. Run `pytest tests/` and confirm all tests pass with zero failures.
**Done Criteria:** All tests pass; no test expects removed artifacts or actions.
**Dependencies:** Tasks 1, 2, 5.
**Risk Notes:** Ensure test isolation; temporary directories must not share state.

### Task 12: Regenerate `context.md` via `aib-context.md`
**Intent:** Regenerate `context.md` after all implementation tasks are complete to reflect the updated product state.
**Inputs:** All updated files (Tasks 1–11).
**Outputs:** Updated `.aib_memory/context.md`.
**External Interfaces:** `aib-context.md` prompt.
**Environment & Configuration:** AI coding interface.
**Procedure:**
1. Confirm all Tasks 1–11 are complete and committed.
2. Execute `aib-context.md` prompt.
3. Verify `context.md` reflects: v1.2.0, `input.md` artifact, updated FR-002 and FR-004, changed request lifecycle, updated menu behavior, `versions/` folder, and new convention sections.
**Done Criteria:** `context.md` is fully regenerated and accurately describes the v1.2.0 product state.
**Dependencies:** Tasks 1–11.
**Risk Notes:** None.

## Testing

- T1 — Initialize creates input.md: Run `initialize.py` on a fresh workspace. Expected outcome: `.aib_memory/input.md` exists containing the seed template sections (Active request, Options with two checkboxes, Input).

- T2 — Analysis auto-creates request from input.md: Execute `aib-analysis.md` with no active request and `input.md` containing user intent. Expected outcome: New request folder created; AI-generated `request.md` present; `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md` exists in request folder; `input.md` reset to seed template.

- T3 — Analysis with active request runs normally: Execute `aib-analysis.md` with one active request. Expected outcome: `analysis.md` created; `request.md` optional sections updated; no new request created; `input.md` unchanged.

- T4 — No-changes mode: Execute `aib-analysis.md` with active request and no-changes toggle checked in `input.md`. Expected outcome: `answer.md` created in request folder; `request.md` not modified; `analysis.md` not generated.

- T5 — No-analysis mode: Execute `aib-analysis.md` with active request and no-analysis toggle checked in `input.md`. Expected outcome: `request.md` optional sections updated; `analysis.md` NOT generated.

- T6 — create-request.py no longer creates request.md or implementation.md: Run `create-request.py --workspace . --title "test"`. Expected outcome: Request folder and register row created; `request.md` absent in folder; `implementation.md` absent in folder.

- T7 — Implement creates implementation.md on-demand: Execute `aib-implement.md` with an active request and no pre-existing `implementation.md`. Expected outcome: `implementation.md` created with implementation log content; request state set to Closed in the register.

- T8 — Implement auto-triggers analysis when no active request: Execute `aib-implement.md` with no active request and non-empty `input.md`. Expected outcome: Analysis branch runs first creating a request; implementation follows; request closed on completion.

- T9 — Menu excludes lifecycle actions and exit: Launch `menu.py`. Expected outcome: "Create request", "Close request", and "Exit" are absent; copy-paste prompts are displayed; remaining scripts (e.g., `reverse-engineer.py`) are accessible.

- T10 — Version marker is v1.2.0: List files in `.aib_brain/`. Expected outcome: Exactly one file named `v1.2.0` exists; `v1.1.2` does not exist.

- T11 — versions/ folder exists and zip files are not gitignored: Check workspace root and `.gitignore`. Expected outcome: `versions/` folder is present; no entry in `.gitignore` excludes `versions/*.zip`.

- T12 — Release bookkeeping produces zip in versions/: Execute `release_bookkeeping.py` in a test environment. Expected outcome: `versions/aib_brain_v*.zip` file created after version bump; reruns are idempotent.

- T13 — README references versions/: Read README installation section. Expected outcome: References `versions/` folder for `.aib_brain` download; no manual copy instruction present.

- T14 — Full test suite passes: Run `pytest tests/` from workspace root. Expected outcome: All tests pass; zero failures.

- T15 — Re-run analysis is idempotent: Execute `aib-analysis.md` twice on the same active request. Expected outcome: `analysis.md` replaced without error; `request.md` optional sections replaced; no duplicate sections.

## Documentation

- `README.md` (ref_id: N/A) — Installation instructions must be updated to reference `versions/` for `.aib_brain` download and reflect the v1.2.0 workflow.

- `.aib_memory/context.md` (ref_id: REF-0001) — Must be regenerated via `aib-context.md` after implementation to reflect: new `input.md` artifact, updated FR-002 (no template seeding) and FR-004, auto-close behavior, updated menu, `versions/` folder, v1.2.0 version, new convention section structure, and corrected product version from v1.0.14 to v1.2.0.

## Purpose

This file is the **primary communication channel between the user and the AI agent**.

Everything written here represents the **current message from the user to the agent** for this request cycle. Its content is **ephemeral** and will be **fully replaced** after the agent completes its work.

The agent MUST treat the contents of this file as the **authoritative source of user intent for the current run**.

---

## What Goes in This File

The user may write **any combination** of the following:

- **Intent**  
  What the user wants to achieve, explore, or change in the current request or explicit requests or steps the agent should perform.

- **Opinions & Preferences**  
  User judgments, concerns, stylistic preferences, or dissatisfaction with the current state.

- **Options & Toggles**  
  On/off flags, modes, constraints, or execution preferences (e.g. safety level, verbosity, scope).

- **Context or Clarifications**  
  Temporary reminders, assumptions, or framing relevant *only* to this execution.

The content is mix of:
- Free‑form natural language
- Structured (lists, sections, key–value pairs)

---

## How the Agent Should Interpret This File

- Treat the entire file as a **single coherent message** from the user.
- Assume **only the latest content matters**; there is no implied history.
- If instructions conflict with opinions or options, **prioritize explicit instructions**, then options, then opinions.
- If something is ambiguous, apply reasonable interpretation aligned with the user’s stated intent and preferences.
- Do NOT assume anything not expressed here unless part of the agent’s predefined capabilities or rules.

---

## Lifecycle

1. User writes or replaces `input.md`
2. Agent reads and executes based on its content
3. After execution, the file MUST be:
   - Replaced entirely for the next interaction

The file is **not a record, log, or contract**. It exists only to express the **current communication**.

---

## Guiding Principle

> If the user wants to say something to the agent,  
> **this is where they say it.**


---

## Seeding Template Example

```
  - [ ] Do not generate analysis.md
  - [ ] Do not change the request.md

--------

Add function for data verification

```

# Goal 2

Creation of a request should happen automatically when `.aib_brain\prompts\aib-analysis.md`
The files request.md and implementation.md should not be created when a new request is created.

Change Request: Introduce `input.md` as Primary User–Agent Communication Channel

## Summary

Introduce a new interaction model where an ephemeral file (`input.md`) serves as the primary communication channel between the user and the AI-based system (`aib-*` commands). This change simplifies the UX by removing explicit “create request” actions and replaces them with a file‑driven workflow.

---

## Motivation

The current interaction model requires an explicit command to create a new request. This adds friction and duplicates functionality already achievable through a conversational, iterative workflow.

By introducing a single, overwrite‑able `input.md` file:
- Users gain a clear and intuitive place to communicate with the system.
- Requests become naturally iterative.
- The system UX aligns more closely with chat‑like interaction while preserving traceability and structure.

---

## Scope of Change

### New Artifact

- **File:** `.aib_memory/input.md`
- **Purpose:**  
  Acts as the **ephemeral, user-authored communication surface** for:
  - Requests
  - Comments
  - Commands
  - Questions
  - Corrections / follow-ups

The content of this file is considered **single‑cycle input** and may be cleared after processing.

Initially and when cleared, the input.md file should have predefined structure

```
## Active request
<ID and description of the active request here> or "No active request"

## Options
- [ ] Create extended analysis 
- [ ] Close the current request and start a new one

##  
```

---

## Behavioral Changes

### 1. Request Creation Flow (via `aib-analyze`)

Update `aib-analyze` behavior as follows:

1. When executed:
   - If there is **no active request**, the system MUST:
     - Read the contents of `.aib_memory/input.md`
     - Create a new request based on that content

2. The system MUST generate:
   - `request.md` in a newly created request folder
   - Content is derived from and structured from `input.md`

3. After successful request generation:
   - `input.md` MUST be cleared
   - MANDATORY: archive the input.md content into the corresponding request folder. Make sure the implementation DO NOT READ this archives - they are for human audit purposes only

4. The user reviews `request.md`:
   - If changes are needed, the user writes corrections into `input.md`
   - Re-running `aib-analyze` updates or regenerates `request.md` accordingly

---

### 2. Request Implementation Flow (via `aib-implement`)

Update `aib-implement` behavior as follows:

1. When executed with an active request:
   - Execute the request as currently specified
   - Generate `implementation.md` in the request folder
   - Automatically close the request upon completion

2. If post‑implementation corrections are required:
   - User writes adjustments into `input.md`
   - Running `aib-analyze` results in the creation of a **new request**

---

### 3. Implicit Analyze + Implement Path

Enhance `aib-implement` with the following logic:

- If `aib-implement` is executed **and no `request.md` exists**:
  1. Automatically run `aib-analyze`
  2. Immediately proceed with implementation
  3. This path assumes **explicit user trust** and skips manual request review

This enables a fast, “trust the system” workflow for experienced users.

---

### 4. Context Handling

- As before, `aib-implement` MUST automatically execute `aib-context`
- No behavior change required here beyond compatibility with the new flow

---

## UX / CLI Changes

- **Remove** the explicit menu command for “Create New Request”
- `input.md` becomes the **only entry point** for initiating work
- All request lifecycle transitions are derived from:
  - File presence
  - Command invocation (`aib-analyze`, `aib-implement`)

---

## Design Principles

- `input.md` is:
  - Ephemeral
  - Overwrite‑friendly
  - Not a record or contract
- Only the **latest content** of `input.md` is relevant
- The system must remain deterministic, inspectable, and recoverable

---

## Expected Outcome

- Reduced cognitive overhead for users
- More natural, conversational workflow
- Cleaner separation between:
  - Communication (`input.md`)
  - Formalized requests (`request.md`)
  - Execution results (`implementation.md`)

# Goal 3

Change the way request.md is created. No need of template anymore as it shall not be seeded but shall be AI generated. The convention should be the autorative guide for the formatting.

Change the way implementation.md is created - no need it to be created in advance. It should appear during aib-implement.md prompt execution. The convention should be the autorative guide for the formatting.

# Goal 4

`.aib_brain\run.bat` menu will not be needed anymore to create and close requests. It will happen automatically from the prompts. Instead of commands, in the menu shoudl be listed copy-paste ready prompts which the user can copy and execute in the AI chat - as per described in the README possible prompts.

No need of exit option in the menu as well - closing the terminal will serve the purpose

# Goal 5

Merge the current section "Code and asset scan for impacted components" of analysis.md file in request.md. 
Add in the request a section for review and evaluation of the request from perspectives of a senior solution architect, a product owner, a user of the system, a security officer, a data governance officer. Merge and move here the section "Internal review of `request.md` and product docs:" from analysis. 
Make the sections "External benchmarking when needed; summarize takeaways without links." and "Result of minimal spikes/experiments" mandatory stand alone sections in analysis and instruct they to be more detailed and holistic.

# Goal 6

Increase the version to v1.2.0


# Goal 7

Create a new folder in root named versions and in it add a zip of .aib_brain during each increment of the version semver number.
Change the installation instruction so .ain_brain folder zip to be downloaded from the folder versions