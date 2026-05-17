## Goal

Increase automation coverage of deterministic AIB operations by: (1) integrating `.aib_brain/tools/test_common.py` into the main test suite and removing it from the tools folder; (2) reviewing all prompts in `.aib_brain/prompts/` to identify activities that are fully or partially doable by Python scripts; (3) adding new Python scripts in `.aib_brain/tools/` for all identified scriptable activities, and updating prompt files with invocation instructions; (4) removing the "No changes — provide answer only" and "Skip analysis document generation" toggle options from `input.md`, `initialize.py`, and all prompts that reference them.

## Background

AIB is a specification-driven framework where AI agents execute prompt-driven workflows. Currently, many deterministic file operations (e.g., archiving `input.md`, resetting `input.md` to seed template, moving attachments) are performed by the AI agent inline rather than by dedicated Python scripts. This wastes AI tokens on trivial operations and prevents those operations from being pre-approved by the developer. Additionally, `test_common.py` lives inside the tools directory (`.aib_brain/tools/`) rather than in the standard test suite under `tests/`, causing a structural inconsistency. Two menu toggle options ("No changes — provide answer only" and "Skip analysis document generation") have been identified as unnecessary; removing them simplifies the interface and reduces AI prompt complexity.

## Scope

- Move and integrate `test_common.py` from `.aib_brain/tools/` into `tests/` under a suitable name (e.g., `test_common_helpers.py`), ensuring imports, fixtures, and CI test discovery continue to work.

- Remove `.aib_brain/tools/test_common.py` from the tools directory.

- Review `.aib_brain/prompts/aib-analysis.md`, `.aib_brain/prompts/aib-implement.md`, and `.aib_brain/prompts/aib-context.md` to identify every deterministic, scriptable activity that the AI currently performs inline.

- Create new Python scripts in `.aib_brain/tools/` for each identified scriptable activity that does not yet have a script. Candidates include: archiving `input.md`, resetting `input.md` to seed template (with active request ID injection), moving attachments to request inputs folder, and writing timestamped answer files.

- Update each prompt file in `.aib_brain/prompts/` to instruct the AI to invoke the new script(s) instead of performing the file operations inline, including invocation syntax examples.

- Remove the following two toggle lines from `input.md` seed template (in `initialize.py`), from `input.md` itself, and from all prompt files where they are referenced:
  - `- [ ] No changes — provide answer only`
  - `- [ ] Skip analysis document generation`

- Remove all logic blocks in prompt files that handle or describe these two toggle options.

- Update `input.md` seed template in `initialize.py` to exclude the two removed toggle lines.

- Update `.aib_brain/README.md` to remove any reference to the removed toggle options.

## Out of scope

- No changes to the core logic of existing scripts (`create-request.py`, `close-request.py`, `move-request-artifacts.py`, `initialize.py` main behavior beyond template change).

- No changes to the `menu.py` state machine, guidance messages, or action injection logic beyond what is required by removing the toggle references.

- No changes to Q-block generation logic, `## Questions` section handling, or the `Minimum questions:` option.

- No changes to `.aib_brain/conventions/` files.

- No changes to CI workflow files.

- No changes to existing closed request archives under `.aib_memory/archives/` or closed request folders.

## Constraints

- All scripts MUST run on Python 3.10+ using the standard library only (no third-party packages).

- The integrated test file MUST be discoverable by `pytest` from the workspace root (i.e., placed in `tests/` and following the existing `test_*.py` naming pattern).

- Scripts MUST import from `common.py` using the existing pattern in `.aib_brain/tools/`.

- Removing the two toggle options MUST NOT break the `Minimum questions:` option, which stays in `input.md ## Options`.

- The AC explicitly requires well-commented code, so all new scripts and modified code MUST have inline comments explaining their purpose and logic.

- No Python virtual environments or third-party library installations.

## Success criteria

- `pytest tests/` runs without errors and the relocated `test_common.py` tests pass from their new location in `tests/`.

- `.aib_brain/tools/test_common.py` no longer exists in the repository.

- At least one new script exists in `.aib_brain/tools/` for each identified scriptable prompt operation, with docstring and inline comments.

- Each new script is invocable via `python .aib_brain/tools/<script-name>.py --workspace .` (or equivalent).

- `.aib_brain/prompts/aib-analysis.md` contains explicit invocation instructions for every new script that replaces an inline AI operation it previously performed.

