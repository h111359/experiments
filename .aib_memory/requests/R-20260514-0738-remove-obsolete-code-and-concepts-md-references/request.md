## Goal

Remove `_DEFAULT_REFS_TABLE` and the associated `TestUpgradeLegacyReferencesWarning` test class from `tests/test_initialize.py`, delete the obsolete `.aib_brain/Concepts.md` file and all references to it, and perform a holistic review of the tool scripts and tests to identify and remove all remaining obsolete or unused code.

## Background

Over several release iterations the AIB framework removed the `references.md` register, the `Concepts.md` domain file, and the iterations sub-workflow. The production scripts and tests that once supported these features were never fully cleaned up. Dead constants (`ITER_ID_PATTERN`, `COMPLETED`), a dead argument (`--iteration-id`), a dead iterations auto-close block in `close-request.py`, dead test fixtures (`_DEFAULT_REFS_TABLE`, `ITER_HEADER`, `IT_HEADER`, `_iterations_with_row`), and dead test classes (`TestUpgradeLegacyReferencesWarning`, `TestCloseRequestAutoClose`) remain in the codebase. Removing them reduces cognitive overhead, eliminates confusion for contributors, and ensures that the test suite covers only live behaviour.

## Scope

- Remove `_DEFAULT_REFS_TABLE` constant and the `TestUpgradeLegacyReferencesWarning` class (three test methods) from `tests/test_initialize.py`.

- Delete `.aib_brain/Concepts.md`.

- Remove `.aib_brain/Concepts.md` from the `_LEGACY_DEFAULT_REFERENCE_PATHS` frozenset in `.aib_brain/tools/initialize.py`.

- Remove dead code from `.aib_brain/tools/common.py`: `ITER_ID_PATTERN` constant, `COMPLETED` constant, and the `--iteration-id` argument from `parse_args`.

- Remove the iterations auto-close block (and the `COMPLETED` import) from `.aib_brain/tools/close-request.py`.

- Remove the `iteration_id` guard branch from `collect_parameters` in `.aib_brain/tools/menu.py`.

- Remove dead iteration-related code from `tests/test_close_request.py`: `ITER_HEADER` constant, `iterations.md` creation in the `_make_request` helper, `_add_active_iteration` helper, and `test_auto_closes_active_iteration` test method.

- Remove dead iteration-related code from `tests/test_tools_common.py`: `IT_HEADER` constant, `_make_iterations_table` helper, and `TestCloseRequestAutoClose` class.

- Remove the unused `_iterations_with_row` helper from `tests/test_menu.py`.

## Out of scope

- Changes to `test_lifecycle_e2e.py` assertions about `iterations.md` not being created (these remain valid regression guards).
- Any changes to `create-request.py`, `finalize-input.py`, `move-request-artifacts.py`, or convention/prompt files.
- Functional behaviour changes to `_warn_about_legacy_references` in `initialize.py` (the function is kept for backward compatibility; only the Concepts.md path is removed from its default-paths set).
- Refactoring or adding new features.

## Constraints

- All existing tests must pass after changes (excluding the tests that are themselves being removed as obsolete).
- Python version compatibility: Python 3.10+, standard library only.
- No new imports or helper functions introduced.
- Removals must be surgical: only dead/obsolete code is deleted; surrounding live code is preserved intact.

## Success criteria

- `_DEFAULT_REFS_TABLE` does not appear anywhere in `tests/test_initialize.py`.
- `TestUpgradeLegacyReferencesWarning` class is absent from `tests/test_initialize.py`.
- `.aib_brain/Concepts.md` does not exist.
- `".aib_brain/Concepts.md"` does not appear in `_LEGACY_DEFAULT_REFERENCE_PATHS` in `initialize.py`.
- `ITER_ID_PATTERN` and `COMPLETED` do not appear in `common.py`.
- `--iteration-id` argument is absent from `parse_args` in `common.py`.
- Iterations auto-close block is absent from `close-request.py`.
- `iteration_id` guard branch is absent from `collect_parameters` in `menu.py`.
- Iteration-related dead fixtures and test classes are absent from `test_close_request.py`, `test_tools_common.py`, and `test_menu.py`.
- `pytest` exits 0 on the full test suite after all changes are applied.

## Assumptions

- A1: The `_warn_about_legacy_references` function in `initialize.py` retains value for developers upgrading from workspaces older than v1.2.12 that may still have a `references.md`; it is kept but its default-paths set is updated.
  - Risk if false: Slightly more code than strictly necessary is retained; acceptable trade-off.

- A2: No active request folder in the wild currently contains an `iterations.md` file that the `close-request.py` iterations block would process; removing the block is safe.
  - Risk if false: An upgrade from a very old workspace version could leave active iterations unhandled; negligible risk given the age of the removal.

- A3: `ITER_ID_PATTERN` is truly unused: the grep across all files confirms it appears only in its definition in `common.py`.
  - Risk if false: None; the grep is authoritative.

- A4: `_iterations_with_row` in `test_menu.py` is never called; confirmed by grep showing only the definition.
  - Risk if false: None; confirmed by grep.

## Plan

