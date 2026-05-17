# Analysis: R-20260510-2056 — Restructure analysis prompt and output format

## Executive Summary

- **Request ID:** R-20260510-2056

- **Title:** Restructure analysis prompt and output format

- **Purpose:** Reduce the analysis artifact to a leaner, more decision-focused document by removing four sections that duplicate `request.md` content or add verbose context without driving decisions (Domain Knowledge Essentials, Technical Knowledge & Terms, Testing, Multi-Perspective Stakeholder Review); add three new mandatory sections (Best Practices, Implementation Alternatives, Files Read During This Analysis Run); improve Q-block generation to proactively derive questions from identified implementation alternatives; and add a developer-configurable minimum-questions option to `input.md`.

- **`request.md` sections updated this run:** Assumptions (A2, A3, A4 confirmed from Q001, Q002, Q003 answers), Plan (Task 1 and Task 2 Done criteria corrected for 8-section count).

- **Q&A status:** All three Q-blocks answered. Q001 confirmed Files Read as a top-level `##` section (mandatory section count is 8). Q002 confirmed free-text minimum-questions option. Q003 confirmed Implementation Alternatives placement after Best Practices.

---

## Domain Knowledge Essentials

**AIB (AI Builder):** A minimal, model-agnostic, file-first framework for specification-driven software development. Operates through markdown prompts executed by an AI agent, with convention files enforcing artifact structure.

**Analysis artifact (`analysis-<request_id>.md`):** A reasoning-only document produced by `aib-analysis.md`. Records the AI's structured understanding of the request. NOT an implementation driver — `implement` must not read it.

**Convention file:** A normative markdown document (in `.aib_brain/conventions/`) defining the required structure, content rules, and quality gates for a specific AIB artifact type.

**Q-block:** A structured decision question written by the AI to `input.md ## Questions`. The developer answers Q-blocks before re-running analysis; unanswered blocks apply the recommended option automatically.

**Seed template:** A hard-coded string in `initialize.py` and `close-request.py` that defines the reset state of `input.md`. Both scripts must carry identical seed template strings.

**Implementation Alternative:** A distinct approach to satisfying the same requirement that leads to materially different code, structure, or behavior outcomes. The new analysis structure requires enumerating alternatives explicitly before generating Q-blocks.

**Minimum-questions option:** A new developer-configurable option (free-text integer, default 0) in `input.md ## Options` that sets a floor for the number of Q-blocks generated per analysis run.

---

## Technical Knowledge & Terms

**`aib-analysis.md`:** The markdown prompt file executed in an AI coding interface to produce `analysis-<request_id>.md` and update `request-<request_id>.md`. Located at `.aib_brain/prompts/`.

**`analysis-convention.md`:** Normative file at `.aib_brain/conventions/` governing the section structure and formatting of all analysis artifacts. Currently defines 9 mandatory sections; this request changes it to 8.

**`initialize.py` / `close-request.py`:** Python scripts in `.aib_brain/tools/` that seed and reset `input.md` to its seed template. Both must carry identical seed template strings. Changes to one must be mirrored in the other.

**`## Options` section:** The section in `input.md` containing opt-in toggles and configuration options. Currently has two toggles; the request adds a third free-text option: `- Minimum questions: 0`.

**Mandatory section count:** The current convention mandates 9 sections. After this change: 8 sections (remove 4, add 3: Best Practices, Implementation Alternatives, Files Read During This Analysis Run). Files Read is a top-level `##` section (confirmed Q001).

**Evidence log:** A sub-section currently required inside Research Results in `analysis-convention.md`. This request removes the requirement — research findings are stated without a formal sub-section.

**UAT scenarios:** Manual test scenarios documented in `UAT_scenarios-<request_id>.md`. The Testing section currently lives in the analysis artifact; this request moves test definition exclusively to `request.md ## Plan` and removes it from the analysis.

---

## Research Results

**Files read during this analysis run:**

- `.aib_memory/requests_register.md`
- `.aib_memory/request-R-20260510-2056.md`
- `.aib_memory/input.md`
- `.aib_memory/instructions.md`
- `.aib_memory/context.md`
- `.aib_memory/analysis-R-20260510-2056.md` (prior run — replaced by this document)
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `tests/test_analysis_prompt_structure.py`

**Findings:**

- `analysis-convention.md` defines 9 mandatory `[REQ]` sections. The four sections targeted for removal (Domain Knowledge Essentials, Technical Knowledge & Terms, Testing, Multi-Perspective Stakeholder Review) are all substantive — none are stubs.

- The prompt `aib-analysis.md` generates Q-blocks under an "Ambiguity detection" step with no prior Implementation Alternatives identification step. Q-block generation is reactive (spec ambiguity) rather than proactive (approach variants).

- Both `initialize.py` and `close-request.py` contain identical seed template strings with two `## Options` toggles. Neither has a minimum-questions option.

- `tests/test_analysis_prompt_structure.py` tests removed headings from `aib-analysis.md` and `request-convention.md`. It does NOT test `analysis-convention.md` section structure; new tests for that are in scope.

