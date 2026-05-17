## Goal

Improve the AIB upgrade workflow with four targeted changes:
1. Do not restore `references.md` from the archive during upgrade — let it be freshly seeded from brain templates.
2. Auto-restart the menu after a successful upgrade instead of requiring the user to re-launch manually.
3. Rename the `backups/` directory concept to `archives/` throughout the codebase, output messages, and tests.
4. Present an interactive prompt before the archive step asking whether old requests should be migrated into the new `.aib_memory/` or left in the archive only; conditionally restore `requests/` and `requests_register.md` based on the user's answer.

## Background

The current `initialize.py --upgrade` procedure (FR-013) creates a timestamped subfolder under `.aib_memory/backups/`, copies the current content, re-seeds from brain templates, and restores several "user-curated" files: `context.md`, `instructions.md`, `requests_register.md`, `references.md`, and the `requests/` directory. This design was implemented in R-20260427-0858.

Four issues have been identified with the current implementation:

1. `references.md` is restored from the old version, but it may contain stale entries tied to the old brain structure. The upgrade should always produce a fresh `references.md` seeded from the new brain, just as a first-time initialization would.
2. After upgrade, `menu.py` displays "Upgrade complete. Please re-launch the AIB menu." and exits. The user must rerun the launcher script manually, which is unnecessary friction for a zero-config tool.
3. The `backups/` folder name implies disaster-recovery semantics. "Archives" more accurately describes the purpose: preserving historical snapshots of previous memory versions for reference, not for active recovery operations.
4. Old requests are always migrated unconditionally. Some users may prefer to start fresh without prior request history, especially when upgrading across major workflow changes.

## Scope

- `initialize.py` — Remove `references.md` from the `restore_files` list; rename all `"backups"` string literals and related variable names to `"archives"`; add an interactive stdin prompt before archiving that asks whether old requests should be migrated or archived; conditionally restore or skip `requests/` and `requests_register.md` based on the answer.

- `menu.py` — Replace the exit-and-re-launch instruction after upgrade with automatic continuation of the menu loop; rename any `backup`/`backups` string references in output messages and inline comments to `archive`/`archives`; adjust `check_version_compatibility()` so that a successful upgrade returns control to the caller to continue showing the menu, rather than returning `False` and exiting.

- `tests/test_initialize.py` — Update all assertions referencing `"backups"` to `"archives"`; add test verifying that `references.md` is freshly seeded after upgrade (not restored); add tests covering the requests-archival prompt for both choices.

- `tests/test_menu.py` — Update upgrade-related tests to reflect the auto-restart behavior (menu continues rather than exits after upgrade).

- `.aib_memory/context.md` — Update FR-013 description and the component map entry for `.aib_memory/backups/` to reflect the renamed folder and changed behaviors.

## Out of scope

- Changes to `context.md` or `instructions.md` restore behavior during upgrade (both continue to be restored from the archive as before).

- Runtime migration of existing `backups/` folders in users' workspaces to `archives/` (users' existing archives are not renamed by this change).

- Changes to the versioned zip archive naming in `versions/` or the release bookkeeping workflow.

- Changes to `close-request.py`, `create-request.py`, `move-request-artifacts.py`, or other tool scripts not involved in the upgrade flow.

- Any GUI-based or web-based menu replacement.

## Constraints

- Python 3.10+ standard library only (NFR-004); no third-party packages may be introduced.

- `references.md` must still be seeded from brain templates during upgrade — the change is only that it is no longer restored from the archive.

- The interactive requests-archival prompt must degrade gracefully when stdin is not a TTY (e.g., during automated testing or CI); the default behavior when non-interactive must be "migrate" (preserve backward compatibility).

- Auto-restart of the menu after upgrade must not create an infinite upgrade loop; the upgrade must be detected as complete before the menu re-enters its normal flow.

- Renaming `backups/` → `archives/` must be applied consistently across all updated source files, tests, and documentation, but must NOT retroactively rename existing `backups/` folders in user workspaces at runtime.

- The `requests_register.md` handling must preserve the single-Active-request invariant (FR-001).

## Success criteria

- SC-1: After upgrade, `.aib_memory/references.md` contains freshly seeded content from brain templates, not the content from the archived pre-upgrade version. A test asserting this passes.

- SC-2: After a successful upgrade triggered from `menu.py`, the AIB menu is displayed automatically without any "Please re-launch" message or manual user intervention.

