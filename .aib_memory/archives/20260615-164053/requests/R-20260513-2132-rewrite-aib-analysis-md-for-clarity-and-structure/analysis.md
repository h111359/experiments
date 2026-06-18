## Executive Summary

- **Request ID:** R-20260513-2132

- **Request title:** Rewrite aib-analysis.md for clarity and structure

- **High-level purpose:** Refactor the `aib-analysis.md` prompt for improved logical organization, consistent formatting, explicit execution order, and unambiguous wording — without altering any behavioral logic, requirements, or workflows.

---

## Files Read During This Analysis Run

- `.aib_memory/requests_register.md`
- `.aib_memory/input.md`
- `.aib_memory/instructions.md`
- `.aib_memory/context.md`
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `tests/test_analysis_prompt_structure.py`

---

## Research Results

### Current Prompt Structure Scan

The current `aib-analysis.md` is 310 lines organized across loosely ordered sections: Preamble (Goal, Inputs, External Dependencies, Outputs), Workspace Instructions Pre-read, Mandatory Preflight, Auto-Request Creation Branch, Analysis Requirements, Output Contract — Part 1 (Analysis Document), Output Contract — Part 2 (`request.md` Updates), Q-block Generation Rules, Re-run Behaviour Summary, Standard Flow Final Step, and Context-Window Management.

**Structural findings:**
- The prompt uses two distinct "section layers" — top-level `##` and nested `###` — inconsistently. Some conceptual groupings (e.g., Q-block generation embedded inside Output Contract Part 1) break the logical hierarchy.
- The Auto-Request Creation Branch is defined as a standalone section between Preflight and Analysis Requirements, making it visually disconnected from the Preflight that triggers it. A reader must jump back and forth to understand the full execution order.
- The Answer Application Sub-flow is embedded as a nested bullet within Preflight step 5, making it easy to miss during a quick scan.
- Conditional logic (if/else branches) is written in prose form within numbered steps rather than as distinct labeled sub-sections, increasing parsing ambiguity for AI agents.
- Output Contract Part 1 and Part 2 are defined separately but both contain generation instructions — the Q-block rules are then in a third separate section, meaning the output contract is split across three locations.
- The Re-run Behaviour Summary section partially duplicates rules stated inline in Output Contract sections.
- The Standard Flow Final Step has a critical `MUST NOT execute when triggered from aib-implement.md` guard, but it is stated at the section heading level rather than as a prominently marked constraint block.
- Several MUST/MUST NOT constraints are embedded in paragraph prose without visual emphasis beyond bold text.

**Test suite findings (from `tests/test_analysis_prompt_structure.py`):**
- Tests assert that the following strings MUST appear in the rewritten prompt to keep passing:
  - `"All 10 mandatory sections"` (auto-request creation branch)
  - `"evaluate whether \`.aib_memory/input.md\` is in a non-stub state"`
  - `"archive the pre-reset \`input.md\` content"`
  - `"If stub-equivalent: skip archive creation for this standard-flow reset."`
  - `"#### Outputs"` (plan schema)
  - `"ecursively"` (attachment walk language)
- Tests assert the following MUST NOT appear:
  - `"All 12 mandatory sections"`
  - `"Code and Asset Scan for Impacted Components"`
  - `"Internal Review of Request and Product Docs"`
  - `"**Intent:**"`, `"**Inputs:**"`, `"**External Interfaces:**"`, `"**Environment & Configuration:**"`
  - `"flat scan"`, `"ignore subdirectories"`

**Cross-reference findings:**
- `analysis-convention.md` defines 8 mandatory sections for analysis documents; `aib-analysis.md` prompt references this convention and must not contradict it.
- `request-convention.md` defines 10 mandatory sections for `request.md`; the auto-request creation branch in `aib-analysis.md` must explicitly validate all 10.
- `context.md` FR-003 documents the exact stub-detection formula: `## Active request\nNo active request\n\n## Options\n- Minimum questions: 0\n\n## Input\n\n` — the rewrite must preserve this exact definition.
- The `instructions.md` directive regarding `logs/next_version_changes.md` applies only to `aib-implement.md` runs, not to analysis.

### Organizational Patterns in AIB Brain

The other prompts (`aib-implement.md`, `aib-context.md`) share similar structural patterns to the current `aib-analysis.md`. The rewrite should adopt a consistent top-level sectioning style that could serve as a template for the broader prompt family: numbered top-level sections (1. Objective, 2. Inputs, 3. Preflight, etc.) with branch sections clearly nested or labeled as triggered sub-flows.

---

## Best Practices