- `context.md` FR-004 explicitly lists 9 mandatory analysis sections. It requires an update to reflect the new 8-section structure.

- Q001 answer (confirmed this run): Files Read is a top-level `## Files Read During This Analysis Run` section, peer of Research Results and other content sections. Mandatory count = 8.

---

## External Benchmarking

**Google Design Document format:**
- Template: Abstract, Background, Design, Alternatives Considered, Cross-Cutting Concerns. Deliberately omits a dedicated "Domain Knowledge" section — background is embedded only when strictly necessary.
- Key takeaway: lean documents are more durable and more consistently maintained.
- Applicability: directly supports removing Domain Knowledge Essentials and Technical Knowledge & Terms from the analysis (that content belongs in `context.md`).

**MADR (Markdown Any Decision Records):**
- Format: Title, Status, Context, Decision Drivers, Considered Options, Decision Outcome, Pros and Cons. Alternatives are a first-class mandatory section — not optional.
- Key takeaway: decision records without explicit alternatives are incomplete by design.
- Applicability: validates adding Implementation Alternatives as a mandatory `[REQ]` section.

**RFC / IETF document structure:**
- Explicitly presents Alternative Solutions before the Selected Approach. Evidence log per finding is NOT a standard RFC requirement.
- Key takeaway: removing the Evidence log sub-section requirement from Research Results is consistent with formal technical standards.
- Applicability: supports removing the Evidence log sub-section from `analysis-convention.md`.

**AWS Well-Architected Framework documentation:**
- Pairs "When to use" and "Trade-offs" sub-sections per pattern, even when one approach is clearly recommended.
- Applicability: validates requiring key trade-offs per alternative in the new Implementation Alternatives section.

---

## Minimal Spikes and Experiments

No spike was conducted. All changes are deterministic text edits to a markdown convention file, a markdown prompt file, and two Python scripts. No technical uncertainty warrants an experiment. The behavior of the three new sections (Best Practices, Implementation Alternatives, Files Read During This Analysis Run) is fully defined by the request scope and the confirmed Q&A answers. Feasibility is established.

---

## AI Copilot Suggestions

**Observation 1 — Q001 confirmed top-level `##` section; plan must reference 8 (not 7) mandatory sections.**
The developer confirmed (Q001 Option A) that "Files Read During This Analysis Run" is a top-level `##` section, not a `###` sub-heading inside Executive Summary. This increases the mandatory section count from the initially estimated 7 to 8. Task 1 and Task 2 Done criteria in the plan have been corrected accordingly. Suggestion: verify during implementation that the convention, the prompt output instructions, and all tests reference 8 sections consistently.

**Observation 2 — Minimum-questions option description risk (confirmed as free-text).**
The developer confirmed (Q002 Option A) the free-text approach: `- Minimum questions: 0`. A free-text integer field relies on the AI parsing the number and acting on it. The default of 0 is safe (preserves existing behavior). Suggestion: the prompt handling rule should specify that the AI generates at least N Q-blocks when N genuine decision points exist, but documents the shortfall explicitly rather than generating filler questions. This prevents the option from becoming a noise source.

**Observation 3 — Section removal improves convention-prompt alignment surface, but introduces three new alignment requirements.**
Removing 4 sections and adding 3 (Best Practices, Implementation Alternatives, Files Read During This Analysis Run) results in a net reduction of the alignment surface. However, each new section requires a matching generation instruction in the prompt. Suggestion: after all tasks are implemented, run a single-pass review to confirm every section in the updated convention has a corresponding generation instruction in `aib-analysis.md` and vice versa. This is the highest-risk consistency check for this request.

**Observation 4 — Scope is well-bounded; the main risk is mismatched seed template strings.**
The change set is contained: one convention file, one prompt file, two Python scripts, and tests. The principal mechanical risk is forgetting to update one of the two seed template occurrences in `aib-analysis.md` (Auto-Request Creation Branch step 8 and Standard flow final step). Suggestion: Task 4 Done criteria explicitly checks all four occurrences (initialize.py, close-request.py, and both in aib-analysis.md) — ensure the implementation preserves this four-way consistency check.

---

## Testing

- T1 — Convention section removal (Domain Knowledge): `analysis-convention.md` must not contain "Domain Knowledge Essentials" as a section heading. Expected outcome: grep on the file returns no match.

- T2 — Convention section removal (Technical Knowledge): `analysis-convention.md` must not contain "Technical Knowledge & Terms" as a section heading. Expected outcome: grep on the file returns no match.

- T3 — Convention section removal (Testing): `analysis-convention.md` must not contain "Testing" as a mandatory `[REQ]` section. Expected outcome: the file does not have a "Testing [REQ]" or "## Testing" entry in the mandatory section list.

- T4 — Convention section removal (Multi-Perspective): `analysis-convention.md` must not contain "Multi-Perspective Stakeholder Review" as a mandatory section. Expected outcome: grep on the file returns no match.

- T5 — Convention new section (Best Practices): `analysis-convention.md` must define "Best Practices" as a mandatory section. Expected outcome: file contains "Best Practices" with a `[REQ]` marker.

