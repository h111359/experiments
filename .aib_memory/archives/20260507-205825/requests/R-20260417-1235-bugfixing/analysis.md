## Executive Summary

- **Request ID:** R-20260417-1235

- **Request title:** bugfixing

- **High-level purpose:** Resolve two residual bugs that surfaced after the R-20260417-0903 implementation — a fatal menu error in any repo and a missing `input.md` artifact in the current workspace.

- **Bug 1 — "ERROR: No actions available":** `reverse-engineer.py` is listed in `EXCLUDE_SCRIPTS` in `menu.py`. Because every `.py` file in `tools/` is either lifecycle, utility, or `reverse-engineer.py`, `discover_tool_scripts()` always returns an empty list. When `total_items == 0`, `choose_action()` raises `SystemExit("ERROR: No actions available")`.

- **Bug 2 — Missing `input.md`:** `initialize.py` was updated in R-20260417-0903 to seed `.aib_memory/input.md`. The current workspace was already initialized before this change, and `ensure_memory_initialized_if_missing()` in `menu.py` only fires when `.aib_memory/` is completely absent — it does not reconcile individual missing files inside an existing memory directory.

- **Root cause of Bug 1:** `reverse-engineer.py` was in `EXCLUDE_SCRIPTS` prior to R-20260417-0903. That request added `create-request.py` and `close-request.py` to the set but did not remove `reverse-engineer.py`, even though the stated scope required "retain interactive functionality for remaining non-lifecycle scripts (e.g., `reverse-engineer.py`)".

- **Root cause of Bug 2:** No mechanism in AIB forces reconciliation of individual missing `.aib_memory/` files when the directory already exists. After upgrading `initialize.py`, the operator must manually re-run it (or the gap persists).

- **Sections added/updated in `request.md`:** Goal, Background, Scope, Out of scope, Constraints, Success criteria (structured from raw text), plus Assumptions, Plan, Testing, Documentation, Code and Asset Scan for Impacted Components, Internal Review of Request and Product Docs, Multi-Perspective Stakeholder Review.

---

## Domain Knowledge Essentials

- **AIB (AI Builder):** Minimal, model-agnostic framework for specification-driven development. Organises work in requests tracked in `.aib_memory/requests_register.md`.

- **Request:** Unit of work in AIB. Has lifecycle states `Active` → `Closed`. Exactly one `Active` request may exist at a time.

- **`.aib_brain/`:** Framework assets (prompts, conventions, templates, tool scripts). Never modified by tool scripts; replaceable as a unit on upgrade.

- **`.aib_memory/`:** Workspace-specific artifacts. Persists across `.aib_brain/` upgrades. Contains `input.md`, `context.md`, `references.md`, `requests_register.md`, and the `requests/` subtree.

- **`EXCLUDE_SCRIPTS`:** A Python `set` constant in `menu.py` listing `.py` file names that `discover_tool_scripts()` will silently skip when building the interactive menu.

- **`input.md`:** Ephemeral user-agent communication file. Introduced in v1.2.0. Seeded by `initialize.py`; read by `aib-analysis.md`; archived per request; reset after processing. Its absence blocks the analysis toggle detection step.

- **Impacted roles:** Developer (blocked from using the CLI menu and from running `aib-analysis.md`). AIB Maintainer (responsible for keeping `EXCLUDE_SCRIPTS` accurate after scope changes).

- **Business processes touched:** "Execute analysis workflow" and "AIB Command Menu" are both broken by these bugs.

---

## Technical Knowledge & Terms

- **`menu.py`:** Interactive CLI launcher. Dynamically discovers tool scripts from `tools/*.py`, excluding names in `EXCLUDE_SCRIPTS`. Renders an arrow-key navigable menu. Writes per-action log files to `.aib_memory/logs/`.

- **`discover_tool_scripts(tools_dir)`:** Globs `tools_dir/*.py`, filters out `EXCLUDE_SCRIPTS`, returns sorted list of filenames. Returns empty list if all files are excluded — which is the direct trigger for Bug 1.

- **`choose_action()`:** Calls `build_script_actions()` → `filter_visible_actions()`. If `total_items == 0`, raises `SystemExit("ERROR: No actions available")` instead of looping. This terminates the process.

- **`ensure_memory_initialized_if_missing(workspace, ...)`:** Runs `initialize.py` if and only if `workspace/.aib_memory` does not exist. Does not inspect individual files inside an existing `.aib_memory/`. This is the guard that fails to create `input.md` in the upgrade scenario.

- **`initialize.py`:** Idempotent seed script. Creates `.aib_memory/` subtree. For each managed file, checks existence before writing; skips with a log message if already present. Running it against an existing workspace with a missing `input.md` will create `input.md` without touching other files.

- **`reverse-engineer.py`:** Non-lifecycle tool script that walks the workspace and emits a JSON Lines file inventory for use by `aib-context.md`. It is the only `.py` file in `tools/` that should appear in the interactive menu.

