## Goal
When a new version of AIB is installed (by replacing `.aib_brain/` assets), the existing `.aib_memory/` folder must be preserved as a timestamped backup rather than silently overwritten. Version compatibility between `.aib_brain/` and `.aib_memory/` must be tracked through matching semver marker files. The AIB run entry point (`menu.py`) must detect a version mismatch at startup and present the user with upgrade options before proceeding. All backup and migration steps must be explicitly confirmed by the user.

## Background
AIB separates its reusable framework assets (in `.aib_brain/`) from workspace-specific state (in `.aib_memory/`). When a new AIB version is released, `.aib_brain/` is replaced by unzipping a new versioned archive. However, `.aib_memory/` currently carries no version marker, so there is no programmatic way to detect whether the installed memory structure is compatible with the new brain. The developer receives no warning, and no backup is taken before any migration.

This gap can cause silent incompatibility: user-curated files such as `context.md`, `instructions.md`, and `requests_register.md` could be overwritten or lost without any notice. Adding a semver marker file to `.aib_memory/` (mirroring the pattern already established in `.aib_brain/` via ADR-0001) and implementing a startup version check in `menu.py` closes this gap with minimal friction.

## Scope

- Add a semver marker file to `.aib_memory/` during initialization (`initialize.py`), named identically to the `.aib_brain/` semver file (e.g., `v1.2.8`), and handled idempotently on re-run.

- Add a `get_semver(dir: Path) -> str | None` helper to `common.py` for reusable semver detection across tool scripts.

- Implement a version consistency check in `menu.py` at startup: detect and compare the semver markers in `.aib_brain/` and `.aib_memory/`; when they differ or `.aib_memory/` has no semver file, display an upgrade prompt before the normal menu.

- Add `--upgrade` flag to `initialize.py` that executes the full upgrade procedure:
  - Creates a timestamped backup subfolder: `.aib_memory/backups/<YYYYMMDD-HHMMSS>/`
  - Copies the full current `.aib_memory/` content (all files and subdirectories, **excluding** `backups/`), including the `logs/` directory, into the new backup subfolder.
  - Any existing `backups/<ts>/` subfolders stay at their current level in `backups/` — they are NOT moved inside the new backup (flat hierarchy guaranteed).
  - Deletes the non-backup content of `.aib_memory/` (all files and dirs except `backups/`).
  - Re-seeds `.aib_memory/` from `.aib_brain/` templates using the existing `initialize.py` seeding logic.
  - Restores `context.md`, `instructions.md`, `requests_register.md`, and `references.md` from the new backup subfolder to `.aib_memory/`.
  - Seeds the new `.aib_memory/` semver marker file matching the installed `.aib_brain/` version.
  - Prints a clear summary of what was backed up, deleted, re-seeded, and restored.

- The `menu.py` upgrade prompt must present at least: (a) proceed with upgrade, (b) skip this time; no file changes may occur without explicit user selection of option (a).

## Out of scope

- Automatic download or installation of a new `.aib_brain/` version (user manually replaces `.aib_brain/`).

- Semantic migration of request content (reformatting `request.md` fields for schema changes between versions).

- Cloud or remote backup; all backup is filesystem-local only.

- Preserving `input.md` across upgrades — it is an ephemeral communication channel that is reset after each analysis run.

- Automatic upgrade without user confirmation.

## Constraints

- Python 3.10+ standard library only (NFR-004).
- Tool scripts MUST NOT write to `.aib_brain/` (ADR-0003).
- The backup must be complete and reversible; no partial writes that leave `.aib_memory/` in an inconsistent state.
- The upgrade procedure must be idempotent: re-running for the same version mismatch creates a new timestamped backup and does not overwrite a prior one.
- `initialize.py` remains idempotent on re-run: existing files are not overwritten unless `--force` is passed.
- The single Active request invariant (FR-001) must remain valid after upgrade (restored `requests_register.md` preserves existing state).
- No file write in the upgrade flow may occur without prior user confirmation via the `menu.py` prompt.

## Success criteria

