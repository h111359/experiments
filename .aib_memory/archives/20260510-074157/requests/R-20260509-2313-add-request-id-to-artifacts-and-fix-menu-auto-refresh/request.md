## Goal

Add the request ID to the names of the three active-request artifact files (`request.md`, `analysis.md`, `implementation.md`) so that simultaneous development on multiple git branches does not produce conflicting filenames during merge. Additionally, restore the automatic 3-second refresh cycle in the interactive menu (`menu.py`) that is currently not functioning correctly.

## Background

AIB keeps three per-request artifact files in `.aib_memory/` root while a request is active: `request.md`, `analysis.md`, and `implementation.md` (plus `UAT_scenarios.md`). When more than one developer (or one developer on multiple branches) works on different requests simultaneously, all active branches write files with the same names into `.aib_memory/`, creating hard merge conflicts.

The interactive menu (`menu.py`) is expected to refresh its display every 3 seconds automatically so that workspace state changes (e.g., a completed AI analysis run) are picked up without manual intervention. The developer reports that this auto-refresh functionality is not working.

## Scope

- Rename all active-phase artifact files to include the request ID:
  - `.aib_memory/request.md` → `.aib_memory/request-<request_id>.md`
  - `.aib_memory/analysis.md` → `.aib_memory/analysis-<request_id>.md`
  - `.aib_memory/implementation.md` → `.aib_memory/implementation-<request_id>.md`
  - `.aib_memory/UAT_scenarios.md` → `.aib_memory/UAT_scenarios-<request_id>.md`

- Update all AIB components that reference these filenames to use the ID-suffixed names:
  - `.aib_brain/tools/move-request-artifacts.py` — `_ARTIFACT_NAMES` constant and move logic
  - `.aib_brain/tools/close-request.py` — any reference to artifact filenames
  - `.aib_brain/prompts/aib-analysis.md` — all path references to `request.md`, `analysis.md`, `UAT_scenarios.md`
  - `.aib_brain/prompts/aib-implement.md` — all path references to `request.md`, `implementation.md`, `UAT_scenarios.md`
  - `.aib_brain/conventions/analysis-convention.md` — mentions `analysis.md` filename
  - `.aib_brain/conventions/request-convention.md` — mentions `request.md` filename

- Investigate and fix the `choose_action()` auto-refresh (TIMEOUT path) in `.aib_brain/tools/menu.py` so the menu reliably refreshes every 3 seconds without any new menu option.

- Update `.aib_memory/context.md` to reflect the new artifact naming convention.

- Update all automated tests affected by the filename changes.

## Out of scope

- Renaming the request folder itself (it already contains the request ID).
- Changing the archived-phase filenames inside the request subfolder (after `move-request-artifacts.py` runs).
- Changes to the git workflow or GitHub Actions CI.
- Renaming any `.aib_brain/` prompt or convention files.
- Changes to `requests_register.md` structure.

## Constraints

- The request ID format is `R-YYYYMMDD-HHmi` (e.g., `R-20260509-2313`).
- The renamed files must not introduce breaking changes to existing closed requests (archived artifacts stay as-is).
- No new menu option may be added for the auto-refresh — it must work transparently via the existing 3-second TIMEOUT path.
- All existing automated tests must pass after the change; update tests as needed.
- `.aib_brain/` prompt and convention files may be modified only to update path references; no behavioral changes to the prompts themselves beyond the filename references.

## Success criteria

