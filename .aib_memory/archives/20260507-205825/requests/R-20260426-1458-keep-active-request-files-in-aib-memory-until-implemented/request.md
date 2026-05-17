## Goal

Change the AIB workflow so that active-request artifacts — `request.md`, `analysis.md`, and `UAT_scenarios.md` — are stored directly in `.aib_memory/` while the request is active, instead of being placed immediately inside the request's dedicated subfolder under `.aib_memory/requests/<request-folder>/`. Upon successful implementation, and before the request is closed, these files must be moved to their respective request folder. All other functionality (request folder creation, input archiving, context generation, etc.) remains unchanged.

## Background

Currently, `aib-analysis.md` writes `request.md`, `analysis.md`, and `UAT_scenarios.md` directly into `.aib_memory/requests/<request-folder>/`. During active development this means the files that the developer most frequently reads and edits are buried one folder level deeper than `.aib_memory/`. Placing them at `.aib_memory/` root while the request is live reduces navigation friction and makes the active working set immediately visible at the top level. After the request scope is implemented, the files are relocated into the request folder for long-term archival before the request is closed.

## Scope

- Modify the `aib-analysis.md` prompt so that `request.md` is written to `.aib_memory/request.md` (not `.aib_memory/requests/<request-folder>/request.md`).

- Modify the `aib-analysis.md` prompt so that `analysis.md` is written to `.aib_memory/analysis.md` (not `.aib_memory/requests/<request-folder>/analysis.md`).

- Modify the `aib-analysis.md` prompt so that `UAT_scenarios.md` (when created) is written to `.aib_memory/UAT_scenarios.md` (not `.aib_memory/requests/<request-folder>/UAT_scenarios.md`).

- Modify the `aib-implement.md` prompt to invoke `move-request-artifacts.py` before invoking `close-request.py`, ensuring all three active-request artifacts are relocated to the request subfolder.

- Create `.aib_brain/tools/move-request-artifacts.py`: a new Python script that deterministically moves `request.md`, `analysis.md`, and `UAT_scenarios.md` from `.aib_memory/` root to the active request's subfolder; idempotent (skips missing files without error); invoked by both `aib-implement.md` and `close-request.py`.

- Modify `close-request.py` to invoke `move-request-artifacts.py` before marking the request Closed, ensuring artifacts are always relocated even when `aib-implement.md` is not used. The move call must be guarded so that a move failure does not block the close operation.

- Update internal references inside `aib-analysis.md` and `aib-implement.md` to consistently resolve the active-request artifact paths.

- Update `analysis-convention.md` (File Naming & Location section) to reflect that during active requests `analysis.md` resides in `.aib_memory/` and is moved to the request folder upon implementation.

- Update `request-convention.md` (File Location & Naming section) to reflect the new two-phase location rule.

- Update `.aib_memory/context.md` (via `aib-context.md`) to reflect the changed component descriptions and architectural facts.

## Out of scope

- Changes to how the request folder itself is created by `create-request.py`.
- Changes to how `input.md` is archived to `<request-folder>/inputs/`.
- Changes to the location of `implementation.md` (generated inside the request folder during implementation).
- Changes to the location of `answer-<timestamp>.md` files.
- Changes to any CI/release-bookkeeping scripts.
- Multi-workspace or multi-request coordination behaviors.

## Constraints

- The single-Active-request invariant must be preserved throughout the entire change.
- The move of active-request artifacts must complete before `close-request.py` is invoked; after close the request folder is read-only.
- File names (`request.md`, `analysis.md`, `UAT_scenarios.md`) remain unchanged; only paths change.
- Tool scripts in `.aib_brain/tools/` must NOT be modified unless strictly necessary.
- The implementation must remain model-agnostic and workspace-local (no cloud or network dependencies).
- Python 3.10+ standard library only for any script changes.

## Success criteria