- SC-3: No `"backups"` string literal remains in `initialize.py` or `menu.py` (excluding archived closed-request files). All occurrences are replaced with `"archives"`. Tests referencing the old folder name are updated.

- SC-4: When the user selects "archive old requests" at the interactive prompt, the upgrade completes without restoring `requests/` or `requests_register.md` from the archive; `.aib_memory/requests/` directory contains only the fresh seed structure and `requests_register.md` is freshly seeded.

- SC-5: When the user selects "migrate old requests" (default/non-interactive), `requests/` and `requests_register.md` are restored from the archive, preserving prior request history.

- SC-6: All previously passing tests continue to pass after the changes; new tests covering SC-1, SC-4, and SC-2-related behavior are added and pass.

## Assumptions

- A1: The `initialize.py --upgrade` entry point is always invoked via `menu.py`; there is no documented non-interactive CI path that calls `initialize.py --upgrade` directly and expects the old `backups/` folder name.
  - Risk if false: Any CI or automation that hard-codes the `backups/` path would break silently after the rename.

- A2: "Auto-restart the menu" means the menu UI re-enters its normal rendering loop in the same process after upgrade, without requiring a second OS-level process launch.
  - Risk if false: A re-exec approach might be required if process-level state isolation is needed; the chosen implementation approach depends on the answer to Q002.

- A3: The `references.md` seeded by brain templates on a fresh init is always preferable to the one restored from the archive, and no user-curated entries are expected in `references.md`.
  - Risk if false: If users have hand-edited `references.md` with custom entries, those entries will be lost during upgrade. This is accepted per the request scope.

- A4: The interactive prompt for requests archival can safely default to "migrate" (Option 2) when stdin is not a TTY, matching the current default behavior.
  - Risk if false: Users running upgrade in non-interactive mode would lose the ability to choose "archive"; they would need a CLI flag (see Q001).

- A5: `check_version_compatibility()` in `menu.py` returning `True` after a successful upgrade (instead of `False`) is sufficient to cause the normal menu flow to continue without re-launching the process.
  - Risk if false: If stale in-process state from the pre-upgrade `.aib_memory/` contents causes incorrect menu rendering, a process re-exec would be required.

## Plan

### Task 1: Rename `backups` → `archives` in `initialize.py`
**Intent:** Replace all occurrences of the `"backups"` folder name (variable names, string literals, comments, and docstrings) with `"archives"` in `initialize.py`.
**Inputs:** `.aib_brain/tools/initialize.py`
**Outputs:** `.aib_brain/tools/initialize.py` (modified)
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+; no config changes
**Procedure:**
1. Replace `backups_dir = memory_root / "backups"` with `archives_dir = memory_root / "archives"`.
2. Replace all `backup_path` variable references with `archive_path`.
3. Replace all `"backups"` string literals used in folder exclusion logic with `"archives"`.
4. Update the docstring in `_run_upgrade` and all inline comments accordingly.
5. Update the print statements that reference "backup" to say "archive".
**Done Criteria:** `grep -n backups initialize.py` returns zero matches on the updated file.
**Dependencies:** None
**Risk Notes:** Must not accidentally rename the function-parameter variable `backup_path` in other contexts.

### Task 2: Remove `references.md` from upgrade restore list in `initialize.py`
**Intent:** Prevent `references.md` from being restored from the archive during upgrade so it is always freshly seeded.
**Inputs:** `.aib_brain/tools/initialize.py` (after Task 1)
**Outputs:** `.aib_brain/tools/initialize.py` (modified)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. In `_run_upgrade`, locate `restore_files = ["context.md", "instructions.md", "requests_register.md", "references.md"]`.
2. Remove `"references.md"` from the list.
3. Update the docstring and the upgrade summary print to note that `references.md` is freshly seeded.
**Done Criteria:** `restore_files` list in `_run_upgrade` does not contain `"references.md"`; after upgrade, the seeded `references.md` matches brain-template content, not the archived copy.
**Dependencies:** Task 1
**Risk Notes:** None.

### Task 3: Add interactive requests-archival prompt to `initialize.py --upgrade`
**Intent:** Ask the user whether old requests should be migrated or archived before performing the restore step, then act on the answer.
**Inputs:** `.aib_brain/tools/initialize.py` (after Task 2)
**Outputs:** `.aib_brain/tools/initialize.py` (modified)
**External Interfaces:** stdin (interactive TTY); defaults to "migrate" when non-interactive
**Environment & Configuration:** None
**Procedure:**
1. After Step 1 (archive creation) and before Step 6 (restore user-curated files), add a function or inline block that:
   a. Detects whether stdin is a TTY (`sys.stdin.isatty()`).
   b. If TTY: prompt "Migrate old requests to new .aib_memory/? [Y=migrate / N=archive only] (Y): ".
   c. If not TTY: silently default to "migrate".