- SC-1: After running `initialize.py` on a fresh workspace, `.aib_memory/` contains exactly one semver marker file whose name matches the `.aib_brain/` semver.
- SC-2: Re-running `initialize.py` on an already-initialized workspace does not overwrite the existing `.aib_memory/` semver marker file (idempotent skip).
- SC-3: Starting `menu.py` when `.aib_brain/` and `.aib_memory/` semver markers match shows the normal menu without an upgrade prompt.
- SC-4: Starting `menu.py` when the semver markers differ (or `.aib_memory/` has no semver marker) shows an upgrade prompt with at least two options before displaying the normal menu.
- SC-5: After confirming and completing the upgrade, `.aib_memory/backups/<timestamp>/` contains the complete pre-upgrade state including the `logs/` directory; `context.md`, `instructions.md`, `requests_register.md`, and `references.md` in the new `.aib_memory/` match the backed-up copies.
- SC-6: If `.aib_memory/backups/` previously contained timestamped subfolders, those subfolders are at the same level as the new backup (flat hierarchy; no nesting of backups inside backups).
- SC-7: When the user selects "skip" at the upgrade prompt, no files are written or deleted.
- SC-8: All existing automated tests continue to pass after implementation.

## Assumptions

- A1: The `.aib_brain/` semver is represented by exactly one empty file named `vMAJOR.MINOR.PATCH` (ADR-0001); the same pattern is extended to `.aib_memory/`.
  - Risk if false: semver detection in `menu.py` and `initialize.py` would require a different discovery strategy.

- A2: `references.md` is also restored from backup during upgrade (in addition to the three files explicitly listed in the request), as it contains user-curated reference entries essential for prompt execution.
  - Risk if false: project-specific references would be silently lost after upgrade; the next analysis run would seed a blank `references.md`.

- A3: The `.aib_memory/logs/` directory is included in the backup (preserving the action log audit trail), but is NOT restored after upgrade — a fresh empty `logs/` directory is created by re-seeding. This preserves log history in the backup without cluttering the refreshed memory structure.
  - Risk if false: if logs are expected to be restored post-upgrade, the restore scope in `initialize.py --upgrade` must be extended.

- A4: The `--upgrade` flag in `initialize.py` uses the existing shared `common.py` helpers (`load_template`, `write_text`, `seed_references_from_product_doc`) for re-seeding, keeping all upgrade logic within the same module entry point and avoiding subprocess coupling.
  - Risk if false: if the upgrade flow grows significantly more complex, it may warrant extraction to a dedicated module; current scope does not require this.

- A5: The `menu.py` version check is executed on every startup (with a clear skip option), not as a dedicated menu action, so the developer sees the warning at the earliest possible point.
  - Risk if false: if user prefers a menu action trigger, the implementation location and UX change.

## Plan

### Task 1: Add `get_semver` helper to `common.py`
**Intent:** Provide a reusable function that detects the semver version marker from any directory.
**Inputs:** `.aib_brain/tools/common.py`
**Outputs:** Modified `.aib_brain/tools/common.py` — new `get_semver(dir: Path) -> str | None` function.
**External Interfaces:** Filesystem (glob).
**Environment & Configuration:** Python 3.10+ standard library.
**Procedure:**
1. Add `get_semver(dir: Path) -> str | None` that globs `dir` for files matching `v[0-9]*.[0-9]*.[0-9]*`.
2. Return the matching file name (e.g., `"v1.2.8"`) if exactly one match found; return `None` otherwise.
**Done Criteria:** `get_semver(brain_dir)` returns `"v1.2.8"` on the current workspace; `get_semver(dir_without_marker)` returns `None`.
**Dependencies:** None.
**Risk Notes:** Multiple semver files in a directory return `None` (fail-safe).

---

### Task 2: Seed `.aib_memory/` semver marker in `initialize.py`
**Intent:** Ensure `initialize.py` creates a semver marker in `.aib_memory/` matching the installed `.aib_brain/` version.
**Inputs:** `.aib_brain/tools/initialize.py`, `common.py` (Task 1), `.aib_brain/v1.2.8`.
**Outputs:** Modified `.aib_brain/tools/initialize.py`; `.aib_memory/<brain_semver>` (empty file) created on init.
**External Interfaces:** Filesystem.
**Environment & Configuration:** Python 3.10+.
**Procedure:**
1. Call `get_semver(brain_dir)` to resolve current brain version.
2. If brain semver not found, print a warning and skip semver seeding.
3. Seed `.aib_memory/<brain_semver>` as an empty file; skip if already present (unless `--force`).
4. On `--force`, overwrite any existing semver file with the current brain version.
**Done Criteria:** SC-1 and SC-2 pass; `test_initialize.py` extended tests pass.
**Dependencies:** Task 1.
**Risk Notes:** None.

---

