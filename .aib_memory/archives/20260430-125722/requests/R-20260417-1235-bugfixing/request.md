## Goal

Fix two bugs introduced or left unresolved by R-20260417-0903:

1. Running `.aib_brain\run.bat` in an empty repo raises `ERROR: No actions available` because `reverse-engineer.py` is incorrectly listed in `EXCLUDE_SCRIPTS` in `menu.py`, leaving no discoverable actions.

2. `.aib_memory/input.md` is absent in the current workspace because `initialize.py` was not re-run after R-20260417-0903 added `input.md` seeding, and the auto-init guard only fires when `.aib_memory/` is completely missing.

## Background

R-20260417-0903 made several improvements including removing lifecycle scripts from the CLI menu and adding `input.md` seeding to `initialize.py`. After that implementation, two residual issues remain.

Bug 1: `reverse-engineer.py` was already in `EXCLUDE_SCRIPTS` before R-20260417-0903. The request scope explicitly required "retain interactive functionality for remaining non-lifecycle scripts (e.g., `reverse-engineer.py`)", but this was not enforced — `reverse-engineer.py` was left in the exclusion set. Since it is the only non-excluded `.py` file in `tools/`, `discover_tool_scripts()` returns an empty list and the menu raises a fatal error.

Bug 2: `initialize.py` now seeds `input.md`, but only when `input.md` does not exist. The `ensure_memory_initialized_if_missing()` guard in `menu.py` only triggers when `.aib_memory/` itself is absent. On the current workspace — which already had `.aib_memory/` — `initialize.py` was never re-run, so `input.md` was never created.

## Scope

- Remove `"reverse-engineer.py"` from `EXCLUDE_SCRIPTS` in `.aib_brain/tools/menu.py` so that `reverse-engineer.py` appears as a discoverable action in the menu.

- Create `.aib_memory/input.md` in the current workspace with the seed template by running `python .aib_brain/tools/initialize.py --workspace .`.

- Add a positive-presence regression test for `reverse-engineer.py` in `tests/test_menu.py` to prevent this exclusion bug from recurring silently.

## Out of scope

- No other changes to `menu.py` logic, rendering, or keyboard handling.

- No changes to `initialize.py` behavior beyond what already exists.

- No changes to any other tool script, convention, or prompt.

- No architectural changes to the auto-init or upgrade reconciliation mechanism.

## Constraints

- All tool scripts must remain Python 3.10+ standard library only; no third-party packages.

- The framework must remain model-agnostic and vendor-agnostic.

- The fix must not break any of the existing 73 passing tests.

- `.aib_brain/` must not be modified by tool scripts (the EXCLUDE_SCRIPTS change is a direct file edit, not a script action).

## Success criteria

- Running `.aib_brain/run.bat` (or `run.sh`) in a fresh empty directory with only `.aib_brain/` present shows at least one action in the interactive menu without any error.

- `reverse-engineer.py` appears as a named action in the menu.

- `.aib_memory/input.md` exists in the current workspace with the canonical seed template (sections `## Active request`, `## Options`, `## Input`).

- All existing 73 tests pass after applying the changes.

- A new test in `tests/test_menu.py` asserts that `reverse-engineer.py` is present in the list of actions returned by `build_script_actions()`.

## Assumptions

- A1: `reverse-engineer.py` is the only `.py` file in `.aib_brain/tools/` that should appear in the interactive menu (all others are correctly excluded by `EXCLUDE_SCRIPTS`).
  - Risk if false: Additional scripts would need to be removed from EXCLUDE_SCRIPTS or explicitly added; scope would expand.

- A2: Re-running `initialize.py --workspace .` on the current workspace will not overwrite or corrupt any existing `.aib_memory/` files.
  - Risk if false: Data loss in `requests_register.md`, `references.md`, or `context.md`; however, code inspection of `initialize.py` confirms all writes are guarded by existence checks.

- A3: No other `.aib_memory/` files are missing from the current workspace beyond `input.md`.
  - Risk if false: Additional files would need to be identified and seeded separately.

## Plan

### Task 1: Remove reverse-engineer.py from EXCLUDE_SCRIPTS
**Intent:** Fix Bug 1 by ensuring `reverse-engineer.py` is discoverable by the menu.
**Inputs:** `.aib_brain/tools/menu.py` — current `EXCLUDE_SCRIPTS` set.
**Outputs:** `.aib_brain/tools/menu.py` — `EXCLUDE_SCRIPTS` without `"reverse-engineer.py"`.
**External Interfaces:** None.
**Environment & Configuration:** No environment variables or secrets involved.
**Procedure:**
1. Open `.aib_brain/tools/menu.py`.
2. Locate the `EXCLUDE_SCRIPTS` set (lines ~18–28).
3. Remove the line `"reverse-engineer.py",` from the set.
4. Save the file.
**Done Criteria:** `"reverse-engineer.py"` is not present in `EXCLUDE_SCRIPTS`; `discover_tool_scripts()` returns `["reverse-engineer.py"]` when called against the tools directory.
**Dependencies:** None.
**Risk Notes:** None — single-line removal with no logic implications.

