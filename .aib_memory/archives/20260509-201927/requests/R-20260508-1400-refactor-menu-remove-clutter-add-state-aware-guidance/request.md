# Request: R-20260508-1400 — Refactor menu: remove clutter, add state-aware guidance

## Goal

Simplify and improve the AIB interactive menu (`menu.py`) by removing UI clutter (copy-paste prompt list, explicit Refresh option, Move Request Artifacts action), switching from auto-discovery to an explicit hard-coded action list, and adding a dynamic state-aware guidance block that tells the developer what to do next based on the current workspace state.

## Background

The current menu (`menu.py`) has accumulated features that create visual noise and conceptual overhead:
- A copy-paste prompt reference block is rendered inline in the menu, cluttering the display.
- An explicit "Refresh" option is listed as a numbered action, even though the menu already auto-refreshes every 3 seconds via the `_REFRESH_TIMEOUT_S` polling loop.
- Menu actions are built via auto-discovery of all `.py` files in `.aib_brain/tools/`, minus an exclusion list (`EXCLUDE_SCRIPTS`). This fragile mechanism means newly added scripts may silently appear unless added to `EXCLUDE_SCRIPTS`. `move-request-artifacts.py` is not in `EXCLUDE_SCRIPTS` and currently appears in the menu, even though it is an internal lifecycle helper.
- There is no contextual guidance: the developer must know from memory which prompt to run next. The menu shows the same options regardless of whether there is an active request, whether analysis has been performed, or whether input has been provided.

## Scope

- Remove the "── AIB Prompts ──" copy-paste block from `render_menu()` in `.aib_brain/tools/menu.py`.

- Remove the `_REFRESH_ACTION` sentinel and all code paths that add or handle the Refresh option (including the module-level constant definition and its injection in `choose_action()`).

- Replace auto-discovery (`discover_tool_scripts()` + `build_script_actions()`) with an explicit hard-coded list of menu actions. The hard-coded list shall include:
  - Reverse Engineer (backed by `reverse-engineer.py`) — utility to walk workspace and emit a JSON Lines file inventory.
  - Move Request Artifacts (removed per request — do NOT include this in the explicit list).
  - Close current request (backed by `close-request.py`) — conditionally visible when an active request exists (existing behavior via `filter_visible_actions`).

  Only the tools that are genuinely useful to the developer from the menu surface shall be included.

- Remove `EXCLUDE_SCRIPTS` entirely from `menu.py`. Since the action list is fully hard-coded, an exclusion mechanism is no longer needed and would be conceptually backwards (a deny-list over a fixed allow-list). Delete both the `EXCLUDE_SCRIPTS` set definition and the only function that consumes it (`discover_tool_scripts()`). Remove the comment block above the deleted set definition. Update the `filter_visible_actions()` docstring to remove the reference to `EXCLUDE_SCRIPTS`.

