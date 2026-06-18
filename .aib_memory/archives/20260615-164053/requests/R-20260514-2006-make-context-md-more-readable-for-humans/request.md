## Goal

Make `context.md` more readable for humans by design.

Change the conventions so the AI-generated `context.md` file can be easily read and even edited by a human.

## Background

The `context.md` file is an AI-generated workspace-level document that stores persistent product context. Currently the formatting conventions governing how this file is written prioritize machine readability and density over human readability. As a result, the file is difficult to scan, edit, or reason about without tooling assistance.

The developer wants formatting rules applied at the convention and prompt level so that every future regeneration of `context.md` produces a document that a human can read and edit comfortably.

Three specific rules have been specified:
- All titles must use markdown headings with appropriate size (e.g., `### Heading`). Bold text must not be used as a heading substitute (`**Heading**`).
- Keep an empty line between list elements (bullets).
- Do not use tables — they are hard to read.

## Scope

- Update the conventions and/or prompts that govern `context.md` generation to embed the three specified formatting rules.

- Identify all prompts that write to `context.md` and ensure they reference and apply the new rules.

- Apply best-practice research findings on human-readable markdown documentation to enrich the formatting rules where appropriate.

- Update the current `context.md` file to comply with the new formatting rules if it exists and violates them.

## Out of scope

- Changes to the structure or semantic content of `context.md` — only formatting is in scope.

- Changes to any other AI-generated file type beyond `context.md`.

- Tooling or script changes; only prompt and convention file edits are in scope.

## Constraints

- All new formatting rules MUST be expressed in a way that the AI agent can deterministically apply them during generation.

- The three formatting rules provided by the developer are mandatory and MUST be included verbatim or equivalently in the updated convention/prompt.

- The existing convention file structure and heading levels MUST be preserved; only add or amend formatting guidance.

## Success criteria

- The conventions and/or prompts that govern `context.md` generation contain the three specified formatting rules (no bold-as-heading, blank line between bullets, no tables).

- At least two additional best-practice formatting rules are documented from industry research and applied.

- The current `context.md` file (if it exists) passes a manual review against all new rules with no violations.

- All automated tests in the test suite continue to pass after changes.

## Assumptions

- A1: The three formatting rules specified in `input.md` are normative requirements, not suggestions; they must appear in the convention as MUST-level constraints.
  - Risk if false: Rules may be treated as optional guidance and ignored by the AI on future `context.md` regenerations.

- A2: The `context-convention.md` Formatting Rules section (rules 1–10) is the canonical formatting authority for `context.md`; adding rules there is sufficient as the primary convention change.
  - Risk if false: There may be additional convention or template files that govern `context.md` formatting that would also need updating.

- A3: The current `context.md` Component Map table should be replaced with a nested bullet list using the pattern `- **Component name** — responsibility sentence.` with Location as a sub-bullet.
  - Risk if false: The chosen replacement format may not match developer expectations; however, no alternative format was specified.

- A4: The ADR sub-field labels (`**Context:**`, `**Decision:**`, `**Rationale:**`, `**Consequences:**`) should be converted from bold labels to plain-text sub-bullets using colon notation (`- Context: ...`) to preserve structure without using bold for labeling.
  - Risk if false: Removing bold from ADR labels without a structural replacement may reduce readability.

- A5: The test suite uses pytest and the same workspace-relative path pattern as `tests/test_analysis_prompt_structure.py`; a new test file can be added following the same pattern.
  - Risk if false: None — the test pattern is well-established in the workspace.

## Plan

### Task 1: Add formatting rules to `context-convention.md`

#### Intent

Extend the Formatting Rules section with a prohibition on Markdown tables, a blank-line-between-bullets requirement, and a heading-depth cap.

#### Outputs

`.aib_brain/conventions/context-convention.md` — updated Formatting Rules section with 3 new rules (rules 11, 12, 13).

#### Procedure

Read the current Formatting Rules section of `.aib_brain/conventions/context-convention.md` to determine the current highest rule number (currently rule 10).

