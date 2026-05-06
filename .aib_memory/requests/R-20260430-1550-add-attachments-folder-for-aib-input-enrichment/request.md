## Goal

Add `.aib_memory/attachments/` as a staging folder for supplementary input files. Files placed there by the developer are treated as part of the current input alongside `input.md`. When the input is consumed by `aib-analysis.md`, all files in `attachments/` are moved to the active request folder together with the archived `input.md`. This enriches the input channel without requiring developers to embed binary or large-file content directly in `input.md`.

## Background

Currently the only input mechanism for the AIB analysis workflow is the text written in `.aib_memory/input.md`. For complex requests a developer may need to provide supplementary context: screenshots, specifications, data samples, log excerpts, or structured files. There is no supported way to include such files in the current workflow without embedding their content as text inside `input.md`, which is impractical for binary files and visually noisy for structured files. Adding an `attachments/` staging folder resolves this gap and makes the input channel richer and more developer-friendly.

## Scope

- Create `.aib_memory/attachments/` directory in `initialize.py` (standard init and `--upgrade` path).

- Update `aib-analysis.md` prompt to declare `.aib_memory/attachments/` as part of the input: any files present in the folder MUST be read (text files) or acknowledged (non-text files) before drafting analysis, in addition to `input.md`.

- Update the auto-request creation branch in `aib-analysis.md` to move all files from `.aib_memory/attachments/` to `<request-folder>/inputs/` when archiving `input.md` (step 6 of the auto-request branch).

- Update the "No changes — provide answer only" path behavior (pending Q003 decision).

- Update `.aib_memory/context.md` and relevant product documentation to reflect the new input channel.

- Update `close-request.py` as a safety net: log a warning if `.aib_memory/attachments/` is non-empty when closing a request (files should have been moved during analysis).

## Out of scope

- Recursive/subdirectory scanning of `attachments/` (flat folder only in this iteration).

- Content indexing or semantic search over attachment files.

- Multi-request attachment queuing (single staging area, cleared on each analysis run).

- Attachment support in `aib-implement.md` (attachments are consumed during analysis; implementation reads `request.md` only).

- Automated binary-file content extraction or OCR.

- Modifications to `move-request-artifacts.py` (that script handles only `request.md`, `analysis.md`, and `UAT_scenarios.md`; attachments are handled during the analysis archiving step).

## Constraints

- Python 3.10+ standard library only; no third-party packages.

- `initialize.py` must remain idempotent: create `attachments/` only if absent.

- The `attachments/` folder at `.aib_memory/attachments/` is a staging area; it MUST be empty after input is consumed.

- No modification to `.aib_brain/` assets except for prompt files (`.aib_brain/prompts/aib-analysis.md`).

- All file move operations must use `shutil.move` for cross-filesystem compatibility.

## Success criteria

- SC-1: After running `initialize.py` on a fresh workspace, `.aib_memory/attachments/` directory exists.

- SC-2: After running `initialize.py` on an existing workspace (re-run), `.aib_memory/attachments/` is created if absent and not overwritten if already present with files.

- SC-3: When `aib-analysis.md` runs with files in `.aib_memory/attachments/`, those files are acknowledged or read as part of the input before analysis is drafted.

- SC-4: After `aib-analysis.md` completes the auto-request creation branch, all files from `.aib_memory/attachments/` are present in `<request-folder>/inputs/` and the `attachments/` folder is empty.

- SC-5: `close-request.py` logs a warning (non-blocking) when `attachments/` is non-empty at close time.

- SC-6: `context.md` accurately reflects the `attachments/` folder as part of the Input Channel component.

## Assumptions

- A1: The `attachments/` folder is a flat staging area; subdirectories placed inside it are ignored in this iteration.
  - Risk if false: Developers placing subdirectories would find their content silently skipped, leading to incomplete input capture.

- A2: All files in `attachments/` are moved (not copied) to `<request-folder>/inputs/` when input is archived; after the move the staging area is empty.
  - Risk if false: Files would accumulate in the staging area across multiple runs, causing stale input pollution.