- Add a **state-aware guidance block** to `render_menu()` that evaluates the current workspace state and displays a short "Next Step" message. The seven states and their guidance text are, evaluated in order:
  - **`idle` — No active request, `input.md ## Input` is empty or seed-only**: Single-line — "No task in progress. Add your description to `.aib_memory/input.md`, then execute: `Execute \`.aib_brain/prompts/aib-analysis.md\``"
  - **`input_ready` — No active request, `input.md ## Input` has substantive content**: Two-line guidance — (1) "Input ready. Execute analysis to create a request: `Execute \`.aib_brain/prompts/aib-analysis.md\``" and (2) "Or go straight to implement — analysis runs automatically: `Execute \`.aib_brain/prompts/aib-implement.md\``"
  - **`request_incomplete` — Active request exists, `.aib_memory/request.md` is absent, `input.md ## Input` is empty**: Single-line — "Request active — no analysis yet. Run: `Execute \`.aib_brain/prompts/aib-analysis.md\``". Covers interrupted flows, mid-analysis crashes, and manual `request.md` deletion.
  - **`questions_pending` — Active request exists, `input.md` has a non-empty `## Questions` section** (evaluated before `request.md` presence check): Two-line guidance — (1) "Questions pending in input.md. Answer them then re-run: `Execute \`.aib_brain/prompts/aib-analysis.md\``" and (2) "Or run implement directly — recommended options will be applied automatically: `Execute \`.aib_brain/prompts/aib-implement.md\``"
  - **`implementation_ready` — Active request exists, `request.md` is present, `input.md ## Input` is empty, no pending questions**: Two-line guidance — (1) "Request analysed and ready. Run: `Execute \`.aib_brain/prompts/aib-implement.md\``" and (2) "To amend: write changes to `.aib_memory/input.md` then re-run: `Execute \`.aib_brain/prompts/aib-analysis.md\``"
  - **`amendment_pending` — Active request exists, `request.md` is present, `input.md ## Input` has substantive content, no pending questions**: Single-line — "Amendments pending in input.md. Re-run analysis to incorporate changes: `Execute \`.aib_brain/prompts/aib-analysis.md\``"
  - **`unknown` — Defensive catch-all when none of the above states match** (e.g., due to filesystem error or unexpected workspace configuration): Single-line — "⚠ Workspace state could not be determined. Check `.aib_memory/` for inconsistencies."

- Add `_is_context_empty(workspace: Path) -> bool` helper that reads `.aib_memory/context.md` and returns `True` if the file is absent or empty after stripping whitespace. Inside `render_menu()`, after the state guidance lines, if `_is_context_empty(workspace)` is `True`, write an additional line: "Context file is empty — run context generation first: `Execute \`.aib_brain/prompts/aib-context.md\``". This check is orthogonal to state detection and applies for any state.

- Update `_detect_guidance_state(state: MenuState, workspace: Path) -> str` to evaluate seven states in order, with the entire function body wrapped in `try/except Exception` returning `"unknown"` on any unhandled error: (1) check `has_active_request`; if False, extract `## Input` content from `input.md` — empty → return `"idle"`; non-empty → return `"input_ready"`; if True, (2) read `input.md ## Questions` — extract text between `## Questions` and next `##` or EOF, strip whitespace; non-empty → return `"questions_pending"`; (3) check `request.md` presence at `.aib_memory/request.md` — absent → return `"request_incomplete"`; (4) check `## Input` content — non-empty → return `"amendment_pending"`; (5) return `"implementation_ready"`. The `questions_pending` check MUST precede the `request.md` presence check.

- Update or remove tests in `tests/test_menu.py` that assert on the old auto-discovery behavior, and add tests for the hard-coded action list and the state-aware guidance logic.

## Out of scope

- Changes to any other tool script (`initialize.py`, `create-request.py`, `close-request.py`, `reverse-engineer.py`, `common.py`).
- Changes to prompt files (`.aib_brain/prompts/`).
- Changes to convention files (`.aib_brain/conventions/`).
- Changes to CI / release bookkeeping scripts.
- Adding new keyboard shortcuts or navigation mechanics to the menu.
- Redesigning the full menu layout beyond what is stated in Scope.

## Constraints

- `menu.py` must remain Python 3.10+, standard library only (no third-party packages).
- Auto-refresh behavior (every `_REFRESH_TIMEOUT_S` seconds on TIMEOUT) must be preserved unchanged.
- The "Close current request" conditional injection via `filter_visible_actions` must remain functional.
- All existing tests for menu functionality that remain valid after the change must continue to pass.
- No external network calls may be introduced.

## Success criteria

