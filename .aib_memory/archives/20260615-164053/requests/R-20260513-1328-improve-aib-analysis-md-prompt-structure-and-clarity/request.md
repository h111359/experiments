## Goal

Rewrite `.aib_brain/prompts/aib-analysis.md` to be well-structured, consistent, human-readable, and clearly defined — while preserving all existing behavior. Additionally, introduce two new requirements:
1. The analysis document must explicitly capture all decision-point cases eligible for Q-block generation.
2. The `## Questions & Decisions` section in `request.md` must be renamed to `## Decisions` and must record only the questions actually asked and the answers chosen (resolved Q&A log), not pending Q-blocks.

## Background

The current `aib-analysis.md` prompt functions correctly but is difficult to navigate as a human-readable reference. Rules are scattered across prose paragraphs, workflow steps lack consistent enumeration, and external scripts and conventions are referenced inline without structured documentation. Two new behavioral requirements (explicit decision-point capture in the analysis document, and a semantic change to `## Questions & Decisions` in `request.md`) have been identified and must be incorporated alongside the structural rewrite.

## Scope

- Rewrite `.aib_brain/prompts/aib-analysis.md`: improve structure, consistency, step enumeration, wording, and explicit documentation of external dependencies (scripts, conventions). Preserve all existing logic and behavior.

- Update the analysis document format: include an explicit enumeration of all decision-point categories (cases) for which Q-blocks may be generated, as a dedicated subsection or table.

- Rename `## Questions & Decisions` to `## Decisions` in `.aib_brain/conventions/request-convention.md` and update its content semantics: `## Decisions` records only resolved Q&A (question asked + answer applied), not pending Q-blocks.

- Update `.aib_brain/prompts/aib-analysis.md` to write resolved Q&A to `## Decisions` in `request.md` instead of to `## Questions & Decisions`.

- Audit and update all cross-references to `## Questions & Decisions` in any other prompt or convention file.

- Investigate and fix the root cause that suppresses Q-block generation even when genuine implementation alternatives exist: invert the Q-block default philosophy (default-to-ask instead of default-to-resolve-autonomously), tighten the mandatory pre-check to require the answer to be explicitly stated rather than merely determinable, and add a mandatory Decision Fork Enumeration step requiring explicit ask/resolve tagging for every identified fork.

## Out of scope

- Changes to `aib-implement.md` beyond updating any cross-reference to the renamed section heading.

- Changes to `create-request.py`, `close-request.py`, or other tool scripts beyond plain-text reference updates (no logic changes).

- Changes to the analysis document's 8 mandatory sections structure.

- Changes to the `## Questions` section mechanics in `input.md` (Q-block format, Answer Application Sub-flow).

- Changes to `aib-context.md`.

## Constraints

- All existing behavior of `aib-analysis.md` must be preserved; no logic may be removed or silently altered.

- The renamed `## Decisions` section must remain parseable by existing tools (tools match section headings as plain text; renaming is safe if all references are updated consistently).

- Output must remain valid Markdown.

- The rewritten prompt must comply with all rules in `.aib_brain/conventions/` that apply to prompt files.

## Success criteria

- The rewritten `aib-analysis.md` has clear, numbered workflow steps; explicit enumeration of external scripts and convention files; and consistent formatting throughout.

- Every analysis document produced by the new prompt explicitly lists all decision-point categories eligible for Q-block generation via a `### Decision Points Catalog` in `## Implementation Alternatives`.

- `## Questions & Decisions` is renamed `## Decisions` in `request-convention.md` and in the prompt.

- `## Decisions` in `request.md` records resolved Q&A entries; no pending Q-blocks appear in this section.

- All cross-references to `## Questions & Decisions` in other prompts and conventions are updated to `## Decisions`.

- The rewritten prompt uses "default-to-ask" philosophy: autonomous resolution requires an explicit justification documented in the Decision Points Catalog.

- The mandatory pre-check requires an answer to be "explicitly and unambiguously stated" in a named source — not merely inferable.

- A mandatory Decision Fork Enumeration step tags every fork as `ask | resolve-autonomously` before Q-block generation.

