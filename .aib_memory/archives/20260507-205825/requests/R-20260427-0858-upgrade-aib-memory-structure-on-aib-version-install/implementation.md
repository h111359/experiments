Files considered during this implementation:
- `.aib_memory/request.md`
- `.aib_memory/references.md`
- `.aib_brain/Concepts.md`
- `.aib_brain/tools/common.py`
- `.aib_brain/tools/initialize.py`
- `.aib_brain/tools/menu.py`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `tests/test_initialize.py`
- `tests/test_menu.py`

## Implementation Log

### Entry 2026-04-29 19:20
#### Scope
Implement .aib_memory/ version-tracking and upgrade capability. Added a `get_semver` helper to `common.py`, semver marker seeding to `initialize.py`, an `--upgrade` flag to `initialize.py` with full backup/restore logic, and a startup version-compatibility check with upgrade prompt in `menu.py`.

#### Changes
- Added `get_semver(dir: Path) -> str | None` to `.aib_brain/tools/common.py`: globs for `vMAJOR.MINOR.PATCH` marker files, returns the name if exactly one found, otherwise None.
- Added `--upgrade` boolean argument to `parse_args()` in `.aib_brain/tools/common.py`.
- Rewrote `.aib_brain/tools/initialize.py`: extracted `_seed_memory()` and `_seed_semver()` helpers; added `_run_upgrade()` that creates a timestamped backup, clears non-backup content, re-seeds from templates, restores curated files and requests/, seeds new semver marker.
- Added duplicate-timestamp guard in `_run_upgrade()` to produce `<ts>-N` suffixed paths when two upgrades happen within the same second.
- Updated `menu.py` import to include `get_semver`; added `check_version_compatibility()` function and updated `main()` to invoke it before showing the menu.
- Extended `tests/test_initialize.py`: added `_make_brain_with_semver` helper, `--upgrade` support in `_run_initialize`, `TestSemverSeeding` class (4 tests), `TestUpgrade` class (6 tests).
- Extended `tests/test_menu.py`: added `TestCheckVersionCompatibility` class (5 tests) covering SC-3, SC-4, SC-7 and invalid-input loop.
- Appended 4 bullets to `logs/next_version_changes.md`.

#### Tests
- unit: `TestSemverSeeding.test_semver_marker_seeded_on_init` — pass (SC-1)
- unit: `TestSemverSeeding.test_semver_marker_skipped_when_exists` — pass (SC-2)
- unit: `TestSemverSeeding.test_semver_marker_force_overwrites` — pass
- unit: `TestSemverSeeding.test_no_semver_in_brain_skips_seeding` — pass
- integration: `TestUpgrade.test_upgrade_creates_backup` — pass (SC-5 partial)
- integration: `TestUpgrade.test_upgrade_backup_includes_logs` — pass (SC-5)
- integration: `TestUpgrade.test_upgrade_restores_curated_files` — pass (SC-5)
- integration: `TestUpgrade.test_upgrade_seeds_new_semver` — pass
- integration: `TestUpgrade.test_upgrade_flat_backup_hierarchy` — pass (SC-6)
- integration: `TestUpgrade.test_upgrade_fails_without_brain_semver` — pass
- unit: `TestCheckVersionCompatibility.test_matching_versions_returns_true` — pass (SC-3)
- unit: `TestCheckVersionCompatibility.test_missing_brain_semver_returns_true_with_warning` — pass
- unit: `TestCheckVersionCompatibility.test_mismatch_shows_prompt_skip_returns_true` — pass (SC-7)
- unit: `TestCheckVersionCompatibility.test_mismatch_missing_memory_semver_shows_prompt` — pass (SC-4)
- unit: `TestCheckVersionCompatibility.test_invalid_then_valid_choice_loops` — pass
- regression: full test suite (122 tests) — all pass

#### Outcome
All 122 tests pass. The implementation fulfils all success criteria (SC-1 through SC-8). The upgrade flow is destructive only after a successful backup and requires explicit user confirmation via the menu prompt.

#### Evidence
- ```
  122 passed in 22.82s
  ```
