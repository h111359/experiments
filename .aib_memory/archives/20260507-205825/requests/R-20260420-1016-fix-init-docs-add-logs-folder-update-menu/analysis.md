# Analysis: R-20260420-1016 — Fix init docs, add logs folder, update menu

## Executive Summary

- **Request ID:** R-20260420-1016

- **Title:** Fix init docs, add logs folder, update menu

- **High-level purpose:** Correct four defects/gaps in the AIB workspace: (1) initialization incorrectly creates `.aib_memory/docs/` and seeds legacy stub files; (2) initialization does not create `.aib_memory/logs/`; (3) the "Close current request" option was fully removed from the interactive menu instead of being made conditionally visible; (4) the prompt-reference block in the menu carries redundant label prefixes.

- **Scope of impact:** Two tool scripts (`initialize.py`, `menu.py`) and two test files (`test_initialize.py`, `test_menu.py`). No prompts, conventions, or external systems are affected.

- **Root cause — docs seeding:** `initialize.py` calls `ensure_doc_seed_files(workspace, requirements)` using `RequirementRef` objects reconstructed from `references-template.md`. Because the template titles ("AIB Context", "AIB Concepts") contain no " - " separator, the parser generates synthetic IDs `REQ-0001` and `REQ-0002` with empty locations, causing stub files to be written to `.aib_memory/docs/`. This is a legacy leftover from the pre-v1.2.0 design where `references.md` pointed to files under `docs/`.

- **Root cause — logs folder:** `initialize.py` never creates `.aib_memory/logs/`; `menu.py._make_log_path()` creates it lazily on first use, leaving the folder absent immediately after initialization.

- **Root cause — close-request:** When lifecycle scripts were moved to `EXCLUDE_SCRIPTS` in a prior refactor, `close-request.py` was included in the set, fully hiding it from the menu. The correct design is to show it only when an active request exists.

- **Root cause — label prefixes:** A prior implementation decision added "Analysis : ", "Implement: ", "Context  : " labels to the prompt-reference block for clarity. The request correctly identifies these as redundant given the prompt file names are self-describing.

- **Changes to `request.md` during this run:** Sections `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`, and `## Multi-Perspective Stakeholder Review` were written. `## Questions & Decisions` was left empty (no unresolvable unknowns identified).


## Domain Knowledge Essentials

- **AIB (AI Builder):** A file-based, model-agnostic framework for specification-driven software development. All workflow state is stored in `.aib_memory/`; reusable assets live in `.aib_brain/`.

- **Initialization:** The one-time (or idempotent repeated) action that seeds `.aib_memory/` with the required folder structure and default files (`requests_register.md`, `references.md`, `context.md`, `input.md`).

- **References register (`references.md`):** A markdown table that lists files AIB may read or edit, indexed by `ref_id`. It is seeded from `references-template.md`.

- **Docs folder (`.aib_memory/docs/`):** A legacy directory from pre-v1.2.0 that held per-requirement stub files. No longer part of the AIB design as of v1.2.0; its continued creation by `initialize.py` is a bug.

- **Logs folder (`.aib_memory/logs/`):** The designated directory for per-action log files written by `menu.py`. Its absence after initialization means the first log write implicitly creates it, making the workspace structure non-deterministic before first menu use.

- **Interactive menu (`menu.py`):** A terminal UI that surfaces AIB tool scripts as numbered choices. It is the primary way users invoke AIB actions without directly calling Python scripts.

- **EXCLUDE_SCRIPTS:** A set in `menu.py` listing scripts that must not appear in the auto-discovered action list. Currently includes `close-request.py`, which should instead be conditionally visible.

- **Lifecycle scripts:** `create-request.py` and `close-request.py`; these manage the single-active-request invariant. Creating a request is AI-prompt-driven; closing should remain user-accessible via menu.

- **Single-active-request invariant (FR-001):** At most one request may be in `Active` state at any time. The close-request menu item must not violate this.


## Technical Knowledge & Terms

- **`initialize.py`:** Seeds `.aib_memory/`. Key functions used: `ensure_doc_seed_files` (creates stub docs — to be removed from call chain), `seed_references_from_product_doc` (returns `(references_md, requirements)` tuple — `requirements` return value will be ignored with `_`).

- **`ensure_doc_seed_files(workspace, requirements)`:** Located in `common.py`. Iterates over `RequirementRef` objects and writes stub `.md` files under `.aib_memory/docs/<location>/<req_id>.md`. When `location` is empty (as with the current template), path collapses to `.aib_memory/docs/<req_id>.md`.

- **`seed_references_from_product_doc(workspace)`:** Located in `common.py`. Reads `references-template.md`; if title column contains no " - " separator, generates `req_id = REQ-<n>` fallback IDs. Returns `(str, List[RequirementRef])`.

- **`RequirementRef`:** Frozen dataclass in `common.py` with fields `req_id`, `title`, `location`. Used only by `ensure_doc_seed_files`.

- **`menu.py._make_log_path(action_id, workspace)`:** Creates `.aib_memory/logs/` lazily with `log_dir.mkdir(parents=True, exist_ok=True)`. Post-fix, the directory will already exist from initialization.

- **`filter_visible_actions(actions, state)`:** In `menu.py`. Currently a pass-through; will be updated to conditionally append `_CLOSE_REQUEST_ACTION` when `state.has_active_request`.

- **`MenuState`:** Frozen dataclass with `active_request_id`, `active_request_folder`, `active_request_title`. Property `has_active_request` returns `True` when `active_request_id` is non-None and non-empty.

- **`EXCLUDE_SCRIPTS`:** Module-level set in `menu.py`. `close-request.py` will remain in this set (preventing auto-discovery) but a hardcoded action dict will be conditionally appended by `filter_visible_actions`.