- SC-01: The rendered menu contains no "── AIB Prompts ──" copy-paste block.
- SC-02: The rendered menu contains no "Refresh" numbered action.
- SC-03: `move-request-artifacts.py` does not appear in the menu action list regardless of auto-discovery state.
- SC-04: All menu actions are sourced from a hard-coded list (no `glob("*.py")` auto-discovery is used to build the primary action list).
- SC-05: When no active request exists and `input.md ## Input` is empty/seed-only, `_detect_guidance_state()` returns `"idle"` and the guidance block displays the "no task in progress" message.
- SC-06: When no active request exists and `input.md ## Input` has substantive content, `_detect_guidance_state()` returns `"input_ready"` and the guidance block displays both the analysis path and the implement shortcut ("analysis runs automatically") as a two-line message.
- SC-07: When an active request exists but `.aib_memory/request.md` is absent and `## Input` is empty, `_detect_guidance_state()` returns `"request_incomplete"` and the guidance block displays the "run analysis" message.
- SC-08: When an active request exists, `request.md` is present, `input.md ## Input` is empty, and no `## Questions` are pending, `_detect_guidance_state()` returns `"implementation_ready"` and the guidance block displays both the implement path and the amendment path as a two-line message.
- SC-09: The existing test suite passes without regressions on unchanged functionality (key handling, `resolve_menu_state`, `filter_visible_actions`, `validate_param`, `collect_parameters`, `build_command`, `check_version_compatibility`).
- SC-10: New tests cover the hard-coded action list (move-request-artifacts absent, correct titles present) and the state-aware guidance rendering for all seven states.
- SC-11: `EXCLUDE_SCRIPTS` does not exist in `menu.py` — no definition and no reference in production code.
- SC-12: When an active request exists and `input.md` contains a non-empty `## Questions` section, `_detect_guidance_state()` returns `"questions_pending"` regardless of `request.md` presence or `## Input` content (priority check).
- SC-13: When the `## Questions` section in `input.md` is absent or empty, the `questions_pending` state is NOT triggered regardless of active request or `request.md` presence.
- SC-14: When an active request exists, `request.md` is present, no `## Questions` are pending, and `input.md ## Input` has substantive content, `_detect_guidance_state()` returns `"amendment_pending"`.
- SC-15: When `_detect_guidance_state()` encounters an unhandled exception during detection, it returns `"unknown"` without propagating the exception.
- SC-16: When `.aib_memory/context.md` is absent or empty, `render_menu()` displays an additional guidance line recommending `Execute \`.aib_brain/prompts/aib-context.md\`` regardless of the current state. When `context.md` is non-empty, this extra line is absent.
- SC-17: The set of keys in `_GUIDANCE_MESSAGES` is exactly `{"idle", "input_ready", "request_incomplete", "questions_pending", "implementation_ready", "amendment_pending", "unknown"}`.

## Assumptions

- A1: The only scripts that belong in the explicit hard-coded menu action list are `reverse-engineer.py` (developer-facing utility) and `close-request.py` (conditionally injected by `filter_visible_actions` — not hard-coded directly). No other scripts currently in `.aib_brain/tools/` need to appear in the menu.
  - Risk if false: A script useful to developers would be invisible after the auto-discovery removal; the hard-coded list would need to be updated.

- A2: "Substantive content" in `input.md ## Input` (or `## Questions`) means: the text of the section, after stripping whitespace, is non-empty. A section containing only blank lines or spaces is treated as empty. The same heuristic applies to both `## Input` and `## Questions` extraction.
  - Risk if false: If the detection heuristic produces false positives or false negatives, the wrong state would be returned. Covered by T5, T6, T13, T14, T15.

- A3: `request.md` is the canonical indicator that analysis has been performed for the active request. Its presence at `.aib_memory/request.md` means the request exists and analysis has been completed. `create-request.py` does NOT seed `request.md` (per FR-002). The "Skip analysis document generation" toggle still writes `request.md`, so `request.md` presence correctly covers that case. `analysis.md` is NOT the canonical indicator.
  - Risk if false: If `request.md` is deleted manually after analysis but before implementation, guidance would incorrectly show "run analysis". Acceptable edge case.

- A4: The `print_prompt_reference()` standalone function at line ~540 of `menu.py` has no callers and can be removed without impact.
  - Risk if false: If there is a caller not visible in the code scan, removing it would break that caller. Code scan confirmed zero callers.