- SC-01: When a request is active, `.aib_memory/` contains `request-<request_id>.md`, `analysis-<request_id>.md`, `implementation-<request_id>.md` (if present), and `UAT_scenarios-<request_id>.md` (if present) instead of the bare filenames.
- SC-02: `move-request-artifacts.py` correctly locates and moves ID-suffixed files from `.aib_memory/` to the request subfolder.
- SC-03: `close-request.py` completes without error after the rename, finding and moving the ID-suffixed artifacts.
- SC-04: `aib-analysis.md` prompt references updated filenames and the analysis run produces `analysis-<request_id>.md` at `.aib_memory/`.
- SC-05: `aib-implement.md` prompt references updated filenames and the implement run reads from `request-<request_id>.md`.
- SC-06: The interactive menu auto-refreshes its display every 3 seconds without any new menu option added.
- SC-07: All automated tests pass (`pytest tests/` with exit code 0).
- SC-08: `.aib_memory/context.md` reflects the updated artifact naming convention.

## Assumptions

- A1: `implementation.md` is created directly in the request subfolder (not at `.aib_memory/` root) and therefore does NOT need to be ID-suffixed at the root level.
  - Risk if false: The implement workflow would produce a bare `implementation.md` at root that `move-request-artifacts.py` fails to find, breaking request closure.

- A2: The archived-phase filenames (inside the request subfolder) remain unchanged (bare `request.md`, `analysis.md`, `UAT_scenarios.md`). The rename applies only to the active-phase root files.
  - Risk if false: Archived request subfolders would need migration, significantly expanding scope.

- A3: The request ID format `R-YYYYMMDD-HHmi` is stable and does not contain characters that are unsafe in filenames on Windows, macOS, or Linux.
  - Risk if false: Filename construction would require sanitization logic.

- A4: The root cause of the menu auto-refresh failure is the missing `if total_items > 0:` guard before modulo operations in `choose_action()`, not a deeper terminal-compatibility issue with `msvcrt.kbhit()`.
  - Risk if false: A deeper fix (e.g., replacing the polling approach) would be needed, significantly expanding the menu scope.

- A5: Convention files (`.aib_brain/conventions/`) are editable as part of this request (they are `.aib_brain/` assets, but the request scope explicitly includes updating path references in them).
  - Risk if false: Convention files cannot be updated, leaving a normative inconsistency.

## Plan

### Task 1: Fix menu auto-refresh (`choose_action()` zero-division guard)
**Intent:** Prevent `ZeroDivisionError` when no actions are visible by guarding modulo operations against `total_items = 0`.
**Outputs:** `.aib_brain/tools/menu.py` (two-line change)
**Procedure:**
1. Open `.aib_brain/tools/menu.py`.
2. Locate the `if key == "UP":` branch in `choose_action()`. Wrap `selected = (selected - 1) % total_items` with `if total_items > 0:`.
3. Locate the `if key == "DOWN":` branch. Wrap `selected = (selected + 1) % total_items` with `if total_items > 0:`.
4. Run `pytest tests/test_menu.py` to confirm no regressions; add a test case for UP/DOWN with `total_items = 0`.
**Done Criteria:** `pytest tests/test_menu.py` exits code 0; no `ZeroDivisionError` when UP/DOWN pressed with no visible actions.
**Dependencies:** None
**Risk Notes:** Minimal — two-line guard with no behavioral change when `total_items > 0`.

### Task 2: Add `artifact_name()` helper to `common.py`
**Intent:** Centralize active-phase artifact filename construction to avoid scattered string literals.
**Outputs:** `.aib_brain/tools/common.py` (new function `artifact_name(artifact_type, request_id)`)
**Procedure:**
1. Open `.aib_brain/tools/common.py`.
2. Add function `artifact_name(artifact_type: str, request_id: str) -> str` that returns `f"{artifact_type}-{request_id}.md"`. Include a validation that `request_id` matches the pattern `R-\d{8}-\d{4}` to prevent path traversal.
3. Export the function in the module's public surface.
4. Run `pytest tests/` to confirm no regressions.
**Done Criteria:** `artifact_name("request", "R-20260509-2313")` returns `"request-R-20260509-2313.md"`; invalid request IDs raise `ValueError`.
**Dependencies:** None
**Risk Notes:** Non-breaking addition; no existing callers yet.