- A3: The `attachments/` folder is VCS-tracked with a `.gitkeep` placeholder (pending Q001 decision). If Q001 resolves to gitignore, implementation switches to adding a `.gitignore` entry instead.
  - Risk if false: An empty directory without `.gitkeep` is not committed to Git, making the feature invisible to newly cloned workspaces.

- A4: `initialize.py`'s `--upgrade` path re-creates `attachments/` via `_seed_memory`, so no separate upgrade-path handling is needed.
  - Risk if false: Upgraded workspaces would lack the `attachments/` directory until manually created.

- A5: The AI agent reads only text files from `attachments/`; binary files are listed by name but not read for content.
  - Risk if false: Attempting to read binary files as text may produce garbage output that corrupts the analysis context.

## Plan

### Task 1: Seed `attachments/` directory in `initialize.py`
**Intent:** Add `attachments/` directory creation to the `_seed_memory` function so every initialized workspace has the staging folder.
**Inputs:** `.aib_brain/tools/initialize.py`, `.aib_brain/tools/common.py`
**Outputs:** Modified `initialize.py` with one additional `mkdir` call; `attachments/` created during init and upgrade.
**External Interfaces:** File system only.
**Environment & Configuration:** Python 3.10+; no config keys.
**Procedure:**
1. Open `initialize.py`.
2. In `_seed_memory`, after the `logs/` directory creation line, add `(memory_root / "attachments").mkdir(parents=True, exist_ok=True)`.
3. Print a status line consistent with existing logging style (e.g., `"Created attachments directory."`).
**Done Criteria:** `initialize.py` exits 0 on fresh workspace and creates `.aib_memory/attachments/`; re-run does not error.
**Dependencies:** None.
**Risk Notes:** Trivial; `exist_ok=True` makes the call safe on re-run.

### Task 2: Update `aib-analysis.md` — read attachments as part of input
**Intent:** Extend the inputs and mandatory preflight steps in `aib-analysis.md` so the AI agent reads text files from `.aib_memory/attachments/` before drafting analysis.
**Inputs:** `.aib_brain/prompts/aib-analysis.md`
**Outputs:** Modified `aib-analysis.md` with updated `Inputs:` declaration and a new step in the standard preflight instructing the agent to list and read attachment files.
**External Interfaces:** File system read of `.aib_memory/attachments/`.
**Environment & Configuration:** No config. Prompt is read by AI agent at execution time.
**Procedure:**
1. Add `.aib_memory/attachments/` to the `Inputs:` section of `aib-analysis.md`.
2. Add a step in the mandatory preflight (after step 4 toggle detection): "Read all files in `.aib_memory/attachments/`. For each file: if text-readable, read and treat as additional input context; if binary, note the filename. Flat scan only — subdirectories are ignored."
3. Add a note that files in `attachments/` are considered part of the input even if not referenced in `input.md`.
**Done Criteria:** Prompt contains explicit instruction to read `attachments/` before analysis drafting; the instruction is in the correct preflight position.
**Dependencies:** Task 1 (directory must exist).
**Risk Notes:** Prompt changes are additive; no existing behavior is removed.

### Task 3: Update `aib-analysis.md` — move attachments during archiving
**Intent:** Extend the auto-request creation branch's input archiving step to move all files from `.aib_memory/attachments/` to `<request-folder>/inputs/` when archiving `input.md`.
**Inputs:** `.aib_brain/prompts/aib-analysis.md`, `<request-folder>/inputs/` path
**Outputs:** Modified step 6 of the auto-request creation branch in `aib-analysis.md`; attachment files relocated to request folder at runtime.
**External Interfaces:** File system write/move using `shutil.move` or Python `Path`.
**Environment & Configuration:** No config.
**Procedure:**
1. In step 6 of the Auto-Request Creation Branch, after archiving `input.md`, add: "For each file in `.aib_memory/attachments/` (flat scan, ignore subdirectories): move it to `<request-folder>/inputs/<filename>` using Python. After moving all files, `.aib_memory/attachments/` MUST be empty."
2. Ensure the instruction specifies using Python (not shell commands) and `shutil.move` for cross-filesystem compatibility.
3. Apply the same move step to the "No changes — provide answer only" path if Q003 is resolved as "move attachments" (conditional on Q003 answer).
**Done Criteria:** After a run of `aib-analysis.md` on the auto-request branch with files in `attachments/`, all files appear in `<request-folder>/inputs/` and `attachments/` is empty.
**Dependencies:** Task 1.
**Risk Notes:** Edge case: if the agent fails mid-move, some files may remain in `attachments/` and others may be in the request folder. This is acceptable for v1; no rollback mechanism is required.

