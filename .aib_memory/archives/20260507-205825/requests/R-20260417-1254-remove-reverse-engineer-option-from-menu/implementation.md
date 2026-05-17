Files taken into consideration:
- .aib_memory/requests_register.md
- .aib_memory/references.md
- .aib_memory/requests/R-20260417-1254-remove-reverse-engineer-option-from-menu/request.md

## Implementation Log

### Entry 2026-04-17 13:15

#### Scope
Remove the reverse-engineer option from the interactive AIB menu by adding `reverse-engineer.py` to `EXCLUDE_SCRIPTS` in `menu.py`. Delete the conflicting regression test `test_reverse_engineer_present` from `tests/test_menu.py`, which asserted the opposite behavior. The `reverse-engineer.py` script is retained as an internal helper tool used by `aib-context.md`.

#### Changes
- Added `"reverse-engineer.py"` to the `EXCLUDE_SCRIPTS` set in `.aib_brain/tools/menu.py`.
- Deleted the `test_reverse_engineer_present` method from `tests/test_menu.py` (asserted old behavior: script visible in menu).

#### Tests
- Unit — `tests/test_menu.py::TestBuildScriptActions::test_excluded_scripts_absent` — verified `reverse-engineer.py` is now absent from discovered menu actions — PASS.
- Unit — `tests/test_reverse_engineer.py` (all 4 tests) — verified `reverse-engineer.py` script logic still functional as internal helper — PASS.
- Full suite — `pytest tests/ -v` — 73 tests collected, 73 passed, 0 failures — PASS.

#### Outcome
Implementation successful. The AIB interactive menu no longer displays a "Reverse Engineer" option. The script itself remains intact as an optional internal helper for `aib-context.md`. All tests pass with zero failures.

#### Evidence
```
============================= test session starts =============================
collected 73 items
...
============================= 73 passed in 2.56s ==============================
```

#### Notes (Optional)
Assumption A1 confirmed: `reverse-engineer.py` is retained as an internal helper. Assumption A2 confirmed: `test_reverse_engineer_present` was deleted (not negated) as specified in the plan.