### Task 3: Update `move-request-artifacts.py` to use ID-suffixed filenames
**Intent:** Replace the static `_ARTIFACT_NAMES` tuple with dynamic ID-suffixed filename resolution using the active request ID.
**Outputs:** `.aib_brain/tools/move-request-artifacts.py`
**Procedure:**
1. Open `.aib_brain/tools/move-request-artifacts.py`.
2. Import `artifact_name` from `common`.
3. Replace the `_ARTIFACT_NAMES` constant lookup with a call to `artifact_name(t, active_request_id)` for each artifact type (`"request"`, `"analysis"`, `"UAT_scenarios"`).
4. The active `request_id` is already available from the register parse; use it directly.
5. Run `pytest tests/test_artifact_placement.py` and confirm test failures (tests still use bare names); update tests in Task 7.
**Done Criteria:** `move_artifacts()` looks for `request-<ID>.md`, `analysis-<ID>.md`, `UAT_scenarios-<ID>.md` at `.aib_memory/` root.
**Dependencies:** Task 2
**Risk Notes:** Tests will fail until Task 7 updates them; do not run full suite until Task 7 is complete.

### Task 4: Update `close-request.py` to use ID-suffixed filenames (if applicable)
**Intent:** Ensure `close-request.py` does not hard-code bare artifact filenames.
**Outputs:** `.aib_brain/tools/close-request.py` (if bare filenames are found)
**Procedure:**
1. Open `.aib_brain/tools/close-request.py` and search for any direct references to `request.md`, `analysis.md`, `UAT_scenarios.md`.
2. If found, replace with calls to `artifact_name()` from `common.py`.
3. If not found (close-request delegates entirely to `move_artifacts`), confirm and skip with a note.
4. Run `pytest tests/test_artifact_placement.py` (will fail until Task 7).
**Done Criteria:** No bare artifact filenames in `close-request.py`; or confirmed none existed.
**Dependencies:** Task 2
**Risk Notes:** Low — `close-request.py` delegates artifact movement to `move-request-artifacts.py`.

### Task 5: Update `aib-analysis.md` prompt with new artifact path references
**Intent:** Update all occurrences of bare `request.md`, `analysis.md`, and `UAT_scenarios.md` path references in the analysis prompt to use the ID-suffixed pattern.
**Outputs:** `.aib_brain/prompts/aib-analysis.md`
**Procedure:**
1. Open `.aib_brain/prompts/aib-analysis.md`.
2. Replace every path reference `.aib_memory/request.md` → `.aib_memory/request-<request_id>.md` (and variants like `request.md` alone) with the pattern `request-<request_id>.md` where `<request_id>` refers to the active request ID resolved in preflight.
3. Apply the same substitution for `analysis.md` → `analysis-<request_id>.md` and `UAT_scenarios.md` → `UAT_scenarios-<request_id>.md`.
4. Verify the seed template reset still uses the correct pattern for `input.md` (unaffected).
**Done Criteria:** No bare `request.md`, `analysis.md`, or `UAT_scenarios.md` path references remain; all use `<artifact_type>-<request_id>.md` pattern.
**Dependencies:** None (prompt is plain text)
**Risk Notes:** Prompt changes are not automatically testable; manual review of the updated prompt is required.

### Task 6: Update `aib-implement.md` prompt with new artifact path references
**Intent:** Update all path references to `request.md` and `UAT_scenarios.md` in the implement prompt.
**Outputs:** `.aib_brain/prompts/aib-implement.md`
**Procedure:**
1. Open `.aib_brain/prompts/aib-implement.md`.
2. Locate the reference "Read it from `.aib_memory/request.md`" and update to `.aib_memory/request-<request_id>.md`.
3. Search for any other bare artifact filename references and update them.
4. Verify no reference to `implementation.md` at `.aib_memory/` root exists (it should not — `implementation.md` lives in the request subfolder).
**Done Criteria:** All `request.md` references in `aib-implement.md` use the ID-suffixed pattern; no bare filenames remain.
**Dependencies:** None
**Risk Notes:** Same as Task 5 — prompt changes require manual review.