- All existing automated tests pass after the changes.

## Assumptions

- A1: The rewrite must preserve all exact strings tested by `tests/test_analysis_prompt_structure.py` (e.g., `"evaluate whether `.aib_memory/input.md` is in a non-stub state"`, `"archive the pre-reset `input.md` content"`, `"If stub-equivalent: skip archive creation for this standard-flow reset."`, `"All 10 mandatory sections"`, `"#### Outputs"`, `"ecursively"`).
  - Risk if false: Immediate test failures on all string-assertion tests in `TestStandardFlowInputArchivingSemantics` and related classes.

- A2: No tool scripts (`.aib_brain/tools/*.py`) reference `## Questions & Decisions` as a section heading to read or parse — only `aib-analysis.md` and the two convention files do.
  - Risk if false: Renaming the section without updating scripts would cause a silent data-loss bug in any script that searches for that heading.

- A3: The Decision Points Catalog is implemented as a mandatory `### Decision Points Catalog` subsection within the `## Implementation Alternatives` section of the analysis document (not as a new top-level section).
  - Risk if false: If placed as a new top-level section, it would violate the 8-section analysis convention and require a convention change with broader impact.

- A4: `## Decisions` in `request.md` records resolved Q&A using the existing Q-block format (question text + chosen option marked `[x]` + `> Answer:` populated) rather than a new format.
  - Risk if false: If a new format is required, additional test updates and convention re-edits would be needed.

- A5: `context.md` will be regenerated via `aib-context.md` after implementation; its stale references to `## Questions & Decisions` do not need manual patching.
  - Risk if false: Stale context.md may mislead a future analysis run if context regeneration is skipped.

- A6: The Q-block suppression root cause is entirely in the prompt language (mandatory pre-check scope and autonomous-fallback default), not in tool scripts or convention files. Fixing it requires only prose rewording within `aib-analysis.md`.
  - Risk if false: If a tool script also suppresses Q-blocks, additional code changes outside the prompt would be needed.

- A7: The philosophy inversion (default-to-ask) applies only when the answer is not *explicitly and unambiguously stated* in a named, specific section of context.md or convention files — not merely consistent with or inferable from those files. This tightens the pre-check without removing it.
  - Risk if false: If the tightening is too aggressive, the AI may ask redundant questions that context.md clearly resolves.

## Plan

### Task 1: Rewrite `aib-analysis.md` with improved structure

#### Intent
Restructure and reword `.aib_brain/prompts/aib-analysis.md` to use numbered steps, explicit preamble, clear section breaks, and a Decision Points Catalog requirement — while preserving all existing logic and test-assertion strings.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` (full content replacement)

#### Procedure
Read `.aib_brain/prompts/aib-analysis.md` in full to capture every rule, step, and behavioral detail.

Redesign the document structure: add a preamble block (Goal, Inputs table, External Dependencies table, Outputs table), convert the Mandatory Preflight to a numbered list (steps 1–9), restructure the Auto-Request Creation Branch as a numbered sub-procedure (steps 1–8), restructure the Standard Analysis Flow as a numbered procedure, restructure Output Part 1 (analysis document) and Output Part 2 (request.md updates) as explicit output contracts.

Add a `### Decision Points Catalog` requirement to the Output Part 1 rules: the `## Implementation Alternatives` section of every generated analysis must contain a `### Decision Points Catalog` table enumerating all Q-block-eligible categories, their trigger conditions, and whether a Q-block was raised for this run.

Invert the Q-block default philosophy: change the mandatory pre-check wording from "verify the answer is not already determinable from context.md, convention files, or instructions.md" to "verify the answer is explicitly and unambiguously stated in a named, specific section of context.md or convention files — not merely inferable." Change the ambiguity detection default from "resolve all other ambiguities autonomously" to "ask unless the answer is explicitly stated in the workspace; document the justification for autonomous resolution in the Decision Points Catalog." Add a mandatory Decision Fork Enumeration step: before Q-block generation, enumerate all identified decision forks and tag each as `ask | resolve-autonomously`; generate Q-blocks for all `ask`-tagged forks; record all forks (including `resolve-autonomously` ones) in the Decision Points Catalog with a rationale.

