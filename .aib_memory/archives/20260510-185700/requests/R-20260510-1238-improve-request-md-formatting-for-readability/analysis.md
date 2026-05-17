## Executive Summary

- **Request ID:** R-20260510-1238

- **Title:** Improve request.md formatting for readability

- **Purpose:** The `request.md` file format is currently dense and hard to scan for human readers. Plan task sub-fields are rendered as bold inline labels (`**Intent:**`, `**Outputs:**`, etc.) rather than structured headings. Procedure steps are not separated by whitespace. This request updates the convention and the generating prompt to produce more readable output using markdown sub-headers, consistent empty-line spacing, and a prohibition on tables.

- **Scope summary:** Changes target `.aib_brain/conventions/request-convention.md` (formatting rules), `.aib_brain/prompts/aib-analysis.md` (plan schema), and `tests/test_analysis_prompt_structure.py` (updated schema assertions). No Python tooling or lifecycle semantics change.

- **`request.md` updates this run:** `## Assumptions`, `## Plan`, and `## Documentation` sections have been added. No Q-blocks raised — the request is unambiguous and all decisions are resolvable from existing workspace documentation.

## Domain Knowledge Essentials

- **request.md** — The primary specification artifact for a single AIB work item. It is AI-generated from `input.md` by `aib-analysis.md` and read by `aib-implement.md`. Its format is normatively defined by `request-convention.md`.

- **Plan task schema** — The structured template used inside the `## Plan` section to describe discrete implementation tasks. Each task currently uses bold inline labels (`**Intent:**`, `**Outputs:**`, etc.) as field identifiers.

- **Level-4 markdown header (`####`)** — A heading level deep enough to function as a section divider inside a `### Task N` block without disrupting the document outline used by the `## Plan` level-2 and `### Task N` level-3 headings.

- **Bold inline label** — The current format for plan sub-fields (e.g., `**Intent:** text`). These are rendered without visual separation from body text, reducing scannability.

- **Seed template** — The baseline state of `input.md`. Any deviation from this template is a "non-stub" state and triggers archiving before reset.

- **Impacted roles:**
  - Developer — primary reader of `request.md`; this change directly reduces cognitive overhead.
  - AI Automation Agent — generates `request.md`; must conform to updated schema.
  - AIB Maintainer — owns the convention files; approves changes.

- **Business processes touched:**
  - Execute analysis workflow (generates `request.md`).
  - Execute implement workflow (reads `request.md`).

## Technical Knowledge & Terms

- **`request-convention.md`** — Normative document defining structure, formatting rules, and content rules for `request.md`. Located at `.aib_brain/conventions/request-convention.md`. All formatting changes must be reflected here first.

- **`aib-analysis.md`** — The analysis prompt that generates `request.md`. It embeds the plan task schema inline. Must be kept synchronised with `request-convention.md`.

- **`test_analysis_prompt_structure.py`** — Automated test suite that asserts presence/absence of specific text fragments in `aib-analysis.md` and `request-convention.md`. Currently asserts `**Outputs:**` is present; this will need updating.

- **Markdown heading hierarchy used in `request.md`:**
  - `##` — Mandatory top-level sections (Goal, Background, Scope, …).
  - `###` — Task headings inside `## Plan` (e.g., `### Task 1: Name`).
  - `####` — Proposed new level for task sub-fields (Intent, Outputs, Procedure, etc.).

- **Empty-line separation** — Markdown rendering collapses multiple blank lines to one; requiring one blank line between procedure steps produces correct spacing in rendered views and improves raw-file readability.

- **Markdown table prohibition** — The request explicitly prohibits tables inside `request.md`. No current template produces tables there; the prohibition is a forward-looking constraint to be encoded in the convention.

- **Files read during this analysis:**
  - `.aib_memory/instructions.md`
  - `.aib_memory/requests_register.md`
  - `.aib_memory/input.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_memory/context.md`
  - `.aib_memory/archives/20260510-122412/requests/R-20260510-0744-archive-input-md-on-standard-flow-reset/request.md` (reference example of current format)
  - `tests/test_analysis_prompt_structure.py`

- **Evidence log:**
  - `test_analysis_prompt_structure.py` asserts `"**Outputs:**" in content` → implication: this assertion breaks when `**Outputs:**` is converted to `#### Outputs`; test must be updated.
  - Existing `request.md` example uses bold labels throughout the Plan → confirms the current state that motivated this request.
  - `request-convention.md` Formatting Rules section currently prohibits only certain heading levels, not tables → table prohibition must be added.

