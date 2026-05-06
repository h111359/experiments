Files taken into consideration:
- `.aib_memory/request.md`
- `.aib_memory/references.md`
- `.aib_memory/context.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/tools/initialize.py`
- `.aib_brain/tools/menu.py`
- `tests/test_initialize.py`
- `tests/test_menu.py`

## Implementation Log

### Entry 2026-04-30 09:30

#### Scope
Implemented four targeted improvements to the AIB upgrade workflow: renamed `backups/` → `archives/` throughout the codebase; removed `references.md` from the upgrade restore list so it is always freshly seeded; added an interactive requests-archival prompt during upgrade with non-interactive default of "migrate"; updated `menu.py` to continue the menu loop automatically after a successful upgrade instead of exiting. Updated `context.md` to reflect changed FR-013 behavior and renamed folder. Updated all affected tests and added new tests covering the new behaviors.

#### Changes
- Renamed all `backups_dir` / `backup_path` variables and `"backups"` string literals in `_run_upgrade` to `archives_dir` / `archive_path` / `"archives"` in `.aib_brain/tools/initialize.py`.
- Added `import sys` to `.aib_brain/tools/initialize.py` (required for `sys.stdin.isatty()`).
- Added `_prompt_migrate_requests()` helper in `.aib_brain/tools/initialize.py` that prompts interactively when stdin is a TTY and defaults to "migrate" otherwise.
- Removed `"references.md"` from `restore_files` list in `_run_upgrade`; `references.md` is now always freshly seeded from brain templates on upgrade.
- Wrapped `requests_register.md` and `requests/` restore steps in `if migrate_requests:` conditional inside `_run_upgrade`.
- Updated upgrade summary print to include `requests` disposition and `references.md` seeding note.
- Updated `_run_upgrade` docstring to describe the new archive-based and interactive behavior.
- Updated `check_version_compatibility()` in `.aib_brain/tools/menu.py` to return `True` (instead of `False`) after a successful upgrade so the menu continues without requiring a relaunch.
- Updated the upgrade info banner in `menu.py` to say "archive" instead of "back up" and removed `references.md` from the listed preserved files.
- Updated `check_version_compatibility()` docstring in `menu.py` to reflect new return value semantics.
- Updated the `main()` comment in `menu.py` to reflect that `False` now only occurs on upgrade failure.
- Updated `TestUpgrade` in `tests/test_initialize.py`: renamed all `backups` → `archives` references in test names, assertions, and variable names.
- Added `test_upgrade_references_freshly_seeded` test to `tests/test_initialize.py` (SC-1).
- Added `test_upgrade_archive_requests_choice` test to `tests/test_initialize.py` (SC-4).
- Added `test_upgrade_migrate_requests_choice` test to `tests/test_initialize.py` (SC-5).
- Fixed `"backups"` → `"archives"` reference in `test_mismatch_shows_prompt_skip_returns_true` in `tests/test_menu.py`.
- Added `test_upgrade_choice_continues_menu` test to `tests/test_menu.py` (SC-2).
- Added `test_failed_upgrade_returns_false` test to `tests/test_menu.py`.
- Updated FR-013 description in `.aib_memory/context.md` to reflect renamed folder, changed behaviors, and auto-restart.
- Updated `.aib_memory/backups/` workspace file inventory entry to `.aib_memory/archives/` in `.aib_memory/context.md`.

#### Tests
- Unit/integration: `tests/test_initialize.py::TestUpgrade` — all 9 tests pass (includes 3 new).
- Unit: `tests/test_menu.py::TestCheckVersionCompatibility` — all 7 tests pass (includes 2 new).
- Full suite: 127 tests pass, 0 failures.

#### Outcome
All four tasks implemented successfully. All 127 tests pass with no regressions. SC-1 through SC-6 success criteria are met.

#### Evidence
```
python -m pytest tests/test_initialize.py tests/test_menu.py -x -q
74 passed in 1.67s

python -m pytest -q
127 passed in 9.14s
```

#### Notes (Optional)
The `_ignore_backups` inner function was removed during the rename (it was unused after refactoring the loop to use an explicit `if item.name == "archives": continue` guard, matching the prior pattern).