Update all references to `## Questions & Decisions` in the rewritten prompt: replace the `### Section: \`## Questions & Decisions\`` output contract header with `### Section: \`## Decisions\``; update the backward-compatibility note to state the rename; update the auto-creation branch step 5 ten-section list to use `## Decisions` in place of `## Questions & Decisions`; update the inline reference in the Plan rules paragraph.

Verify that all required test-assertion strings are present verbatim in the new document and all prohibited strings are absent. Run `python -m pytest tests/test_analysis_prompt_structure.py -v` against `.aib_brain/prompts/aib-analysis.md` and confirm 0 failures.

#### Done criteria
- `.aib_brain/prompts/aib-analysis.md` contains a preamble section listing inputs, external dependencies, and outputs.
- All preflight steps are numbered 1–N with no gaps.
- The two execution branches are clearly separated and labeled.
- The mandatory pre-check uses "explicitly and unambiguously stated" language (not "determinable").
- The ambiguity detection rule defaults to asking rather than resolving autonomously.
- A mandatory Decision Fork Enumeration step exists before Q-block generation.
- `"All 10 mandatory sections"` appears in the auto-creation branch step that validates section presence.
- `"#### Outputs"` appears in the Plan task schema.
- `"ecursively"` appears in the attachments scan step.
- `"evaluate whether `.aib_memory/input.md` is in a non-stub state"` appears in the standard-flow final step.
- `"archive the pre-reset `input.md` content"` appears in the standard-flow final step.
- `"If stub-equivalent: skip archive creation for this standard-flow reset."` appears in the standard-flow final step.
- `"## Questions & Decisions"` does NOT appear as a section heading in the document (only `"## Decisions"` is used).
- `tests/test_analysis_prompt_structure.py` passes with 0 failures.

#### Dependencies
None

#### Risk notes
The exact test-assertion string check requires literal string preservation. The rewrite must treat each asserted string as a verbatim constraint — restructuring must work around them, not through them. The philosophy inversion changes behavioral output; manually verify Q-block generation on a test request after the rewrite.

---

### Task 2: Update `request-convention.md` — rename section 10 and update semantics

#### Intent
Rename section 10 from `## Questions & Decisions` to `## Decisions` and redefine its content as a resolved-Q&A log.

#### Outputs
`.aib_brain/conventions/request-convention.md` (section 10 updated)

#### Procedure
Read `.aib_brain/conventions/request-convention.md` sections 9–10 (lines ~100–130) to understand the current definition.

Replace the section 10 heading `## Questions & Decisions` with `## Decisions`.

Replace the content description: remove the Q-block pending-questions format definition (checkbox options, recommended marker, Answer field for incoming questions). Replace with: `## Decisions` records one entry per question that was asked to the developer and answered. Each entry uses the format: `**Q<nnn>:** <question text> → **Chosen:** <chosen option text>`. Entries are appended by `aib-analysis.md` when applying answered Q-blocks; they are never removed after being written.

Update the re-run preservation rule (line 118): remove the rule about applying answered questions to `request.md` sections and appending new unanswered questions — this behavior now applies only to `input.md ## Questions`. The re-run rule for `## Decisions` is: append-only; never modify or remove existing entries.

#### Done criteria
- `request-convention.md` section 10 heading is `## Decisions`.
- Section 10 body defines the entry format for resolved Q&A (question + chosen answer) and the append-only rule.
- No reference to `## Questions & Decisions` remains in `request-convention.md`.
- The old Q-block pending-questions format definition is absent from section 10.

#### Dependencies
None

#### Risk notes
The convention change affects how future `aib-analysis.md` runs write to `request.md`. Consistency with Task 1 is required — both files must use `## Decisions` semantics simultaneously.

---

### Task 3: Update cross-reference in `analysis-convention.md`

#### Intent
Replace the stale `## Questions & Decisions` reference in `analysis-convention.md` with `## Decisions`.

#### Outputs
`.aib_brain/conventions/analysis-convention.md` (line ~232 updated)

