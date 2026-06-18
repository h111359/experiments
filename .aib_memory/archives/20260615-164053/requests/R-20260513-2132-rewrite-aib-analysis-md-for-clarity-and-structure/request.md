## Goal

Transform `.aib_brain/prompts/aib-analysis.md` into a well-structured, logically organized, and deterministic version that is clear, consistent in terminology and formatting, easy to follow for an AI agent executing it repeatedly, while preserving every existing requirement, rule, workflow, and behavior from the original without exception.

## Background

The `aib-analysis.md` prompt is the primary analysis workflow driver for AIB. It is executed by an AI agent and must be deterministic and unambiguous for reliable repeated execution. The current version contains implicit logic, mixed formatting conventions, inconsistent section organization, and vague wording in some areas. These issues can cause non-deterministic interpretation by AI agents and make the prompt harder for maintainers to audit and update. A structural and clarity rewrite is needed — with no behavioral changes.

## Scope

- Rewrite the content of `.aib_brain/prompts/aib-analysis.md` for improved clarity and structure.

- Organize the prompt into clearly defined, consistently hierarchical sections (e.g., Objective, Inputs, Preflight, Workflow, Outputs, Constraints).

- Convert implicit logic into explicit step-by-step flow; ensure execution order is unambiguous.

- Make all constraints, MUST/MUST NOT behaviors, and validation logic explicit and easy to scan.

- Improve phrasing to be concise but precise; eliminate vague or ambiguous wording.

- Clearly separate standard flow and conditional branches (Auto-Request Creation, Answer Application Sub-flow).

- Define when and how external scripts and conventions must be used.

- Clearly separate output artifact definitions with exact file names, locations, and structure requirements.

- Explicitly describe re-run logic, stateful behavior, input mutation, and side effects.

## Out of scope

- Changing any behavioral logic, execution semantics, workflows, or rules in the prompt.

- Adding new features, requirements, or behaviors not present in the original prompt.

- Modifying any other files outside of `.aib_brain/prompts/aib-analysis.md`.

- Rewriting or modifying other prompts, conventions, or tool scripts.

## Constraints

- Every instruction, rule, and behavior from the original `aib-analysis.md` MUST be preserved in the rewritten version.

- The rewrite MUST NOT simplify by omitting details.

- The rewrite MUST NOT reinterpret intent or introduce new functionality.

- The rewrite MUST NOT change workflows or execution order unless strictly improving clarity.

- Output must be a complete, production-grade, immediately usable Markdown prompt.

- Clean Markdown structure required: consistent headings, code blocks for commands/templates, tables only when they improve clarity.

## Success criteria

- The rewritten `aib-analysis.md` contains all original requirements, rules, logic, and behaviors — a line-by-line review finds no missing elements.

- Existing tests that validate `aib-analysis.md` behavior pass without modification.

- Execution order is explicitly numbered and unambiguous throughout.

- All MUST/MUST NOT constraints are clearly highlighted and scannable.

- Conditional branches (Auto-Request, Answer Application Sub-flow) are clearly delineated.

- Every external dependency (scripts, conventions, files) is explicitly named and its usage point specified.

- Maintainers can audit the rewritten prompt end-to-end without referencing the original.

## Assumptions

- A1: The rewrite must preserve all string literals currently asserted by `tests/test_analysis_prompt_structure.py` verbatim; these include exact phrases like `"All 10 mandatory sections"`, `"If stub-equivalent: skip archive creation for this standard-flow reset."`, and `"#### Outputs"`.
  - Risk if false: Existing tests will fail and test suite will require modification.

- A2: No other test file outside `tests/test_analysis_prompt_structure.py` checks the content of `aib-analysis.md`.
  - Risk if false: Additional hidden test assertions may break.

- A3: The rewrite produces a single file at `.aib_brain/prompts/aib-analysis.md`; no multi-file split is needed or desired.
  - Risk if false: If a multi-file structure were required, the approach would need rethinking.

- A4: The current `aib-analysis.md` (310 lines) contains all behaviors described in `context.md` FR-003, FR-004, FR-007, FR-008; no behavior has drifted out of sync.
  - Risk if false: A drifted behavior would need to be addressed as a separate bug-fix request, not in this rewrite.

## Plan

### Task 1: Audit current aib-analysis.md against test assertions

#### Intent
Produce a complete map of all test-checked string literals and their required location in the rewritten prompt.

#### Outputs
An internal working reference (not a written file) listing every string literal from `tests/test_analysis_prompt_structure.py` that must appear verbatim in the rewritten output.

#### Procedure
Read `tests/test_analysis_prompt_structure.py` (`.aib_brain/../tests/test_analysis_prompt_structure.py`) in full.

Extract every `assert "..." in content` and `assert "..." not in content` statement and record the exact string.

Verify each must-have string currently appears in `.aib_brain/prompts/aib-analysis.md`.

#### Done criteria
All must-have strings confirmed present in current prompt; all must-not-have strings confirmed absent. Working reference is complete.

