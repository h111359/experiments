# Implementation Log

Append-only entries. Add a new section for every execution update.

Files consulted:
- `.aib_memory/references.md`
- `.aib_memory/context.md` (REF-0001)
- `.aib_brain/Concepts.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/implementation-convention.md`

## Implementation Log

### Entry 2026-04-16 10:30
#### Scope
Redirect AIB action execution logs from the workspace root `logs/` directory to `.aib_memory/logs/`. Updated `menu.py` `_make_log_path()`, `.gitignore` exclusion pattern, `tests/test_menu.py` assertions, and regenerated `.aib_memory/context.md`.

#### Changes
- Updated `_make_log_path()` in `.aib_brain/tools/menu.py`: changed `log_dir` from `(workspace or Path.cwd()) / "logs"` to `(workspace or Path.cwd()) / ".aib_memory" / "logs"`; updated docstring to reference `.aib_memory/logs/`.
- Updated `.gitignore`: replaced `logs/aib-action-*.log` with `.aib_memory/logs/aib-action-*.log`.
- Updated `tests/test_menu.py` `TestMakeLogPath.test_creates_log_in_logs_dir`: changed expected parent from `tmp_path / "logs"` to `tmp_path / ".aib_memory" / "logs"`.
- Updated `tests/test_menu.py` `TestMakeLogPath.test_creates_logs_directory`: changed asserted directory from `tmp_path / "logs"` to `tmp_path / ".aib_memory" / "logs"`.
- Regenerated `.aib_memory/context.md`: updated FR-008, Component Map Logs row, Observability section, `.gitignore` row in Repository Structure, Data Storage section, and Workspace File Inventory (removed gitignored action log entries and fixed duplicate inventory block).

#### Tests
- unit: `pytest tests/test_menu.py::TestMakeLogPath -v` — 2/2 pass
- unit: `pytest tests/test_menu.py -v` — 37/37 pass
- integration: `pytest` (full suite) — 69/69 pass
- manual: `.gitignore` inspection — `.aib_memory/logs/aib-action-*.log` present; old `logs/aib-action-*.log` absent

#### Outcome
All tasks completed successfully with zero test failures. Action execution logs now target `.aib_memory/logs/`. Release version logs remain unaffected in `logs/`. `context.md` reflects the new log location.

#### Evidence
- `.aib_brain/tools/menu.py` `_make_log_path()` — `log_dir` uses `.aib_memory/logs/`
- `.gitignore` line 7 — `.aib_memory/logs/aib-action-*.log`
- `tests/test_menu.py` `TestMakeLogPath` — assertions reference `.aib_memory/logs`
- `.aib_memory/context.md` — FR-008 and Observability reference `.aib_memory/logs/`

```
============================= 69 passed in 2.64s ==============================
```
