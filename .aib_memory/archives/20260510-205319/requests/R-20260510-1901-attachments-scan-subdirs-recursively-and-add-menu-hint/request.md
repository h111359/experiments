## Goal

Update `.aib_brain/prompts/aib-analysis.md` to replace the flat-scan attachment reading and moving logic with a recursive-walk approach that includes all files in all subdirectories of `.aib_memory/attachments/`. Additionally, update `.aib_brain/tools/menu.py` to display a short reminder about the attachments folder in the menu guidance states where the developer is prompted to write into `input.md`.

## Background

The `aib-analysis.md` prompt currently reads attachments via a "flat scan" that ignores subdirectories, and moves files to `<request-folder>/inputs/` using the same flat approach. This constrains developers to placing supplementary files only at the root of `.aib_memory/attachments/` — subfolders and complex directory structures are silently skipped, causing supplementary context to be lost. Developers working with organized file collections (e.g., nested specs, screen captures grouped by feature) cannot use the attachments folder at full capacity.

Separately, the menu does not currently surface any guidance about the attachments folder. Developers who are new to AIB or haven't read the documentation may not discover that they can place supplementary files alongside their `input.md` descriptions. The menu already directs developers to write into `input.md` in two key states (`idle` and `implementation_ready`); a short reminder about the attachments folder in those same guidance lines would complete the picture without adding new screens or complex UI changes.

## Scope

- `.aib_brain/prompts/aib-analysis.md` — replace "flat scan" language in preflight step 4 (reading attachments) with a recursive-walk (walk all files including subdirectories) specification; replace "flat scan, ignore subdirectories" in Auto-Request Creation Branch step 6 (moving attachments) with recursive-walk language that preserves relative subdirectory structure under `<request-folder>/inputs/`.

- `.aib_brain/tools/menu.py` — add a short attachments reminder line to the `"idle"` guidance message (state where the menu advises the developer to fill in `input.md`) and to the `"implementation_ready"` guidance message (amendment line where the developer is prompted to write changes into `input.md`).

- `.aib_memory/context.md` — update the Attachments Staging Folder component description (currently "flat staging folder") and any FR text that references the "flat scan" behavior for attachments, to reflect recursive-walk semantics.

- `tests/` — add test cases to cover: (a) `aib-analysis.md` no longer contains "flat scan" or "ignore subdirectories" in the attachments preflight step; (b) menu guidance for `"idle"` and `"implementation_ready"` states contains an `attachments` reference.

## Out of scope

- No changes to `close-request.py` (its non-blocking non-empty check at close time is unrelated to the reading/moving logic).

- No changes to `initialize.py` (attachments folder creation is already correct).

- No renaming of the `attachments/` folder or the attachments concept.

- No changes to the `## Questions` or toggle behavior of `input.md`.

- No changes to archive-file naming conventions for attachments content already in `<request-folder>/inputs/`.

## Constraints

- Python tools must remain Python 3.10+ standard-library only (no new third-party dependencies).

- Menu guidance text must remain concise — the attachments reminder must not exceed one short line per state.

- The recursive move step must preserve relative subdirectory structure when moving files from `attachments/` to `<request-folder>/inputs/` (not flatten).

- Existing behavior for flat attachment structures (files at the root of `attachments/`) must remain unchanged.

## Success criteria

- SC-1: The phrase "flat scan" does not appear in the attachments-reading step (preflight step 4) of `.aib_brain/prompts/aib-analysis.md`.
- SC-2: The phrase "ignore subdirectories" does not appear in the attachments sections of `.aib_brain/prompts/aib-analysis.md`.
- SC-3: `.aib_brain/prompts/aib-analysis.md` explicitly describes reading all files recursively (including subdirectories) in `.aib_memory/attachments/`.
- SC-4: `.aib_brain/prompts/aib-analysis.md` Auto-Request Creation Branch step 6 explicitly describes moving attachments recursively, preserving relative structure.
- SC-5: The `"idle"` guidance entry in `.aib_brain/tools/menu.py` includes a reference to `.aib_memory/attachments/`.
- SC-6: The `"implementation_ready"` guidance entry in `.aib_brain/tools/menu.py` includes a reference to `.aib_memory/attachments/`.
- SC-7: `.aib_memory/context.md` no longer describes the attachments folder as a "flat staging folder" without qualification.
- SC-8: The full test suite passes after all changes (no regressions).

## Assumptions

