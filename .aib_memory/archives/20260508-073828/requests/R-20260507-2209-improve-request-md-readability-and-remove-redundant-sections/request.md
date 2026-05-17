## Goal

Improve the readability and precision of generated `request.md` files so humans can verify them faster while preserving full implementation guidance for AI. Remove redundant verification content and duplicated statements, simplify task descriptions by embedding task metadata inside procedure steps, include documentation updates in the plan flow, and eliminate the `## Code and Asset Scan for Impacted Components` and `## Internal Review of Request and Product Docs` sections from the `request.md` structure.

## Background

The current `request.md` format has become too heavy for review. It contains repeated statements, separate task metadata blocks that fragment readability, and two sections (`Code and Asset Scan` and `Internal Review`) that duplicate information that should either be expressed in the plan or handled via questions/decisions. The request aims to simplify the contract while keeping deterministic behavior, explicit implementation direction, and testability.

## Scope

- Update `.aib_brain/prompts/aib-analysis.md` so generated `request.md` files no longer require `## Code and Asset Scan for Impacted Components` or `## Internal Review of Request and Product Docs`.

- Update `.aib_brain/conventions/request-convention.md` to define the new `request.md` section set and remove the two eliminated sections.

- Update the `## Plan` task schema requirements in both the prompt and convention so that `Inputs`, `External Interfaces`, and `Environment & Configuration` metadata are incorporated into `Procedure` steps instead of separate labeled fields. `## Outputs` MUST remain as a labeled field per task.

- Require every `Procedure` step to reference the exact file path it operates on.

- Keep `## Documentation` represented and explicitly planned inside `## Plan` tasks. Documentation steps MUST follow the same explicitness standard as code steps: specify the target file path, describe what to change, and state an acceptance test.

- Pre-flight flags previously captured in `## Internal Review of Request and Product Docs` (cross-reference issues, missing information, factual inconsistencies) must be redistributed into the relevant Plan task's `Risk Notes` field or raised as Q-blocks in `## Questions & Decisions` when user input is needed.

- Ensure auto-request creation rules in `aib-analysis.md` are aligned to the updated mandatory section count and order.

- Update tests that validate request structure and analysis prompt behavior so they assert the new section model.

- Regenerate `.aib_memory/context.md` after implementation so product docs reflect the new request model.

## Out of scope

- No changes to request lifecycle scripts (`create-request.py`, `close-request.py`, `move-request-artifacts.py`) beyond test fixture adjustments required by section schema changes.

- No changes to `analysis.md` mandatory section structure.

- No changes to CI release bookkeeping behavior.

- No changes to attachment ingestion or archiving mechanics.

## Constraints

- Keep AIB deterministic and fail-closed where already required by conventions.

- Maintain Python 3.10+ standard-library-only constraints for tool scripts.

- Preserve question-threshold behavior and existing Q-block merge rules.

- Ensure backward compatibility for processing already archived requests.

- Avoid duplicated directives inside generated `request.md`; each requirement should be stated once in its most relevant section.

## Success criteria

- SC-1: `.aib_brain/prompts/aib-analysis.md` no longer requires `## Code and Asset Scan for Impacted Components` and `## Internal Review of Request and Product Docs` in generated `request.md` output.

- SC-2: `.aib_brain/conventions/request-convention.md` no longer lists those two sections as mandatory and reflects the revised section count/order.

- SC-3: The Plan schema in prompt and convention no longer requires separate `Inputs`, `External Interfaces`, and `Environment & Configuration` labeled fields; those details are required inside ordered `Procedure` steps. `Outputs` MUST remain as a labeled field per task.

- SC-3b: Every Procedure step in generated `request.md` plans must reference the exact file path it operates on.

- SC-4: The prompt explicitly requires documentation updates to be part of the plan procedure (not a detached mention), with each documentation step specifying target file, change description, and acceptance test.

- SC-5: Auto-request creation in `aib-analysis.md` validates the updated mandatory section list and count.

- SC-6: Automated tests covering request structure and analysis prompt contract pass after updates.

- SC-7: Repository search confirms removed section headings are absent from active request-convention and analysis-prompt request output rules.

- SC-8: `.aib_memory/context.md` is regenerated and reflects the new request model without obsolete section requirements.

## Assumptions

- A1: The simplification is intended to change both generation rules (`aib-analysis.md`) and the normative contract (`request-convention.md`), not only one of them.
  - Risk if false: Prompt and convention drift would break deterministic validation.

- A2: Existing tests do not directly assert the 12-section count or the presence of the removed section headings by name; adding regression assertions is safe and will not break existing tests.
  - Risk if false: Adding tests may conflict with currently passing test logic.

- A3: Eliminating the two sections does not remove critical implementation guidance because impacted-file information and factual doc checks are redistributed into Plan task Risk Notes and Q&D blocks.
  - Risk if false: Important pre-flight information may become less visible if Risk Notes are skimmed.