Append the following three new rules at the end of the Formatting Rules section of `.aib_brain/conventions/context-convention.md`:

- Rule 11: `Markdown tables MUST NOT appear anywhere in the document. Use nested bullet lists to represent structured multi-attribute data.`

- Rule 12: `One blank line MUST appear between each list item when items contain more than one sentence or when the list is inside a section that will be read directly by humans.`

- Rule 13: `Heading nesting MUST NOT exceed H3 (###) except inside the Workspace File Inventory section where H4 is not used anyway. Avoid H4 in all sections unless strictly necessary for a sub-schema.`

Verify the three new rules appear in the file after editing.

#### Done criteria

- `.aib_brain/conventions/context-convention.md` contains the three new rules as normative MUST-level statements.

- The file still passes a manual scan for structural integrity (no broken headings, no duplicate rules).

#### Dependencies

None.

#### Risk notes

None.

---

### Task 2: Add formatting checklist to `aib-context.md` Phase 4

#### Intent

Add an explicit formatting reminder to `aib-context.md`'s Phase 4 synthesis section so the AI has a second enforcement layer for the most critical prohibitions.

#### Outputs

`.aib_brain/prompts/aib-context.md` — updated Phase 4 with a "Formatting requirements" paragraph referencing the three developer-specified rules.

#### Procedure

Read Phase 4 (Synthesis) of `.aib_brain/prompts/aib-context.md` to locate the correct insertion point (after the section preamble and before sub-section 4.1 Preamble, or at the end of 4.2 Mandatory sections instructions).

Insert a "Formatting requirements (MUST enforce for every section)" checklist in Phase 4 of `.aib_brain/prompts/aib-context.md` with the following items:

- Do NOT use Markdown tables anywhere in the document. Replace multi-attribute structured data with nested bullet lists.

- Insert one blank line between each list item in every section.

- Do NOT use bold text (`**text**`) as a section or field label. Bold is permitted only for glossary term definitions and critical callouts.

Verify the checklist text appears in the file at the correct location.

#### Done criteria

- `.aib_brain/prompts/aib-context.md` contains the three formatting checklist items under Phase 4.

- The existing Phase 4 structure (sub-sections 4.1–4.3) is preserved unchanged.

#### Dependencies

Task 1 (the convention is the authoritative source; the prompt is the reminder layer).

#### Risk notes

None.

---

### Task 3: Reformat current `context.md` — remove table

#### Intent

Replace the Component Map Markdown table in `.aib_memory/context.md` with a nested bullet list.

#### Outputs

`.aib_memory/context.md` — Component Map section reformatted as bullet list.

#### Procedure

Read the Component Map section of `.aib_memory/context.md` to extract all rows (Component, Location, Responsibility).

Replace the full table block in `.aib_memory/context.md` with a nested bullet list in the following format for each component:

```
- **ComponentName** (`location/path`) — Responsibility sentence.
```

where the component name is the display label, location is in backticks, and the responsibility is the sentence from the table. Use one blank line between each component bullet.

Verify the table syntax (`| --- |`) no longer appears in `.aib_memory/context.md`.

#### Done criteria

- The `| --- |` table delimiter pattern is absent from `.aib_memory/context.md`.

- The Component Map content is preserved in bullet-list form.

- One blank line separates each component entry.

#### Dependencies

None.

#### Risk notes

The current `context.md` is auto-generated and will be fully replaced on the next `aib-context.md` run. This reformatting provides immediate human-readability value but has a limited lifespan.

---

### Task 4: Reformat current `context.md` — fix bold labels and bullet spacing

#### Intent

Remove bold sub-field labels from ADR blocks and add missing blank lines between list items throughout `.aib_memory/context.md`.

#### Outputs

`.aib_memory/context.md` — ADR blocks reformatted; inter-item blank lines added in dense bullet sections.

#### Procedure

Scan `.aib_memory/context.md` for inline bold labels used as field identifiers within list items (patterns like `**Context:**`, `**Decision:**`, `**Rationale:**`, `**Consequences:**`).

Replace each bold label with a plain-text colon-notation label in `.aib_memory/context.md`:

- `**Context:**` → `- Context:`
- `**Decision:**` → `- Decision:`
- `**Rationale:**` → `- Rationale:`
- `**Consequences:**` → `- Consequences:`

Scan `.aib_memory/context.md` for bullet list sections where multiple items appear consecutively with no blank line between them. Insert one blank line between items in those sections.

Verify that `**Context:**`, `**Decision:**`, `**Rationale:**`, `**Consequences:**` no longer appear as bold patterns in the file.

#### Done criteria

- No `**Context:**`, `**Decision:**`, `**Rationale:**`, `**Consequences:**` bold label patterns remain in `.aib_memory/context.md`.

- Dense bullet list sections in Requirements Summary and Business Context have blank lines between items.

#### Dependencies

Task 3 (both tasks reformat the same file; Task 3 should be applied first to reduce merge conflicts).

#### Risk notes

The file is very long (~350+ lines). Bulk whitespace insertion should be done carefully to avoid adding excess blank lines in sections that are already well-spaced.

---

### Task 5: Add regression tests for the new formatting rules

#### Intent

Add a pytest test file that asserts the three developer-specified rules are present in `context-convention.md` and that `aib-context.md` contains the formatting checklist.

#### Outputs

`tests/test_context_formatting_rules.py` — new test file with test classes for convention and prompt coverage.

#### Procedure

Create `tests/test_context_formatting_rules.py` following the pattern in `tests/test_analysis_prompt_structure.py`.

Add a test class `TestContextConventionFormattingRules` in `tests/test_context_formatting_rules.py` with test methods asserting:

- The phrase `MUST NOT appear anywhere in the document` (or equivalent no-tables language) is present in `.aib_brain/conventions/context-convention.md`.

- A blank-line-between-bullets rule (`blank line` or `one blank line`) is present in `.aib_brain/conventions/context-convention.md`.

- A heading-depth cap rule is present in `.aib_brain/conventions/context-convention.md`.

Add a test class `TestContextPromptFormattingChecklist` in `tests/test_context_formatting_rules.py` with test methods asserting:

- The `aib-context.md` prompt contains the no-tables prohibition text.

- The `aib-context.md` prompt contains the blank-line requirement text.

Run the test suite via `python -m pytest tests/test_context_formatting_rules.py -v` to confirm all new tests pass.

#### Done criteria

- `tests/test_context_formatting_rules.py` exists and all tests pass.

- The test assertions are specific enough to catch regression if the rules are removed from the convention or prompt.

#### Dependencies

Tasks 1 and 2 (tests validate outputs of those tasks).

#### Risk notes

None.

---

### Task 6: Update documentation files

#### Intent

Ensure `.aib_memory/context.md` and `logs/next_version_changes.md` reflect the changes made by this request.

#### Outputs

- `.aib_memory/context.md` — already updated by Tasks 3 and 4; no further changes needed.

- `logs/next_version_changes.md` — append change bullets for this implementation run per the workspace directive in `instructions.md`.

#### Procedure

After Tasks 1–5 are complete, read `logs/next_version_changes.md` at `logs/next_version_changes.md` to check its current content.

Append the following bullets to `logs/next_version_changes.md`:

- `- Add no-tables, blank-line-between-bullets, and heading-depth-cap formatting rules to context-convention.md.`

- `- Add formatting checklist to aib-context.md Phase 4 synthesis instructions.`

- `- Reformat context.md to remove Component Map table and fix bold label patterns.`

- `- Add regression tests for context.md formatting convention rules.`

Verify the bullets are present at the end of `logs/next_version_changes.md`.

Acceptance test: read the last 10 lines of `logs/next_version_changes.md` and confirm the four bullets appear without modification.

#### Done criteria

- `logs/next_version_changes.md` contains the four new bullets at the end of the file.

#### Dependencies

Tasks 1–5.

#### Risk notes

None.

## Documentation

- `logs/next_version_changes.md` (ref_id: N/A) — Append change bullets describing the formatting rule additions and `context.md` reformat per the `instructions.md` workspace directive.

## Decisions