- A1: The implementing agent will update only the two target occurrences of "flat scan" / "ignore subdirectories" in `aib-analysis.md` and will not inadvertently alter other parts of the prompt.
  - Risk if false: Unintended changes to unrelated prompt logic could break analysis runs.

- A2: `Path.rglob('*')` with `f.is_file()` filtering is the idiomatic and accepted way to express recursive file traversal in this prompt's Python context instructions.
  - Risk if false: The implementing agent may choose a less idiomatic pattern; however, any correct recursive traversal satisfies SC-3 and SC-4.

- A3: `_GUIDANCE_MESSAGES` in `menu.py` supports lists of any length; `render_menu()` iterates and displays each element on a separate line with no maximum-line enforcement.
  - Risk if false: A hidden line-limit in the render function could clip the new guidance lines; verified by code inspection to be safe.

- A4: The `close-request.py` flat `iterdir()` check is intentionally out of scope and must not be changed.
  - Risk if false: Changing `close-request.py` would affect the non-blocking close-time warning behavior, which is unrelated to this request.

- A5: All test cases in this request scope are automatable; no UAT scenarios file is required.
  - Risk if false: Low. The changes are file-content and dict-value checks with no visual or interactive aspects.

## Plan

### Task 1: Update attachments read step in `aib-analysis.md`

#### Intent
Replace the flat-scan specification in preflight step 4 with a recursive-walk specification.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` (modified)

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, locate preflight step 4 (the step labelled "Read attachments (MUST execute before toggle detection)"). Find the sentence: `"Perform a flat scan of \`.aib_memory/attachments/\` (ignore subdirectories)."` and replace it with: `"Recursively walk all files in \`.aib_memory/attachments/\` (including files in subdirectories at any depth)."` The surrounding bullet structure and the rest of step 4's content remain unchanged.

#### Done criteria
- The string `"flat scan"` does not appear in the preflight step 4 paragraph of `.aib_brain/prompts/aib-analysis.md`.
- The string `"ignore subdirectories"` does not appear in that paragraph.
- The string `"Recursively"` or equivalent recursive-walk language is present in the updated paragraph.

#### Dependencies
None

#### Risk notes
None

---

### Task 2: Update attachments move step in `aib-analysis.md`

#### Intent
Replace the flat-scan move specification in Auto-Request Creation Branch step 6 with recursive-walk language that preserves relative subdirectory structure.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` (modified)

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, locate the Auto-Request Creation Branch step 6. Find the clause: `"move all files from \`.aib_memory/attachments/\` (flat scan, ignore subdirectories, skip \`.gitkeep\`) to \`<request-folder>/inputs/<filename>\` using Python's \`shutil.move\` for cross-filesystem compatibility."` Replace with: `"Recursively walk all files in \`.aib_memory/attachments/\` (including subdirectories, skip \`.gitkeep\`), and for each file move it to \`<request-folder>/inputs/<relative-path>\` using Python's \`shutil.move\` for cross-filesystem compatibility (create destination parent directories with \`mkdir(parents=True, exist_ok=True)\` as needed to preserve relative subdirectory structure)."` The rest of step 6 (the sentence "After all moves, `.aib_memory/attachments/` MUST contain only `.gitkeep`") remains unchanged.

#### Done criteria
- `"flat scan, ignore subdirectories"` does not appear in step 6 of the Auto-Request Creation Branch in `.aib_brain/prompts/aib-analysis.md`.
- The updated clause explicitly mentions `<relative-path>` (or equivalent) and `mkdir(parents=True, exist_ok=True)`.

#### Dependencies
None

#### Risk notes
Do NOT change the `close-request.py` `iterdir()` check — it is a flat-level check by design and is out of scope.

---

### Task 3: Add attachments reminder to `menu.py` guidance messages

#### Intent
Amend the `_GUIDANCE_MESSAGES` dict in `menu.py` to surface the attachments folder in `"idle"` and `"implementation_ready"` states.

#### Outputs
`.aib_brain/tools/menu.py` (modified)

#### Procedure
In `.aib_brain/tools/menu.py`, locate `_GUIDANCE_MESSAGES["idle"]`. It currently has one string element. Add a second element: `"Tip: Place supporting files in \`.aib_memory/attachments/\` to include extra context."`.

In `.aib_brain/tools/menu.py`, locate `_GUIDANCE_MESSAGES["implementation_ready"]`. It currently has two string elements. Add a third element with the same attachments reminder text.

