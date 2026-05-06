## Executive Summary

- **Request ID:** R-20260417-1254

- **Request title:** Remove reverse engineer option from menu

- **Purpose:** The AIB interactive menu (`menu.py`) dynamically discovers Python scripts in `.aib_brain/tools/` that are not in `EXCLUDE_SCRIPTS`. `reverse-engineer.py` is currently discoverable and appears as a menu item. This conflicts with `FR-010` which restricts menu items to the three core prompt invocations. The request asks to remove it from the menu and to assess whether the script itself should be retained or deleted.

- **Assessment outcome:** `reverse-engineer.py` has a defined, ongoing role as an optional internal helper for `aib-context.md` (Phase 3 reverse-engineering mode). The `aib-context.md` prompt explicitly documents `You MAY use .aib_brain/tools/reverse-engineer.py` and specifies the prompt must work without it. The script itself generates a deterministic JSONL file inventory used for workspace scanning. It is NOT a user-facing action; it is a library-like helper. **Conclusion: retain the script, exclude it from the menu.**

- **Files examined:** `menu.py`, `reverse-engineer.py`, `aib-context.md`, `context.md`, `Concepts.md`, `references.md`, `test_menu.py`, `test_reverse_engineer.py`.

- **`request.md` sections added/updated in this run:** `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`.


---

## Domain Knowledge Essentials

- **AIB (AI Builder):** A minimal, model-agnostic framework for specification-driven development. It provides file-first workflows for managing requests, maintaining product documentation, and automating release bookkeeping.

- **Interactive menu (`menu.py`):** Terminal UI launcher displayed when the user runs `.aib_brain/run.bat` or `run.sh`. It surfaces tool scripts as numbered options and shows copy-paste-ready prompt invocations for the three core prompts. It does NOT expose lifecycle commands.

- **`EXCLUDE_SCRIPTS`:** A hard-coded set in `menu.py` that prevents named scripts from being returned by dynamic discovery. Scripts in this set are managed internally (by the AI agent or CI) and are not surfaced to end users.

- **Dynamic discovery:** `build_script_actions()` in `menu.py` scans `tools/*.py` for any script not in `EXCLUDE_SCRIPTS` and adds it as a numbered menu action. This is the mechanism by which `reverse-engineer.py` currently appears.

- **`reverse-engineer` action (Concepts.md):** Listed in the Concepts.md action contract as a supported user-triggered action with the description "Reverse engineer the workspace to populate editable documentation based on conventions." However, this high-level action is now implemented entirely via `aib-context.md`; the Python script `reverse-engineer.py` is an optional internal helper only.

- **`aib-context.md` prompt:** Synthesizes and fully replaces `.aib_memory/context.md`. Incorporates a reverse-engineering mode (Phase 3) for workspaces with no product-doc content. Optionally uses `reverse-engineer.py` to emit a JSONL inventory, but the prompt is designed to work without it.

- **`FR-010`:** Functional requirement: the menu displays copy-paste-ready prompt invocations for `aib-analysis.md`, `aib-implement.md`, and `aib-context.md`; it does NOT expose lifecycle commands or an exit option.


---

## Technical Knowledge & Terms

- **`EXCLUDE_SCRIPTS` (set):** A Python `set[str]` of script filenames defined at module level in `menu.py`. Scripts in this set are filtered out during `discover_tool_scripts()` execution. Adding `"reverse-engineer.py"` to this set is the single, non-invasive change required to remove it from the menu.

- **`discover_tool_scripts(tools_dir)`:** Iterates `tools_dir/*.py`, skips any script in `EXCLUDE_SCRIPTS`, returns the remaining list sorted. This is the dynamic discovery function in `menu.py`.

- **`build_script_actions(tools_dir)`:** Calls `discover_tool_scripts` and wraps each result into an action dict. Renumbers IDs sequentially after building the list.

- **`test_reverse_engineer_present` (test_menu.py:167):** A regression test that currently asserts `"reverse-engineer.py"` is NOT in `EXCLUDE_SCRIPTS` and IS in the discovered actions. This test was written to prevent accidental exclusion of the script. After this request's change, it directly conflicts with the new intended behavior and must be removed.

- **`test_excluded_scripts_absent` (test_menu.py:162):** A general test that iterates `EXCLUDE_SCRIPTS` and verifies none appear in discovered scripts. This test will continue to pass after `"reverse-engineer.py"` is added to `EXCLUDE_SCRIPTS` — no change needed.