- Neither the string `No changes — provide answer only` nor `Skip analysis document generation` appears in `input.md`, `initialize.py`, or any `.aib_brain/prompts/` file.

- The existing `input.md` in `.aib_memory/` no longer contains those two toggle lines.

- All automated tests pass after changes.

## Assumptions

- A1: The `conftest.py` `_seed_workspace` helper and `test_common.py`'s `_setup_workspace` can be reconciled by keeping the conftest version as the canonical fixture; `test_common.py` tests that use `_setup_workspace` locally will be updated to use either `tempfile.TemporaryDirectory` directly or the `workspace_dir` fixture.
  - Risk if false: If the two helpers are not reconcilable, some tests may fail due to missing template files or workspace structure differences.

- A2: Moving `test_common.py` to `tests/` requires removing the `sys.path.insert(0, ...)` line that is currently at the top of that file, since `conftest.py` already inserts the tools path into `sys.path` for all tests in `tests/`.
  - Risk if false: If `conftest.py`'s path insertion runs after test_tools_common.py is imported, the import of `common` would fail. However, `conftest.py` is loaded before test modules by pytest design.

- A3: A single `finalize-input.py` script (Archive 2 — single combined script) is the implementation approach. It accepts `--workspace` and optionally `--request-id` (defaults to the active request). It archives `input.md`, moves attachments, and resets `input.md` in one atomic call.
  - Risk if false: If the developer prefers two separate scripts, the plan must be adjusted before Task 2.

- A4: The `finalize-input.py` script implements the stub-equivalence check: if `input.md` is already seed-template-equivalent (after whitespace normalization), the archive step is skipped. This matches the existing AI behavior described in FR-003.
  - Risk if false: Skipping this check would cause empty or stub-equivalent input files to be needlessly archived.

- A5: `.aib_memory/input.md` currently contains the two toggle lines and will be updated directly. Since it is an active workspace file (not archived), editing it is in scope.
  - Risk if false: No meaningful risk.

- A6: `.aib_memory/archives/` files are not modified (per scope exclusion). Legacy archived `input.md` copies may still contain the toggle lines; this is acceptable.
  - Risk if false: No functional risk; archives are read-only historical snapshots.

## Plan

### Task 1: Integrate test_common.py into tests/

#### Intent
Relocate `.aib_brain/tools/test_common.py` into `tests/test_tools_common.py` and delete the original, ensuring all tests pass from the standard test location.

#### Outputs
- New file: `tests/test_tools_common.py` (moved and adapted from `.aib_brain/tools/test_common.py`)
- Deleted: `.aib_brain/tools/test_common.py`

#### Procedure
Read `.aib_brain/tools/test_common.py` in full.

Compare `_setup_workspace` in `test_common.py` with `_seed_workspace` in `tests/conftest.py`. Determine which tests use `_setup_workspace` and whether the conftest `workspace_dir` fixture can replace it. Update affected test methods to use `tempfile.TemporaryDirectory` directly (the pattern already used throughout test_common.py) — no fixture replacement is needed since all test_common.py tests use `TestCase` classes, not pytest fixtures.

Copy the file content to `tests/test_tools_common.py`. Remove the `sys.path.insert(0, ...)` line at the top (line 12 of test_common.py), because `conftest.py` already inserts the tools path.

Delete `.aib_brain/tools/test_common.py`.

Run `pytest tests/test_tools_common.py -v` and confirm all tests pass.

#### Done criteria
- `pytest tests/test_tools_common.py` reports 0 failures, 0 errors.
- `.aib_brain/tools/test_common.py` does not exist.
- `tests/test_tools_common.py` exists and is importable.

#### Dependencies
None.

#### Risk notes
If any test in `test_common.py` relied on the `sys.path.insert` executing before `conftest.py` (not possible with pytest), it would fail. This is not expected; pytest always loads conftest before test files.

---

### Task 2: Create `finalize-input.py` script

#### Intent
Create a new Python script that atomically archives `input.md` (with stub-equivalence check), moves attachments, and resets `input.md` to the seed template with the active request ID injected.

#### Outputs
- New file: `.aib_brain/tools/finalize-input.py`

#### Procedure
Read `.aib_brain/tools/common.py` to identify available helper functions (especially `read_text`, `write_text`, `parse_markdown_table`, `requests_register_path`, `resolve_active_request_or_explicit`, `now_iso`).

