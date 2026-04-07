# Implementation Log

Append-only entries. Add a new section for every execution update.

## Entry Template

### [YYYY-MM-DD HH:mi] Iteration [ID]

#### Implemented changes

#### Technical notes

#### Verification steps

#### Evidences for done

#### End result summary

#### Guidance for human how to verify

### [2026-03-22 00:40] Iteration 02

#### Implemented changes

- Implemented automatic `.aib_memory/` initialization on menu launch when the folder is missing.
- Removed the “Initialize AIB memory” action from the interactive menu.
- Made the menu dynamic (state-aware) for request/iteration lifecycle actions.
- Removed the two instruction blocks from the menu UI and added them to `.aib_brain/README.md`.
- Added concise display of active request and active iteration in the menu header.

#### Technical notes

- Auto-init trigger is directory existence only: if `.aib_memory/` exists, initialization is skipped to avoid any mutation of existing state.
- Dynamic visibility is implemented by filtering actions based on active request/iteration state derived from `.aib_memory/requests_register.md` and the active request’s `iterations.md`.
- Fixed `SyntaxWarning: invalid escape sequence` in the ASCII banner by using raw string literals.

#### Verification steps

- unit: `python -m unittest discover .aib_memory/requests/R-20260321-2314-issue-23 -p "test_*.py"` — pass
- build/syntax: `python -m compileall .aib_brain/tools` — pass

#### Evidences for done

- Updated menu implementation: `.aib_brain/tools/menu.py`
- Updated menu config: `.aib_brain/tools/menu_config.json`
- Updated menu docs: `.aib_brain/README.md`
- Unit tests: `.aib_memory/requests/R-20260321-2314-issue-23/test_menu_dynamic.py`

#### End result summary

Done. Launching the menu now auto-initializes `.aib_memory/` only when missing, the menu shows active request/iteration concisely, hides invalid lifecycle actions based on state, and no longer shows the instruction blocks.

Follow-ups:
- None required for the defined scope.

#### Guidance for human how to verify

- Fresh workspace (no `.aib_memory/`): run `.aib_brain\run.bat` and confirm the menu opens and `.aib_memory/` is created.
- Existing workspace (has `.aib_memory/`): run `.aib_brain\run.bat` and confirm `.aib_memory/` contents are not modified.
- Verify dynamic actions:
	- No active request: shows “Create request”; hides “Close request”, “Create iteration”, “Close iteration”.
	- Active request + no active iteration: shows “Close request” + “Create iteration”; hides “Create request” + “Close iteration”.
	- Active request + active iteration: shows “Close request” + “Close iteration”; hides “Create request” + “Create iteration”.