2. Store the result as a boolean `migrate_requests`.
3. In Step 6 (restore loop) and Step 7 (restore `requests/`), wrap the `requests_register.md` and `requests/` restore operations in `if migrate_requests:` conditions.
4. Update the upgrade summary print to show whether requests were migrated or archived.
**Done Criteria:** Running upgrade with stdin mocked as "N" results in fresh `requests_register.md` and empty `requests/`; running with "Y" or non-TTY preserves requests.
**Dependencies:** Task 2
**Risk Notes:** Must not break the non-interactive test invocation path. See Q001 for the non-TTY fallback strategy.

### Task 4: Auto-restart menu after upgrade in `menu.py`
**Intent:** After a successful upgrade, continue the menu loop automatically instead of printing "Please re-launch" and exiting.
**Inputs:** `.aib_brain/tools/menu.py`
**Outputs:** `.aib_brain/tools/menu.py` (modified)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. In `check_version_compatibility()`, after `result.returncode == 0`, replace `print("\nUpgrade complete. Please re-launch the AIB menu.")` and `return False` with `print("\nUpgrade complete. Continuing to menu...")` and `return True`.
2. Rename all `"backup"` / `"backups"` string references in output messages and inline comments to `"archive"` / `"archives"`.
3. Ensure the upgrade summary still prints the archive path for user confirmation.
**Done Criteria:** After a simulated upgrade in tests, `check_version_compatibility` returns `True` and the menu continues; no "Please re-launch" message is printed.
**Dependencies:** None (independent of Tasks 1–3)
**Risk Notes:** See A5 and Q002 for potential issues with in-process state after upgrade.

### Task 5: Update `tests/test_initialize.py`
**Intent:** Update existing tests to use the renamed `archives/` folder and add new tests for the changed behaviors.
**Inputs:** `tests/test_initialize.py`
**Outputs:** `tests/test_initialize.py` (modified)
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+, pytest
**Procedure:**
1. Replace all `"backups"` path references with `"archives"` in all assertions.
2. Add `test_upgrade_does_not_restore_references_md`: verify that after upgrade, `references.md` differs from the archived copy (or matches fresh seed content).
3. Add `test_upgrade_archive_requests_choice`: mock stdin to return "N"; verify empty `requests/` and fresh `requests_register.md` after upgrade.
4. Add `test_upgrade_migrate_requests_choice`: mock stdin to return "Y"; verify `requests/` and `requests_register.md` are restored.
5. Add `test_upgrade_non_tty_defaults_to_migrate`: mock `sys.stdin.isatty()` to return `False`; verify requests are migrated.
**Done Criteria:** `pytest tests/test_initialize.py -v` passes with all new and updated tests green.
**Dependencies:** Tasks 1, 2, 3
**Risk Notes:** None.

### Task 6: Update `tests/test_menu.py`
**Intent:** Update upgrade-behavior tests to reflect that the menu continues after upgrade rather than exits.
**Inputs:** `tests/test_menu.py`
**Outputs:** `tests/test_menu.py` (modified)
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+, pytest
**Procedure:**
1. Locate any tests that assert `check_version_compatibility` returns `False` after a successful upgrade.
2. Update them to assert `True` (continue) on success.
3. Update any tests that check for the "Please re-launch" message to assert the new "Continuing to menu..." message instead.
**Done Criteria:** `pytest tests/test_menu.py -v` passes.
**Dependencies:** Task 4
**Risk Notes:** None.

### Task 7: Update `context.md`
**Intent:** Reflect the renamed archives folder and changed upgrade behaviors in the product context document.
**Inputs:** `.aib_memory/context.md`
**Outputs:** `.aib_memory/context.md` (modified)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. In FR-013, replace `backups/` with `archives/`; remove `references.md` from the restore list description; note the new requests-archival prompt and auto-restart behavior.
2. In the Component Map, rename `.aib_memory/backups/` to `.aib_memory/archives/` and update its description.
3. In the `initialize.py` tool entry, update the description to reflect the new behaviors.
**Done Criteria:** No `backups` string (as a folder name concept) remains in the updated sections; new behaviors are accurately described.
**Dependencies:** Tasks 1–4
**Risk Notes:** `context.md` is auto-generated by `aib-context.md`; manual edits may be overwritten on next context run. Note this risk in the Internal Review.