Create `.aib_brain/tools/finalize-input.py` with:
- `parse_args()` accepting `--workspace` (required) and `--request-id` (optional, defaults to active).
- Helper `_is_stub_equivalent(content: str) -> bool` that normalizes whitespace/line-endings and compares to the seed template string.
- Archive step: read `input.md`; if not stub-equivalent, write to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`; create parent dirs as needed.
- Attachment-move step: walk `.aib_memory/attachments/` recursively; for each non-`.gitkeep` file, move it to `<request-folder>/inputs/<relative-path>` using `shutil.move`; create parent dirs as needed.
- Reset step: write seed template to `.aib_memory/input.md` with `## Active request\n<request_id> — <title>` as the first two lines (replacing `No active request`). Seed template MUST contain only `## Options\n- Minimum questions: 0` (no toggle lines).
- All operations wrapped in `try/except ValidationError` with `raise SystemExit(1)`.
- Docstring and inline comments explaining each section per the AC requirement.

Run `python .aib_brain/tools/finalize-input.py --help` to confirm it parses arguments without error.

#### Done criteria
- `python .aib_brain/tools/finalize-input.py --workspace . --request-id R-TEST` (with a seeded test workspace) completes without error.
- Script is importable without side effects.
- Docstring and inline comments are present.

#### Dependencies
Task 1 (none — Task 2 is independent, but logically follows the test setup pattern).

#### Risk notes
The stub-equivalence check must normalize CRLF/LF and trailing whitespace before comparison to avoid false negatives on Windows.

---

### Task 3: Update `aib-analysis.md` to use `finalize-input.py`

#### Intent
Replace all inline archive/move/reset instructions in `aib-analysis.md` with a single `finalize-input.py` invocation, and remove the two toggle detection blocks.

#### Outputs
- Modified: `.aib_brain/prompts/aib-analysis.md`

#### Procedure
Read `.aib_brain/prompts/aib-analysis.md` in full.

Identify and remove the entire `## Toggle detection and Q&A re-run check` sub-section that handles the `"No changes — provide answer only"` branch (the block from step 5 that says "If the **'No changes — provide answer only'** option is checked...Stop here.").

Remove the `"Skip analysis document generation"` toggle check line (step 5: "If the **'Skip analysis document generation'** option is checked...").

Update step 5 toggle detection to only cover Q&A re-run check (Answer Application Sub-flow), removing any reference to the two toggles.

In the Auto-Request Creation Branch, remove step 1's check: `"Check ## Options for the 'No changes — provide answer only' toggle. If checked, output ERROR..."`.

In Auto-Request Creation Branch step 6 (archive input.md) and step 7/8 (reset), replace the inline instructions with:
```
python .aib_brain/tools/finalize-input.py --workspace . --request-id <request_id>
```
Include a note that `<request_id>` is resolved from the register in the same step.

In the standard-flow reset (end of main flow), replace inline reset instructions with the same script invocation.

Update all seed template string occurrences in the prompt that contain `- [ ] No changes — provide answer only\n- [ ] Skip analysis document generation\n` to use the new trimmed seed template (only `- Minimum questions: 0`).

#### Done criteria
- Neither `No changes — provide answer only` nor `Skip analysis document generation` appears anywhere in `.aib_brain/prompts/aib-analysis.md`.
- The prompt contains at least one `python .aib_brain/tools/finalize-input.py` invocation with example syntax.
- The prompt file is valid Markdown (no broken headings or orphaned continuation lines).

#### Dependencies
Task 2.

#### Risk notes
`aib-analysis.md` is the most complex prompt file; manual editing must preserve the numbering of all remaining steps and ensure no step references a removed step by number.

---

### Task 4: Remove toggle options from `initialize.py` and `input.md`

#### Intent
Remove the two toggle lines from `initialize.py`'s seed template and from the current `.aib_memory/input.md`.

#### Outputs
- Modified: `.aib_brain/tools/initialize.py`
- Modified: `.aib_memory/input.md`

#### Procedure
In `.aib_brain/tools/initialize.py`, locate the `input_seed` string in `_seed_core_memory`. Remove the lines `"- [ ] No changes — provide answer only\n"` and `"- [ ] Skip analysis document generation\n"` from the string.

In `.aib_memory/input.md`, remove the lines `- [ ] No changes — provide answer only` and `- [ ] Skip analysis document generation`.

Verify that `initialize.py` still runs without error: `python .aib_brain/tools/initialize.py --help`.

#### Done criteria
- Neither toggle string appears in `.aib_brain/tools/initialize.py`.
- Neither toggle string appears in `.aib_memory/input.md`.
- `python .aib_brain/tools/initialize.py --help` exits with code 0.

