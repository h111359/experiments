## Executive Summary

- **Request ID:** R-20260514-2006

- **Request title:** Make context.md more readable for humans

- **High-level purpose:** Add explicit human-readability formatting rules to the convention and prompt that govern `context.md` generation, then apply those rules immediately to the current `context.md` file to eliminate existing violations.

---

## Files Read During This Analysis Run

- `.aib_memory/requests_register.md`
- `.aib_memory/instructions.md`
- `.aib_memory/input.md`
- `.aib_memory/request-R-20260514-2006.md`
- `.aib_memory/context.md`
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/prompts/aib-context.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `tests/test_analysis_prompt_structure.py`

---

## Research Results

### Violations confirmed in the current `context.md`

Scanning the current `.aib_memory/context.md` against the three developer-specified rules produced the following findings.

- **Table violation:** The `### Component Map` subsection in `## Architecture & Key Decisions` uses a Markdown table with three columns: Component, Location, Responsibility. This is the only table in the file, but it spans ~20 rows.

- **Bold-as-label violation:** ADR blocks use bold text for sub-field labels: `**ADR-0001 — Single SemVer marker file for version**` as a list-item lead, and `**Context:**`, `**Decision:**`, `**Rationale:**`, `**Consequences:**` as inline field labels within sub-bullets. The existing context-convention.md Rule 6 already states bold MUST be used only for glossary term definitions and critical callouts, meaning these labels are already a convention violation. No standalone bold-as-heading-substitute pattern (a bold line by itself on a line functioning as a heading) was found; the violations are all inline labels.

- **Missing blank lines between bullets:** The `## Requirements Summary`, `## Business Context`, and `## Architecture & Key Decisions` sections contain bullet lists where items have no blank lines between them. Items are often multi-sentence, making the sections difficult to scan.

### Coverage gap in `context-convention.md` Formatting Rules

The existing Formatting Rules section (rules 1–10) already covers:

- Rule 5: heading level hierarchy (H1 title, H2 sections, H3 subsections, H4 sub-subsections)

- Rule 6: bold text restricted to glossary definitions and critical callouts

Rules that are **absent** and need to be added:

- Prohibition on Markdown tables

- Requirement for one blank line between list items

### `aib-context.md` synthesis phase coverage

Phase 4 of `aib-context.md` delegates all formatting constraints entirely to `context-convention.md` without any inline reminders. Adding a compact formatting checklist to Phase 4 will create a second enforcement layer and reduce the chance of the AI overlooking the convention rules during synthesis.

### Test coverage

No existing test file validates the formatting rules in `context-convention.md` or checks that `aib-context.md` references the key prohibitions. The pattern established in `tests/test_analysis_prompt_structure.py` (asserting the presence or absence of specific strings in prompt and convention files) is directly reusable for the new regression tests.

---

## Best Practices

- **ATX headings for all structural labels** (Markdown Guide, GitHub Documentation Style Guide): Use `##`, `###`, `####` for every section and subsection label. Bold text within prose should signal emphasis, not structure. Documents using headings correctly benefit from browser and editor outline views, automatic TOC generation, and screen reader navigation. Applicability: directly supports replacing bold inline ADR labels with proper heading levels in the convention and reformatting the ADR blocks in `context.md`.

- **One blank line between list items for prose-heavy documents** (Diataxis documentation framework, Plain Text Working Group): For reference documentation where list items contain more than a single short phrase, inserting one blank line between items significantly improves scanability in both rendered and raw Markdown form. Applicability: directly supports the developer's second rule; the blank-line spacing requirement should be codified as a normative rule in the convention.

- **Prefer prose with nested bullets over tables for entity-attribute data** (Google Developer Documentation Style Guide): Tables are appropriate for comparative data with two or more semantically orthogonal columns. For a component registry where each row describes properties of a single entity, a bullet list with inline attribute notation is easier to read in raw Markdown, degrades better in narrow viewports, and is simpler to edit without a table editor. Applicability: directly supports replacing the Component Map table with a nested bullet list in `context.md`.

- **Cap heading nesting at H3 in prose documentation** (Divio documentation system, CommonMark tooling conventions): Reference documents read directly by humans should avoid H4 except for highly structured schemas (e.g., API field documentation). This rule keeps the outline shallow and the document scannable. Applicability: medium — the current `context.md` already stays mostly at H2/H3; the rule acts as a guardrail for future generations.

---

## External Benchmarking

- **Google Developer Documentation Style Guide — Tables versus Lists:** Google's guide specifies that tables are appropriate only when the data has two or more semantically distinct columns where the column relationship is important for comprehension. For entity-property data (such as a component map), a bulleted list is explicitly preferred because it is easier to scan in source form and more accessible on small screens. Takeaway: the Component Map table in `context.md` is a textbook case for the list-over-table pattern; the convention should mandate this.

- **Microsoft Writing Style Guide — Bold text usage:** Microsoft's guide restricts bold to UI control labels, key terms on first use, and critical warnings. Using bold as a field label inside a list item (e.g., `**Context:** ...`) is explicitly discouraged unless the term is being introduced for the first time. Takeaway: the ADR block formatting in `context.md` violates this guidance; the convention rule already captures the intent but the ADR formatting pattern crept in via prior generations.

- **CommonMark specification and Prettier Markdown formatting:** The CommonMark community and widely adopted Prettier formatter enforce one blank line between list items when items contain more than one line of content. This is the industry standard for readable Markdown source. Takeaway: the blank-line-between-bullets rule is not an aesthetic preference but an established Markdown authoring standard. Codifying it in the convention gives it normative weight.