### Task 8: Run full test suite and validate success criteria
**Intent:** Verify all success criteria pass and no regressions are introduced.
**Inputs:** All modified files from Tasks 1–7; pytest
**Outputs:** Test run report
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+, `.venv` activated
**Procedure:**
1. Run `pytest tests/ -v` and verify zero failures.
2. Manually verify SC-1 by running a test upgrade and inspecting `references.md` content.
3. Verify SC-2 by running `menu.py` in a workspace with a version mismatch (or by reviewing the updated `check_version_compatibility` logic).
4. Verify SC-3 by grepping for `"backups"` in the modified source files.
5. Verify SC-4 and SC-5 via the new tests added in Task 5.
**Done Criteria:** All tests pass; all SC checks are green; no `"backups"` literal remains in modified source files.
**Dependencies:** Tasks 1–7

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Update FR-013, component map entry `.aib_memory/backups/`, and `initialize.py` tool description to reflect renamed `archives/` folder, removal of `references.md` from restore list, new interactive requests prompt, and auto-restart menu behavior.

## Questions & Decisions

**Q001**: How should the interactive requests-archival prompt behave when stdin is not a TTY (e.g., automated tests or CI)?
- [ ] Option A: Default to "migrate" silently when not a TTY.
- [x] Option B: Default to "migrate" and print a notice that interactive mode is unavailable. *(recommended)*
- [ ] Option C: Accept a `--requests-mode {migrate|archive}` CLI flag to `initialize.py --upgrade` for explicit non-interactive control.
- [ ] Other: ___
> Answer: 

**Q002**: How should auto-restart of the menu work after a successful upgrade — in-process continuation or process re-exec?
- [ ] Option A: Re-exec the current process using `subprocess.run` (clean state, but adds complexity and may require re-parsing arguments).
- [x] Option B: Return `True` from `check_version_compatibility` after upgrade, allowing the existing menu loop to continue in-process. *(recommended)*
- [ ] Other: ___
> Answer: 

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/initialize.py` | Modified | Rename `backups` → `archives`; remove `references.md` from restore list; add interactive requests-archival prompt |
| `.aib_brain/tools/menu.py` | Modified | Auto-restart menu after upgrade; rename `backup` references in messages |
| `tests/test_initialize.py` | Modified | Update `"backups"` assertions to `"archives"`; add new tests for SC-1, SC-4, SC-5 |
| `tests/test_menu.py` | Modified | Update upgrade behavior assertions for auto-restart |
| `.aib_memory/context.md` | Modified | Update FR-013, component map, and tool descriptions |
| `.aib_memory/references.md` | Read-only dependency | Consulted to determine documentation files; not changed by this request |
| `.aib_brain/Concepts.md` | Read-only dependency | Domain reference; "backup" appears only in a generic DSR table row, not as AIB-specific naming — no change needed |
| `.aib_memory/requests/R-20260427-0858-upgrade-aib-memory-structure-on-aib-version-install/request.md` | Read-only dependency | Prior request that introduced the upgrade flow; consulted for historical context |

## Internal Review of Request and Product Docs

- Contradiction: `.aib_memory/context.md` FR-013 — States that `references.md` is among the restored user-curated files; this directly contradicts the request's intent to NOT restore it. The contradiction is intentional and will be resolved by this request.
- Cross-ref issue: `.aib_memory/context.md` component map — Entry for `.aib_memory/backups/` will be stale after rename; must be updated in Task 7.
- Missing info: `tests/test_initialize.py` — No existing test asserts that `references.md` is NOT restored from the archive (only `instructions.md` and `requests_register.md` are checked in `test_upgrade_restores_curated_files`). This gap is addressed by the new test in Task 5.
- Ambiguity: `menu.py` `check_version_compatibility` — The function currently returns `False` to signal "exit" and `True` to signal "continue". After Task 4, it would return `True` for both "continue normally" and "continue after upgrade", which is semantically correct but removes the ability for the caller to distinguish the two cases. Evaluate whether the caller's logic needs updating.
- OK: `initialize.py` `_run_upgrade` docstring — Accurately describes current behavior; will need updating alongside code changes.
- OK: `tests/test_initialize.py` `TestUpgrade` class — Covers six upgrade scenarios; all will be affected by the `backups` → `archives` rename but logic is otherwise sound.