- After an analysis run with no prior Active request, `request.md` exists at `.aib_memory/request.md` and NOT at `.aib_memory/requests/<request-folder>/request.md`.
- After an analysis run, `analysis.md` exists at `.aib_memory/analysis.md` and NOT at `.aib_memory/requests/<request-folder>/analysis.md`.
- When UAT scenarios are generated during analysis, `UAT_scenarios.md` exists at `.aib_memory/UAT_scenarios.md`.
- After successful implementation, `request.md`, `analysis.md`, and `UAT_scenarios.md` (if present) exist inside `.aib_memory/requests/<request-folder>/` and no longer exist at `.aib_memory/` root.
- All existing automated tests pass without modification.
- New tests cover the new file-placement behavior (write to `.aib_memory/`, move on implement).

## Assumptions

- A1: The single-Active-request invariant (FR-001) guarantees that at most one `request.md` and one `analysis.md` exist at `.aib_memory/` root at any given time. Collisions between concurrent active-request artifacts are structurally impossible.
  - Risk if false: Multiple active requests could overwrite each other's root-level artifacts.

- A2: The move of artifacts from `.aib_memory/` root to the request subfolder is performed by a dedicated Python script (`move-request-artifacts.py`) invoked by both `aib-implement.md` (pre-close) and `close-request.py` (as a safety net). Using a dedicated script ensures deterministic, model-agnostic execution without risk of AI misinterpretation. The move completes before `close-request.py` marks the request Closed.
  - Risk if false: Files remain at `.aib_memory/` root after request closure, creating orphan state.

- A3: When `UAT_scenarios.md` does not exist at `.aib_memory/` (no manual UAT was needed for the request), the move script silently skips it without error.
  - Risk if false: Move script fails trying to move a non-existent file.

- A4: `close-request.py` invokes the move script before marking the request Closed, ensuring `request.md`, `analysis.md`, and `UAT_scenarios.md` (if present) are always relocated to the request subfolder regardless of whether `aib-implement.md` was used. If the move script raises an exception, `close-request.py` logs a warning but completes the close operation — close must always succeed.
  - Risk if false: Orphaned files at `.aib_memory/` root after direct close without implement; or a stuck close that leaves the register in an inconsistent Active state.

- A5: `aib-implement.md` reads `request.md` from `.aib_memory/request.md` (the new active location) rather than from the request subfolder. The prompt's input resolution section must be updated to reflect this.
  - Risk if false: Implementation reads stale or missing content and produces incorrect results.

- A6: The move script is idempotent: if called twice (e.g., once by `aib-implement.md` and once by `close-request.py`), the second call finds no source files at `.aib_memory/` root and exits cleanly without error. Idempotency is achieved via a `Path.exists()` check before each `shutil.move` call.
  - Risk if false: `close-request.py` (which always invokes the move script) would fail when called after `aib-implement.md` already performed the move, potentially blocking the close.

## Plan

### Task 1: Update `aib-analysis.md` — write artifacts to `.aib_memory/` root
**Intent:** Change all file write targets in `aib-analysis.md` so that `request.md`, `analysis.md`, and `UAT_scenarios.md` are written to `.aib_memory/` instead of `.aib_memory/requests/<request-folder>/`.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (current); `.aib_brain/conventions/analysis-convention.md`; `.aib_brain/conventions/request-convention.md`
**Outputs:** `.aib_brain/prompts/aib-analysis.md` (updated)
**External Interfaces:** None
**Environment & Configuration:** Workspace-local only; no environment variables or secrets
**Procedure:**
1. Read `aib-analysis.md` in full.
2. Identify every occurrence of `<request-folder>/request.md`, `<request-folder>/analysis.md`, and `<request-folder>/UAT_scenarios.md` path patterns.
3. Update each occurrence to `.aib_memory/request.md`, `.aib_memory/analysis.md`, and `.aib_memory/UAT_scenarios.md` respectively.
4. Update the Auto-Request Creation Branch step 5 (generate `request.md`) and Part 1/Part 2 output descriptions accordingly.
5. Verify no occurrence of the old paths remains in the file.
**Done Criteria:** `aib-analysis.md` contains no path references to artifact files inside `<request-folder>/` for `request.md`, `analysis.md`, or `UAT_scenarios.md`; artifact write targets are `.aib_memory/`.
**Dependencies:** None
**Risk Notes:** Path patterns appear in multiple sections; a missed occurrence would create inconsistent behavior.