#### Dependencies
None.

#### Risk notes
`test_initialize.py` may assert the presence of the toggle lines in the seeded `input.md`; if so, those assertions must be updated in this task.

---

### Task 5: Update `.aib_brain/README.md`

#### Intent
Remove the usage instruction paragraph referencing the "No changes — provide answer only" toggle from `README.md`.

#### Outputs
- Modified: `.aib_brain/README.md`

#### Procedure
Read `.aib_brain/README.md` to locate the paragraph referencing the "No changes — provide answer only" toggle (approximately line 59 based on grep results).

Remove that paragraph or bullet point in its entirety.

Review the surrounding context to ensure no orphaned headings or broken list structure remains.

#### Done criteria
- `No changes — provide answer only` does not appear in `.aib_brain/README.md`.
- The file renders as valid Markdown with no orphaned list items.

#### Dependencies
None.

#### Risk notes
None.

---

### Task 6: Write automated tests

#### Intent
Add tests for the new `finalize-input.py` script, covering archive, attachment-move, reset, and stub-equivalence skip logic; update any existing tests that assert the presence of removed toggle lines.

#### Outputs
- New file: `tests/test_finalize_input.py`
- Modified (if needed): `tests/test_initialize.py` (remove assertions about toggle lines)
- Modified (if needed): `tests/test_analysis_prompt_structure.py` (remove assertions about toggle lines)

#### Procedure
Create `tests/test_finalize_input.py` with test cases covering:
- Non-stub input.md is archived to `<request-folder>/inputs/input-archive-*.md`.
- Stub-equivalent input.md is NOT archived (archive file does not exist after run).
- Non-`.gitkeep` attachment files are moved to `<request-folder>/inputs/`.
- After run, input.md contains the active request ID in `## Active request` line.
- After run, input.md does NOT contain either toggle line.
- Missing `--workspace` argument produces a non-zero exit code.

In `tests/test_initialize.py`, search for any assertions that expect the toggle lines in seeded `input.md`. If found, update those assertions to reflect the new seed template.

In `tests/test_analysis_prompt_structure.py`, search for any assertions that expect toggle lines in prompt text. If found, update.

Run `pytest tests/ -v` and confirm all tests pass.

#### Done criteria
- `pytest tests/` reports 0 failures, 0 errors.
- `tests/test_finalize_input.py` exists and covers the scenarios listed above.

#### Dependencies
Tasks 2, 4.

#### Risk notes
If `test_analysis_prompt_structure.py` or `test_initialize.py` perform byte-for-byte prompt content checks, they may need targeted string-replacement updates rather than full rewrites.

---

### Task 7: Update documentation

#### Intent
Update `.aib_memory/context.md` to reflect the removal of the two toggle options, the new `finalize-input.py` script, and the relocation of `test_common.py`; update any other documentation files as needed.

#### Outputs
- Modified: `.aib_memory/context.md`

#### Procedure
Execute `.aib_brain/prompts/aib-context.md` to regenerate `.aib_memory/context.md` in full, which will synthesize the updated workspace state after Tasks 1–6 are complete.

Acceptance test: After regeneration, `context.md` does not contain the strings `No changes — provide answer only` or `Skip analysis document generation` in any functional section (FR-007, architecture table). If the context regeneration prompt cannot be run immediately, manually update the following sections in `.aib_memory/context.md`:
1. FR-007 — remove toggle descriptions; keep `Minimum questions` description.
2. Architecture table, Input Channel row — remove toggle references from the description.
3. Component Map / Tool Scripts table — add row for `finalize-input.py`.

Acceptance test: `grep "No changes" .aib_memory/context.md` returns no matches in functional sections.

#### Done criteria
- `.aib_memory/context.md` does not describe the removed toggles in any functional section.
- `.aib_memory/context.md` documents `finalize-input.py`.
- All automated tests still pass.

#### Dependencies
Tasks 1–6.

#### Risk notes
Context regeneration (via `aib-context.md` prompt) is the preferred approach; manual update is a fallback if the prompt cannot be executed in the same session.

## Documentation

- `.aib_memory/context.md` (ref_id: N/A) — Update FR-007 to remove the two toggle descriptions; update the architecture table Input Channel row; add `finalize-input.py` to the tool scripts inventory.
- `.aib_brain/README.md` (ref_id: N/A) — Remove the paragraph describing the "No changes — provide answer only" toggle workflow.

## Questions & Decisions

