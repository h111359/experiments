Implementation record for request R-20260514-0738 — Remove obsolete code and Concepts.md references.

Files taken into consideration:
- `.aib_memory/request-R-20260514-0738.md`
- `.aib_memory/context.md`
- `.aib_memory/instructions.md`
- `.aib_brain/tools/common.py`
- `.aib_brain/tools/initialize.py`
- `.aib_brain/tools/close-request.py`
- `.aib_brain/tools/menu.py`
- `.aib_brain/Concepts.md`
- `tests/test_initialize.py`
- `tests/test_close_request.py`
- `tests/test_tools_common.py`
- `tests/test_menu.py`

## Implementation Log

### Entry 2026-05-14 07:55

#### Scope
Removed all dead and obsolete code identified in the analysis: the `_DEFAULT_REFS_TABLE` fixture and `TestUpgradeLegacyReferencesWarning` test class from `tests/test_initialize.py`; the obsolete `.aib_brain/Concepts.md` file; the `".aib_brain/Concepts.md"` entry from `_LEGACY_DEFAULT_REFERENCE_PATHS` in `initialize.py`; the `ITER_ID_PATTERN` and `COMPLETED` constants and the `--iteration-id` argument from `common.py`; the iterations auto-close block and its `COMPLETED` import from `close-request.py`; the `"iteration_id"` guard from `collect_parameters` in `menu.py`; dead iteration-related fixtures, helpers, and test classes from `test_close_request.py`, `test_tools_common.py`, and `test_menu.py`.

#### Changes
- Removed `_DEFAULT_REFS_TABLE` constant and `TestUpgradeLegacyReferencesWarning` class (3 test methods) from `tests/test_initialize.py`.
- Deleted `.aib_brain/Concepts.md`.
- Removed `".aib_brain/Concepts.md"` from `_LEGACY_DEFAULT_REFERENCE_PATHS` frozenset in `.aib_brain/tools/initialize.py`, leaving only `".aib_memory/context.md"`.
- Removed `ITER_ID_PATTERN = re.compile(r"^\d{2}$")` from `.aib_brain/tools/common.py`.
- Removed `COMPLETED = "Completed"` from `.aib_brain/tools/common.py`.
- Removed `--iteration-id` argument from `parse_args` in `.aib_brain/tools/common.py`.
- Removed `COMPLETED` from imports and removed iterations auto-close block (15 lines) from `.aib_brain/tools/close-request.py`.
- Changed `{"request_id", "iteration_id"}` to `{"request_id"}` in `collect_parameters` guard in `.aib_brain/tools/menu.py`.
- Removed `ITER_HEADER` constant, `iterations.md` write in `_make_request`, `_add_active_iteration` helper, and `test_auto_closes_active_iteration` test method from `tests/test_close_request.py`.
- Removed `import subprocess`, `IT_HEADER` constant, `_make_iterations_table` helper, and `TestCloseRequestAutoClose` class from `tests/test_tools_common.py`.
- Removed `_iterations_with_row` helper from `tests/test_menu.py`.
- Appended curated change bullets to `logs/next_version_changes.md`.

#### Tests
- Integration: full `pytest tests/` run — 268 tests passed, 0 failed, 0 errors (exit code 0).

#### Outcome
All dead-code removals applied successfully. The test suite confirms no regressions: 268 tests pass. The codebase no longer contains references to the removed `references.md` register, the obsolete `Concepts.md` file, or the iterations sub-workflow. The `_warn_about_legacy_references` function is retained in `initialize.py` for backward-compatibility upgrade handling but its default-paths set now correctly excludes the deleted file.

#### Evidence
```
268 passed in 11.49s
```

#### Notes (Optional)
`context.md` required no changes — it contained no references to `Concepts.md` or iteration internals at the time of this implementation run.