### Task 1: Remove `_DEFAULT_REFS_TABLE` and `TestUpgradeLegacyReferencesWarning` from `tests/test_initialize.py`

#### Intent
Delete the legacy reference-table fixture and its three associated test methods that test the now-removed `references.md` warning.

#### Outputs
`tests/test_initialize.py` — section from line ~244 to line ~293 removed.

#### Procedure
Open `tests/test_initialize.py` and delete the block starting with the comment `# Tests for the upgrade-time legacy references.md warning (SC-9).`, the `_DEFAULT_REFS_TABLE` constant, and the entire `TestUpgradeLegacyReferencesWarning` class (three test methods: `test_upgrade_warns_when_legacy_references_has_extra_rows`, `test_upgrade_silent_when_only_default_references_present`, `test_upgrade_handles_unparseable_legacy_references`).

#### Done criteria
- `_DEFAULT_REFS_TABLE` does not appear in `tests/test_initialize.py`.
- `TestUpgradeLegacyReferencesWarning` class does not appear in `tests/test_initialize.py`.
- File is syntactically valid Python.

#### Dependencies
None.

#### Risk notes
None; these are pure test fixtures and classes with no callers outside the class itself.

---

### Task 2: Delete `.aib_brain/Concepts.md`

#### Intent
Remove the obsolete Concepts.md file that the file itself marks as "obsolete and will be removed".

#### Outputs
`.aib_brain/Concepts.md` deleted from the filesystem.

#### Procedure
Delete `.aib_brain/Concepts.md`.

#### Done criteria
`.aib_brain/Concepts.md` does not exist.

#### Dependencies
None.

#### Risk notes
Verify no prompt or convention file reads `Concepts.md` at runtime before deleting.

---

### Task 3: Update `_LEGACY_DEFAULT_REFERENCE_PATHS` in `initialize.py`

#### Intent
Remove the `".aib_brain/Concepts.md"` entry from the legacy-reference default paths set now that the file is deleted.

#### Outputs
`.aib_brain/tools/initialize.py` — `_LEGACY_DEFAULT_REFERENCE_PATHS` frozenset updated.

#### Procedure
In `.aib_brain/tools/initialize.py`, locate the `_LEGACY_DEFAULT_REFERENCE_PATHS` frozenset and remove `".aib_brain/Concepts.md"` from it, leaving only `".aib_memory/context.md"`.

#### Done criteria
`".aib_brain/Concepts.md"` does not appear in `_LEGACY_DEFAULT_REFERENCE_PATHS`.

#### Dependencies
Task 2 (Concepts.md deleted).

#### Risk notes
`_warn_about_legacy_references` continues to function; it will only no longer exempt `Concepts.md` paths (which are now correctly treated as non-default if encountered in an old archive).

---

### Task 4: Remove dead code from `common.py`

#### Intent
Delete three dead items: the `ITER_ID_PATTERN` regex constant, the `COMPLETED` state constant, and the `--iteration-id` argument from `parse_args`.

#### Outputs
`.aib_brain/tools/common.py` — three dead items removed.

#### Procedure
In `.aib_brain/tools/common.py`:

Remove the line `ITER_ID_PATTERN = re.compile(r"^\d{2}$")`.

Remove the line `COMPLETED = "Completed"`.

Remove the `parser.add_argument("--iteration-id", ...)` line from `parse_args`.

Verify that `re` is still used elsewhere in `common.py` after removing `ITER_ID_PATTERN` (it is — `REQ_ID_PATTERN` and `slugify` use it).

#### Done criteria
- `ITER_ID_PATTERN` absent from `common.py`.
- `COMPLETED` absent from `common.py`.
- `--iteration-id` absent from `common.py`.
- File is syntactically valid Python.

#### Dependencies
Task 5 (which also removes the only importer of `COMPLETED`).

#### Risk notes
Must confirm no other script imports `ITER_ID_PATTERN` or `COMPLETED` from `common.py` before deletion (grep confirms none).

---

### Task 5: Remove iterations auto-close block from `close-request.py`

#### Intent
Delete the dead code that inspects and auto-closes `iterations.md`, along with its `COMPLETED` import.

#### Outputs
`.aib_brain/tools/close-request.py` — iterations block and `COMPLETED` import removed.

#### Procedure
In `.aib_brain/tools/close-request.py`:

Remove `COMPLETED` from the `from common import (...)` block.

Delete the iterations auto-close block: the lines from `iterations_path = workspace / folder_rel / "iterations.md"` through the closing `for r in active_iterations: print(...)` statement, including the `if iterations_path.exists():` guard.

#### Done criteria
- `COMPLETED` not imported in `close-request.py`.
- Iterations block absent from `close-request.py`.
- File is syntactically valid Python and passes existing non-iteration tests.

#### Dependencies
None (safe to apply before Task 4).

#### Risk notes
The `folder_rel` variable used just before the iterations block remains in use for the move-artifacts call; verify that removing only the iterations block leaves `folder_rel` still used.

---

### Task 6: Remove `iteration_id` guard from `menu.py`

#### Intent
Delete the dead `iteration_id` guard branch in `collect_parameters` that was added for action parameters that no longer exist.

