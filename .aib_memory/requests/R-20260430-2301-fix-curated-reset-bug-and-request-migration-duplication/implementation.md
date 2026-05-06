Files considered during this implementation run:
- `.aib_memory/request.md` (active request, authoritative scope)
- `.aib_memory/context.md` (product context)
- `.aib_memory/instructions.md` (workspace directives)
- `.aib_brain/tools/initialize.py` (modified)
- `tests/test_initialize.py` (modified)

## Implementation Log

### Entry 2026-05-01 14:00
#### Scope
Fix request migration duplication in `initialize.py --upgrade`: when the user chooses Y (migrate), the `requests/` directory was being copied to active memory while also remaining in the timestamped archive, creating identical copies in two locations. The fix ensures `requests/` is removed from the archive immediately after a successful copy, so it exists in exactly one location. Tests and documentation updated to reflect the new "moved" semantics.

#### Changes
- Modified `.aib_brain/tools/initialize.py` Step 8 in `_run_upgrade`: added `shutil.rmtree(str(requests_archive))` after the `shutil.copytree` call to remove `requests/` from the archive post-migration.
- Updated `restored.append("requests/")` to `restored.append("requests/ (moved from archive)")` for clarity in the upgrade summary output.
- Updated the `requests_disposition` variable from `"migrated"` to `"moved to active memory (removed from archive)"` when migration is chosen.
- Updated `_run_upgrade` docstring to document moved (not copied) semantics: archive will NOT contain `requests/` after a successful Y migration.
- Updated `tests/test_initialize.py` `test_upgrade_migrate_requests_choice`: seeds a request subfolder before upgrade, asserts migrated content exists in active memory, asserts archive does NOT contain `requests/` after migration (SC-1).
- Updated `tests/test_initialize.py` `test_upgrade_archive_requests_choice`: seeds a request subfolder before upgrade, asserts `requests/` IS present in archive when N is chosen (SC-2).
- Updated `.aib_memory/context.md` FR-013 description to state that `requests/` is MOVED (not copied) during migration and will not be in the archive after a successful migration.
- Appended curated change bullets to `logs/next_version_changes.md`.

#### Tests
- unit/integration: `tests/test_initialize.py::TestUpgrade::test_upgrade_migrate_requests_choice` — pass (asserts SC-1: no `requests/` in archive, content in active memory)
- unit/integration: `tests/test_initialize.py::TestUpgrade::test_upgrade_archive_requests_choice` — pass (asserts SC-2: `requests/` remains in archive when N chosen)
- unit/integration: `tests/test_initialize.py::TestUpgrade` (all remaining tests) — pass

#### Outcome
Successful. SC-1 and SC-2 are satisfied. After upgrade with Y, `requests/` exists only in active memory; after upgrade with N, `requests/` exists only in the archive. No existing tests broken.

#### Evidence
- Modified file: `.aib_brain/tools/initialize.py` (Step 8 of `_run_upgrade`)
- Modified file: `tests/test_initialize.py` (two test methods in `TestUpgrade`)
- Modified file: `.aib_memory/context.md` (FR-013 bullet)
- Modified file: `logs/next_version_changes.md` (curated bullets appended)
