# Analysis — R-20260509-2024 — Remove Reverse Engineer option from menu

## Executive Summary

- **Request ID:** R-20260509-2024

- **Title:** Remove Reverse Engineer option from menu

- **Purpose:** Remove the "Reverse Engineer" entry from the AIB interactive menu's `_SCRIPT_ACTIONS` list and reorder `render_menu()` so the "-- Next Step --" state guidance block is displayed before the numbered options list.

- **Scope summary:** Two source files change (`menu.py`, `test_menu.py`) and one documentation file updates (`context.md`). The `reverse-engineer.py` script itself is untouched.

- **`request.md` sections added/updated in this run:** Assumptions (A1–A3), Plan (Tasks 1–4), Documentation, Questions & Decisions (none generated — no ambiguous decision forks identified).

---

## Domain Knowledge Essentials

**AIB (AI Builder):** A minimal, file-first framework for specification-driven development in a repository workspace. It provides deterministic workflows for managing requests and automating release bookkeeping.

**Interactive menu (`menu.py`):** The developer-facing launcher script. It renders an ANSI terminal UI showing the active-request status, a numbered list of available tool actions, and a state-aware "-- Next Step --" guidance block with the recommended next command.

**Hard-coded action list (`_SCRIPT_ACTIONS`):** An explicit Python list of action dictionaries defined in `menu.py`. Each entry carries `id`, `title`, `description`, `script`, `destructive`, and `parameters` keys. There is no dynamic filesystem discovery; the list is the sole source of numbered menu items. Currently the list contains exactly one entry: Reverse Engineer.

**State-aware guidance block:** A section rendered below the numbered options in the current menu. It detects one of seven workspace states (`idle`, `input_ready`, `request_incomplete`, `questions_pending`, `implementation_ready`, `amendment_pending`, `unknown`) and displays the recommended next action command accordingly.

**`filter_visible_actions`:** A menu function that passes through `_SCRIPT_ACTIONS` and conditionally appends the `close-request` action when an active request exists. It does not remove actions.

**Impacted roles:** Developer (menu user). AIB Maintainer (owns `menu.py`).

**Business process touched:** "Communicate user intent" / "Execute analysis workflow" — the menu is the developer's primary launcher for AIB tooling.

---

## Technical Knowledge & Terms

**`_SCRIPT_ACTIONS`:** Module-level list in `menu.py`. `build_script_actions()` returns a copy with sequentially renumbered IDs. Emptying this list makes the base menu contain only "0) Quit" (plus the injected close-request action when a request is active).

**`render_menu()`:** Builds the full terminal frame into an `io.StringIO` buffer and flushes atomically to avoid blink. Current rendering order: banner → active-request line → options list → "0) Quit" → blank line → "-- Next Step --" block → context-empty line. The requested reorder places "-- Next Step --" immediately after the active-request line, followed by the options list and footer.

**`build_script_actions(tools_dir)`:** Accepts `tools_dir` for API compatibility but does not use it; returns a copy of `_SCRIPT_ACTIONS` with re-indexed IDs.

**`EXCLUDE_SCRIPTS`:** A symbol referenced in `.aib_brain/tools/test_common.py` test `test_exclude_scripts_contains_new_entries`. This attribute does not currently exist in `menu.py` — `tests/test_menu.py` explicitly asserts its absence. This is a pre-existing inconsistency in `test_common.py` and is out of scope.

**pytest conftest.py:** `tests/conftest.py` provides the `tools_dir` fixture used by `test_menu.py`. It resolves to `.aib_brain/tools/`.

**Technologies involved:** Python 3.10+, ANSI escape codes (VT100), pytest 7+, standard library only.

---

## Research Results

**Current `_SCRIPT_ACTIONS` list:** One entry — Reverse Engineer (`reverse-engineer.py`). Removing it makes the list `[]`.

**`render_menu()` current block order (lines ~665–714 in `menu.py`):**
1. ANSI clear
2. `ascii_banner()`
3. `Active request:` line
4. Numbered options loop (from `script_actions`)
5. `0) Quit` footer
6. Blank line
7. `── Next Step ──` block (guidance state lookup + lines)
8. Context-empty warning line (conditional)
9. `\033[J]` erase trailing content

**Proposed order after change:**
1. ANSI clear
2. `ascii_banner()`
3. `Active request:` line
4. Blank line
5. `── Next Step ──` block
6. Context-empty warning line (conditional)
7. Blank line (separator before options)
8. Numbered options loop
9. `0) Quit` footer
10. `\033[J]` erase trailing content

**Tests directly impacted in `tests/test_menu.py`:**
- `TestHardCodedActionList.test_reverse_engineer_present` — asserts `"reverse-engineer.py" in scripts`; must be **removed**.
- `TestHardCodedActionList.test_reverse_engineer_title` — asserts title equals `"Reverse Engineer"`; must be **removed**.
- `TestHardCodedActionList.test_no_glob_discovery` — asserts `len(actions) == 1` and `actions[0]["script"] == "reverse-engineer.py"`; must be updated to assert `len(actions) == 0`.

