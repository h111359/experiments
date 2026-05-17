# Analysis: R-20260511-2019

## Executive Summary

- **Request ID:** R-20260511-2019

- **Request title:** Script prompt ops, integrate test_common, clean menu

- **High-level purpose:** Increase automation coverage of deterministic AIB operations by moving `test_common.py` to the standard test suite, scripting repetitive file operations currently performed inline by the AI agent in prompts, and removing two unused toggle options from `input.md` and all prompt files that reference them.

## Files Read During This Analysis Run

- `.aib_memory/requests_register.md`
- `.aib_memory/input.md`
- `.aib_memory/instructions.md`
- `.aib_memory/context.md`
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/prompts/aib-implement.md`
- `.aib_brain/prompts/aib-context.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `.aib_brain/tools/test_common.py`
- `.aib_brain/tools/create-request.py`
- `.aib_brain/tools/initialize.py`
- `.aib_brain/tools/menu.py`
- `.aib_brain/tools/common.py` (via grep — referenced from test_common.py imports)
- `.aib_brain/templates/request-template.md`
- `tests/conftest.py`
- `tests/test_initialize.py`
- `tests/test_menu.py`

## Research Results

### test_common.py placement inconsistency

`test_common.py` currently resides at `.aib_brain/tools/test_common.py`. The main test suite is under `tests/`. The `conftest.py` in `tests/` already adds `.aib_brain/tools/` to `sys.path` for importing AIB modules, so the relocated test file will be able to import from `common.py` without modification. No test file in `tests/` currently imports `test_common.py`; it is a standalone `unittest.TestCase` module that runs in isolation via `pytest` if present in the test path. The existing `conftest.py` also provides a `workspace_dir` fixture and a `_seed_workspace` helper that partially overlaps with the helper functions in `test_common.py`; these overlaps will need to be reconciled during integration (e.g., `test_common.py`'s `_setup_workspace` and conftest's `_seed_workspace` serve similar purposes but differ in scope).

### Scriptable prompt operations (identified by prompt review)

The following deterministic file operations are currently performed inline by the AI agent inside `aib-analysis.md`; they have no dedicated script:

1. **Archive `input.md`** — reads `.aib_memory/input.md`, creates `<request-folder>/inputs/` directory, writes content to `input-archive-<YYYY-MM-DD_HH-MI-SS>.md`. Pure file I/O, fully deterministic.
2. **Move attachments** — recursively walks `.aib_memory/attachments/`, moves each non-`.gitkeep` file to `<request-folder>/inputs/<relative-path>` using `shutil.move`. Deterministic file move.
3. **Reset `input.md`** to seed template — writes the fixed seed string with active request ID and title injected into the `## Active request` line. Requires reading the register to resolve active request; otherwise pure file write.

These three operations are always performed together in both the Auto-Request Creation Branch and the direct standard-flow reset; they naturally form a single cohesive script action.

### Toggle options scope

The strings `No changes — provide answer only` and `Skip analysis document generation` appear in:
- `.aib_brain/prompts/aib-analysis.md` (multiple references: toggle detection block, seed template strings, Auto-Request branch error check, step 8 reset string)
- `.aib_brain/tools/initialize.py` (seed template string in `_seed_core_memory`)
- `.aib_memory/input.md` (two toggle lines in `## Options`)
- `.aib_memory/context.md` (FR-007, architecture table — documentation only)
- `.aib_brain/README.md` (usage instruction referencing "No changes" toggle)
- `.aib_memory/archives/` (archived snapshots — not modified per scope)

All non-archive occurrences must be updated. The `context.md` and `README.md` updates are documentation tasks.

### Existing script pattern

All existing `.aib_brain/tools/` scripts follow a consistent pattern: `parse_args()`, `ensure_workspace()`, `ValidationError` for error handling, `write_text()` for output, and `print()` for success messages. New scripts must follow this exact pattern to remain consistent.

## Best Practices

- **Single Responsibility Principle for CLI tools:** Each script should do one thing. Industry practice (Unix philosophy, Python CLI tooling guidelines) recommends granular scripts over monolithic ones. However, when two operations are always performed together with no legitimate use case for calling one without the other, combining them into one script reduces accidental partial-state issues. For the archive-and-reset case, both operations (`archive input.md + move attachments` and `reset input.md`) are always triggered together in the analysis flow; a single script `finalize-input.py` is therefore preferable and reduces the chance the AI invokes only one half.

  *Applicability:* Apply for the new `finalize-input.py` script — combine archive, attachment-move, and reset into one atomic operation. This prevents a partial-state failure mode where input.md is archived but not reset.

- **Test colocation with project test suite:** Python ecosystem best practices (pytest documentation, Google Python Style Guide) require that all test files live in the designated test directory (`tests/`) and follow the `test_*.py` naming convention for auto-discovery. Placing tests inside a non-test tools directory violates test isolation and makes CI configuration unnecessarily complex.

  *Applicability:* Directly applicable — `test_common.py` must be moved to `tests/` and renamed consistently with the existing test file naming convention.

- **Feature flag removal discipline:** When an opt-in feature toggle is removed, all detection logic, error messages, seed templates, and documentation referencing that toggle must be updated atomically. Partial removal leaves dead conditional paths that are never exercised but still consume AI tokens and create confusion. The YAGNI principle supports removing features that have no demonstrated value.

  *Applicability:* Both toggle removals should be treated as a single atomic change: update all occurrence sites in one implementation pass.