### Task 3: Add `--upgrade` flag to `initialize.py`
**Intent:** Extend `initialize.py` with an `--upgrade` flag that fully backs up `.aib_memory/`, re-seeds it from brain templates, and restores user-curated files.
**Inputs:** `.aib_brain/tools/initialize.py`, `.aib_brain/templates/`, `.aib_memory/` (pre-upgrade state), `common.py`.
**Outputs:** Modified `.aib_brain/tools/initialize.py` with upgrade branch; `.aib_memory/backups/<ts>/` (backup); refreshed `.aib_memory/` with restored user files and updated semver.
**External Interfaces:** Filesystem.
**Environment & Configuration:** Python 3.10+ standard library; no subprocess invocation.
**Procedure:**
1. Add `--upgrade` boolean flag to `parse_args()` in `common.py`.
2. In `initialize.py main()`, if `--upgrade` is set: resolve brain semver via `get_semver(brain_dir)`; abort with clear error if not found.
3. Generate timestamp string `<YYYYMMDD-HHMMSS>` and create `.aib_memory/backups/<ts>/`.
4. Copy all `.aib_memory/` content (files and subdirectories, including `logs/`) into `backups/<ts>/` using `shutil.copytree` with `ignore=shutil.ignore_patterns('backups')` to exclude the `backups/` directory itself.
5. Delete all non-`backups` files and directories from `.aib_memory/`.
6. Re-seed `.aib_memory/` using the existing seeding helpers: `load_template`, `write_text`, `seed_references_from_product_doc`; create `requests/` and `logs/` dirs; seed `input.md` and `instructions.md`.
7. Seed `.aib_memory/<brain_semver>` as an empty file.
8. Restore `context.md`, `instructions.md`, `requests_register.md`, and `references.md` from `backups/<ts>/` into `.aib_memory/` (overwrite freshly seeded versions).
9. Also restore `.aib_memory/requests/` directory from `backups/<ts>/requests/` if it exists (preserves request history).
10. Print a structured summary: backup location, files backed up, files restored, new semver.
**Done Criteria:** SC-5, SC-6 pass; backup subfolder contains pre-upgrade state including `logs/`; restored files match originals.
**Dependencies:** Task 1.
**Risk Notes:** Step 5 is destructive; it runs only after step 4 (backup) succeeds. If step 4 fails, abort without deleting.

---

### Task 4: Add version consistency check to `menu.py`
**Intent:** Detect semver mismatch at `menu.py` startup and present the user with upgrade options before the normal menu.
**Inputs:** `.aib_brain/tools/menu.py`, `common.py` (Task 1), `initialize.py --upgrade` (Task 3).
**Outputs:** Modified `.aib_brain/tools/menu.py`.
**External Interfaces:** Terminal (stdout, stdin); filesystem (semver files).
**Environment & Configuration:** Python 3.10+.
**Procedure:**
1. At the start of `main()`, call `get_semver(brain_dir)` and `get_semver(memory_dir)` to read both versions.
2. If brain semver is `None`, print a warning and continue (brain version unknown; do not block).
3. If memory semver is `None` or differs from brain semver, display a version mismatch banner showing both versions (or "unknown" if absent).
4. Present numbered options: `[1] Upgrade .aib_memory/ now`, `[2] Skip for this session`.
5. Read user input; if `1`, invoke `initialize.py --upgrade` as a subprocess (`subprocess.run([sys.executable, str(tools_dir / 'initialize.py'), '--workspace', str(workspace), '--upgrade'])`) and then exit (user re-launches menu after upgrade); if `2`, continue to normal menu.
6. If user input is invalid, re-display options.
**Done Criteria:** SC-3 and SC-4 pass; `test_menu.py` extended tests pass.
**Dependencies:** Tasks 1 and 3.
**Risk Notes:** `initialize.py` is already in `EXCLUDE_SCRIPTS` in `menu.py`, so no additional exclusion is needed for the upgrade flag.

---

### Task 5: Write automated tests
**Intent:** Verify all testable success criteria with automated test cases.
**Inputs:** `tests/test_initialize.py`, `tests/test_menu.py`.
**Outputs:** Extended `tests/test_initialize.py` (semver seeding + upgrade flow) and `tests/test_menu.py` (version check).
**External Interfaces:** Filesystem (temp dirs).
**Environment & Configuration:** Python 3.10+, pytest.
**Procedure:**
1. Add to `test_initialize.py`: semver seeding test (SC-1), idempotent re-run test (SC-2).
2. Add to `test_initialize.py` (upgrade flow tests via `--upgrade` flag):
   - Test backup creation: backup subfolder created with correct content including `logs/` directory (SC-5).
   - Test flat hierarchy: existing backup subfolders remain at `backups/` level (SC-6).
   - Test file restoration: `context.md`, `instructions.md`, `requests_register.md`, `references.md` restored from backup (SC-5).
   - Test skip: when user selects skip in menu, no files change (SC-7).