- T6 — Convention new section (Implementation Alternatives): `analysis-convention.md` must define "Implementation Alternatives" as a mandatory section. Expected outcome: file contains "Implementation Alternatives" with a `[REQ]` marker.

- T7 — Files Read as a top-level `##` section: `analysis-convention.md` must define "Files Read During This Analysis Run" as a top-level `##` mandatory section (confirmed by Q001). Expected outcome: file contains a `## Files Read During This Analysis Run` or similar heading at the `##` level with a `[REQ]` marker.

- T8 — Executive Summary scoped to 3 fields only (Request ID, Title, Purpose): `analysis-convention.md` Executive Summary rule must not list Files Read as a sub-heading (confirmed by Q001). Expected outcome: convention text for Executive Summary does not reference a "Files Read" sub-heading.

- T9 — Evidence log absent from Research Results: `analysis-convention.md` must not require an Evidence log sub-section. Expected outcome: grep for "evidence log" in the file (case-insensitive) returns no match.

- T10 — Prompt has Implementation Alternatives step: `aib-analysis.md` must include an explicit step for identifying implementation alternatives before Q-block generation. Expected outcome: the phrase "Implementation Alternatives" appears in the main flow section of the prompt (not only in output section labels).

- T11 — Minimum-questions option in seed templates: `initialize.py` and `close-request.py` must both contain `Minimum questions` in their seed template strings. Expected outcome: grep on each file returns at least one match.

- T12 — Mandatory section count is 8 in convention: `analysis-convention.md` mandatory section list contains exactly 8 items. Expected outcome: counting `[REQ]` entries in the mandatory section list yields 8.

- T13 — Existing test suite does not regress: `pytest tests/` exits with code 0. Expected outcome: all previously passing tests continue to pass after all changes.

See UAT_scenarios-R-20260510-2056.md — UAT-01 for manual verification of the full analysis run producing the correct new section structure.

---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The request is a well-scoped, low-risk document restructuring. Removing Domain Knowledge Essentials and Technical Knowledge & Terms from the analysis is architecturally sound: those sections belong in `context.md`, which is the designated product knowledge store. The analysis artifact should focus on reasoning about the specific request, not re-explaining standing product concepts. Adding "Implementation Alternatives" as a named mandatory section creates an auditable record of the decision space considered by the AI — a meaningful traceability improvement. The Q001 answer (Files Read as a top-level `##` section) is architecturally coherent: making it a peer section ensures it appears in all markdown navigators and is independently linkable.

- Risk: Convention and prompt must be updated atomically; mismatch between them leaves the system in an inconsistent state.
- Risk: Tests that check for old section names in `analysis-convention.md` do not yet exist; Task 5 adds them.
- Risk: Two seed template occurrences exist in `aib-analysis.md`; missing either one creates a behavioural inconsistency.
- Recommendation: The four-way consistency check in Task 4 Done criteria (initialize.py, close-request.py, both aib-analysis.md occurrences) is essential and must not be omitted.

### Product Owner

The change delivers clear value: shorter, more focused analysis artifacts are more likely to be read and acted upon. Removing Multi-Perspective Stakeholder Review reduces performative content; adding Implementation Alternatives makes decision points visible and gives the developer a meaningful, actionable interaction opportunity. The minimum-questions option gives developers control over decision transparency, supporting adoption across different working styles.

- The scope is correctly bounded; no lifecycle changes are included.
- Success criteria are measurable and file-level, consistent with AIB's test approach.
- The Q001 decision (top-level `##`) is easy to navigate in any markdown renderer — it improves the product's auditability story.
- Risk: If the Testing section is fully removed from the analysis but test definitions in `request.md ## Plan` are not comprehensive, coverage may erode over time.

### User

The restructured analysis will be shorter and faster to read. Markdown headings instead of bold titles improve navigation. Removing four sections and replacing them with three more focused ones reduces cognitive load. The minimum-questions option is a useful control; its discoverability depends on it appearing clearly in `input.md` after each seed reset. The Files Read section as a top-level `##` section (Q001 confirmed) makes it immediately visible in any document outline — developers can quickly verify the AI read the correct context.

- Improvement: Implementation Alternatives makes decision trade-offs explicit and scannable before answering Q-blocks.
- Risk: Developers who used Domain Knowledge Essentials as an orientation tool will need to consult `context.md` directly.
- Risk: If the minimum-questions default (0) is never changed, developers may not realize they can surface more alternatives explicitly.

### Security Officer

No security impact. This request modifies markdown prompt and convention files only. No authentication, authorization, data exposure, or network surface changes are introduced. The minimum-questions option is a plain-text integer field; no injection risk if treated as a numeric hint rather than executable content. Seed template changes in Python scripts are string literals; no dynamic content is involved.

### Data Governance Officer

No data governance impact. All modified artifacts are internal engineering documentation files. No personally identifiable information, customer data, or regulated data is involved. Classification remains Internal engineering documentation. Retention is governed by VCS history (unchanged). No external data sources are introduced.