- A5: `test_excluded_scripts_absent` must be **deleted** (not updated) because `EXCLUDE_SCRIPTS` will no longer exist in `menu.py`. The local import of `EXCLUDE_SCRIPTS` inside that method body means deletion causes no module-level ImportError. All other test classes remain valid without changes.
  - Risk if false: Additional tests may need updating if they indirectly rely on auto-discovery.

- A6: `EXCLUDE_SCRIPTS` is referenced only in `discover_tool_scripts()` in production code and locally inside `test_excluded_scripts_absent` in tests. Both consumers are removed in this request. Code scan confirms no other references exist in production code.
  - Risk if false: An undetected caller would cause an `AttributeError` at runtime.

- A7: The `questions_pending` state takes priority over all request.md-presence checks in `_detect_guidance_state()`. The `## Questions` extraction MUST precede the `request.md` presence check. When both `request.md` is present AND `## Questions` is non-empty, `questions_pending` wins — this prevents Q-blocks from being silently hidden.
  - Risk if false: If the detection order is reversed, `implementation_ready` or `amendment_pending` would display even when Q-blocks are pending.

- A8: The `## Questions` and `## Input` sections in `input.md` are extracted using the same pattern: read file text, locate the heading, take content up to the next `##` heading or EOF, strip whitespace. Non-empty result means the section has content.
  - Risk if false: Extraction heuristic produces false positives (e.g., matches a different section). Covered by T13 and T14 (whitespace-only body treated as empty) and T15 (non-empty body triggers `amendment_pending`).

- A9: Guidance messages are stored as `list[str]` values in `_GUIDANCE_MESSAGES` (one element per displayed line). Two-line states (`input_ready`, `questions_pending`, `implementation_ready`) have two-element lists. Single-line states (`idle`, `request_incomplete`, `amendment_pending`, `unknown`) have one-element lists. `render_menu()` iterates the list and writes each string as a line.
  - Risk if false: If embedded `\n` strings are used instead, per-line test assertions would need updating.

- A10: `amendment_pending` is the correct state when an active request has `request.md` present AND `input.md ## Input` has content AND no `## Questions` are pending. This state captures the "developer has written amendment notes to input.md" scenario. It is evaluated after the `questions_pending` check and after the `request.md` presence check.
  - Risk if false: If `## Input` check is evaluated before `## Questions` check, a developer with both Q-blocks and amendment notes would see `amendment_pending` instead of `questions_pending`. The evaluation order in A7 prevents this.

- A11: `unknown` is returned by `_detect_guidance_state()` only when an unhandled exception occurs within the detection body (e.g., unexpected filesystem error). In normal operation, the seven states above are exhaustive. The `unknown` state is defensive — it should never appear in a correctly functioning workspace.
  - Risk if false: If the detection logic has an unreachable else branch that is never triggered, `unknown` would be reachable only via exception — which is the intended design.

- A12: `_is_context_empty(workspace: Path) -> bool` reads `.aib_memory/context.md`, returns `True` if absent or empty after stripping. If `context.md` has any non-whitespace content, returns `False`. An `OSError` (e.g., permission error) is treated as `True` (empty) to err on the side of showing the guidance line.
  - Risk if false: If context.md has whitespace-only content, the check may show the extra guidance line even though the file technically exists. Acceptable — whitespace-only context.md is functionally empty.

## Plan