- **`test_reverse_engineer.py`:** A separate test file covering the functional behavior of `reverse-engineer.py` itself (file inventory, exclusion, JSONL output). These tests test the script's logic — not the menu — and do NOT need to change if the script is retained.

- **JSON Lines (JSONL):** Output format used by `reverse-engineer.py`. One JSON object per line, each representing a file in the workspace inventory (fields: `path`, `size_bytes`, `mtime_epoch`, `extension`).

- **Evidence log:**

  | Evidence | Implication |
  | --- | --- |
  | `EXCLUDE_SCRIPTS` does not contain `"reverse-engineer.py"` | Script currently appears in the dynamic menu |
  | `aib-context.md` Phase 3 explicitly calls `reverse-engineer.py` optional | Script has remaining value as an internal helper |
  | `FR-010` restricts menu to three prompt invocations | Script should not appear as a menu item |
  | `test_reverse_engineer_present` asserts script is in menu | This test must be deleted after the change |
  | `test_reverse_engineer.py` tests script logic independent of menu | These tests remain valid and must continue to pass |

- **Files read:**
  - `.aib_brain/tools/menu.py`
  - `.aib_brain/tools/reverse-engineer.py`
  - `.aib_brain/prompts/aib-context.md`
  - `.aib_memory/context.md`
  - `.aib_brain/Concepts.md`
  - `.aib_memory/references.md`
  - `tests/test_menu.py`
  - `tests/test_reverse_engineer.py`


---

## Research Results

**Pattern: script exclusion via deny-list**

The existing `EXCLUDE_SCRIPTS` mechanism in `menu.py` is already the established pattern for hiding scripts from the dynamic menu. Scripts like `create-request.py`, `close-request.py`, `initialize.py`, and `common.py` are all excluded using this pattern. Adding `reverse-engineer.py` to this set follows the same established pattern without requiring new logic or refactoring.

**Pattern: regression test negation**

`test_reverse_engineer_present` was written as a regression guard for the opposite behavior — to ensure the script was visible in the menu. Now that the requirement changes, the test must be negated (or removed). The cleanest approach is removal since the general test `test_excluded_scripts_absent` will cover the new behavior transitively once `"reverse-engineer.py"` is in `EXCLUDE_SCRIPTS`.

**Pattern: optional internal helpers**

`common.py` is similarly an internal helper (excluded from the menu, used by other scripts). This confirms the established pattern: internal helpers and utilities live in `tools/` but are excluded from user-facing menu discovery. `reverse-engineer.py` fits this pattern.


---

## External Benchmarking

**Comparable pattern: CLI tool hiding via exclusion list**

In CLI toolkits (e.g., `click`, `argparse`-based launchers, `Makefile` targets), it is common practice to maintain an explicit exclusion or "internal" annotation for helper scripts that are not intended for direct user invocation. Examples:
- GNU `make` uses `.PHONY` and prefixes to hide internal targets.
- Click-based CLIs use `hidden=True` on commands.
- AIB already uses `EXCLUDE_SCRIPTS` for this purpose.

Takeaway: The deny-list approach is the idiomatic, low-complexity solution for this type of problem. Adoption is straightforward.

**Comparable pattern: optional plugin / helper tool design**

Tools like `pytest`, `pylint`, and similar Python frameworks allow optional plugins that enhance behavior when present but are not required. `reverse-engineer.py` follows this pattern: `aib-context.md` explicitly documents the script as optional. This is a well-established design that validates retaining the script while removing its menu exposure.

Takeaway: Retaining `reverse-engineer.py` as an optional helper while removing its user-facing menu entry is idiomatic and well-precedented in the Python tooling ecosystem.


---

## Minimal Spikes and Experiments

No spike was required. The change is:

1. A single-line set addition (`"reverse-engineer.py"`) to `EXCLUDE_SCRIPTS` in `menu.py`.
2. Deletion of one test method (`test_reverse_engineer_present`) in `test_menu.py`.

Both changes are directly supported by existing code patterns in the same files. The impact is deterministic, reversible, and has no external dependencies or uncertainty. The existing test suite (`test_menu.py` and `test_reverse_engineer.py`) provides sufficient coverage to validate the change post-implementation.