#### Dependencies
None.

#### Risk notes
None. Purely a read operation.

---

### Task 2: Draft restructured aib-analysis.md

#### Intent
Produce the full rewritten content of `.aib_brain/prompts/aib-analysis.md` with improved structure, clarity, and consistency — without changing any behavior.

#### Outputs
Rewritten content for `.aib_brain/prompts/aib-analysis.md`.

#### Procedure
Organize the prompt into numbered top-level sections: (1) Objective, (2) Inputs & External Dependencies, (3) Preflight, with the Auto-Request Creation Branch as a labeled sub-section immediately following the preflight step that triggers it, and the Answer Application Sub-flow as a labeled sub-section immediately following the Q&A check step.

Convert all sequential execution steps in Preflight, Auto-Request Branch, Answer Application Sub-flow, and Standard Flow Final Step into explicit numbered lists.

Move all MUST/MUST NOT invariant constraints into visually prominent blocks (e.g., blockquote or bold constraint paragraph) at the top of each section where they apply.

Consolidate the Re-run Behaviour Summary rules into the relevant sections rather than maintaining a parallel summary section, OR clearly label the summary as a navigational reference derived from those sections (not authoritative).

Preserve verbatim all string literals required by `tests/test_analysis_prompt_structure.py` (identified in Task 1).

Preserve verbatim the stub-detection formula from the Standard Flow Final Step: `` `## Active request\nNo active request\n\n## Options\n- Minimum questions: 0\n\n## Input\n\n` ``.

#### Done criteria
Rewritten prompt contains all behavioral elements of the original. All test-required string literals are present verbatim. Execution order is explicitly numbered and unambiguous. MUST/MUST NOT constraints are visually prominent. No new functionality is introduced.

#### Dependencies
Task 1.

#### Risk notes
Risk of inadvertent semantic change through rewording. Mitigation: keep all original prose for named rules (test-checked strings) verbatim; rewrite only organizational glue text.

---

### Task 3: Replace aib-analysis.md with rewritten version

#### Intent
Atomically replace `.aib_brain/prompts/aib-analysis.md` with the rewritten content.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — full content replacement.

#### Procedure
Write the full rewritten content to `.aib_brain/prompts/aib-analysis.md`, replacing the existing file entirely.

Verify the file was written successfully by reading it back.

#### Done criteria
`.aib_brain/prompts/aib-analysis.md` contains the rewritten content. File size is plausible (≥ 300 lines for a complete prompt). No truncation.

#### Dependencies
Task 2.

#### Risk notes
File write replaces the only existing copy; ensure the rewritten draft is complete before writing.

---

### Task 4: Run automated tests

#### Intent
Confirm the rewritten prompt passes all existing structural assertions without test modifications.

#### Outputs
Test run result confirming pass/fail status of `tests/test_analysis_prompt_structure.py`.

#### Procedure
Run the test suite from the workspace root: `python -m pytest tests/test_analysis_prompt_structure.py -v`. Expected output location: terminal stdout.

If any test fails, return to Task 2, identify which required string literal is missing or which forbidden string was introduced, and fix the draft before re-running.

#### Done criteria
All tests in `tests/test_analysis_prompt_structure.py` pass with exit code 0.

#### Dependencies
Task 3.

#### Risk notes
A test failure at this stage indicates a verbatim string was altered; fix is low-effort (find-and-restore the exact string).

---

### Task 5: Update documentation and context

#### Intent
Record the change and update relevant documentation files to reflect the rewritten prompt.

#### Outputs
- `logs/next_version_changes.md` — new bullet entry appended.
- `.aib_memory/context.md` — reviewed for accuracy; updated only if the rewrite changes any FR description.

#### Procedure
Append a bullet to `logs/next_version_changes.md`: `- Rewrite aib-analysis.md prompt for improved structure, clarity, and deterministic execution order.`

Read `.aib_memory/context.md` and check whether FR-003 or FR-004 descriptions reference any structural aspect of `aib-analysis.md` that changed. If any description is now inaccurate, update the relevant sentence.

Acceptance test for `logs/next_version_changes.md`: the file ends with the new bullet line followed by a newline. The bullet is the last entry.

Acceptance test for `context.md`: all FR descriptions remain accurate relative to the rewritten prompt behavior.

#### Done criteria
`logs/next_version_changes.md` has the new bullet appended. `context.md` is accurate.

#### Dependencies
Task 3.

#### Risk notes
`context.md` is auto-generated by `aib-context.md`; if the change to `aib-analysis.md` is purely structural (no behavior change), FR descriptions should not need updating.

## Documentation

- `logs/next_version_changes.md` — append one bullet summarizing the prompt rewrite for release bookkeeping.
- `.aib_memory/context.md` — review FR-003 and FR-004 descriptions for accuracy after the structural rewrite; update only if a description references prompt structure in a way that no longer matches the rewritten version.

