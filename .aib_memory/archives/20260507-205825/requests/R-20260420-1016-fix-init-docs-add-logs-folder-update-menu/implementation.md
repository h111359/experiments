Files considered during implementation:
- `.aib_memory/requests/R-20260420-1016-fix-init-docs-add-logs-folder-update-menu/request.md`
- `.aib_memory/references.md`
- `.aib_brain/Concepts.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/implementation-convention.md`

## Implementation Log

### Entry 2026-04-20 12:10
#### Scope
Fix four bugs/gaps in the AIB workspace: (1) remove docs folder creation from initialize.py, (2) add logs folder creation to initialize.py, (3) add conditional close-request menu action in menu.py, (4) remove label prefixes from prompt-reference block in menu.py. Update tests accordingly.

#### Changes
- Modified `.aib_brain/tools/initialize.py`: removed `ensure_doc_seed_files` from imports; removed `(memory_root / "docs").mkdir(...)` line; added `(memory_root / "logs").mkdir(parents=True, exist_ok=True)` after the `requests/` directory creation; replaced `references_md, requirements = seed_references_from_product_doc(workspace)` + `ensure_doc_seed_files(workspace, requirements)` with `references_md, _ = seed_references_from_product_doc(workspace)`; removed `requirements = None` in the skip branch and the conditional `if requirements is not None:` print.
- Modified `.aib_brain/tools/menu.py`: added `_CLOSE_REQUEST_ACTION` module-level constant defining the close-request menu entry; updated `filter_visible_actions` to append a copy of `_CLOSE_REQUEST_ACTION` (with sequential id) when `state.has_active_request` is True; removed "Analysis : ", "Implement: ", "Context  : " label prefixes from both `render_menu` inline block and `print_prompt_reference` — lines now start with "Execute `...`" directly.
- Modified `tests/test_initialize.py`: added `test_does_not_create_docs_folder` asserting `.aib_memory/docs/` does not exist after init; added `test_creates_logs_folder` asserting `.aib_memory/logs/` is a directory after init; added `test_creates_logs_folder_idempotent` asserting second run does not error and logs folder still exists.
- Modified `tests/test_menu.py`: replaced `TestFilterVisibleActions` tests to reflect new conditional visibility: `test_returns_all_actions_when_no_active_request`, `test_close_request_not_visible_without_active_request`, `test_close_request_visible_with_active_request`, `test_create_request_never_visible`, `test_active_request_adds_one_action`.

#### Tests
- unit: `tests/test_initialize.py::TestInitialize::test_does_not_create_docs_folder` — pass
- unit: `tests/test_initialize.py::TestInitialize::test_creates_logs_folder` — pass
- unit: `tests/test_initialize.py::TestInitialize::test_creates_logs_folder_idempotent` — pass
- unit: `tests/test_menu.py::TestFilterVisibleActions::test_returns_all_actions_when_no_active_request` — pass
- unit: `tests/test_menu.py::TestFilterVisibleActions::test_close_request_not_visible_without_active_request` — pass
- unit: `tests/test_menu.py::TestFilterVisibleActions::test_close_request_visible_with_active_request` — pass
- unit: `tests/test_menu.py::TestFilterVisibleActions::test_create_request_never_visible` — pass
- unit: `tests/test_menu.py::TestFilterVisibleActions::test_active_request_adds_one_action` — pass
- integration: full pytest suite (78 tests) — pass

#### Outcome
All four scope items implemented successfully. The full test suite passes with 78 tests and 0 failures or skips. Initialization no longer creates `.aib_memory/docs/` and now creates `.aib_memory/logs/` on a fresh workspace. The menu conditionally shows "Close current request" only when an active request is present, and prompt-reference lines are displayed without redundant label prefixes.

#### Evidence
```
============================= 78 passed in 3.08s ==============================
```

#### Notes (Optional)
`ensure_doc_seed_files` remains in `common.py` as per out-of-scope constraint; only the call site in `initialize.py` was removed.