- A4: Keeping `Outputs` as a labeled field while embedding `Inputs`, `External Interfaces`, and `Environment & Configuration` into Procedure steps yields readable tasks without losing machine interpretability.
  - Risk if false: Task execution quality could degrade if embedded metadata is underspecified.

- A5: The developer's amendment to require exact file-path citations in every Procedure step is a generation-time rule (applied by the AI at analysis time) rather than a validation-time rule enforced by a parser.
  - Risk if false: A stricter enforcement mechanism would require additional tooling changes outside scope.

## Plan

### Task 1: Update analysis prompt request schema
**Intent:** Align `aib-analysis.md` request generation and update rules to the simplified `request.md` structure.
**Outputs:** `.aib_brain/prompts/aib-analysis.md` — updated with removed sections, revised plan-task schema, file-path step requirement, documentation-step explicitness rule, and Internal Review redistribution rule.
**Procedure:**
1. In `.aib_brain/prompts/aib-analysis.md`: replace the mandatory section list (currently 12) with the new 10-section set, removing `## Code and Asset Scan for Impacted Components` and `## Internal Review of Request and Product Docs`.
2. In `.aib_brain/prompts/aib-analysis.md`: update the auto-request creation branch validation step so it references the 10 mandatory sections in exact order.
3. In `.aib_brain/prompts/aib-analysis.md`: rewrite the Plan task schema block so `Inputs`, `External Interfaces`, and `Environment & Configuration` are embedded in numbered `Procedure` steps; `**Outputs:**` MUST remain as a standalone labeled field.
4. In `.aib_brain/prompts/aib-analysis.md`: add an explicit rule that every Procedure step must reference the exact file path it operates on.
5. In `.aib_brain/prompts/aib-analysis.md`: add an explicit rule that documentation steps must specify (a) the target file path, (b) what to change, and (c) an acceptance test.
6. In `.aib_brain/prompts/aib-analysis.md`: remove the Part 2 replacement-rule blocks for Code Scan and Internal Review sections.
**Done Criteria:** Full-text search of `.aib_brain/prompts/aib-analysis.md` returns zero matches for `Code and Asset Scan for Impacted Components` and `Internal Review of Request and Product Docs` in generation-rule context; schema block contains `**Outputs:**` but not `**Inputs:**`, `**External Interfaces:**`, or `**Environment & Configuration:**` as standalone labels.
**Dependencies:** None.
**Risk Notes:** Prompt may contain stale references in non-obvious paragraphs (e.g., re-run behavior summary, Q&D mapping hints). Cross-reference: `context.md` currently documents the two removed sections in FR-004 and component-map entries — must be addressed in Task 6.

### Task 2: Update request convention
**Intent:** Make the normative `request.md` contract in `request-convention.md` match the simplified structure.
**Outputs:** `.aib_brain/conventions/request-convention.md` — updated mandatory sections list, revised plan task schema, documentation-step rule.
**Procedure:**
1. In `.aib_brain/conventions/request-convention.md`: remove sections 11 (`## Code and Asset Scan for Impacted Components`) and 12 (`## Internal Review of Request and Product Docs`) from the mandatory section list; renumber remaining items to produce a 10-section list.
2. In `.aib_brain/conventions/request-convention.md`: update section descriptions, validation rules, and any occurrence of "sections (1–12)" to reflect the 10-section model.
3. In `.aib_brain/conventions/request-convention.md`: replace the Plan task schema block so `Inputs`, `External Interfaces`, and `Environment & Configuration` are removed as standalone labeled fields; `**Outputs:**` MUST remain as a labeled field.
4. In `.aib_brain/conventions/request-convention.md`: add the requirement that every Procedure step cites the exact file path it operates on.
5. In `.aib_brain/conventions/request-convention.md`: add the documentation-step explicitness rule (target file, change description, acceptance test).
**Done Criteria:** Convention's mandatory section list has exactly 10 entries ending with `## Questions & Decisions`; schema block contains `**Outputs:**` but not the three removed field labels.
**Dependencies:** Task 1.
**Risk Notes:** Divergence between prose references and the schema example can cause future drift if not updated consistently throughout the file.