### Task 1: Remove copy-paste prompt block, Refresh action, and orphaned functions from `menu.py`
**Intent:** Remove three sources of UI clutter and dead code: the inline "── AIB Prompts ──" block in `render_menu()`, the `_REFRESH_ACTION` sentinel and all code paths that reference it, and the orphaned `print_prompt_reference()` function.
**Outputs:** `.aib_brain/tools/menu.py` — three removal edits applied.
**Procedure:**
1. In `.aib_brain/tools/menu.py`, delete the six lines comprising the inline "── AIB Prompts ──" block from `render_menu()` (starting with `buf.write("\n")` before the `──` line and ending with the trailing `buf.write("\n")`).
2. In `.aib_brain/tools/menu.py`, delete the `print_prompt_reference()` function definition (confirmed zero callers).
3. In `.aib_brain/tools/menu.py`, delete the module-level `_REFRESH_ACTION` dict constant.
4. In `.aib_brain/tools/menu.py`, in `choose_action()`, replace `filter_visible_actions(all_script_actions, state) + [_REFRESH_ACTION]` with `filter_visible_actions(all_script_actions, state)`.
5. In `.aib_brain/tools/menu.py`, in `choose_action()`, remove both `if action.get("type") == "refresh":` branches (one under `ENTER`, one under `DIGIT:`).
**Done Criteria:** `grep -n "_REFRESH_ACTION\|print_prompt_reference\|AIB Prompts" .aib_brain/tools/menu.py` returns no matches.
**Dependencies:** None
**Risk Notes:** `print_prompt_reference()` confirmed orphaned by code scan (zero callers). `_REFRESH_ACTION` referenced at exactly three locations in `choose_action()` — all three must be removed together.

### Task 2: Remove `EXCLUDE_SCRIPTS`, `discover_tool_scripts()`, and replace auto-discovery with hard-coded list
**Intent:** Delete `EXCLUDE_SCRIPTS` and `discover_tool_scripts()` entirely, and replace the `build_script_actions()` body with an explicit allow-list containing only `reverse-engineer.py`.
**Outputs:** `.aib_brain/tools/menu.py` — `EXCLUDE_SCRIPTS` set and comment block deleted; `discover_tool_scripts()` removed; `build_script_actions()` body replaced.
**Procedure:**
1. In `.aib_brain/tools/menu.py`, delete the `EXCLUDE_SCRIPTS` set definition and the comment block above it (lines beginning with `# Lifecycle scripts are excluded from dynamic discovery…` through the closing `}`).
2. In `.aib_brain/tools/menu.py`, remove the `discover_tool_scripts()` function (confirmed: only caller is `build_script_actions()`; not imported in any test file).
3. In `.aib_brain/tools/menu.py`, replace the `build_script_actions()` function body with a hard-coded list returning a single action: `reverse-engineer.py` titled "Reverse Engineer" with description "Walk workspace filesystem and emit a JSON Lines file inventory." and a `--workspace` parameter. Add a comment block: "Only scripts explicitly registered here appear in the menu. Add new developer-facing tools by hand; do not rely on auto-discovery."
4. In `.aib_brain/tools/menu.py`, update the `filter_visible_actions()` docstring to remove the sentence referencing `EXCLUDE_SCRIPTS`.
**Done Criteria:** `hasattr(menu, 'EXCLUDE_SCRIPTS')` is `False`; `hasattr(menu, 'discover_tool_scripts')` is `False`; `build_script_actions(tools_dir)` returns exactly one action with `script == 'reverse-engineer.py'`.
**Dependencies:** None
**Risk Notes:** Code scan confirms `EXCLUDE_SCRIPTS` has no production-code reference outside `discover_tool_scripts()`. The only test reference is inside `test_excluded_scripts_absent`, which is deleted in Task 5.

