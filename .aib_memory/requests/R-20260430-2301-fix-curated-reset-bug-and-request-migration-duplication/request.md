## Goal

Fix confirmed bugs in the AIB system:

1. **Request migration duplication**: When `initialize.py --upgrade` is run and the user chooses to migrate old requests (Y), the `requests/` directory is both retained in the timestamped archive AND copied back to `.aib_memory/requests/`, creating an identical copy in both locations. The user's stated intent is that requests should exist in exactly one place — either the archive (archive-only choice) or active memory (migrate choice), never both.


## Background

The AIB upgrade workflow (`initialize.py --upgrade`) was introduced in R-20260427-0858 and improved in R-20260430-0808 to:
- Archive the current `.aib_memory/` to a timestamped subfolder under `.aib_memory/archives/`
- Clear non-archive content from `.aib_memory/`
- Re-seed from `.aib_brain/` templates
- Restore curated files (`context.md`, `instructions.md`)
- Conditionally restore `requests_register.md` and `requests/` based on an interactive prompt

The current implementation of the migration step uses `shutil.copytree` to copy `requests/` from the archive back to `.aib_memory/`. Because the archive was created by `shutil.copytree` in step 2, the result is that `requests/` exists identically in both locations. The user discovered this when running the upgrade and noticing requests in both the archive and the active memory.

## Scope

- Fix `_run_upgrade()` in `.aib_brain/tools/initialize.py` to ensure that when the user chooses to migrate requests (Y), the `requests/` folder is removed from the archive after being copied to active memory (or moved directly, avoiding the intermediate duplication).

- Add or update automated tests in `tests/test_initialize.py` to assert no duplication after a migrate upgrade.

- Update `.aib_memory/context.md` to reflect any changed behavior in FR-013 and FR-011.

## Out of scope

- Changes to the upgrade archive format or the content of what gets archived beyond the requests duplication fix.

- Changes to how `context.md`, `instructions.md`, or `requests_register.md` are restored.

- Changes to the interactive prompt wording or logic beyond what is strictly needed to fix the bugs.

- Changes to the `aib-implement.md`, `aib-analysis.md`, or `aib-context.md` prompts.

## Constraints

- All tool scripts must use Python 3.10+ standard library only (NFR-004).
- `shutil.move` must be used (not `os.rename`) for any file-move operations for cross-filesystem compatibility (per existing convention).
- The fix must not break the archive-only (N) path: when the user declines migration, `requests/` must remain exclusively in the archive.
- The fix must remain idempotent: running `--upgrade` twice does not compound the issue.
- Tests must not use external dependencies beyond `pytest` and the Python standard library.
- The curated reset bug fix scope is gated behind developer confirmation of the exact failing scenario (see `## Questions & Decisions`).

## Success criteria

- SC-1: After running `initialize.py --upgrade` and choosing Y (migrate), `.aib_memory/requests/` contains all migrated request folders AND the timestamped archive folder does NOT contain a `requests/` subfolder.
- SC-2: After running `initialize.py --upgrade` and choosing N (archive only), `.aib_memory/requests/` is empty (freshly seeded) AND the archive contains `requests/` with all prior request folders.
- SC-3: `tests/test_initialize.py::TestUpgrade::test_upgrade_migrate_requests_choice` is updated or supplemented to assert SC-1 (no `requests/` in archive after migration).
- SC-4: All existing `TestUpgrade` tests continue to pass after the fix.


## Assumptions

- A1: The correct fix for request migration duplication is to delete `requests/` from the archive after copying it to active memory. The archive is not expected to serve as a permanent rollback target for request content once the migration choice is made.
  - Risk if false: Deleting from the archive makes the archive an incomplete snapshot; if the developer needs to roll back after a failed migration, request data would be unrecoverable without VCS.

- A2: The `requests/` directory is the only candidate for the "one place or the other" constraint. Other restored files (`context.md`, `instructions.md`, `requests_register.md`) are either small or also in VCS, so duplication is acceptable for them.
  - Risk if false: The developer may also want `requests_register.md` to not be duplicated in the archive.

- A4: The workspace's `requests/` folder is always migratable in full (no partial migration of individual request folders is needed).
  - Risk if false: If requests contain VCS-tracked binary assets exceeding expected sizes, move operations could be slow.

## Plan

