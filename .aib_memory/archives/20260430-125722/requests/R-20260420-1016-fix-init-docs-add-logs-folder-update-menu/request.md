## Goal

Fix three distinct bugs/gaps in the AIB workspace and one cosmetic improvement in the interactive menu:

1. Initialization must not create `.aib_memory/docs/` folder or seed any files inside it (REQ-0001.md, REQ-0002.md are no longer expected artefacts).
2. Initialization must create `.aib_memory/logs/` folder so that log artefacts have a deterministic home immediately after initialization.
3. Restore a "Close current request" option in the interactive menu (`menu.py`) that appears only when an active request exists and invokes `close-request.py`.
4. Remove the label prefixes "Analysis : ", "Implement: ", and "Context  : " from the prompt-reference block displayed in the menu — the prompt file name already conveys the intent.

## Background

Since v1.2.0 the references register no longer stores paths under `.aib_memory/docs/`; the template (`references-template.md`) points to `context.md` and `Concepts.md` directly. However, `initialize.py` still calls `ensure_doc_seed_files`, which extracts `RequirementRef` objects from the template rows and writes fallback files `REQ-0001.md` and `REQ-0002.md` into `.aib_memory/docs/`. This directory and its contents are unexpected, confusing, and inconsistent with the current product design.

The logs directory (`.aib_memory/logs/`) is created on-demand by `menu.py._make_log_path()` only when a tool action is first executed. It is not created during initialization, so the folder is absent until the menu is run — violating the principle that initialization should produce a deterministic, stable workspace structure.

The interactive menu previously exposed a "Close current request" action that was later removed when lifecycle scripts were moved to `EXCLUDE_SCRIPTS`. The removal was too aggressive: closing a request is a valid user-facing operation that should remain accessible from the menu when an active request exists. Creating a new request, by contrast, is correctly handled by the AI agent and should not appear in the menu.

The prompt-reference display lines use redundant labels ("Analysis : ", "Implement: ", "Context  : ") because the prompt file names themselves already identify the operation. Removing the labels shortens the lines and reduces noise.

## Scope

- Remove `(memory_root / "docs").mkdir(...)` from `initialize.py`.

- Remove `ensure_doc_seed_files(workspace, requirements)` call from `initialize.py`. The `requirements` return value from `seed_references_from_product_doc` is no longer needed; the variable should be discarded (use `_`).

- Add `(memory_root / "logs").mkdir(parents=True, exist_ok=True)` in `initialize.py` alongside the existing `requests` directory creation.

- Add a conditional "Close current request" action in `menu.py` that:
  - Invokes `close-request.py` with the `--workspace` parameter.
  - Appears in the action list only when `state.has_active_request` is `True`.
  - Disappears automatically when the request is closed (next menu refresh).

- Remove label prefixes from the prompt-reference block in `render_menu()` and `print_prompt_reference()` in `menu.py`:
  - Before: `"  Analysis : Execute \`...\`"`
  - After: `"  Execute \`...\`"`

- Update tests in `tests/test_initialize.py` to assert that `.aib_memory/docs/` is NOT created and that `.aib_memory/logs/` IS created after initialization.

- Update tests in `tests/test_menu.py` to reflect that `close-request.py` is now conditionally visible (not universally excluded), and that `filter_visible_actions` now depends on `state.has_active_request`.

## Out of scope

- No changes to `close-request.py` script logic.
- No changes to `common.py` (`ensure_doc_seed_files` remains in the module but is no longer called from `initialize.py`).
- No changes to `references-template.md` or any other template.
- No changes to `create-request.py` — creating requests stays AI-prompt-driven.
- No changes to `aib-context.md`, `aib-analysis.md`, or `aib-implement.md` prompts.
- No changes to the `EXCLUDE_SCRIPTS` set for `create-request.py` and other excluded items; only `close-request.py` is affected.

## Constraints

- Python 3.10+ standard library only; no new dependencies.
- `initialize.py` must remain idempotent: running it twice must not error on the `logs/` or `requests/` directories already existing (use `exist_ok=True`).
- The close-request menu item must not appear when no active request exists — do not break the single-active-request invariant.
- No changes to `.aib_brain/` tool scripts beyond `initialize.py` and `menu.py`.
- Changes to `context.md` are out of scope; `aib-context.md` regenerates it on the next run.
- All existing passing tests must remain passing; updated tests must also pass.

## Success criteria