### Task 2: Create `move-request-artifacts.py` — deterministic move script
**Intent:** Create a new Python tool script that moves `request.md`, `analysis.md`, and `UAT_scenarios.md` from `.aib_memory/` root to the active request's subfolder; idempotent and model-agnostic.
**Inputs:** `.aib_brain/tools/common.py` (for `parse_args`, `ensure_workspace`, `parse_markdown_table`, `read_text`, `requests_register_path`); `.aib_memory/requests_register.md` (runtime)
**Outputs:** `.aib_brain/tools/move-request-artifacts.py` (new script)
**External Interfaces:** Filesystem; reads `.aib_memory/` root; writes to active request subfolder
**Environment & Configuration:** Python 3.10+ standard library only; workspace-local
**Procedure:**
1. Create `.aib_brain/tools/move-request-artifacts.py`.
2. Implement `main()`: resolve active request folder from `requests_register.md` using existing `common.py` helpers.
3. For each target file (`request.md`, `analysis.md`, `UAT_scenarios.md`): if `source.exists()`, call `shutil.move(source, dest)`; otherwise skip silently.
4. Print a summary of moved and skipped files.
5. Exit with code 0 on success; raise `ValidationError` only for workspace-level errors (register missing, no active request, etc.).
**Done Criteria:** Script exists; moves existing files; skips missing files without error; calling twice exits cleanly on second call; `pytest tests/test_artifact_placement.py` passes.
**Dependencies:** None
**Risk Notes:** Must use `shutil.move` (handles cross-filesystem moves); must NOT use `os.rename` alone (fails across filesystems on some platforms).

### Task 3: Update `aib-implement.md` — read from `.aib_memory/` and invoke move script
**Intent:** Update `aib-implement.md` to resolve `request.md` from `.aib_memory/request.md` and invoke `move-request-artifacts.py` before `close-request.py`.
**Inputs:** `.aib_brain/prompts/aib-implement.md` (current)
**Outputs:** `.aib_brain/prompts/aib-implement.md` (updated)
**External Interfaces:** None
**Environment & Configuration:** Workspace-local only
**Procedure:**
1. Read `aib-implement.md` in full.
2. Update Input resolution section: clarify that `request.md` is read from `.aib_memory/request.md` (not from the request subfolder).
3. Add a pre-close step: invoke `python .aib_brain/tools/move-request-artifacts.py --workspace .` before `close-request.py`.
4. Verify ordering: move script step precedes `close-request.py` invocation.
**Done Criteria:** `aib-implement.md` reads `request.md` from `.aib_memory/request.md`; move script invocation is present and precedes `close-request.py`.
**Dependencies:** Task 2 (move script must exist)
**Risk Notes:** None identified.

### Task 4: Modify `close-request.py` — invoke move script before closing
**Intent:** Add a guarded call to `move-request-artifacts.py` functionality in `close-request.py` before marking the request Closed, ensuring artifacts are always relocated regardless of implementation path.
**Inputs:** `.aib_brain/tools/close-request.py` (current); `.aib_brain/tools/move-request-artifacts.py` (Task 2 output)
**Outputs:** `.aib_brain/tools/close-request.py` (modified)
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+ standard library only
**Procedure:**
1. Read `close-request.py` in full.
2. Import the move function from `move-request-artifacts.py` directly (prefer direct import over subprocess to avoid PATH dependencies).
3. Before the line `target[col["state"]] = CLOSED`, add a try/except call to the move function; log a warning on exception but do not re-raise (close must always complete).
4. Run `pytest tests/` to confirm no regressions.
**Done Criteria:** `close-request.py` invokes the move operation before marking Closed; a move failure logs a warning but does not prevent close; all existing tests pass.
**Dependencies:** Task 2 (move script must exist before modifying close-request.py)
**Risk Notes:** Guard is critical — an unguarded move failure would leave the register in an inconsistent Active state.