## Research Results

1. **Pattern scan — existing request.md files:** The archived request `R-20260510-0744` shows the current state: all plan task sub-fields are bold labels with no blank lines between them. Procedure steps are numbered consecutive lines with no spacing. This confirms the problem statement.

2. **Convention alignment check:** `request-convention.md` defines the Plan task schema using the same bold-label format as produced by `aib-analysis.md`. Both files must be updated together.

3. **Test impact scan:** `test_analysis_prompt_structure.py` contains a positive assertion `assert "**Outputs:**" in content` for both `aib-analysis.md` and `request-convention.md`. Converting `**Outputs:**` to `#### Outputs` will cause these two assertions to fail. The test suite must be updated to match the new format.

4. **Table prohibition scope:** No current `request.md` template or existing example uses markdown tables. The prohibition is a preventive constraint only; no retroactive cleanup of existing files is required.

5. **Scope check — `analysis-convention.md`:** This convention governs `analysis.md`, not `request.md`. It contains similar bold labels in quoted schema blocks (documentation only). It is out of scope for this request.

## External Benchmarking

- **GitHub's documentation style guide (Microsoft Docs / GitHub docs conventions):** Both recommend using heading levels as semantic structure over bold text for sub-sections. Takeaway: converting `**Field:**` to `#### Field` aligns with industry standard documentation practice.
  - Key takeaway: headings produce collapsible sections in some Markdown renderers and improve accessibility compared to bold labels.
  - Applicability: directly supports the proposed change; adopted.

- **Diátaxis documentation framework (structuring technical documentation):** The Diátaxis framework (used by many open-source projects including ReadTheDocs) emphasises visual chunking — clear block separation with whitespace — as a prerequisite for scannability in procedural/reference documents. Takeaway: the request's requirement for empty lines between procedure steps is consistent with this principle.
  - Key takeaway: blank lines between procedure steps reduce error rates when following multi-step instructions.
  - Applicability: directly supports the empty-line requirement; adopted.

- **Google Developer Documentation Style Guide — Lists and procedures:** Recommends that numbered procedure steps be visually separated from each other, and that sub-sections within a procedure use headings rather than inline labels. This corroborates both the heading conversion and the spacing requirement.
  - Key takeaway: numbered steps are more readable with vertical breathing room; consistent with the request's intent.
  - Applicability: adopted; reinforces the proposed changes.

## Minimal Spikes and Experiments

No spikes are required. The changes are purely formatting/text changes to two convention/prompt files and one test file. All affected files are plain text; no runtime behaviour changes.

A manual readability comparison can be done by viewing the archived `request.md` (bold-label format) against a re-formatted version — no code execution is needed to validate the change intent.

## AI Copilot Suggestions

1. **Consider heading level consistency across the whole document.** The proposal to use `####` for task sub-fields is sound, but the convention should also address spacing between `## Plan` top-level section and the first `### Task` block, and between consecutive tasks. Without explicit guidance, AI-generated files may be inconsistent. Suggestion: add a rule stating that one blank line separates each `### Task N` block from the next, and one blank line follows the `## Plan` heading before the first task.

2. **The "No markdown tables" constraint has no enforcement mechanism.** Currently there is no validation test for table presence in `request.md`. If the convention adds this rule, consider also adding a negative assertion in `test_analysis_prompt_structure.py` (or a new test file) that checks the convention and prompt do not embed a markdown table pattern within the Plan schema block. Suggestion: add at least one assertion to the existing test suite that verifies the Plan schema block in both files does not contain `|` as a table delimiter.

3. **Scope may be narrower than the developer intended.** The input says "revise the format of the whole request.md file" but the actionable specifics only cover the Plan task schema. The other mandatory sections (Goal, Background, Scope, etc.) do not have known formatting issues beyond the Plan section. Suggestion: explicitly confirm in the convention that top-level sections only require one blank line between them (already implicit but not written), and flag any other specific non-Plan improvements the developer has in mind — if none, scope is correct as defined. No scope creep is recommended beyond what is stated.

## Testing

- T1 — Convention sub-header format assertion: Assert that `request-convention.md` contains `#### Intent` and `#### Outputs` in the Plan schema block. Expected outcome: both strings present; test passes.

- T2 — Prompt sub-header format assertion: Assert that `aib-analysis.md` contains `#### Intent` and `#### Outputs` in the Plan schema block. Expected outcome: both strings present; test passes.