### Task 7: Update automated tests
**Intent:** Update `tests/test_artifact_placement.py` and any other tests that reference bare artifact filenames to use ID-suffixed names.
**Outputs:** `tests/test_artifact_placement.py`, potentially `tests/test_lifecycle_e2e.py` and others
**Procedure:**
1. Search all test files for occurrences of `"request.md"`, `"analysis.md"`, `"UAT_scenarios.md"` (as file creation/assertion targets).
2. Update each occurrence to use the ID-suffixed form matching the test's request ID fixture.
3. Add a new test case to `tests/test_menu.py`: simulate `choose_action()` with `total_items = 0` and verify no `ZeroDivisionError` on UP/DOWN.
4. Run `pytest tests/` and confirm exit code 0.
**Done Criteria:** `pytest tests/` exits code 0 with no failures or errors.
**Dependencies:** Tasks 1, 3, 4
**Risk Notes:** Some test helpers (e.g., `_make_active_request`) may need updating to create ID-suffixed files.

### Task 8: Update `analysis-convention.md` and `request-convention.md`
**Intent:** Update normative convention files to reflect the new artifact naming pattern.
**Outputs:** `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`
**Procedure:**
1. Open `.aib_brain/conventions/analysis-convention.md`. Locate the section stating the file must be named `analysis.md`. Update to `analysis-<request_id>.md` (pattern notation). Update the two-phase placement rule description accordingly.
2. Acceptance test: search for `analysis.md` as a bare filename; confirm it no longer appears as a normative requirement.
3. Open `.aib_brain/conventions/request-convention.md`. Locate file naming requirements. Update `request.md` → `request-<request_id>.md`. Update the two-phase placement rule.
4. Acceptance test: search for `request.md` as a bare filename; confirm it no longer appears as a normative requirement.
**Done Criteria:** Both convention files describe the ID-suffixed pattern; no normative reference to bare `request.md` or `analysis.md` remains.
**Dependencies:** None
**Risk Notes:** Normative changes propagate to every future analysis run — must be precise.

### Task 9: Update `context.md` and other documentation
**Intent:** Reflect the new artifact naming convention in the workspace product documentation.
**Outputs:** `.aib_memory/context.md`
**Procedure:**
1. Open `.aib_memory/context.md`.
2. Locate FR-003, FR-004, FR-005, and any other requirement bullets that reference `request.md`, `analysis.md`, `UAT_scenarios.md` at `.aib_memory/` root as bare filenames. Update each to the ID-suffixed pattern.
3. Locate FR-010 or any menu-related requirement; update to note the zero-division guard added in Task 1.
4. Acceptance test: after update, search `context.md` for bare `request.md`, `analysis.md`; confirm they appear only in historical or archived-phase context (e.g., inside the request subfolder), not as active-phase filenames.
**Done Criteria:** `context.md` accurately describes the ID-suffixed active-phase naming convention and the menu fix.
**Dependencies:** Tasks 1–8
**Risk Notes:** `context.md` is auto-generated by `aib-context.md`; manual edits will be overwritten on the next context regeneration. The implement prompt triggers a context regeneration at the end of the run, which will overwrite the manual update. The documentation task here is to ensure the changes are captured accurately when context regeneration runs.

## Documentation

- `.aib_brain/conventions/analysis-convention.md` — Update the normative filename from `analysis.md` to `analysis-<request_id>.md` and revise the two-phase placement rule description.
- `.aib_brain/conventions/request-convention.md` — Update the normative filename from `request.md` to `request-<request_id>.md` and revise the two-phase placement rule description.
- `.aib_memory/context.md` — Update FR-003, FR-004, FR-005 artifact path references and FR-010 menu behavior description to reflect this request's changes.

## Questions & Decisions