### Task 5: Update `analysis-convention.md` — two-phase placement rule
**Intent:** Revise Section 3 (File Naming & Location) to define the two-phase placement rule for `analysis.md`.
**Inputs:** `.aib_brain/conventions/analysis-convention.md` (current)
**Outputs:** `.aib_brain/conventions/analysis-convention.md` (updated)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read `analysis-convention.md` in full.
2. Update Section 3: replace the single-location rule with a two-phase rule stating (a) during active request, `analysis.md` resides at `.aib_memory/analysis.md`; (b) upon implementation completion (before close), it is moved to `.aib_memory/requests/<request-folder>/analysis.md`.
3. Add a note that re-runs of analysis fully replace the active copy at `.aib_memory/` root without merging.
**Done Criteria:** Section 3 expresses the two-phase rule; no reference to a single fixed location in `<request-folder>/`.
**Dependencies:** None
**Risk Notes:** Convention update must precede next analysis run to remain normatively consistent.

### Task 6: Update `request-convention.md` — two-phase placement rule
**Intent:** Revise the File Location & Naming section to define the two-phase placement rule for `request.md`.
**Inputs:** `.aib_brain/conventions/request-convention.md` (current)
**Outputs:** `.aib_brain/conventions/request-convention.md` (updated)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read `request-convention.md` in full.
2. Update File Location & Naming: add two-phase rule — active state at `.aib_memory/request.md`; archived state at `.aib_memory/requests/<request-folder>/request.md`.
3. Note that re-runs of analysis fully replace the active copy at `.aib_memory/` root.
**Done Criteria:** File Location & Naming section contains the two-phase rule; naming convention (`request.md`) is unchanged.
**Dependencies:** None
**Risk Notes:** Existing closed requests are unaffected; the rule applies only to future active requests.

### Task 7: Write automated tests for move script and close-request.py behavior
**Intent:** Add test cases covering the move script behavior (T1–T5) and close-request.py integration (T6–T7), and confirm all existing tests pass (T8).
**Inputs:** `tests/` directory; `tests/conftest.py`; `.aib_brain/tools/move-request-artifacts.py` (Task 2 output); `.aib_brain/tools/close-request.py` (Task 4 output)
**Outputs:** `tests/test_artifact_placement.py` (new test file)
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+; pytest; no external dependencies
**Procedure:**
1. Create `tests/test_artifact_placement.py`.
2. Write tests for T1–T5: move script moves `request.md`, `analysis.md`, `UAT_scenarios.md`; skips missing `UAT_scenarios.md`; is idempotent.
3. Write tests for T6–T7: `close-request.py` invokes move before closing; completes even when no artifacts at root.
4. Run `pytest tests/` and confirm all tests pass.
**Done Criteria:** `tests/test_artifact_placement.py` covers T1–T7; `pytest tests/` exits zero.
**Dependencies:** Tasks 2 and 4
**Risk Notes:** Tests simulate file operations directly using test workspaces; they do not invoke AI prompts.

### Task 8: Update `context.md` and all editable documents in `references.md`
**Intent:** Regenerate `context.md` to reflect the updated component descriptions and two-phase placement rule; verify no stale references to the old single-location behavior remain.
**Inputs:** `.aib_memory/references.md`; all updated files from Tasks 1–5; `.aib_brain/prompts/aib-context.md`
**Outputs:** `.aib_memory/context.md` (fully replaced)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Execute `aib-context.md` prompt after all Tasks 1–5 are complete.
2. Verify the generated `context.md` describes the two-phase placement rule in Component Map (Request Artifacts) and prompt descriptions for `aib-analysis.md`, `aib-implement.md`, and `close-request.py`.
3. Confirm no occurrence of the old single-location rule remains in `context.md`.
**Done Criteria:** `context.md` is regenerated; contains two-phase placement rule; no stale single-location references.
**Dependencies:** Tasks 1–7 complete
**Risk Notes:** `context.md` is fully replaced on every `aib-context.md` run; no manual merge needed.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Update component descriptions for Request Artifacts, `aib-analysis.md`, `aib-implement.md`, and `close-request.py` to reflect two-phase placement; update FR-003, FR-004, FR-005 entries.
- `.aib_brain/conventions/analysis-convention.md` (ref_id: N/A) — Update Section 3 (File Naming & Location) with the two-phase placement rule and re-run overwrite note.
- `.aib_brain/conventions/request-convention.md` (ref_id: N/A) — Update File Location & Naming section with the two-phase placement rule.