- **`_REFRESH_ACTION`:** Sentinel dict appended by `choose_action` after `filter_visible_actions`; close-request action must be inserted before it.

- **`render_menu(state, script_actions, selected_index)`:** Buffers the entire menu to `io.StringIO` and flushes in one write. Prompt-reference block is inline inside this function. `print_prompt_reference()` is a standalone function with the same content (used for standalone display, less critical but should also be updated for consistency).

- **Files read during this analysis:**
  - `.aib_brain/tools/initialize.py`
  - `.aib_brain/tools/menu.py`
  - `.aib_brain/tools/common.py`
  - `.aib_brain/tools/create-request.py`
  - `.aib_brain/Concepts.md`
  - `.aib_memory/context.md`
  - `.aib_memory/references.md`
  - `.aib_brain/templates/references-template.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/conventions/analysis-convention.md`
  - `tests/test_initialize.py`
  - `tests/test_menu.py`


## Research Results

**Pattern: Lazy vs. eager directory creation**

The AIB workspace uses `exist_ok=True` for all directory creation (verified in `initialize.py` and `common.py.write_text`). The pattern of creating all required directories during initialization (eager) rather than on first use (lazy) is consistent with ADR-0002 (fail-closed convention enforcement) and produces a deterministic workspace layout. All existing directories (`requests/`) are created eagerly; `logs/` should follow the same pattern.

**Pattern: Conditional menu item visibility**

The current `filter_visible_actions` is a pass-through and the docstring explicitly states "lifecycle filtering is no longer needed." This needs to be updated. The pattern of evaluating state inside `filter_visible_actions` on each menu loop iteration is already supported by the architecture — `choose_action` calls `resolve_menu_state` on every loop, then passes `state` to `filter_visible_actions`. No architectural changes are needed; only the function body changes.

**Pattern: Action dict schema**

All menu actions use the same dict schema: `id`, `title`, `description`, `script`, `destructive`, `parameters`. The `parameters` list uses `name`, `flag`, `type`, `required`, `default`, `prompt`, `hint`. The close-request action needs only the `workspace` parameter (the script resolves the active request from the register internally).

**Pattern: Test coverage for init artifacts**

`test_initialize.py` tests confirm creation of `requests/`, `requests_register.md`, `references.md`, and `input.md`. There are no tests for `docs/` presence or absence, and no test for `logs/`. The test for `test_creates_aib_memory_structure` asserts `requests` dir exists but does not assert other dirs. New tests will follow the same pattern (temp dir + `_make_brain_only_workspace` + `_run_initialize`).

**Pattern: Test coverage for menu filter**

`TestFilterVisibleActions::test_lifecycle_scripts_not_in_actions` asserts that `close-request.py` is NOT in `build_script_actions`. This will still be true — the close-request action is added by `filter_visible_actions`, not by `build_script_actions`. The assertion in `test_lifecycle_scripts_absent` on `build_script_actions` also remains valid. The tests that must change are those asserting that `filter_visible_actions` is a pure pass-through.


## External Benchmarking

**Comparable pattern: Lazy vs. eager directory initialization in CLI tools**

Many CLI project scaffolding tools (e.g., Poetry, Pipenv, npm init) create all required subdirectories during initialization rather than lazily. The rationale is that a deterministic workspace layout aids tooling, IDE integration, and `.gitignore` authoring. AIB's current partial eagerness (creates `requests/` but not `logs/`) is inconsistent with this well-established practice. Adoption: apply the same eager pattern to `logs/`.

**Comparable pattern: Conditional menu item visibility by application state**

Terminal UI frameworks such as `curses`-based menus and prompt_toolkit consistently show/hide menu items based on application state rather than relying on static exclusion lists. The approach of re-evaluating visible actions on each render cycle (AIB's current model) is architecturally correct and widely used. Adaptation: extend the existing state-aware filter rather than introducing a new mechanism.

**Comparable pattern: Removing redundant label decorators from CLI outputs**

Tools such as `git status`, `kubectl`, and `cargo` have progressively removed redundant field labels from their outputs in favour of layout-based context (indentation, colour, ordering). The AIB prompt-reference block similarly relies on layout and file-name convention, making the "Analysis : " labels superfluous. Adoption: remove the labels; the file names are self-documenting.


## Minimal Spikes and Experiments

**Spike: Does `Path("") / "REQ-0001.md"` collapse as expected on Windows?**

- Hypothesis: `(workspace / ".aib_memory" / "docs" / Path("") / "REQ-0001.md")` resolves to `workspace/.aib_memory/docs/REQ-0001.md` on both Windows and Unix.
- Approach: Traced `common.py.sanitize_location_to_path("")` which returns `""` (empty string joined is `""`); `Path("")` resolves to `.` on Python 3.10, so the path is `workspace/.aib_memory/docs/REQ-0001.md`.
- Outcome: Confirmed — verified by reading the `pathlib` documentation and the `sanitize_location_to_path` implementation. `"".split("/")` yields `[""]`; filtering empty parts yields `[]`; joining yields `""`.
- Conclusion: The legacy docs seeding bug is confirmed to produce `.aib_memory/docs/REQ-0001.md` and `.aib_memory/docs/REQ-0002.md` on all platforms.

**Spike: Does removing `ensure_doc_seed_files` call break any other code path?**

- Hypothesis: `ensure_doc_seed_files` is only called from `initialize.py`; removing the call is safe.
- Approach: Searched the workspace for calls to `ensure_doc_seed_files` using file content scan.
- Outcome: The function is defined in `common.py` and imported + called only in `initialize.py`. No other script or prompt references it.
- Conclusion: Removing the call and the import in `initialize.py` is safe and complete.