### Task 2: Add positive-presence regression test
**Intent:** Prevent future silent re-exclusion of `reverse-engineer.py` from the menu.
**Inputs:** `tests/test_menu.py` — existing test module.
**Outputs:** `tests/test_menu.py` — new test asserting `reverse-engineer.py` is in `build_script_actions()` results.
**External Interfaces:** None.
**Environment & Configuration:** Pytest test suite; Python 3.10+.
**Procedure:**
1. Open `tests/test_menu.py`.
2. Add a new test method `test_reverse_engineer_present` inside `TestBuildScriptActions` (or `TestFilterVisibleActions`).
3. Assert that `"reverse-engineer.py"` is present in `[a["script"] for a in build_script_actions(...)]`.
4. Save the file.
**Done Criteria:** New test passes; `reverse-engineer.py` is in the action list.
**Dependencies:** Task 1 (file must not be in EXCLUDE_SCRIPTS for test to pass).
**Risk Notes:** None.

### Task 3: Seed input.md in the current workspace
**Intent:** Fix Bug 2 by running the idempotent `initialize.py` to create the missing `input.md`.
**Inputs:** `.aib_brain/tools/initialize.py`; current workspace root.
**Outputs:** `.aib_memory/input.md` — created with seed template.
**External Interfaces:** Filesystem only.
**Environment & Configuration:** Python 3.10+; virtual environment activated.
**Procedure:**
1. Run `python .aib_brain/tools/initialize.py --workspace .` from the workspace root.
2. Observe output: "input.md already exists — skipping overwrite." should NOT appear; "Initialized .aib_memory structure successfully." should appear.
3. Verify `.aib_memory/input.md` exists and contains the seed template.
**Done Criteria:** `.aib_memory/input.md` exists with `## Active request`, `## Options`, and `## Input` sections.
**Dependencies:** None (independent of Tasks 1 and 2).
**Risk Notes:** If any other file in `.aib_memory/` is inadvertently detected as missing by `initialize.py`, it would be created — acceptable because creation is idempotent.

### Task 4: Run the full test suite
**Intent:** Confirm no regressions from Tasks 1–3.
**Inputs:** All files under `tests/`; `.aib_brain/tools/*.py`.
**Outputs:** Pytest output; all tests pass.
**External Interfaces:** Pytest test runner.
**Environment & Configuration:** Virtual environment with `pytest` installed; workspace root.
**Procedure:**
1. Run `pytest tests/ -v` from the workspace root.
2. Confirm output shows ≥74 passed, 0 failed (73 existing + 1 new).
**Done Criteria:** Exit code 0; no test failures.
**Dependencies:** Tasks 1, 2, 3.
**Risk Notes:** None anticipated.

## Testing

- T1 — EXCLUDE_SCRIPTS does not contain reverse-engineer.py: Inspect `menu.py` `EXCLUDE_SCRIPTS` set. Expected outcome: `"reverse-engineer.py"` is absent from the set.

- T2 — Menu action list contains reverse-engineer.py: Call `build_script_actions(tools_dir)` in a test; check the `"script"` field of returned actions. Expected outcome: `"reverse-engineer.py"` is present in the list.

- T3 — Empty-repo menu launches without error: Run `python .aib_brain/tools/menu.py --workspace <empty-temp-dir>` with a mocked `get_key` returning QUIT. Expected outcome: No `SystemExit("ERROR: No actions available")` is raised; the menu renders at least one action.

- T4 — input.md exists with correct seed content: Read `.aib_memory/input.md` after running `initialize.py`. Expected outcome: File exists and contains `## Active request`, `## Options`, `- [ ] No changes — provide answer only`, `- [ ] Skip analysis document generation`, `## Input`.

- T5 — initialize.py is idempotent on re-run: Run `initialize.py --workspace .` twice; check `.aib_memory/input.md` is not overwritten on second run. Expected outcome: Second run prints "input.md already exists — skipping overwrite." and file content is unchanged.

- T6 — Full test suite passes: Run `pytest tests/ -v`. Expected outcome: Exit code 0; ≥74 tests pass; 0 failures.

## Documentation