3. Add to `test_menu.py`: version match → no prompt (SC-3); version mismatch → prompt shown (SC-4); missing memory semver → prompt shown (SC-4).
4. Run full test suite and confirm SC-8.
**Done Criteria:** All new and existing tests pass; no regressions.
**Dependencies:** Tasks 1–4.
**Risk Notes:** `menu.py` tests use `unittest.mock`; `subprocess.run` call in `menu.py` for upgrade invocation must be patched via `unittest.mock.patch('subprocess.run')`.

---

### Task 6: Update documentation and context
**Intent:** Ensure `context.md` and `references.md` reflect the new components introduced by this request.
**Inputs:** `.aib_memory/context.md` (REF-0001), `.aib_memory/references.md`.
**Outputs:** Updated `.aib_memory/context.md`; unchanged `.aib_memory/references.md` (no new product-doc references needed for this request).
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Update the description of `initialize.py` in the Component Map to note semver seeding and the new `--upgrade` flag.
2. Update `menu.py` description to note version check at startup.
3. Add a new ADR for the `.aib_memory/` semver pattern extension and upgrade-in-place approach.
4. Update Requirements Summary to reflect new FR (semver in `.aib_memory/`, upgrade flow via `initialize.py --upgrade`, version check in `menu.py`).
**Done Criteria:** `context.md` accurately describes all new components; no stale references.
**Dependencies:** Tasks 1–4.
**Risk Notes:** None.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Update Component Map (update `initialize.py` for `--upgrade` flag, update `menu.py` for version check at startup), Requirements Summary, and Architecture sections to reflect semver extension and upgrade flow.

## Questions & Decisions



## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/common.py` | Modified | Add `get_semver(dir)` helper function. |
| `.aib_brain/tools/initialize.py` | Modified | Seed `.aib_memory/` semver marker on init; add `--upgrade` flag for backup-restore upgrade procedure. |
| `.aib_brain/tools/menu.py` | Modified | Add version consistency check at startup; invoke upgrade flow. |
| `.aib_memory/v1.2.8` | Created | Semver marker seeded by `initialize.py`; reflects current brain version. |
| `tests/test_initialize.py` | Modified | Add semver seeding tests (SC-1, SC-2) and upgrade flow tests (SC-5, SC-6, SC-7). |
| `tests/test_menu.py` | Modified | Add version check tests (SC-3, SC-4). |
| `.aib_memory/context.md` | Modified | Update Component Map, Requirements, Architecture sections. |
| `.aib_memory/requests_register.md` | Read-only dependency | Read during upgrade restoration to preserve request history. |
| `.aib_memory/references.md` | Read-only dependency | Read during upgrade restoration; preserved user content. |
| `.aib_brain/templates/` | Read-only dependency | Source for re-seeding `.aib_memory/` after backup. |

## Internal Review of Request and Product Docs

- OK: `context.md` (REF-0001) — ADR-0001 confirms the semver-as-empty-file pattern in `.aib_brain/`; extension to `.aib_memory/` is consistent with existing architecture.
- OK: `context.md` — `initialize.py` is already described as idempotent; semver seeding and the new `--upgrade` flag must both respect this invariant.
- OK: `context.md` — `menu.py` currently has no version-check logic; the startup hook is a clean extension point.
- Resolved: Request input — which files to restore after upgrade is partially specified (`context.md`, `instructions.md`, `requests_register.md`); `references.md` is not listed but contains user-curated content. Resolved via A2 (also restore `references.md`).
- Resolved (Q001): Version check fires on every `menu.py` startup (Option A selected) — already reflected in Task 4 plan.
- Resolved (Q002): Upgrade logic extends `initialize.py --upgrade` (Option B selected) — plan updated accordingly.
- Missing info: No specification for how `initialize.py --upgrade` should handle an Active request at upgrade time (the register row for an active request would be in `requests_register.md`, which is restored; `request.md` at `.aib_memory/request.md` is also backed up and restored via Task 3 step 9: restore `requests/` directory).
- Cross-ref issue: `context.md` acceptance criterion 7 states "Exactly one SemVer marker `v1.2.0` exists in `.aib_brain/`"; this will need updating to reflect `v1.2.8` (the actual current version) and extend to mention `.aib_memory/` — captured in Task 6.