- Running `initialize.py` on a fresh workspace creates `.aib_memory/requests/` and `.aib_memory/logs/` but does NOT create `.aib_memory/docs/` or any files within it.
- Running `initialize.py` twice on the same workspace does not error.
- The interactive menu shows a "Close current request" item only when an active request is present; the item disappears after the request is closed.
- The prompt-reference block in the menu displays lines starting with "Execute" only, with no "Analysis : " / "Implement: " / "Context  : " prefix.
- The full test suite (`pytest`) passes without skips or failures.

## Assumptions

- A1: `ensure_doc_seed_files` in `common.py` is only called from `initialize.py`; removing the call from `initialize.py` is sufficient to stop docs seeding without touching `common.py`.
  - Risk if false: Another call site exists and docs will still be created.

- A2: The "Close current request" menu item should run `close-request.py` with only `--workspace`; no additional parameters are needed because the script resolves the active request from the register.
  - Risk if false: `close-request.py` may require a `--request-id` in some edge cases, leaving the action incomplete.

- A3: Adding the close-request action inside `filter_visible_actions` (rather than `build_script_actions`) is architecturally correct because its visibility is state-dependent and `filter_visible_actions` is re-evaluated on every menu loop iteration.
  - Risk if false: An alternative placement (e.g. inside `choose_action`) would also work but must be consistently applied.

- A4: The `_REFRESH_ACTION` is appended after `filter_visible_actions` in `choose_action`; the close-request action should be placed at the end of the filtered list (before Refresh) so that it has the highest fixed number in the visible list.
  - Risk if false: ID sequencing may be inconsistent if the action is inserted elsewhere.

## Plan

### Task 1: Remove docs folder and seed call from initialize.py
**Intent:** Stop `initialize.py` from creating `.aib_memory/docs/` and seeding `REQ-0001.md` / `REQ-0002.md`.
**Inputs:** `.aib_brain/tools/initialize.py`
**Outputs:** Modified `initialize.py`
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+; workspace with `.aib_brain/`
**Procedure:**
1. Delete the line `(memory_root / "docs").mkdir(parents=True, exist_ok=True)`.
2. In the `references_file` branch, replace `references_md, requirements = seed_references_from_product_doc(workspace)` and `ensure_doc_seed_files(workspace, requirements)` with `references_md, _ = seed_references_from_product_doc(workspace)` (drop the requirements variable and the `ensure_doc_seed_files` call).
3. Remove the `requirements = None` assignment in the skip branch (no longer needed).
4. Remove `ensure_doc_seed_files` from the import list in `initialize.py`.
**Done Criteria:** `initialize.py` runs without creating `.aib_memory/docs/` on a fresh workspace.
**Dependencies:** None
**Risk Notes:** `seed_references_from_product_doc` still returns a tuple; using `_` for the second element avoids an unused-variable warning.

### Task 2: Add logs folder creation to initialize.py
**Intent:** Ensure `.aib_memory/logs/` exists immediately after initialization.
**Inputs:** `.aib_brain/tools/initialize.py`
**Outputs:** Modified `initialize.py`
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+
**Procedure:**
1. After `(memory_root / "requests").mkdir(parents=True, exist_ok=True)`, add `(memory_root / "logs").mkdir(parents=True, exist_ok=True)`.
**Done Criteria:** `.aib_memory/logs/` exists after initialization on a fresh workspace; second run does not error.
**Dependencies:** Task 1

### Task 3: Add conditional close-request action to menu.py
**Intent:** Restore "Close current request" as a menu item visible only when an active request exists.
**Inputs:** `.aib_brain/tools/menu.py`
**Outputs:** Modified `menu.py`
**External Interfaces:** `close-request.py` invoked via `build_command` / `run_action`
**Environment & Configuration:** Python 3.10+; menu running inside workspace with `.aib_memory/`
**Procedure:**
1. Define a module-level constant `_CLOSE_REQUEST_ACTION` dict with `id`, `title`, `description`, `script = "close-request.py"`, `destructive = False`, and `parameters` containing only the `workspace` parameter.
2. In `filter_visible_actions`, append `_CLOSE_REQUEST_ACTION` to the returned list when `state.has_active_request` is `True`.
3. Renumber action IDs after the filter so the displayed numbers remain sequential.
**Done Criteria:** With an active request, the menu shows the close item; without an active request, the item is absent; selecting it runs `close-request.py` successfully.
**Dependencies:** None
**Risk Notes:** Renumbering must happen after filtering; `choose_action` uses list position for key dispatch, so ID fields are cosmetic but should match.

