Files read during this implementation run: `.aib_memory/request-R-20260515-1311.md`, `.aib_memory/context.md`, `.aib_memory/instructions.md`, `.aib_brain/tools/initialize.py`, `.aib_brain/tools/common.py`, `.aib_brain/tools/menu.py`, `tests/conftest.py`, `tests/test_initialize.py`, `tests/test_lifecycle_e2e.py`, `tests/test_tools_common.py`, `.aib_brain/conventions/coding-general-convention.md`, `.aib_brain/conventions/coding-python-convention.md`, `.aib_brain/conventions/context-convention.md`, `.aib_brain/conventions/implementation-convention.md`.

## Implementation Log

### Entry 2026-05-15 13:30

#### Scope

Remove the `.aib_brain/templates/` folder and its single file (`requests_register-template.md`) from the AIB framework. Replace the `load_template`-based seeding in `initialize.py` with a hardcoded inline string. Remove the `load_template` helper from `common.py`. Update all test fixtures and test classes that depended on the templates folder. Update `menu.py` user-visible upgrade text and `context.md` component references to eliminate all mentions of the deleted folder.

#### Changes

- Replaced `load_template(brain_dir, "requests_register-template.md")` call in `.aib_brain/tools/initialize.py` with a hardcoded inline string constant producing the same register heading and empty Markdown table.
- Removed `load_template` from the `from common import (...)` block in `.aib_brain/tools/initialize.py`.
- Deleted `load_template` function from `.aib_brain/tools/common.py`.
- Deleted `.aib_brain/templates/requests_register-template.md` and the now-empty `.aib_brain/templates/` directory.
- Removed `TEMPLATES_DIR` constant, `import shutil`, `.aib_brain/templates` mkdir call, and template-copying loop from `tests/conftest.py`; `_seed_workspace` now creates `.aib_brain/` without a `templates/` subdirectory.
- Removed `TEMPLATES_DIR` constant, `import shutil`, and template-copying logic from `tests/test_initialize.py`; `_make_brain_only_workspace` now creates only `.aib_brain/`.
- Removed `TEMPLATES_DIR` constant, `import shutil`, and template-copying logic from `tests/test_lifecycle_e2e.py`; `_make_brain_only_workspace` now creates only `.aib_brain/`.
- Removed `load_template` from the import block and deleted `TestLoadTemplate` class from `tests/test_tools_common.py`.
- Updated `.aib_brain/tools/menu.py` line 792: changed "brain templates" to "brain assets" in the upgrade prompt text.
- Removed "AIB Templates" component bullet from `context.md` Component Map section (line 123).
- Removed `**Templates** (.aib_brain/templates/)` block from `context.md` Module Breakdown section.
- Removed `.aib_brain/templates/` and `.aib_brain/templates/requests_register-template.md` entries from `context.md` Workspace File Inventory section.
- Updated "brain templates" phrase to "brain assets" in `context.md` FR-013 description.
- Updated three `.aib_brain/` asset-listing phrases in `context.md` to remove "templates" from the enumerated asset types.
- Appended 12 curated change bullets to `logs/next_version_changes.md`.

#### Tests

- Unit/integration: ran `pytest tests/ -v` — 284 passed, 6 subtests passed, 0 failures, 0 errors in 9.58 s.

#### Outcome

All tasks completed successfully with zero test failures. The `.aib_brain/templates/` folder no longer exists in the repository. `load_template` is absent from `common.py` and all tool scripts. `initialize.py` seeds `requests_register.md` from a hardcoded inline string, preserving idempotent behaviour. All test fixtures no longer require or reference the templates folder.

#### Evidence

```
pytest tests/ -v
284 passed, 6 subtests passed in 9.58s
```

- Grep for `load_template` across workspace: zero matches after removal.
- Grep for `.aib_brain/templates` in `context.md`: zero matches after cleanup.