### Task 3: Add seven-state detection function and `_GUIDANCE_MESSAGES` dict
**Intent:** Implement `_detect_guidance_state()` with seven-state evaluation order and `_GUIDANCE_MESSAGES` dict mapping each state key to a list of guidance strings.
**Outputs:** `.aib_brain/tools/menu.py` — new `_detect_guidance_state()` function; new `_GUIDANCE_MESSAGES` dict.
**Procedure:**
1. In `.aib_brain/tools/menu.py`, add a module-level dict `_GUIDANCE_MESSAGES: dict[str, list[str]]` with exactly seven entries (one per state key: `idle`, `input_ready`, `request_incomplete`, `questions_pending`, `implementation_ready`, `amendment_pending`, `unknown`). Single-line states: one-element list. Two-line states (`input_ready`, `questions_pending`, `implementation_ready`): two-element list. `unknown` element should begin with `"⚠ "`.
2. In `.aib_brain/tools/menu.py`, add helper `_detect_guidance_state(state: MenuState, workspace: Path) -> str`. Body: wrap entirely in `try/except Exception: return "unknown"`. Inside try: (a) if not `state.has_active_request`: read `input.md`, extract `## Input` section, strip — empty → return `"idle"`, non-empty → return `"input_ready"`; (b) if `state.has_active_request`: read `input.md`, extract `## Questions` section, strip — non-empty → return `"questions_pending"`; (c) check `(workspace / ".aib_memory" / "request.md").exists()` — False → return `"request_incomplete"`; (d) re-read `## Input` section of same `input.md` content — non-empty → return `"amendment_pending"`; (e) return `"implementation_ready"`. All `input.md` reads use `try/except OSError: content = ""`.
3. Add a module-level assertion: `assert set(_GUIDANCE_MESSAGES.keys()) == {"idle", "input_ready", "request_incomplete", "questions_pending", "implementation_ready", "amendment_pending", "unknown"}`.
**Done Criteria:** `_detect_guidance_state()` returns correct keys for all seven scenarios; `_GUIDANCE_MESSAGES` has seven entries; module-level assertion passes on import.
**Dependencies:** Tasks 1–2 (action list stabilised; `render_menu()` partially updated)
**Risk Notes:** `questions_pending` check MUST precede `request.md` presence check (per A7). `OSError` on `input.md` read treated as empty string in all branches. `amendment_pending` detection reuses the same `## Input` extraction as `idle`/`input_ready`.

### Task 4: Add `_is_context_empty()` helper and update `render_menu()` for guidance rendering
**Intent:** Implement the `_is_context_empty()` helper and update `render_menu()` to accept `workspace: Path`, render the state-aware guidance block, and optionally append the context.md extra line.
**Outputs:** `.aib_brain/tools/menu.py` — new `_is_context_empty()` function; `render_menu()` signature and body updated; `choose_action()` call to `render_menu()` updated.
**Procedure:**
1. In `.aib_brain/tools/menu.py`, add `_is_context_empty(workspace: Path) -> bool`: read `.aib_memory/context.md` from `workspace` (wrap in `try/except OSError: return True`); return `not content.strip()`.
2. In `.aib_brain/tools/menu.py`, update `render_menu(state, script_actions, selected_index, workspace: Path)` to add the `workspace` parameter. After the active-request line and before the action list, add: call `_detect_guidance_state(state, workspace)`; iterate `_GUIDANCE_MESSAGES[state_key]` and write each line with `buf.write(line + "\n")`; then if `_is_context_empty(workspace)`: write the context.md extra guidance line.
3. In `.aib_brain/tools/menu.py`, update the single caller of `render_menu()` in `choose_action()` to pass `workspace`.
**Done Criteria:** `render_menu()` accepts `workspace` parameter; guidance lines appear in rendered output for each state; context.md extra line appears when `context.md` is absent/empty and is absent when `context.md` has content.
**Dependencies:** Tasks 1–3
**Risk Notes:** `render_menu` has no direct callers in `test_menu.py` — signature change has zero test impact. All `input.md` reads in `_detect_guidance_state()` are guarded by `OSError` handlers.