## External Benchmarking

- **pytest's approach to test organization:** pytest recommends placing all tests under a top-level `tests/` directory or alongside source modules. AIB uses `tests/` as the single test directory. The `conftest.py` mechanism provides shared fixtures across all test files in `tests/`. Placing tests inside a non-test directory like `.aib_brain/tools/` means they are only discoverable if `pytest` is explicitly pointed there; `pytest tests/` (the standard invocation pattern) would miss them entirely. Moving `test_common.py` to `tests/` aligns with the pytest-recommended layout.

  *Takeaway:* Move test file to `tests/`; no pytest configuration change should be needed because `conftest.py` already adds the tools path to `sys.path`.

- **CLI script atomicity patterns (argparse/Click community):** In open-source Python CLI tooling (e.g., `click`, `typer`, common argparse patterns), operations that must execute together to avoid partial state are grouped into one command rather than separate sub-commands. This prevents scripts from being called in the wrong order by automated agents. For the AIB context, archiving input.md and resetting it are tightly coupled — resetting without archiving loses content; archiving without resetting leaves the AI loop in an inconsistent state. A single `finalize-input.py --workspace . --request-id <id>` script enforces the correct order atomically.

  *Takeaway:* Implement as a single script; name it `finalize-input.py` to reflect its role as the final input-processing step of an analysis run.

- **Removing dead code / unused feature flags (Martin Fowler, Refactoring):** Removing a feature toggle that has no active users eliminates a class of conditional logic bugs and reduces cognitive overhead for new contributors. The "No changes" and "Skip analysis" toggles appear from `context.md` history and prompt review to be rarely (if ever) used in practice; they are not tested in the test suite (`test_analysis_prompt_structure.py` may cover them, but removing them is the stated request). Removing them simplifies the `aib-analysis.md` prompt significantly, reducing AI token consumption per run.

  *Takeaway:* Remove both toggles completely; do not replace them with a "hidden" or "soft-disabled" alternative.

## Minimal Spikes and Experiments

No spike was conducted. All operations are fully deterministic file I/O with no external dependencies or ambiguous behaviors. The integration of `test_common.py` into `tests/` requires only path adjustment; the `conftest.py` sys.path configuration already handles the import. The scriptable operations identified (archive, move attachments, reset) are all implemented using the Python standard library functions already used elsewhere in `.aib_brain/tools/`. Uncertainty is sufficiently low.

## Implementation Alternatives

### Alternative 1: Two separate scripts — `archive-input.py` + `reset-input.py`

Create two scripts: one that archives `input.md` and moves attachments, one that resets `input.md` to the seed template. The AI calls them sequentially.

- **Trade-offs:** More modular; each script has a single responsibility. However, calling them in sequence creates a window where `input.md` is archived but not yet reset — if the AI fails between the two calls, state is inconsistent.
- **Codebase impact:** Two new files; two invocation blocks in prompt; slightly more prompt text.

### Alternative 2: Single combined script — `finalize-input.py` *(recommended)*

Create one script that atomically: (1) archives `input.md` and moves attachments, (2) resets `input.md` to the seed template with the active request ID and title injected. The AI calls it once after all analysis artifacts are written.

- **Trade-offs:** Slightly less granular, but eliminates the partial-state failure mode. The operations are logically inseparable — they always occur together.
- **Codebase impact:** One new file; one invocation block in prompt; cleaner prompt.

**Recommendation:** Alternative 2. Combining archive and reset into a single script enforces atomicity and reduces the number of AI invocation steps. The two operations have no legitimate use case for being called independently within the AIB workflow.

## AI Copilot Suggestions

**Observation 1 — test_common.py has overlapping setup helpers with conftest.py (maintainability risk):**
`test_common.py`'s `_setup_workspace` function and `conftest.py`'s `_seed_workspace` function serve similar purposes but differ in scope (the conftest version is more comprehensive, copying real templates). During integration, these must be reconciled rather than simply placing `test_common.py` in `tests/` and having two parallel workspace-setup helpers. The implementation task should explicitly compare the two and consolidate where possible to avoid test setup divergence.

**Observation 2 — Scope is well-bounded; execution risk is low:**
All four steps are concrete, localized changes: file move, new scripts, prompt edits, and two-line removal. The highest risk is the prompt edits (removing toggle logic from `aib-analysis.md`) — these sections have nested branching logic. Careful line-by-line editing with test coverage verification is needed. A test in `tests/test_analysis_prompt_structure.py` (if it currently validates for the presence of the toggle lines) would need updating.

**Observation 3 — The `finalize-input.py` script should handle the stub-equivalence check:**
Per `FR-003` (context.md), in the direct standard-flow reset, input.md archiving is skipped when the pre-reset content is stub-equivalent. The current AI logic handles this with inline reasoning. The new `finalize-input.py` script should encode this check in code (compare normalized content to the seed template) so the AI doesn't need to re-implement it on each run. This is a correctness improvement, not scope creep.

**Observation 4 — Scope appears correct for the stated goal:**
The four steps are necessary and sufficient to achieve the stated goal ("All deterministic operations should be executed by a ready in AIB python script to save tokens"). No unnecessary scope is present. One potential simplification: if the stub-equivalence check in `finalize-input.py` is deemed complex, it could be deferred to a follow-up request — but including it in this request avoids producing a script that is immediately incomplete relative to the prompt it replaces.