## Questions & Decisions



## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/prompts/aib-analysis.md` | Modified | Change artifact write targets from `<request-folder>/` to `.aib_memory/` root for `request.md`, `analysis.md`, `UAT_scenarios.md`. |
| `.aib_brain/prompts/aib-implement.md` | Modified | Update `request.md` read path to `.aib_memory/request.md`; invoke `move-request-artifacts.py` before `close-request.py`. |
| `.aib_brain/tools/move-request-artifacts.py` | Created | New script to deterministically move active-request artifacts from `.aib_memory/` root to the request subfolder; idempotent. |
| `.aib_brain/tools/close-request.py` | Modified | Invoke `move-request-artifacts.py` before marking request Closed (Q001 Option B resolution). |
| `.aib_brain/conventions/analysis-convention.md` | Modified | Update Section 3 to define two-phase placement rule for `analysis.md`. |
| `.aib_brain/conventions/request-convention.md` | Modified | Update File Location & Naming to define two-phase placement rule for `request.md`. |
| `.aib_memory/context.md` | Modified | Regenerated by `aib-context.md` to reflect updated component descriptions and FR entries. |
| `tests/test_artifact_placement.py` | Created | New test file covering move script and close-request.py artifact placement behavior (T1–T7). |
| `.aib_brain/tools/create-request.py` | Read-only dependency | Not modified; creates folder only, no artifact files. |

## Internal Review of Request and Product Docs

- OK: `.aib_memory/context.md` — FR-001 single-Active-request invariant is consistent; at most one artifact set exists at `.aib_memory/` root at any time.
- OK: `.aib_memory/context.md` — FR-002 confirms `create-request.py` does NOT seed `request.md`; consistent with new behavior where `request.md` is written by analysis to `.aib_memory/` root.
- OK: `.aib_memory/context.md` — FR-003 describes `aib-analysis.md` auto-create behavior and `input.md` reset as the last step; no contradiction with proposed path change.
- Updated: `.aib_memory/context.md` — FR-005 previously stated `close-request.py` only resets `input.md` with no mention of artifact file handling. Q001 Option B applied: `close-request.py` will now invoke the move script before closing. FR-005 must be updated in `context.md` regeneration (Task 8).
- OK: `.aib_memory/context.md` — FR-006 `aib-implement.md` auto-triggers `aib-analysis.md` when no Active request; unchanged.
- Ambiguity: `.aib_brain/Concepts.md` — Folder structure section documents `.aib_memory/requests/<request-folder>/` as containing `request.md` and `analysis.md`. This will be incorrect after implementation. `Concepts.md` has `edit_allowed = N` in `references.md`; cannot be updated by this request. Flagged as a follow-up item for the AIB Maintainer.
- OK: `.aib_brain/conventions/analysis-convention.md` Section 3 — currently defines single fixed location at `<request-folder>/analysis.md`; will be updated in Task 5 as part of scope.
- OK: `.aib_brain/conventions/request-convention.md` File Location & Naming — currently defines single fixed location inside `<request-folder>/`; will be updated in Task 6 as part of scope.
- OK: No active Q-blocks remain; Q001 applied (Option B: modify `close-request.py` to invoke move script) and removed from `## Questions & Decisions`.