### Task 4: Remove prefixes from prompt-reference block in menu.py
**Intent:** Clean up the prompt-reference display by removing "Analysis : ", "Implement: ", "Context  : " labels.
**Inputs:** `.aib_brain/tools/menu.py`
**Outputs:** Modified `menu.py`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. In `render_menu`, update the three `buf.write` lines for the prompt-reference block.
2. In `print_prompt_reference`, update the three `print` lines.
**Done Criteria:** Menu renders "  Execute `...`" lines without leading labels.
**Dependencies:** None

### Task 5: Update tests for initialize.py changes
**Intent:** Validate that docs folder is not created and logs folder is created.
**Inputs:** `tests/test_initialize.py`
**Outputs:** Modified `test_initialize.py`
**External Interfaces:** `initialize.py`, temp workspace
**Environment & Configuration:** pytest; Python 3.10+
**Procedure:**
1. Add test `test_does_not_create_docs_folder` asserting `(root / ".aib_memory" / "docs").exists()` is `False` after init.
2. Add test `test_creates_logs_folder` asserting `(root / ".aib_memory" / "logs").is_dir()` after init.
**Done Criteria:** Both new tests pass; existing tests still pass.
**Dependencies:** Tasks 1, 2

### Task 6: Update tests for menu.py changes
**Intent:** Reflect the new conditional visibility of the close-request action and the renaming of labels.
**Inputs:** `tests/test_menu.py`
**Outputs:** Modified `test_menu.py`
**External Interfaces:** `menu.py`
**Environment & Configuration:** pytest
**Procedure:**
1. Update `TestFilterVisibleActions::test_lifecycle_scripts_not_in_actions` — `close-request.py` MAY appear conditionally; assert only `create-request.py` is not in actions. Keep assertion that `close-request.py` is absent from `build_script_actions` output directly.
2. Update `TestFilterVisibleActions::test_active_request_does_not_change_visible_actions` — rename or delete since the behavior now intentionally differs by state; replace with two tests: one asserting close-request absent when no active request, one asserting it present when active.
3. Update `TestBuildScriptActions::test_lifecycle_scripts_absent` to keep asserting `close-request.py` is NOT in `build_script_actions` (still true; it's in EXCLUDE_SCRIPTS).
4. Update `TestFilterVisibleActions::test_returns_all_actions_unchanged` to reflect that `filter_visible_actions` may append the close-request action.
**Done Criteria:** All updated tests pass; no regressions.
**Dependencies:** Task 3

## Testing

- T1 — Init does not create docs folder: Run `initialize.py` on a fresh temp workspace; assert `.aib_memory/docs/` does not exist. Expected outcome: directory absent.
- T2 — Init creates logs folder: Run `initialize.py` on a fresh temp workspace; assert `.aib_memory/logs/` is a directory. Expected outcome: directory present.
- T3 — Init idempotent with logs: Run `initialize.py` twice on same workspace; assert no error and `.aib_memory/logs/` still exists. Expected outcome: exit code 0 on second run.
- T4 — Close action absent without active request: Call `filter_visible_actions(actions, MenuState(None, None))` and assert `"close-request.py"` is not in resulting script names. Expected outcome: action list unchanged.
- T5 — Close action present with active request: Call `filter_visible_actions(actions, MenuState("R-001", ".aib_memory/requests/R-001"))` and assert `"close-request.py"` IS in resulting script names. Expected outcome: one close-request entry in list.
- T6 — Prompt reference block content: Capture rendered menu output and assert it does NOT contain `"Analysis : "`, `"Implement: "`, or `"Context  : "`. Expected outcome: strings absent from rendered output.
- T7 — Full test suite: Run `pytest tests/` and confirm all tests pass. Expected outcome: 0 failures, 0 errors.

## Documentation

- .aib_memory/context.md (ref_id: REF-0001) — Update "initialize" action description in component map to remove `.aib_memory/docs/` and add `.aib_memory/logs/`; update acceptance criteria item 1 and FR-010 to match new menu behavior (close-request option visible when active request present).

## Questions & Decisions

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/initialize.py` | Modified | Remove docs folder creation and ensure_doc_seed_files call; add logs folder creation |
| `.aib_brain/tools/menu.py` | Modified | Add conditional close-request action; remove prompt-reference label prefixes |
| `tests/test_initialize.py` | Modified | Add tests for no-docs and yes-logs post-init |
| `tests/test_menu.py` | Modified | Update assertions for conditional close-request visibility and label-free prompt block |
| `.aib_memory/context.md` | Modified | Regenerated by aib-context.md after implementation to reflect new component map and FRs |
| `.aib_brain/tools/common.py` | Read-only dependency | ensure_doc_seed_files remains in module but is no longer called |

## Internal Review of Request and Product Docs

- OK: `.aib_brain/tools/initialize.py` — Current code matches problem description; docs folder and ensure_doc_seed_files call are present and need removal.
- OK: `.aib_brain/tools/menu.py` — EXCLUDE_SCRIPTS contains `close-request.py`; prompt-reference labels are present.
- Contradiction: `Concepts.md` action contract matrix — lists `.aib_memory/docs/` as an `initialize` output. Post-implementation this will be incorrect; context.md regeneration covers context.md but Concepts.md is `edit_allowed = N` and is outside scope of this request.
- Ambiguity: `filter_visible_actions` docstring states "lifecycle filtering is no longer needed" — this will need updating after Task 3 changes the function to perform conditional filtering.
- Missing info: No test currently validates the absence of `.aib_memory/docs/`; must be added.
- Missing info: No test currently validates the presence of `.aib_memory/logs/` after init; must be added.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect
The request makes targeted, low-risk changes that correct three technical debt items and one UX paper cut. Removing the docs seeding eliminates a confusing artefact that contradicts the current references schema. Adding logs folder creation during initialization aligns with the "deterministic workspace" principle (ADR-0002). The conditional close-request menu item correctly restores a lifecycle action without violating FR-001 (single active request invariant). The architectural risk is low: all changes are confined to two tool scripts and two test files; no inter-component contracts change except the menu rendering, which has no downstream consumers.

- Removing `ensure_doc_seed_files` from `initialize.py` is safe because `common.py` retains the function for any future use.
- Logs folder creation is idempotent (`exist_ok=True`); no risk of double-run failure.
- Conditional action visibility via `filter_visible_actions` is already re-evaluated on every menu loop iteration, so the new close-request item will appear/disappear correctly without additional state management.
- `Concepts.md` (edit_allowed=N) will remain slightly out of date after this change; this is acceptable as the next Concepts.md revision can address it.

### Product Owner
The changes address three user-visible friction points and one internal correctness issue. The docs folder creation was never part of the user-facing workflow description and its artefacts (REQ-0001.md, REQ-0002.md) were confusing. Restoring the close-request menu item improves workflow completeness. The label removal simplifies the menu display. Acceptance criteria in the request are measurable and testable.

- Business value: medium — reduces confusion, restores missing UX affordance.
- Scope clarity: high — each change is independently identifiable.
- Acceptance criteria completeness: good — test cases cover all four changes.
- Risk: the close-request action in the menu must not create a false sense of "no confirmation required"; the current `close-request.py` behavior (auto-closes without additional prompt) should be documented or surfaced to users.

### User
From a user perspective, the initialization will no longer produce surprising `.aib_memory/docs/REQ-0001.md` and `REQ-0002.md` files. The `.aib_memory/logs/` folder being present immediately after init is a quality-of-life improvement. The menu item for closing the active request is a welcome restoration. The prompt-reference display without labels is slightly more compact but unambiguous.

- The disappearance of the close-request item when no active request is present is intuitive and consistent with context-sensitivity.
- Users may need to re-learn that the menu item appears conditionally; a brief descriptive text in the menu item itself ("Close active request") helps.
- No user-facing documentation files are changed in this request; impact on onboarding docs is deferred.

### Security Officer
No security-relevant changes are introduced. No credentials, secrets, tokens, or external network calls are affected. The `close-request.py` action invoked from the menu runs with the same privileges as the rest of the menu session. The conditional visibility of the close-request item does not introduce an authorization bypass risk since menu access itself is filesystem-gated.

- No new attack surface introduced.
- No data exposure risk.
- No authentication or authorization impact.

### Data Governance Officer
No data lineage or retention impact. The docs folder removal eliminates stub files that were not governed artefacts. The logs folder creation ensures observability logs have a deterministic location from initialization, improving auditability. No PII or sensitive data is involved.

- The `inputs/input-archive-*.md` files (governed by NFR-006) are unaffected.
- Log files in `.aib_memory/logs/` are already classified as Internal engineering documentation; creating the folder deterministically does not change their classification.
- No compliance impact.