- T3 — Convention bold-label absence: Assert that `request-convention.md` does NOT contain `**Intent:**` or `**Done Criteria:**` as plan-schema labels. Expected outcome: neither string present; test passes.

- T4 — Prompt bold-label absence: Assert that `aib-analysis.md` does NOT contain `**Intent:**` as a plan-schema label. Expected outcome: string absent; test passes.

- T5 — Empty-line procedure step requirement present in convention: Assert that `request-convention.md` contains wording requiring empty lines between procedure steps. Expected outcome: the requirement text is present; test passes.

- T6 — Table prohibition present in convention: Assert that `request-convention.md` explicitly prohibits markdown tables in `request.md`. Expected outcome: prohibition text present; test passes.

- T7 — Updated `**Outputs:**` test assertion: The existing positive assertion `assert "**Outputs:**" in content` in `test_analysis_prompt_structure.py` must be updated to `assert "#### Outputs" in content`. Expected outcome: test passes with new assertion; old assertion removed.

- T8 — Full test suite regression: Run `pytest tests/test_analysis_prompt_structure.py` and confirm all tests pass. Expected outcome: zero failures.

- T9 — Re-run idempotency: Run `aib-analysis.md` again after implementation and confirm `request-R-20260510-1238.md` Plan section uses `####` headers and the analysis file is fully replaced without merge artifacts. Expected outcome: clean re-run with conformant output.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The requested formatting change is technically straightforward: replace bold inline labels with level-4 markdown headings in two text files, add empty-line guidance, and update one test file. The architectural risk is low — no runtime code, no data model, no lifecycle semantics change. The primary risk is convention-test drift: if the test file is not updated atomically with the convention, CI will fail. The two-file atomicity (convention + prompt) is a known pattern in this codebase (previous requests like R-20260507 established this). The solution is well within established patterns.

Findings:
- The change is low-risk and easily reversible.
- The test file update is the highest-risk element (brittle text assertions).
- Convention and prompt must be updated in the same implementation run to avoid transient CI failures.
- No schema version bump is required; format changes are backward-compatible for archived files.
- A table-prohibition test is missing from the plan; recommend adding it.

### Product Owner

The request has clear business value: developers spend time with `request.md` during analysis and implementation; reducing reading friction reduces cognitive overhead. The success criteria are measurable and testable. The scope is appropriately narrow. The risk of scope creep is low because the developer gave specific examples (plan sub-fields, procedure step spacing). One gap: "propose other formatting improvements" is open-ended and may invite uncontrolled scope growth. Recommend that the plan treat this as a bounded task with explicit proposals listed, not an open invitation.

Findings:
- Clear business value with low delivery risk.
- "Propose other improvements" clause should be bounded in the plan.
- No acceptance criteria require user-facing UI changes.
- Completion is verifiable via test suite and manual file review.
- Documentation impact is light (convention + prompt only).

### User (Developer)

The change directly addresses the stated pain point: the `request.md` plan section is hard to read in its current dense, bold-label format. Converting to `#### Sub-headers` with empty lines between sections and steps will noticeably improve scannability in both raw Markdown and rendered views. No workflow changes are required from the developer; the improvement is automatic in all future AI-generated files.

Findings:
- Direct, visible improvement to daily developer experience.
- No new actions required from the developer post-implementation.
- Archived files will not be updated (out of scope) — existing closed requests retain old format.
- The prohibition on tables avoids future readability regressions.
- The change is non-breaking for the developer's usage patterns.

### Security Officer

This request involves only plain-text formatting changes to convention and prompt files. There is no code execution, no data handling, no authentication or authorization surface, and no new dependencies. Attack surface impact: none. Data exposure risk: none. No security concerns are raised.

Findings:
- No security-relevant changes.
- No new file permissions required.
- No external data sources introduced.
- No user-input handling modified.
- No OWASP Top 10 concerns apply to this change.

### Data Governance Officer

The affected files (`request-convention.md`, `aib-analysis.md`, `test_analysis_prompt_structure.py`) are internal engineering documentation and tooling assets. They are VCS-tracked and classified as Internal. No data lineage, retention, or compliance concerns are raised by a formatting change to these files. The `request.md` files generated in the future will contain the same categories of information as before (engineering specifications); only their formatting changes.

Findings:
- No change to data classification of affected files.
- No new data retention obligations.
- No PII or sensitive data involved.
- VCS tracking ensures full audit trail for the convention changes.
- No compliance impact.