**Tests indirectly affected (verified still pass):**
- `TestFilterVisibleActions.test_active_request_adds_one_action`: asserts `len(visible_with_req) == len(visible_no_req) + 1`. With empty base list: `1 == 0 + 1` ✓
- `TestFilterVisibleActions.test_returns_all_actions_when_no_active_request`: `visible == actions` where both are `[]` ✓
- `TestRenderMenuGuidance` tests: check string presence only, not ordering ✓
- `tests/test_reverse_engineer.py`: tests the `reverse-engineer.py` script's logic, no dependency on menu ✓

**FR-010 in `context.md`:** Currently reads "the list contains `reverse-engineer.py`". Must be updated to reflect the list is now empty.

---

## External Benchmarking

Common CLI tool menu patterns (e.g., `git`, Homebrew, npm scripts) place status/context information at the top before the action list, so the developer sees the current state first and then the available actions. The proposed reordering aligns with this convention. Removing an action from a menu that is no longer needed is a routine UX hygiene operation with no external precedent concerns.

---

## Minimal Spikes and Experiments

No spikes required. The changes are confined to:
1. Setting `_SCRIPT_ACTIONS = []` in a well-understood module.
2. Reordering 10–15 lines of string-buffer writes in `render_menu()`.
3. Updating 3 test methods.
4. One sentence update in `context.md`.

All code paths are covered by the existing test suite; no experimental implementation is needed to de-risk the change.

---

## AI Copilot Suggestions

**Observation 1 — Scope is minimal and well-contained.**
The change touches exactly one runtime file (`menu.py`), one test file (`test_menu.py`), and one documentation file (`context.md`). No cross-file logic changes are required. The risk of regression is very low. Suggestion: implement atomically in a single commit to keep the diff readable.

**Observation 2 — Empty `_SCRIPT_ACTIONS` is a valid state but may surprise future maintainers.**
After removing Reverse Engineer, the base action list is `[]`. The menu will only show numbered actions when an active request exists (because `filter_visible_actions` injects `close-request`). A developer opening the menu with no active request will see only "0) Quit". This is a logically correct but potentially surprising UX. Suggestion: ensure the test for `test_no_glob_discovery` is updated with a clear comment reflecting that the list is intentionally empty, so future maintainers understand this is by design.

**Observation 3 — Render order change has no test coverage for ordering.**
`TestRenderMenuGuidance` checks for string presence only; no test verifies that "-- Next Step --" appears before the options list in the rendered output. The current tests will pass regardless of rendering order. Suggestion: add a test asserting that the `── Next Step ──` substring appears before any numbered action line in the rendered output. This prevents silent regression if the order is accidentally reverted. This is included in the plan as an optional but recommended test case.

**Observation 4 — `test_common.py` inconsistency is out of scope but worth noting.**
`.aib_brain/tools/test_common.py` contains `test_exclude_scripts_contains_new_entries` which asserts `EXCLUDE_SCRIPTS` exists in `menu.py` and contains `"reverse-engineer.py"`. This attribute was removed in a prior iteration. After this request, it becomes even more stale. The maintainer should consider deleting or fixing this test in a separate clean-up request to avoid confusion.

---

## Testing

- T1 — Hard-coded list is empty: Call `build_script_actions(tools_dir)`; assert `len(result) == 0`. Expected outcome: assertion passes with no items.

- T2 — Reverse Engineer absent from menu: Call `build_script_actions(tools_dir)`; assert `"reverse-engineer.py"` is not in the `scripts` list extracted from the result. Expected outcome: assertion passes.

- T3 — No-glob assertion updated: `test_no_glob_discovery` asserts `len(actions) == 0` with no second assertion on `actions[0]`. Expected outcome: test passes without `IndexError`.

- T4 — Ordering: `render_menu()` output must contain `── Next Step ──` before any line matching `r"^\s+[1-9]\d*\)"`. Expected outcome: `output.index("── Next Step ──") < output.index(first_numbered_option)`, or if no numbered option exists, the ordering assertion trivially passes.

- T5 — Close-request still injected: With an active request, `filter_visible_actions([], state)` returns a list of length 1 containing `close-request.py`. Expected outcome: assertion passes.

- T6 — Full pytest suite passes: Run `pytest tests/` with no active filter. Expected outcome: exit code 0, zero failures.

- T7 — Idempotency: Re-running analysis on the same request produces the same `request.md` structure. Expected outcome: second run does not alter mandatory sections beyond Assumptions/Plan/Documentation.

> T4 requires rendering `render_menu()` to a string buffer and comparing index positions. This is an automated assertion implementable with `pytest` and `io.StringIO`. No UAT scenarios required.

---

## Multi-Perspective Stakeholder Review

**Developer (menu user):**
Removing the Reverse Engineer option simplifies the menu. After the change, opening the menu without an active request will show only "0) Quit" as a numbered option. This is correct if the reverse-engineer capability is no longer needed from the menu surface, but could feel sparse. If the developer intends to re-add actions later, the empty `_SCRIPT_ACTIONS` list and the `build_script_actions()` function remain as the right extension point. The reordering improvement (guidance block before options) makes the recommended next action more prominent.

**AIB Maintainer:**
The change is low-risk. `reverse-engineer.py` is preserved on disk so the capability is not lost, only de-surfaced. The `_SCRIPT_ACTIONS` list remains the canonical extension point for adding future menu items. Test coverage for the ordering change (T4) is recommended but not strictly required to pass the existing suite.

**CI / Release pipeline:**
No impact. The change involves no CI workflow files. The `logs/next_version_changes.md` file will receive a curated bullet during implementation per workspace instructions.