### Task 4: Update `close-request.py` — safety-net warning for non-empty `attachments/`
**Intent:** Add a non-blocking check in `close-request.py` that warns when `.aib_memory/attachments/` is non-empty at close time, helping developers identify missed archiving.
**Inputs:** `.aib_brain/tools/close-request.py`
**Outputs:** Modified `close-request.py` with a post-close check; warning printed to stdout.
**External Interfaces:** File system check only.
**Environment & Configuration:** No config.
**Procedure:**
1. After the `update_requests_register` call and before the `input.md` reset, add: `attachments_dir = workspace / ".aib_memory" / "attachments"; if attachments_dir.exists() and any(attachments_dir.iterdir()): print("WARNING: .aib_memory/attachments/ is non-empty. Files were not archived — consider running aib-analysis.md before closing.")`.
2. Confirm the check is non-blocking (no raise, no SystemExit).
**Done Criteria:** Invoking `close-request.py` with a non-empty `attachments/` prints a warning but exits 0 and marks the request Closed.
**Dependencies:** Task 1.
**Risk Notes:** The `.iterdir()` call is safe on an empty directory; no edge case risk.

### Task 5: Automated tests
**Intent:** Add/update automated tests covering SC-1 through SC-3, SC-6, and T6/T7.
**Inputs:** `tests/test_initialize.py`, `tests/test_close_request.py` (or new test file), `initialize.py`, `close-request.py`
**Outputs:** New or updated test cases; `pytest tests/` green.
**External Interfaces:** None (tests use temp directories).
**Environment & Configuration:** Python 3.10+, pytest.
**Procedure:**
1. In `tests/test_initialize.py`, add `test_creates_attachments_dir` verifying `(root / ".aib_memory" / "attachments").is_dir()` after `_run_initialize`.
2. Add `test_initialize_idempotent_attachments_dir` placing a sentinel file in `attachments/`, re-running init, and confirming the sentinel survives.
3. In `tests/test_close_request.py` (or a new `test_attachments.py`), add `test_close_request_warns_nonempty_attachments` verifying the warning is printed (capture stdout) when `attachments/` contains a file.
4. Run `pytest tests/ -v` and confirm all tests pass.
**Done Criteria:** All existing tests pass; new tests pass; no regressions.
**Dependencies:** Tasks 1 and 4.
**Risk Notes:** Test isolation relies on temp directories; no cross-test pollution risk.

### Task 6: Update documentation (`context.md` and `README.md`)
**Intent:** Update `context.md` to reflect the `attachments/` folder in the Input Channel component description and architecture; update README if it documents the input channel.
**Inputs:** `.aib_memory/context.md` (REF-0001), `.aib_brain/README.md`
**Outputs:** Updated `context.md` and README with `attachments/` folder documented.
**External Interfaces:** None.
**Environment & Configuration:** No config.
**Procedure:**
1. Execute `.aib_brain/prompts/aib-context.md` to regenerate `context.md` with the new component.
2. Manually verify the `Input Channel` component in the Architecture section includes `attachments/` with lifecycle description.
3. Add a brief note to `.aib_brain/README.md` (if it documents input.md) describing the `attachments/` folder.
**Done Criteria:** `context.md` Input Channel section references `attachments/`; README updated if applicable; `aib-context.md` run completes without error.
**Dependencies:** Tasks 1–4.
**Risk Notes:** Context regeneration is idempotent.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Update Input Channel component to include `attachments/` folder description, lifecycle semantics, and VCS policy. Update FR-003 and Architecture Component Map.