### Task 1: Fix request migration duplication in initialize.py
**Intent:** Ensure that when the user chooses Y (migrate), `requests/` is removed from the archive after being copied to active memory.
**Inputs:** `.aib_brain/tools/initialize.py` (`_run_upgrade` function, step 8); the existing `shutil.copytree` call.
**Outputs:** Modified `.aib_brain/tools/initialize.py` with a `shutil.rmtree` call on the archive's `requests/` directory after migration.
**External Interfaces:** `shutil.rmtree`, `shutil.copytree` (Python standard library).
**Environment & Configuration:** Python 3.10+; local developer workspace; no secrets.
**Procedure:**
1. In `_run_upgrade`, after `shutil.copytree(str(requests_archive), str(requests_dest))` completes successfully, add `shutil.rmtree(str(requests_archive))`.
2. Update the `restored.append("requests/")` print to note that requests were moved (not just restored).
3. Update the upgrade summary print to reflect "moved" semantics.
**Done Criteria:** After upgrade with Y, `(archive_path / "requests").exists()` is False; `(memory_root / "requests").exists()` is True with expected content.
**Dependencies:** None.
**Risk Notes:** If `copytree` succeeds but `rmtree` fails (e.g., permissions), requests will be in both locations. Add try/finally or a post-check to handle this gracefully.

### Task 2: Update tests for no-duplication assertion
**Intent:** Add test coverage for the new SC-1 requirement (no `requests/` in archive after migration).
**Inputs:** `tests/test_initialize.py` (`TestUpgrade.test_upgrade_migrate_requests_choice`); existing test infrastructure.
**Outputs:** Updated test asserting `(archive_path / "requests").exists()` is False AND `(memory_root / "requests").exists()` is True.
**External Interfaces:** Existing `_run_initialize`, `_make_brain_with_semver` helpers.
**Environment & Configuration:** `pytest`; Python standard library only.
**Procedure:**
1. In `test_upgrade_migrate_requests_choice`, seed `requests/` with at least one subfolder before running upgrade.
2. After upgrade with Y, assert the requests subfolder exists in `.aib_memory/requests/`.
3. Assert the archive does NOT contain `requests/` (resolve archive path via `archives/` glob or capture in test).
4. Verify that the archive-only (N) test still passes and `requests/` remains in the archive.
**Done Criteria:** Both `test_upgrade_migrate_requests_choice` and `test_upgrade_archive_requests_choice` pass with the updated assertions.
**Dependencies:** Task 1.
**Risk Notes:** Archive path is timestamped; resolve it in the test by globbing `archives/` for subdirectories after the upgrade run.

### Task 4: Update documentation and context.md
**Intent:** Reflect changed behavior in FR-013 (upgrade migrate semantics) and any FR-011 changes in `.aib_memory/context.md`.
**Inputs:** `.aib_memory/context.md`; `FR-013` description; `ADR-0003`; `_run_upgrade` docstring.
**Outputs:** Updated `.aib_memory/context.md`; updated `_run_upgrade` docstring in `initialize.py`.
**External Interfaces:** None.
**Environment & Configuration:** Local workspace.
**Procedure:**
1. In `context.md`, update FR-013 to state that `requests/` is moved (not copied) from the archive to active memory during migration — i.e., the archive will NOT contain `requests/` after a successful migration.
2. Update the `_run_upgrade` docstring in `initialize.py` to reflect "moved" semantics.
3. Append curated change bullets to `logs/next_version_changes.md` per the workspace `instructions.md` directive.
**Done Criteria:** FR-013 description in `context.md` uses "moved" and mentions that the archive excludes `requests/` after migration; `initialize.py` docstring is consistent.
**Dependencies:** Task 1.
**Risk Notes:** None.

## Documentation

- `.aib_memory/context.md` (ref_id: N/A) — FR-013 description must be updated to reflect "moved" (not copied) semantics for `requests/` migration; archive is not a full backup for `requests/` after migration choice.

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/initialize.py` | Modified | Add `shutil.rmtree` after `shutil.copytree` in `_run_upgrade` step 8 to remove `requests/` from archive after migration; update docstring. |
| `tests/test_initialize.py` | Modified | Update `test_upgrade_migrate_requests_choice` to assert no `requests/` in archive after migration; add new assertion for SC-1. |
| `.aib_memory/context.md` | Modified | Update FR-013 to reflect moved (not copied) `requests/` semantics. |
| `logs/next_version_changes.md` | Modified | Append curated change bullets during implementation. |