#### Outputs
`.aib_brain/tools/menu.py` — the `if name in {"request_id", "iteration_id"}` branch simplified.

#### Procedure
In `.aib_brain/tools/menu.py`, locate the `if name in {"request_id", "iteration_id"} and not required:` guard in `collect_parameters`. Change `{"request_id", "iteration_id"}` to `{"request_id"}` (removing only the `"iteration_id"` member) so that `request_id` still receives its special skip treatment.

#### Done criteria
`"iteration_id"` not present in the guard condition.

#### Dependencies
None.

#### Risk notes
`request_id` handling must remain unchanged; only the `iteration_id` name is removed from the set.

---

### Task 7: Remove iterations dead code from `tests/test_close_request.py`

#### Intent
Delete the `ITER_HEADER` constant, `iterations.md` creation in `_make_request`, the `_add_active_iteration` helper, and the `test_auto_closes_active_iteration` test method.

#### Outputs
`tests/test_close_request.py` — dead iteration-related code removed.

#### Procedure
In `tests/test_close_request.py`:

Remove the `ITER_HEADER` constant definition.

Remove the `write_text(folder / "iterations.md", ...)` call from the `_make_request` helper (keep all other file writes in that helper).

Remove the entire `_add_active_iteration` function.

Remove the `test_auto_closes_active_iteration` test method from `TestCloseRequest`.

#### Done criteria
- `ITER_HEADER` absent.
- `iterations.md` write absent from `_make_request`.
- `_add_active_iteration` absent.
- `test_auto_closes_active_iteration` absent.
- File is syntactically valid Python.

#### Dependencies
Task 5 (iterations block removed from the production code).

#### Risk notes
`format_markdown_table` import may no longer be needed in `test_close_request.py` if `ITER_HEADER` removal means no more table construction there; verify and remove the import if unused.

---

### Task 8: Remove iterations dead code from `tests/test_tools_common.py`

#### Intent
Delete `IT_HEADER`, `_make_iterations_table`, and `TestCloseRequestAutoClose` — all of which test the removed iterations auto-close behaviour.

#### Outputs
`tests/test_tools_common.py` — three dead items removed.

#### Procedure
In `tests/test_tools_common.py`:

Remove the `IT_HEADER` constant.

Remove the `_make_iterations_table` helper function.

Remove the entire `TestCloseRequestAutoClose` class.

#### Done criteria
- `IT_HEADER` absent.
- `_make_iterations_table` absent.
- `TestCloseRequestAutoClose` absent.
- File is syntactically valid Python.

#### Dependencies
Task 5.

#### Risk notes
The `subprocess` import in `test_tools_common.py` is used by `TestCloseRequestAutoClose`; verify it is not used elsewhere in that file and remove if so.

---

### Task 9: Remove `_iterations_with_row` from `tests/test_menu.py`

#### Intent
Delete the helper function that is defined but never called.

#### Outputs
`tests/test_menu.py` — `_iterations_with_row` function removed.

#### Procedure
In `tests/test_menu.py`, remove the `_iterations_with_row` function definition (approximately lines 53–60).

#### Done criteria
`_iterations_with_row` absent from `tests/test_menu.py`.

#### Dependencies
None.

#### Risk notes
None; confirmed never called.

---

### Task 10: Run full test suite and verify

#### Intent
Confirm all surviving tests pass after the dead-code removals.

#### Outputs
Terminal output from `pytest` with exit code 0.

#### Procedure
Run `pytest tests/ -v` from the workspace root `c:\Hristo\projects\AI_Builder`.

Inspect output for failures unrelated to the removed tests and address any regressions.

#### Done criteria
`pytest` exits 0; no failures in tests that were not explicitly removed.

#### Dependencies
Tasks 1–9.

#### Risk notes
If `subprocess` import in `test_tools_common.py` is removed and it is actually needed elsewhere, a NameError will surface here; resolve by restoring only the import.

---

### Task 11: Update `.aib_memory/context.md`

#### Intent
Reflect the removal of `Concepts.md`, the iterations sub-workflow code, and the legacy references code in the product context document.

#### Outputs
`.aib_memory/context.md` — updated to remove mentions of `Concepts.md` and iterations where they appear as active features.

#### Procedure
Read `.aib_memory/context.md` and identify any references to `.aib_brain/Concepts.md` as an active file or component, and any references to iterations as an active sub-workflow.

In `.aib_memory/context.md`, remove or update entries that treat `Concepts.md` as a current framework asset.

Verify there are no misleading entries suggesting `iterations.md` is a current artifact produced by any tool script.

Acceptance test: grep `context.md` for `Concepts.md` — zero matches in the current component map.

#### Dependencies
Tasks 1–9.

#### Risk notes
`context.md` is auto-generated by `aib-context.md`; manual edits will be overwritten on the next context run. Add a note in the context run's next execution to exclude `Concepts.md` from its component inventory.

## Documentation

- `.aib_memory/context.md` (ref_id: N/A) — Remove references to `.aib_brain/Concepts.md` as an active component; remove any references to `iterations.md` as a currently produced artifact.

## Decisions