- `.aib_brain/README.md` (ref_id: N/A) — Add a section or note describing the `attachments/` folder as part of the developer input workflow.

## Questions & Decisions

**Q001**: Should `.aib_memory/attachments/` be tracked by VCS (Git)?
- [x] Option A: Track with VCS — add a `.gitkeep` placeholder; developers commit attachments alongside their request context. *(recommended)*
- [ ] Option B: Exclude from VCS — add `.aib_memory/attachments/` to `.gitignore`; attachments remain local only and are never committed.
- [ ] Other: ___
> Answer: 

**Q002**: Where should files from `attachments/` be placed inside the request folder when archiving?
- [x] Option A: `<request-folder>/inputs/` — same directory as `input-archive-*.md`; all input artifacts in one place. *(recommended)*
- [ ] Option B: `<request-folder>/attachments/` — dedicated subfolder inside the request folder; keeps text-archive and binary files separated.
- [ ] Other: ___
> Answer: 

**Q003**: Should files in `.aib_memory/attachments/` be moved to the request folder when the "No changes — provide answer only" toggle is checked?
- [ ] Option A: Yes — move attachments alongside the answer file; the spec's "exactly two file writes" invariant is updated to allow additional moves.
- [x] Option B: No — ignore attachments when "No changes" is active; attachments remain in the staging folder until the next regular analysis run. *(recommended)*
- [ ] Other: ___
> Answer: 

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/initialize.py` | Modified | Add `attachments/` directory creation in `_seed_memory`. |
| `.aib_brain/prompts/aib-analysis.md` | Modified | Add `attachments/` to Inputs declaration; add preflight step to read attachment files; add archiving step to move attachments to request folder. |
| `.aib_brain/tools/close-request.py` | Modified | Add non-blocking safety-net warning when `attachments/` is non-empty at close time. |
| `.aib_memory/context.md` | Modified | Update Input Channel component, FR-003, and Architecture Component Map to include `attachments/`. |
| `.aib_brain/README.md` | Modified | Document `attachments/` folder as part of the developer input workflow. |
| `tests/test_initialize.py` | Modified | Add test cases for `attachments/` directory creation and idempotency. |
| `tests/test_close_request.py` | Modified | Add test case for non-empty `attachments/` warning on close. |
| `.aib_memory/attachments/` | Created | New staging directory for supplementary input files. |
| `.gitignore` | Modified | Add entry or `.gitkeep` depending on Q001 resolution. |

## Internal Review of Request and Product Docs

- OK: `request.md` — All 12 mandatory sections present; sections 1–6 are non-empty and consistent with each other.

- OK: `context.md` (REF-0001) — FR-003 describes the auto-request creation branch including input archiving; this request extends that flow. No contradiction.

- Ambiguity: `aib-analysis.md` (prompt) — Step 6 of the Auto-Request Creation Branch states "Use python to create the `inputs/` subfolder and write the archive file." The word "write" currently covers only `input-archive-*.md`. After this request, "write" must also cover the attachment move. The wording update is tracked in Task 3.

- Ambiguity: `aib-analysis.md` (prompt) — "No changes — provide answer only" branch states "exactly two file writes." If Q003 is resolved as Option A, this invariant must be updated. Tracked in Q003.

- Missing info: `context.md` — The Input Channel component description does not mention `attachments/`. This is the current state; update is planned in Task 6.

- Cross-ref issue: `context.md` Architecture Component Map — The `Input Channel` row references only `input.md` as the content of `.aib_memory/input.md`. After implementation, this row must also reference `attachments/`. Tracked in Task 6.

- OK: `Concepts.md` — The `input.md` lifecycle section does not conflict with the new attachments concept; it describes the text-input flow which remains unchanged. The new attachments are additive.

- OK: `references.md` — REF-0001 (`context.md`) is the only `product-doc` and is correctly identified. No new references need to be added for the `attachments/` folder itself.