### Task 5: Update `tests/test_menu.py` for new seven-state behavior and hard-coded list
**Intent:** Delete obsolete tests, update auto-discovery tests to reflect the hard-coded list, and add comprehensive coverage for all seven states, `_is_context_empty()`, and guidance message content.
**Outputs:** `tests/test_menu.py` — updated test file.
**Procedure:**
1. In `tests/test_menu.py`, **delete** `TestBuildScriptActions.test_excluded_scripts_absent` — `EXCLUDE_SCRIPTS` no longer exists.
2. In `tests/test_menu.py`, update `TestBuildScriptActions.test_returns_list_of_actions`, `test_ids_are_sequential_strings`, `test_lifecycle_scripts_absent` to assert against the hard-coded one-entry list (reverse-engineer.py only).
3. In `tests/test_menu.py`, add `TestHardCodedActions` class: (a) `move-request-artifacts.py` not in base list; (b) `reverse-engineer.py` present with title "Reverse Engineer"; (c) list has exactly one action; (d) `not hasattr(menu, "EXCLUDE_SCRIPTS")`; (e) `not hasattr(menu, "discover_tool_scripts")`.
4. In `tests/test_menu.py`, update `TestFilterVisibleActions.test_returns_all_actions_when_no_active_request` and `test_active_request_adds_one_action` to use the hard-coded `build_script_actions()`.
5. In `tests/test_menu.py`, add `TestDetectGuidanceState` class with tests T5–T22 as defined in the Testing section of `analysis.md`: all seven states, priority tests (T12, T22), content tests (T19, T20, T21), and `_is_context_empty()` tests (T17, T18).
6. In `tests/test_menu.py`, add `conftest.py` fixture `input_md_file(tmp_path)` if not already present (provides a helper to write `input.md` content in tests). If conftest already has this, reuse it.
7. In `tests/test_menu.py`, run `pytest tests/test_menu.py -v` from the workspace root to verify all tests pass.
**Done Criteria:** `pytest tests/test_menu.py -v` exits with code 0; `TestStateAwareGuidance` / `TestDetectGuidanceState` covers all seven states plus the three priority tests.
**Dependencies:** Tasks 1–4
**Risk Notes:** `discover_tool_scripts` not imported at module level in `test_menu.py` (confirmed) — no ImportError risk. `render_menu()` not directly called in tests (confirmed) — no breakage from signature change.

### Task 6: Update `.aib_memory/context.md` documentation
**Intent:** Reflect the menu changes in the product context document: FR-010, component map, and acceptance criteria.
**Outputs:** `.aib_memory/context.md` — targeted updates to FR-010, component map `AIB Command Menu` row, and acceptance criterion AC-5.
**Procedure:**
1. In `.aib_memory/context.md`, update FR-010 to describe: seven-state guidance block (`idle`, `input_ready`, `request_incomplete`, `questions_pending`, `implementation_ready`, `amendment_pending`, `unknown`); hard-coded action allow-list; removal of copy-paste block and Refresh action; `_is_context_empty()` extra guidance line when context.md is absent/empty; `questions_pending` priority over all other active-request states.
2. In `.aib_memory/context.md`, update the `AIB Command Menu` component row in the component map to describe: hard-coded allow-list; `_detect_guidance_state()` reading `input.md` and `request.md`; `_is_context_empty()` reading `context.md`; seven state keys.
3. In `.aib_memory/context.md`, update acceptance criterion AC-5: replace "prompt invocations are displayed" with "state-aware seven-state next-step guidance block is displayed; context.md empty check adds extra guidance line when applicable."
4. Acceptance test: `grep -i "amendment_pending\|idle\|request_incomplete" .aib_memory/context.md` returns at least one match in FR-010; `grep -i "copy-paste" .aib_memory/context.md` in menu-related entries returns no matches.
**Done Criteria:** `context.md` accurately describes the new seven-state guidance block and hard-coded action list.
**Dependencies:** Tasks 1–5 (changes stabilised)
**Risk Notes:** `context.md` is auto-generated by `aib-context.md` — manual edits may be overwritten on next context regeneration. This is acceptable and noted.

## Documentation

- `.aib_memory/context.md` — Update FR-010 to describe the seven-state guidance block (idle, input_ready, request_incomplete, questions_pending, implementation_ready, amendment_pending, unknown), hard-coded action allow-list, `_is_context_empty()` extra line, and `questions_pending` priority. Update `AIB Command Menu` component map row. Update acceptance criterion AC-5 to reference state-aware guidance. Acceptance test: `grep -i "amendment_pending" .aib_memory/context.md` returns a match; `grep -i "copy-paste" .aib_memory/context.md` in menu-related entries returns no matches.

## Questions & Decisions