---

## Minimal Spikes and Experiments

- **Spike: Verify current `context.md` violations against the three developer rules**
  - Hypothesis: The current `context.md` violates at least one of the three developer-specified formatting rules.
  - Approach: Manual scan of the full `context.md` content read during this analysis run, checking for Markdown table syntax, bold-text label patterns, and missing blank lines between list items.
  - Outcome: All three rule types are violated: one table (Component Map), multiple inline bold labels in ADR blocks, and dense bullet lists without inter-item spacing throughout.
  - Conclusion: Reformatting of the current `context.md` is necessary and has a well-defined scope (one table, ADR labels, whitespace normalization).

- **Spike: Verify the convention coverage gap**
  - Hypothesis: `context-convention.md` does not yet contain a table prohibition or a blank-line-between-bullets rule.
  - Approach: Read the Formatting Rules section of `context-convention.md` (rules 1–10).
  - Outcome: Confirmed — no table prohibition, no blank-line-between-bullets rule. Rule 6 (bold restriction) already exists but is insufficient alone to prevent the violations observed.
  - Conclusion: Adding exactly two new normative rules to the Formatting Rules section is the minimal sufficient convention change.

---

## Implementation Alternatives

### Alternative A — Convention-only

Update `context-convention.md` Formatting Rules with the five rules (three developer-specified plus two best-practice additions). Leave `aib-context.md` unchanged; leave current `context.md` unreformed.

- Trade-offs: Minimal change; DRY; single source of truth. The AI reads the convention on each run, so future `context.md` generations will be correct. Does not address existing violations in the current file.

- Codebase impact: 1 file changed.

### Alternative B — Convention + Prompt reinforcement

Add the five rules to `context-convention.md` AND add a compact "Formatting requirements" paragraph to `aib-context.md` Phase 4 synthesis instructions explicitly restating the most critical prohibitions (no tables, no bold labels, blank lines between bullets).

- Trade-offs: Dual-layer enforcement increases AI compliance reliability. Minor redundancy is acceptable because the convention remains the authoritative source and the prompt note is a brief reference. Does not address the existing `context.md` violations.

- Codebase impact: 2 files changed.

### Alternative C — Convention + Prompt + current `context.md` reform (recommended)

All of Alternative B, plus immediate manual reformatting of the current `context.md`: replace the Component Map table with a nested bullet list, replace ADR bold labels with plain-text labels or proper sub-headings, and insert blank lines between list items throughout.

- Trade-offs: Maximum immediate value for a developer who needs to read or edit `context.md` today. Cost is bounded — one table replacement, label reformatting in ~5 ADR blocks, and whitespace normalization. The next `aib-context.md` run will replace the file anyway, but the convention fix guarantees the next generation is also correct.

- Codebase impact: 3 files changed (convention, prompt, context.md).

**Recommendation: Alternative C.** The success criteria explicitly require the current `context.md` to be updated when violations exist. Violations are confirmed. The reformatting cost is bounded and the developer expressed a desire to read and edit the file now.

### Decision Points Catalog

| Decision Fork | Category | Tag | Rationale / Resolution |
| --- | --- | --- | --- |
| Whether to add formatting rules to both convention and prompt, or convention only | Documentation | resolve-autonomously | `input.md` `### Instructions` explicitly states "in the prompts and conventions" — both are in scope. |
| Whether to update the current `context.md` immediately | Documentation | resolve-autonomously | Success criteria in `request-R-20260514-2006.md` requires it when violations are confirmed; violations confirmed in spike. |
| Replacement format for the Component Map table | Documentation | resolve-autonomously | Developer rule prohibits tables; nested bullet list is the idiomatic substitute per Google Developer Docs Style Guide (External Benchmarking section). |
| Which additional best-practice rules to adopt beyond the three developer-specified ones | Documentation | resolve-autonomously | Success criteria requires at least two; research identifies blank-line spacing (already one of the three) and heading-depth cap as high-applicability practices with industry sources cited in Best Practices section. |

No `ask`-tagged forks identified. No Q-blocks generated.

---

## AI Copilot Suggestions

- **The "no tables" rule will permanently increase `context.md` length.** The Component Map table (20+ rows × 3 columns) is currently compact. Converting it to a nested bullet list will expand it substantially — possibly doubling the line count for that section. This is the correct tradeoff for human readability, but plan for a permanently longer file. The context-window management heuristic in `aib-context.md` (80% guard) may trigger more often after this change. Consider whether the Phase 4 context-window management note in `aib-context.md` needs a reminder to prioritize the Component Map section even when context is tight.

- **The ADR sub-field labels are a structural pattern, not just a formatting choice.** The `**Context:**`, `**Decision:**`, `**Rationale:**`, `**Consequences:**` labels inside ADR blocks serve as mini-schema field indicators. Simply removing bold will make the blocks harder to parse, not easier. A better approach is to convert ADR sub-fields from bold labels in a flat list to proper sub-bullet items with colon notation: `- Context: ...`, `- Decision: ...`. This preserves the field structure without using bold for labeling. The plan should specify this replacement pattern explicitly to avoid ambiguity during implementation.

- **Testing coverage should be regression-focused, not format-validation of the generated file.** Asserting the exact formatting of `context.md` is fragile because the file is fully replaced on each run and its content is AI-generated. The more durable tests are those that verify the convention and prompt files contain the required rule text — exactly the pattern used in `test_analysis_prompt_structure.py`. The plan should include those tests rather than trying to parse the generated `context.md`.