#### Procedure
Read `.aib_brain/conventions/analysis-convention.md` around line 232 to locate the exact line containing `## Questions & Decisions`.

Replace `request.md` -> `## Questions & Decisions`` with `request.md` -> `## Decisions\`` (or equivalent surrounding text).

Verify no other occurrence of `## Questions & Decisions` remains in the file.

#### Done criteria
- `analysis-convention.md` contains no occurrence of `## Questions & Decisions`.
- The replacement text correctly points to `## Decisions` in `request.md`.

#### Dependencies
None

#### Risk notes
Low risk — single occurrence, targeted replacement.

---

### Task 4: Add automated tests for the rename

#### Intent
Add regression tests asserting that `## Questions & Decisions` is absent from the rewritten prompt and convention, and that `## Decisions` is referenced correctly.

#### Outputs
`tests/test_analysis_prompt_structure.py` (new test class appended)

#### Procedure
Read `tests/test_analysis_prompt_structure.py` to understand the existing test class structure and locate the end of the file.

Append a new test class `TestDecisionsSectionRename` with the following test methods:
- `test_questions_and_decisions_absent_from_prompt`: asserts `"## Questions & Decisions"` is not in `aib-analysis.md` content (as a section heading pattern `## Questions & Decisions`).
- `test_questions_and_decisions_absent_from_request_convention`: asserts `"## Questions & Decisions"` is not in `request-convention.md`.
- `test_decisions_present_in_request_convention`: asserts `"## Decisions"` appears in `request-convention.md`.
- `test_decision_points_catalog_required_in_prompt`: asserts `"Decision Points Catalog"` appears in `aib-analysis.md`.

Run `python -m pytest tests/test_analysis_prompt_structure.py -v` and confirm all new tests pass with 0 failures.

#### Done criteria
- Four new test methods exist in `TestDecisionsSectionRename`.
- All tests in `tests/test_analysis_prompt_structure.py` pass (0 failures).

#### Dependencies
Tasks 1, 2, 3 (test assertions target the output of those tasks)

#### Risk notes
None — tests are pure string-assertion checks against static files.

---

### Task 5: Update documentation

#### Intent
Record all changes made in `logs/next_version_changes.md` and note that `context.md` requires regeneration.

#### Outputs
`logs/next_version_changes.md` (new bullets appended)

#### Procedure
Read `logs/next_version_changes.md` to find the current end of file.

Append the following bullets (one per logical change):
- `- Restructure aib-analysis.md prompt with numbered steps, preamble, and explicit section breaks.`
- `- Add Decision Points Catalog subsection requirement to analysis document format.`
- `- Rename ## Questions & Decisions to ## Decisions in request.md and update semantics to resolved-Q&A log.`
- `- Update request-convention.md section 10 for ## Decisions rename.`
- `- Update analysis-convention.md cross-reference from ## Questions & Decisions to ## Decisions.`
- `- Add regression tests for ## Decisions rename and Decision Points Catalog presence.`

Verify `logs/next_version_changes.md` ends with a trailing newline.

Note for the developer: `.aib_memory/context.md` will need regeneration via the `aib-context.md` prompt after this request is closed, as it contains stale references to `## Questions & Decisions` (lines 23, 42, 420).

#### Done criteria
- `logs/next_version_changes.md` contains all 6 new bullets.
- File ends with a trailing newline.
- Developer has been informed that `context.md` requires regeneration.

#### Dependencies
Tasks 1–4 (changes must be complete before documenting them)

#### Risk notes
If CI has not cleared `logs/next_version_changes.md` since the last release, new bullets append correctly per the append-only directive in `instructions.md`.

## Documentation

- `.aib_brain/prompts/aib-analysis.md` — full rewrite as the primary deliverable of this request.
- `.aib_brain/conventions/request-convention.md` — section 10 rename and semantics update.
- `.aib_brain/conventions/analysis-convention.md` — cross-reference update for `## Decisions`.
- `logs/next_version_changes.md` — append curated change bullets for this request.
- `.aib_memory/context.md` — requires regeneration via `aib-context.md` after request close (stale `## Questions & Decisions` references at lines 23, 42, 420).

## Decisions
