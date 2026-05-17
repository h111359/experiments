## Goal
Define and enforce a consistent archiving behavior for `.aib_memory/input.md` so that non-stub reset events in the standard analysis flow always preserve the prior input content.

## Background
The current prompt flow archives `input.md` only in the Auto-Request Creation Branch. In the standard flow with amendment content present in `input.md`, there is no explicit archiving step before reset. This can lose traceability of the human-provided amendment text and create inconsistency between first-run and re-run lifecycle behavior.

## Scope
- Update the analysis workflow behavior so archiving of `input.md` is applied whenever a non-stub reset occurs in standard flow.

- Keep lifecycle semantics consistent across auto-request and standard request paths regarding preservation of operator input.

- Ensure resulting behavior remains deterministic and compatible with existing request/analysis/implement lifecycle tooling.

## Out of scope
- No redesign of request ID generation, register schema, or request state machine.
- No unrelated changes to implementation behavior outside input archiving/reset handling.
- No changes to CI release bookkeeping flows unless directly required by this request.

## Constraints
- Must preserve existing prompt conventions and required section structures.
- Must not introduce multiple active requests or break register validation rules.
- Must maintain compatibility with current repository layout and automation scripts.

## Success criteria
- The standard analysis flow archives `input.md` before non-stub reset events.
- Archive behavior is explicitly defined and testable for both standard and auto-request creation paths.
- Existing analysis execution remains deterministic and idempotent across re-runs.

## Assumptions
- A1: The required behavior adjustment is a prompt-spec clarification in `.aib_brain/prompts/aib-analysis.md` and does not require Python tool-script changes.
  - Risk if false: Prompt-only edits may not enforce runtime behavior if a conflicting script path exists.

- A2: "Non-stub" can be defined deterministically from the seed template state of `.aib_memory/input.md`.
  - Risk if false: Ambiguous interpretation can produce inconsistent archive behavior across runs.

- A3: Existing prompt-structure tests can enforce this lifecycle requirement with text assertions.
  - Risk if false: Additional end-to-end harnessing may be needed to catch semantic drift.

## Plan
### Task 1: Clarify standard-flow archive semantics
**Intent:** Define explicit, deterministic wording that standard-flow non-stub resets archive prior `input.md` content before reset.
**Outputs:** Updated prompt text in `.aib_brain/prompts/aib-analysis.md`.
**Procedure:**
1. Edit `.aib_brain/prompts/aib-analysis.md` to add a standard-flow archive-before-reset requirement scoped to non-stub input.
2. Edit `.aib_brain/prompts/aib-analysis.md` to state the condition for skipping archive when `input.md` is still at seed-template state.
3. Re-read `.aib_brain/prompts/aib-analysis.md` and verify the new requirement is deterministic and does not alter unrelated flow gates.
**Done Criteria:** Prompt text defines both archive and no-archive conditions unambiguously for direct standard-flow execution.
**Dependencies:** None.
**Risk Notes:** Undefined non-stub criteria could create inconsistent interpretation between runs.

### Task 2: Preserve branch boundaries and reset ordering
**Intent:** Ensure archive clarification does not change side-effect limits for toggle branches or final reset semantics.
**Outputs:** Branch-safe wording in `.aib_brain/prompts/aib-analysis.md`.
**Procedure:**
1. Inspect `.aib_brain/prompts/aib-analysis.md` and verify `No changes` still enforces exactly two file writes and immediate stop.
2. Inspect `.aib_brain/prompts/aib-analysis.md` and verify the standard-flow reset remains the last action when run directly.
3. Inspect `.aib_brain/prompts/aib-analysis.md` and verify `Skip analysis document generation` behavior remains unchanged apart from archive-condition clarity.
**Done Criteria:** No toggle branch receives unintended additional writes or altered control flow.
**Dependencies:** Task 1.
**Risk Notes:** Overbroad language can accidentally apply standard-flow archive logic to the `No changes` branch.

### Task 3: Add lifecycle regression assertions
**Intent:** Lock the clarified archive condition and branch guards with automated tests.
**Outputs:** Updated assertions in `tests/test_analysis_prompt_structure.py`.
**Procedure:**
1. Edit `tests/test_analysis_prompt_structure.py` to assert presence of explicit standard-flow archive-before-reset wording.
2. Edit `tests/test_analysis_prompt_structure.py` to assert wording preserves `No changes` two-write constraints.
3. Run `c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe -m pytest tests/test_analysis_prompt_structure.py` and review terminal output for pass/fail results in the command output stream.
**Done Criteria:** The prompt-structure suite passes with new archive-condition coverage.
**Dependencies:** Task 1, Task 2.
**Risk Notes:** Literal-fragment assertions can become brittle if wording changes without semantic drift.

### Task 4: Run related workflow regression tests
**Intent:** Confirm no collateral regression in adjacent input/question/artifact behaviors.
**Outputs:** Test evidence from related suites under `tests/`.
**Procedure:**
1. Run `c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe -m pytest tests/test_questions_in_input_md.py tests/test_artifact_placement.py` and capture results from terminal output.
2. Run `c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe -m pytest tests/test_menu.py -k "questions_pending or amendment_pending"` and capture results from terminal output.
3. Map any failure signatures from terminal output back to changed prompt wording in `.aib_brain/prompts/aib-analysis.md` before deciding remediation.
**Done Criteria:** Related suites pass, or failures are clearly triaged against changed semantics.
**Dependencies:** Task 3.
**Risk Notes:** Pre-existing instability in unrelated tests can mask real lifecycle regressions.

### Task 5: Update context and docs alignment
**Intent:** Keep product documentation synchronized with finalized archive semantics.
**Outputs:** Updated `.aib_memory/context.md` and aligned documentation list in `.aib_memory/request-R-20260510-0744.md`.
**Procedure:**
1. Edit `.aib_memory/context.md` to include standard-flow conditional archive behavior and preserve existing auto-request branch statements; acceptance test: both behaviors are explicitly documented without contradiction.
2. Edit `.aib_memory/context.md` to define non-stub reset terminology if introduced; acceptance test: the term appears with one clear definition and consistent usage.
3. Edit `.aib_memory/request-R-20260510-0744.md` (`## Documentation`) so every modified documentation/test file is listed; acceptance test: all changed files appear with rationale.
**Done Criteria:** Prompt, tests, and context describe one coherent archive lifecycle.
**Dependencies:** Task 1, Task 3.
**Risk Notes:** Context drift will reintroduce ambiguity in future analysis runs.

## Documentation
- .aib_brain/prompts/aib-analysis.md — Clarify deterministic standard-flow archive condition before non-stub reset.
- tests/test_analysis_prompt_structure.py — Add prompt-structure assertions for archive condition and branch safety.
- .aib_memory/context.md — Synchronize lifecycle documentation with the finalized archive semantics.
- .aib_memory/request-R-20260510-0744.md — Refresh request-scoped documentation index to match implemented file changes.

## Questions & Decisions