#### Done criteria
- `_GUIDANCE_MESSAGES["idle"]` has exactly 2 elements; the second contains the word `"attachments"`.
- `_GUIDANCE_MESSAGES["implementation_ready"]` has exactly 3 elements; the third contains the word `"attachments"`.

#### Dependencies
None

#### Risk notes
The `test_exactly_seven_keys` test in `test_menu.py` checks only the key count of `_GUIDANCE_MESSAGES`, not element counts within each key — no regression risk from that test. New tests (Task 4) will assert the element content.

---

### Task 4: Add automated tests

#### Intent
Add test cases for the new recursive-scan language and the menu guidance changes.

#### Outputs
`tests/test_analysis_prompt_structure.py` (modified), `tests/test_menu.py` (modified)

#### Procedure
In `tests/test_analysis_prompt_structure.py`, add a new class `TestAttachmentsScanLanguage` with the following test methods:

- `test_flat_scan_absent_from_attachments_steps`: reads `.aib_brain/prompts/aib-analysis.md`; asserts `"flat scan"` does not appear; asserts `"ignore subdirectories"` does not appear.

- `test_recursive_language_present`: reads `.aib_brain/prompts/aib-analysis.md`; asserts `"Recursively"` (or `"recursively"`) appears in the file content.

In `tests/test_menu.py`, add a new class `TestGuidanceAttachmentsHint` with the following test methods:

- `test_idle_guidance_contains_attachments_reminder`: imports `menu`; asserts `any("attachments" in line for line in menu._GUIDANCE_MESSAGES["idle"])`.

- `test_implementation_ready_guidance_contains_attachments_reminder`: imports `menu`; asserts `any("attachments" in line for line in menu._GUIDANCE_MESSAGES["implementation_ready"])`.

Run `python -m pytest tests/ -v` from the workspace root. Expected output: all tests pass (0 failures, 0 errors).

#### Done criteria
- New test class and methods are present in `tests/test_analysis_prompt_structure.py`.
- New test class and methods are present in `tests/test_menu.py`.
- `python -m pytest tests/ -v` exits with code 0.

#### Dependencies
Tasks 1, 2, 3

#### Risk notes
None

---

### Task 5: Update `context.md` documentation

#### Intent
Revise all "flat staging folder" and "flat scan" references in `.aib_memory/context.md` that describe the attachments folder behavior, to reflect recursive-walk semantics.

#### Outputs
`.aib_memory/context.md` (modified)

#### Procedure
In `.aib_memory/context.md`, locate the Attachments Staging Folder component row (approximately line 80). Update the description: replace `"Flat staging folder for developer-supplied supplementary input files"` with `"Staging folder for developer-supplied supplementary input files (supports nested subdirectory structure)"`. Update the phrase `"read by \`aib-analysis.md\` before drafting analysis (text files read in full; binary files acknowledged by name)"` to add `"(recursive walk, including subdirectories)"`.

In `.aib_memory/context.md`, locate FR-003 description (approximately line 41). Find the phrase `"flat scan, skip \`.gitkeep\`"` in the attachments-reading clause and replace with `"recursive walk (all files including subdirectories, skip \`.gitkeep\`)"`.

In `.aib_memory/context.md`, locate the analysis workflow description (approximately line 178) that references `"flat scan, skip \`.gitkeep\`"`. Apply the same replacement as above.

In `.aib_memory/context.md`, locate the architecture section (approximately line 250) that describes `".aib_memory/attachments/"` as `"flat staging folder"`. Remove the word `"flat"` from that description.

Acceptance test: running a text search for `"flat staging folder"` in `.aib_memory/context.md` yields zero results.

#### Done criteria
- `"flat staging folder"` does not appear in `.aib_memory/context.md`.
- `"flat scan"` does not appear in any attachments-related description in `.aib_memory/context.md`.
- All modified descriptions accurately reflect recursive-walk semantics.

#### Dependencies
None (documentation-only task; can run in any order)

#### Risk notes
`context.md` contains archived versions' context rows (from the archives subfolder) that are NOT to be edited — only the active `.aib_memory/context.md` is in scope. Do not edit files under `.aib_memory/archives/`.

## Documentation

- `.aib_memory/context.md` — update Attachments Staging Folder component description and FR-003/analysis workflow references from "flat staging folder"/"flat scan" to recursive-walk semantics.

## Questions & Decisions