- **Files read during analysis:**
  - `.aib_brain/tools/menu.py`
  - `.aib_brain/tools/initialize.py`
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_memory/context.md` (REF-0001)
  - `.aib_brain/Concepts.md` (REF-0002)
  - `.aib_memory/requests/R-20260417-0903-request-improvement/implementation.md`
  - `.aib_memory/requests/R-20260417-0903-request-improvement/request.md`
  - `tests/test_menu.py`
  - `tests/test_initialize.py`
  - `.aib_memory/requests_register.md`

- **Non-functional attributes:** Both fixes are low-risk, single-file changes. No network, cloud, or external system involvement. All changes are local and reversible via VCS.

- **Evidence log:**

  | Evidence | Implication |
  | --- | --- |
  | `EXCLUDE_SCRIPTS` in `menu.py` includes `"reverse-engineer.py"` | Every `.py` in `tools/` is excluded → 0 actions → fatal error |
  | `discover_tool_scripts` returns empty list with current EXCLUDE_SCRIPTS | Confirmed by code inspection; no runtime ambiguity |
  | R-20260417-0903 scope: "retain interactive functionality for remaining non-lifecycle scripts (e.g., `reverse-engineer.py`)" | The intended fix was not applied; `reverse-engineer.py` must be removed from EXCLUDE_SCRIPTS |
  | `.aib_memory/` directory exists; `input.md` absent | Bug 2 confirmed; `ensure_memory_initialized_if_missing` will not fire |
  | `initialize.py` has idempotent `input.md` seeding block | Re-running `initialize.py --workspace .` will create `input.md` without touching other files |
  | No test in `test_menu.py` asserts `reverse-engineer.py` IS in the menu | Regression risk; a positive-presence test should be added |

---

## Research Results

**Pattern scan — CLI tool discovery exclusion lists:**

Existing prior requests in this workspace establish the pattern: `EXCLUDE_SCRIPTS` is the canonical mechanism for hiding scripts from the menu. R-20260320-0906 and R-20260403-0939 both touched menu behavior. Neither added a positive-presence regression test for discoverable scripts. The absence of such a test allowed the `reverse-engineer.py` regression to go undetected in R-20260417-0903.

**Pattern scan — workspace initialization gaps:**

R-20260404-1826 and R-20260415-2247 both modified `.aib_memory/` structure. Neither introduced a reconciliation mechanism for existing workspaces when new managed files are added. The current `ensure_memory_initialized_if_missing` guard is strictly a cold-start guard, not an upgrade reconciler. This is an accepted architectural pattern in AIB (ADR-0003: brain/memory separation); upgrades to `initialize.py` implicitly require a manual re-run.

**Conclusion:** Both fixes are point corrections requiring no new architectural decisions. A positive-presence test for `reverse-engineer.py` in `test_menu.py` is the only net-new artifact beyond the two targeted fixes.

---

## External Benchmarking

**Benchmark 1 — Python CLI frameworks (Click, Typer) plugin discovery:**

Click and Typer both support dynamic command/plugin discovery via entry points. A consistent industry pattern is to show an empty state message rather than terminate fatally when no plugins are discovered. The common approach is a graceful "no commands registered" message with actionable guidance. AIB's current behavior (fatal `SystemExit`) is stricter but acceptable because the invariant "at least one non-excluded script exists in `tools/`" should always hold by design. The fix (removing `reverse-engineer.py` from EXCLUDE_SCRIPTS) restores that invariant.

- Key takeaway: Exclusion lists and allowlists in CLI launchers must be audited whenever the tool inventory changes. Automated tests asserting positive membership are the recommended safeguard.

- Adoption decision: The AIB fix follows this pattern — remove from exclusion set + add positive test. No need to adopt a full plugin framework.

**Benchmark 2 — Idempotent workspace reconciliation (Poetry, Cookiecutter, npm init):**

Tooling in Python packaging (Poetry `add`, `npm init --yes`) and scaffolding (Cookiecutter `--overwrite-if-exists`) follows the pattern of detecting and adding missing files without destroying existing state. Poetry specifically reconciles `pyproject.toml` presence on every invocation. The AIB approach (check-exists-before-write in `initialize.py`) matches this pattern. The gap is that `initialize.py` is not automatically invoked in upgrade scenarios.

- Key takeaway: Mature scaffolding tools either auto-detect drift on startup or provide an explicit "sync" command. AIB does not have an upgrade sync command; the recommended workaround is documented operator steps (re-run `initialize.py`).

- Adoption decision: No new sync command is in scope for this request. The fix is to run `initialize.py` once for the affected workspace.

---

## Minimal Spikes and Experiments

No spike was conducted. Both root causes were identified deterministically by code inspection:

- Bug 1: Presence of `"reverse-engineer.py"` in `EXCLUDE_SCRIPTS` and absence of any other discoverable `.py` file is directly observable in `menu.py` lines 18–28. The fix is a single-line set membership removal.

- Bug 2: Absence of `input.md` in `.aib_memory/` was confirmed by directory listing. `initialize.py`'s idempotent seeding logic (lines 55–65) confirms re-running it will create the missing file without side effects.

Uncertainty was low enough across both issues that experimentation would not change the remediation approach.