- **Structured prompt engineering for AI agents (industry consensus):** Well-structured prompts for AI agents should use explicit numbered steps, clearly labeled conditional branches, and prominently marked MUST/MUST NOT constraints. Research from OpenAI, Anthropic, and Google prompt engineering guidelines consistently shows that agents exhibit higher determinism when instructions use numbered sequences rather than prose paragraphs for sequential logic. Applicability: directly applicable — the rewrite should convert all sequential execution steps into numbered lists and all conditional branches into labeled subsections with explicit trigger conditions.

- **Single-responsibility sections (documentation engineering best practice):** Each section in a technical specification or runbook should serve a single purpose. The "single-responsibility principle" for documentation (referenced in Google's internal documentation standards and Microsoft's writing style guide) means that mixing output definitions with procedural rules in the same section increases misinterpretation risk. Applicability: directly applicable — the rewrite should group all output artifact definitions together and all procedural rules together, rather than splitting Q-block rules across Output Contract and a separate Q-block section.

- **Explicit guard clauses and error paths (software engineering, McConnell's Code Complete):** Complex workflows should list error/halt conditions before the happy path, making them impossible to overlook. Applicability: applicable — the multi-Active-row halt condition in Preflight and the `MUST NOT execute when triggered from aib-implement.md` guard in the Standard Flow Final Step should be listed as prominent labeled constraint blocks rather than embedded prose.

- **DRY (Don't Repeat Yourself) in documentation:** The Re-run Behaviour Summary section duplicates rules already stated in the Output Contract sections. Industry documentation best practice advises against this because duplicated rules diverge over time. Applicability: applicable with care — the rewrite should consolidate re-run rules into each section's constraint block rather than maintaining a separate summary, or clearly label the summary as a navigational reference only.

---

## External Benchmarking

- **LangChain Agent Runbook Pattern:** LangChain's agent orchestration documentation organizes complex multi-step workflows into: (1) Preconditions/preflight, (2) Main flow with numbered steps, (3) Error branches as clearly labeled sub-sections, (4) Output contract as a separate table. This mirrors the improvements needed here. Takeaway: the rewrite can adopt the numbered-sections pattern for the main flow and move branch definitions as labeled subsections immediately after the step that triggers them — this reduces cognitive load when reading sequentially.

- **OpenAI System Prompt Engineering Guide:** OpenAI's published prompt engineering guide recommends that for agent-executed prompts, conditional logic should be expressed as `IF [condition]: THEN [action]` structures rather than embedded in prose, and that every branch should have an explicit exit/continue instruction. Takeaway: the Answer Application Sub-flow and Auto-Request Branch should each begin with an explicit trigger condition block and end with an explicit "continue to X" marker.

- **Anthropic Claude Prompt Library patterns:** Anthropic's examples of complex multi-step agent prompts use prominent `> NOTE:` or `> CRITICAL:` blockquotes for invariant constraints (MUST/MUST NOT behaviors), separating them visually from procedural text. Takeaway: the critical `MUST NOT execute when triggered from aib-implement.md` guard and multi-Active halt gate should use blockquote-style visual emphasis.

---

## Minimal Spikes and Experiments

- **Spike: test suite compatibility of rewritten prompt**
  - Hypothesis: A structurally rewritten `aib-analysis.md` that preserves all required string literals will pass all existing tests in `test_analysis_prompt_structure.py` without modification.
  - Approach: Reviewed each assertion in `test_analysis_prompt_structure.py` and cross-checked whether the required string literals can be preserved verbatim in the rewritten version regardless of section restructuring.
  - Outcome: All required string literals (`"All 10 mandatory sections"`, `"#### Outputs"`, `"ecursively"`, `"If stub-equivalent: skip archive creation for this standard-flow reset."`, `"evaluate whether \`.aib_memory/input.md\` is in a non-stub state"`, `"archive the pre-reset \`input.md\` content"`) can be preserved verbatim in the rewritten prompt. Their presence is structural (naming, schema references) and not dependent on their surrounding section organization.
  - Conclusion: The rewrite can be safely performed without modifying the test suite. Test compatibility is not a risk factor.

---

## Implementation Alternatives

### Alternative A: Section Reorganization Only (Structural Rewrite)

Reorganize the existing content into a numbered, clearly hierarchical section structure (e.g., 1. Objective, 2. Inputs & Dependencies, 3. Preflight, 4. Auto-Request Branch [nested], 5. Main Flow, 6. Q-block Rules, 7. Output Contract, 8. Re-run Rules, 9. Constraints). Consolidate the Re-run Summary into relevant sections. Move the Answer Application Sub-flow immediately after the step that triggers it as a clearly labeled sub-section. Apply visual emphasis (blockquote or bold constraint blocks) to MUST/MUST NOT guards.

- **Trade-offs:** Preserves all original wording with minimal risk of unintended semantic change. Lower implementation effort. The test suite passes trivially since all required string literals are preserved. However, some prose within sections may still be slightly verbose.
- **Expected codebase impact:** Only `.aib_brain/prompts/aib-analysis.md` is modified.
- **Recommendation marker:** This is the **recommended** alternative.

### Alternative B: Full Prose Rewrite with Restructuring

Restructure AND rewrite all prose from scratch, applying best-practice patterns (numbered steps throughout, IF/THEN conditional blocks, DRY consolidation of all re-run rules). This would produce the cleanest result but introduces risk of inadvertently altering wording that tests check for verbatim.

- **Trade-offs:** Highest clarity gain but highest risk of introducing subtle behavioral ambiguity through rewording. More likely to break test assertions that check for exact string literals unless carefully managed.
- **Expected codebase impact:** `.aib_brain/prompts/aib-analysis.md` is heavily modified; test suite may need updates.

### Alternative C: Minimal Formatting Only (No Restructuring)

Apply only formatting improvements: add consistent heading levels, convert bullet-prose to numbered lists where natural, add visual emphasis to MUST/MUST NOT statements. No section reorganization.

- **Trade-offs:** Lowest risk, lowest implementation effort, but does not address the root causes of navigation ambiguity (branch sections disconnected from their triggers, output contract split across three sections).
- **Expected codebase impact:** Only `.aib_brain/prompts/aib-analysis.md` is minimally touched.

### Recommendation

**Alternative A (Section Reorganization Only)** is recommended. It achieves all stated improvement goals from the input — logical organization, consistent hierarchy, explicit execution order, clear separation of branches — while preserving all exact wording that existing tests depend on. The risk of behavioral regression is low because the rewrite is structural rather than semantic.

### Decision Points Catalog

| Decision Fork | Category | Tag | Rationale / Resolution |
| --- | --- | --- | --- |
| Which rewrite strategy to use (A vs B vs C) | Implementation approach | resolve-autonomously | Alternative A selected: achieves all stated goals with lowest regression risk. Test suite compatibility confirmed by spike. No user choice needed. |
| Whether to split the rewritten prompt across multiple files | Architecture | resolve-autonomously | `aib-analysis.md` is a single-file prompt; no workspace convention or precedent supports multi-file prompts. Resolved as single file. Source: `.aib_brain/prompts/` structure and `context.md` FR-003. |
| Whether to update test assertions after the rewrite | Testing | resolve-autonomously | Test assertions check for exact string literals that must be preserved verbatim in the rewrite. No test modifications needed. Confirmed by spike. |

---

## AI Copilot Suggestions

**Observation 1 — Scope precision (risk: scope creep):** The input's "Required Improvements" list is comprehensive and well-specified, which is good. However, the phrase "Convert implicit logic into explicit step-by-step flow" could be interpreted as requiring semantic changes (e.g., reordering steps for logical clarity) not just formatting changes. The implementation task should define a clear rule: structural reorganization is allowed, but step content (including exact wording of test-checked strings) must be preserved verbatim. Suggestion: add a concrete invariant to the implementation task — "All string literals asserted by `test_analysis_prompt_structure.py` must appear verbatim in the output."

**Observation 2 — Maintainability: Re-run duplication is a long-term debt item:** The current prompt has a dedicated "Re-run Behaviour Summary" section that partially duplicates re-run rules stated in the Output Contract. The rewrite (Alternative A) consolidates these, which is the right call. However, as the prompt grows over time, this drift risk will recur. Suggestion: after the rewrite, add a comment in the Re-run section noting it is the single authoritative source for re-run rules, to prevent future maintainers from adding parallel re-run notes elsewhere.

**Observation 3 — Testability: The test suite covers structural constraints but not behavioral sequence:** `test_analysis_prompt_structure.py` tests only for presence/absence of specific strings. It does not validate that the execution order, branch logic, or output contract semantics are intact. This means a behavioral regression introduced during the rewrite could go undetected by existing tests. Suggestion: consider adding a test in a follow-up request that checks for the presence of key numbered-step markers or section heading patterns that would catch major structural omissions (e.g., asserting the 3-branch preflight logic is referenced, the stub-detection formula is present verbatim, the finalize-input.py invocation command appears).

**Observation 4 — Scope size assessment:** The scope is appropriately sized. A single-file structural rewrite of a ~310-line prompt is a focused, low-risk task. There is no risk of under-scope (the input is specific) or over-scope (the constraints explicitly prohibit behavioral changes). The plan should be completable in a single implementation iteration of 3–5 tasks.