### Task 3: Adjust request-analysis Part 2 update behavior
**Intent:** Ensure Part 2 update rules in `aib-analysis.md` only target still-valid optional sections.
**Outputs:** `.aib_brain/prompts/aib-analysis.md` — Part 2 section rules cleaned of removed-section references.
**Procedure:**
1. In `.aib_brain/prompts/aib-analysis.md` Part 2 block: keep replacement rules for `## Assumptions`, `## Plan`, `## Documentation`, and `## Questions & Decisions`.
2. In `.aib_brain/prompts/aib-analysis.md` Part 2 block: remove any replacement-rule or mention of Code Scan and Internal Review sections.
3. In `.aib_brain/prompts/aib-analysis.md` re-run behavior summary: remove Code Scan and Internal Review from the "always fully replaced" list.
**Done Criteria:** Part 2 and re-run summary reference only the four retained optional sections; no mention of the two removed sections remains.
**Dependencies:** Task 1, Task 2.
**Risk Notes:** Residual references in prose paragraphs outside the section-rule blocks may be missed; a full-text grep pass is required.

### Task 4: Update automated tests for schema changes
**Intent:** Preserve confidence and deterministic behavior after request structure simplification.
**Outputs:** `tests/test_instructions_md.py` or a new test file — regression tests asserting the two removed section headings are absent from active prompt and convention; existing structural tests updated if any assert section count/names.
**Procedure:**
1. In `tests/` directory: search for any test asserting mandatory section names, section count at 12, or the field labels `Inputs`, `External Interfaces`, `Environment & Configuration` in plan schemas. Update those assertions to the new model.
2. In `tests/test_instructions_md.py` (or a new `tests/test_analysis_prompt_structure.py`): add a test class that reads `.aib_brain/prompts/aib-analysis.md` and asserts `## Code and Asset Scan for Impacted Components` is absent.
3. In the same test file: add an assertion that `## Internal Review of Request and Product Docs` is absent from `.aib_brain/prompts/aib-analysis.md`.
4. Add parallel assertions for `.aib_brain/conventions/request-convention.md`.
5. Add an assertion that `**Outputs:**` is present as a labeled field in the Plan schema in both files.
**Done Criteria:** `pytest tests/` passes with zero failures; new regression tests are present and red if the removed sections are reintroduced.
**Dependencies:** Task 1, Task 2, Task 3.
**Risk Notes:** If a test file asserts the full mandatory section list verbatim, it must be updated; missing such a test allows silent contract regressions.

### Task 5: Execute verification checks
**Intent:** Validate all testable success criteria and confirm idempotent behavior.
**Outputs:** Terminal output confirming pass/fail for SC-1 through SC-7; documented in `implementation.md`.
**Procedure:**
1. Run `pytest tests/` in the repository root; record pass/fail count against each relevant Success Criterion.
2. Run text search for `Code and Asset Scan for Impacted Components` in `.aib_brain/prompts/aib-analysis.md` and `.aib_brain/conventions/request-convention.md`; expected: zero matches.
3. Run text search for `Internal Review of Request and Product Docs` in the same two files; expected: zero matches.
4. Run text search for `**Outputs:**` in both files; expected: at least one match each.
5. Re-run steps 2–4 to confirm idempotent stability.
**Done Criteria:** All searches return expected results; `pytest` passes with zero failures.
**Dependencies:** Task 4.
**Risk Notes:** Full test-suite runtime may be longer on slow environments; partial runs targeting impacted modules are acceptable but gaps must be logged.

### Task 6: Update documentation and context
**Intent:** Keep product documentation aligned with the implemented contract.
**Outputs:** `.aib_memory/context.md` — regenerated to reflect 10-section `request.md` model; `logs/next_version_changes.md` — curated changelog bullets appended.
**Procedure:**
1. After Tasks 1–5 are complete: execute `aib-context.md` to regenerate `.aib_memory/context.md` for the workspace.
2. In `.aib_memory/context.md`: verify FR-004 no longer lists Code Scan and Internal Review as `request.md` sections; verify acceptance criterion 3 reflects 10 mandatory sections.
3. In `logs/next_version_changes.md` (`.aib_brain/prompts/aib-analysis.md`): append curated changelog bullets per persistent workspace instruction in `.aib_memory/instructions.md`.
4. Acceptance test for this task: search regenerated `.aib_memory/context.md` for `Code and Asset Scan` and `Internal Review` as required `request.md` sections; expected: zero matches in the mandatory-section enumeration.
**Done Criteria:** Context and changelog reflect the new request model; no stale structure remains.
**Dependencies:** Task 5.
**Risk Notes:** Stale context can mislead future analysis/implementation runs. If `aib-context.md` is not run, this task is incomplete.

## Documentation

- `.aib_brain/prompts/aib-analysis.md` — Remove Code Scan and Internal Review section requirements; revise plan task schema and add file-path and documentation-step explicitness rules.
- `.aib_brain/conventions/request-convention.md` — Update normative request structure to 10 sections; revise plan schema.
- `.aib_memory/context.md` — Regenerate to reflect updated request model after implementation.
- `logs/next_version_changes.md` — Append curated changelog bullets during implementation run per workspace instruction.

## Questions & Decisions

No open questions at threshold 3. All identified decision points were resolvable from the input, current conventions, and product context.