- .aib_memory/context.md (ref_id: REF-0001) — Verify the `menu.py` description accurately reflects that `reverse-engineer.py` is no longer in EXCLUDE_SCRIPTS. No textual change needed (current description only mentions lifecycle scripts as excluded, which remains accurate). Confirm on next `aib-context.md` run.

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/menu.py` | Modified | Remove `"reverse-engineer.py"` from `EXCLUDE_SCRIPTS` to fix Bug 1. |
| `.aib_memory/input.md` | Created | Seed with canonical template to fix Bug 2. |
| `tests/test_menu.py` | Modified | Add positive-presence regression test for `reverse-engineer.py`. |
| `.aib_brain/tools/initialize.py` | Read-only dependency | Run to create `input.md`; no code changes needed. |
| `.aib_brain/tools/common.py` | Read-only dependency | Imported by `menu.py` and `initialize.py`; no changes. |

## Internal Review of Request and Product Docs

- OK: `request.md` — Goal, Background, Scope, Out of scope, Constraints, and Success criteria are all present and non-empty.

- OK: `.aib_memory/context.md` (REF-0001) — Accurately describes the menu behavior: "Lifecycle scripts (create-request.py, close-request.py) are in EXCLUDE_SCRIPTS and do not appear in the menu." This statement remains correct after Bug 1 is fixed.

- Ambiguity: `.aib_memory/context.md` (REF-0001) — The Technical Design section lists `reverse-engineer.py` in `EXCLUDE_SCRIPTS` for `menu.py` without commentary. After the fix, `reverse-engineer.py` will no longer be in `EXCLUDE_SCRIPTS`; however, the context.md description does not explicitly enumerate all items in `EXCLUDE_SCRIPTS`, so no factual contradiction exists. The context.md statement "Lifecycle scripts (create-request.py, close-request.py) are in EXCLUDE_SCRIPTS" is an inclusive statement, not an exhaustive one.

- Missing info: No test in `tests/test_menu.py` prior to this request asserts positive presence of `reverse-engineer.py` in the menu. This gap is addressed by Task 2.

- Cross-ref issue: R-20260417-0903 implementation log (Task 5) states "Added `create-request.py` and `close-request.py` to `EXCLUDE_SCRIPTS`" but did not note that `reverse-engineer.py` was already (incorrectly) present and needed removal. This is an oversight in the prior request's implementation record; no fix needed in this request.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

Both bugs are shallow point-corrections with no architectural implications. Bug 1 is a set membership error in a constant; Bug 2 is an operational gap in an existing idempotent initialization mechanism. Neither requires new components, new abstractions, or changes to data flow. The only design observation is that the AIB upgrade process lacks a formal reconciliation step for existing workspaces — this is an accepted limitation per ADR-0003 (brain/memory separation) and is out of scope for this request.

- Fix is minimal and non-disruptive.
- No risk to `EXCLUDE_SCRIPTS` semantics after removal of one entry.
- `initialize.py` idempotency is verified by code inspection and existing tests.
- Adding a positive-presence test strengthens the regression safety net for future menu changes.
- No new dependencies introduced.

### Product Owner

Both bugs directly block the primary developer workflow: the menu is unusable and the analysis prompt cannot detect toggles. The fixes deliver full restoration of the expected UX from R-20260417-0903 with zero scope creep. Success criteria are specific and testable.

- Business value: high — unblocks the core AIB loop for all users of the current workspace and any empty-repo scenario.
- Scope is appropriately narrow; no gold-plating.
- Acceptance criteria cover both happy paths and idempotency.
- One minor concern: the "Documentation" section notes context.md may need a future update, but this is correctly deferred to the next `aib-context.md` run.

### User

After these fixes, the developer can run `run.bat` in any repo (empty or existing) and see the `Reverse Engineer` action in the menu. The `input.md` file will be present, so the analysis prompt can read toggles without error. No workflow steps change; the fix is transparent.

- Improved experience: menu works from first invocation in a fresh repo.
- No new steps or concepts introduced to the user-facing workflow.
- The positive test prevents this class of silent regression from recurring.

### Security Officer

No security surface is affected. Both changes are:

- A constant set edit in a Python file (no execution path changes beyond scope of discoverable actions).
- Creation of a plaintext Markdown file with no sensitive content.
- No credentials, tokens, secrets, or network calls involved.
- No authentication or authorization paths affected.
- No new input parsing or external data sources introduced.

### Data Governance Officer

No data lineage, retention, classification, or compliance implications. `input.md` contains only ephemeral developer intent text (classified as Internal engineering documentation per context.md). The file is archived per request and reset, maintaining the existing audit trail. No PII or regulated data is involved.
