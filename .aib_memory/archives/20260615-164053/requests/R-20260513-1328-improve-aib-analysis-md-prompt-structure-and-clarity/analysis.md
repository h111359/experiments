## Executive Summary

- **Request ID:** R-20260513-1328

- **Request title:** Improve aib-analysis.md prompt structure and clarity

- **High-level purpose:** Rewrite `aib-analysis.md` for structure, clarity, and consistency; introduce a Decision Points Catalog in the analysis artifact; rename `## Questions & Decisions` to `## Decisions` in `request-convention.md`; and — addressing the developer's amended input — fix the root cause that suppresses Q-block generation even when genuine implementation alternatives exist.

---

## Files Read During This Analysis Run

- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/input.md`
- `.aib_memory/context.md`
- `.aib_memory/request-R-20260513-1328.md`
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `tests/test_analysis_prompt_structure.py`

---

## Research Results

### Scan: Q-block Suppression Root Causes in `aib-analysis.md`

The developer's amended `## Input` asks: why does AIB seldom ask questions? A static analysis of the current prompt reveals five compounding suppression factors:

1. **Over-broad mandatory pre-check** — Before generating any Q-block the AI must verify the answer "is not already determinable from `.aib_memory/context.md`, convention files, `.aib_memory/instructions.md`". The AIB workspace maintains a rich, comprehensive `context.md` that covers requirements, architecture, component roles, and integration points. Because context.md is dense, the AI almost always finds a passage to cite, justifying autonomous resolution and bypassing Q-block creation entirely.

2. **"Materially different" threshold is subjectively high** — Both the ambiguity detection rule and the Q-block trigger require "multiple plausible interpretations leading to materially different implementation or design outcomes." For well-scoped AIB requests, the AI interprets most choices as not sufficiently "material" to warrant user input. No calibration guidance is provided on what constitutes a material difference.

3. **Autonomous resolution is the unchecked default** — The instruction "resolve all other ambiguities autonomously and document the chosen option inline in the relevant `request.md` section" makes autonomous resolution the easy default. There is no nudge to prefer Q-blocks over inline assumptions, and no requirement to explain why a Q-block was suppressed.

4. **Chain dependency creates self-resolution bias** — Q-blocks for implementation choices MUST reference alternatives by name from the Implementation Alternatives section. Since the AI enumerates the alternatives itself, it tends to self-select the recommended option during enumeration and suppresses the Q-block that would otherwise have asked the developer.

5. **No question floor by default** — The soft limit is 9 Q-blocks but the default minimum is 0. With `Minimum questions: 0` the AI never feels compelled to surface any Q-block. Even a `Minimum questions: 1` would pressure the AI to search for at least one genuine decision point.

### Scan: Structural Issues in `aib-analysis.md`

- The prompt mixes preflight steps, auto-request branch steps, standard flow, and output contracts in a single flat document. Step numbering is inconsistent across sections.
- External dependencies (scripts: `create-request.py`, `finalize-input.py`; conventions: `analysis-convention.md`, `request-convention.md`) are referenced inline without a dedicated preamble index.
- The `## Questions & Decisions` backward-compatibility note is a stale migration artifact that creates confusion.

### Scan: Cross-references to `## Questions & Decisions`

| File | Context | Update needed |
|---|---|---|
| `.aib_brain/prompts/aib-analysis.md` | Section contract header, inline references | Replace with `## Decisions` |
| `.aib_brain/conventions/request-convention.md` | Section 10 heading and definition | Replace heading; redefine semantics |
| `.aib_brain/conventions/analysis-convention.md` | Determinism rules line 232 | Replace reference |
| `.aib_memory/context.md` | Lines 23, 42, 420 (approx.) | Regenerate via `aib-context.md` after close |

Tool scripts (`.aib_brain/tools/*.py`) do **not** reference `## Questions & Decisions` as a parseable heading — the rename is safe at the script level.

### Scan: Test-Assertion Strings

Strings that MUST survive in the rewritten `aib-analysis.md` (per `tests/test_analysis_prompt_structure.py`):

- `evaluate whether \`.aib_memory/input.md\` is in a non-stub state`
- `archive the pre-reset \`input.md\` content`
- `If stub-equivalent: skip archive creation for this standard-flow reset.`
- `All 10 mandatory sections`
- `#### Outputs`
- `ecursively`

Strings that MUST NOT appear after rewrite: `flat scan`, `ignore subdirectories`, `Code and Asset Scan for Impacted Components`, `Internal Review of Request and Product Docs`, `**Intent:**`, `**Inputs:**`, `**External Interfaces:**`, `**Environment & Configuration:**`, `All 12 mandatory sections`.

---

## Best Practices

- **Structured prompt engineering (default-to-ask heuristic):** LangChain agent frameworks, AutoGPT-style workflows, and interactive CLI scaffolding tools (Yeoman, create-react-app) treat human-in-the-loop clarification as the default path and autonomous resolution as the exception that requires justification. Research on chain-of-thought prompting shows that inserting an explicit deliberation step ("for each fork, state whether I am asking or resolving autonomously, and why") increases coverage of surfaced decisions. Applicability: **High** — the current prompt inverts this heuristic. Reversing the default would align with interactive-specification best practices and reduce silent scope misinterpretation.

- **Tighter resolution gate: "explicitly stated" vs. "inferable"** — OpenAI function-calling and Anthropic tool-use patterns distinguish "I have enough information" from "I need more information" as explicit decision states. The canonical pattern is: check if information is *explicitly stated* in the source; if only *inferable*, treat the question as open. Applying this distinction to the mandatory pre-check (change "determinable from context.md" to "explicitly stated in a named section of context.md") would shrink the pre-check's suppression radius. Applicability: **High** — this is a targeted, single-sentence change with significant behavioral impact.

- **Decision Log as a first-class artifact (ADR pattern, Nygard 2011):** Architecture Decision Records treat every significant decision as a first-class artifact with context, options, decision, and consequences. Making the Decision Points Catalog require explicit tagging (`ask | resolve-autonomously`) for every identified fork would implement the ADR pattern and make suppression a visible, auditable choice rather than a silent default. Applicability: **Medium-high** — the proposed `### Decision Points Catalog` subsection partially implements this pattern; adding mandatory tagging completes it.

---

## External Benchmarking

- **Anthropic Claude prompt guidelines ("be clear and direct"):** Recommend placing the most important instructions at the top, using numbered steps for sequential procedures, and avoiding deeply nested conditionals. Benchmarked approach: expose the two-branch decision (auto-request vs. standard flow) as an explicit routing block at the top of the document, before any numbered steps. Applicability: **High** — the current prompt buries the branch decision inside preflight step 1; surfacing it as a routing section improves navigability.

- **OpenAI prompt engineering guide (use delimiters, separate instructions from content):** Recommends using clear delimiters (`---`, `###`) between major logical blocks and separating "when to do it" from "how to do it." Benchmarked approach: add a preamble section (goal, inputs table, external dependencies table, outputs table) before all procedure steps, following the runbook/SOP pattern (Purpose → Prerequisites → Procedure → Expected Output). Applicability: **High** — directly applicable to the rewrite goal; eliminates the current mixing of prose rules and procedural steps.

---

## Minimal Spikes and Experiments

**Spike: Q-block generation trace under current prompt logic**

- Hypothesis: The mandatory pre-check combined with the rich context.md and the autonomous-fallback default causes near-zero Q-block generation for well-scoped AIB requests.
- Approach: Mentally traced the Q-block decision path for the current request (well-specified, prior analysis run exists) and a hypothetical ambiguous request using the current prompt rules.
- Outcome: For the current request, every potential decision fork is resolvable by citing a specific passage in context.md or request.md — the pre-check passes for all forks and Q-blocks are suppressed. For a hypothetical request with two plausible implementation approaches, the rich context.md still provides enough material for the AI to justify autonomous resolution.
- Conclusion: Root cause confirmed as the combination of (a) overly broad "determinable from context" pre-check and (b) autonomous-resolution as the unchecked default. Both must be addressed in the rewrite.

---

## Implementation Alternatives

### Alternative A: Philosophy Inversion — Default to Ask (Recommended)

**Description:** Change the prompt's default from "resolve autonomously unless no resolution is possible" to "ask unless the answer is explicitly stated in the workspace." Autonomous resolution requires an explicit justification documented in the Decision Points Catalog.

**Trade-offs:**
- Benefits: Surfaces genuine decision points that the AI currently swallows; makes autonomous decisions auditable; aligns with interactive-specification best practices.
- Drawbacks: May surface Q-blocks the developer considers obvious on clear requests; minor increase in friction.

**Codebase impact:** Rewording of the ambiguity detection and mandatory pre-check paragraphs in `aib-analysis.md`. No tool-script changes.

**Recommendation:** ✅ Preferred. The developer's `## Input` content explicitly asks for this philosophy shift.

---

### Alternative B: Lowered Threshold Only

**Description:** Retain the autonomous-first philosophy but lower the "materially different" threshold to "any meaningful implementation difference." No philosophy shift.

**Trade-offs:**
- Benefits: Less disruptive; preserves the existing prompt philosophy.
- Drawbacks: The broad mandatory pre-check will still suppress most Q-blocks via context.md. Root cause not addressed.

**Codebase impact:** Single sentence change in the ambiguity detection rule.

---

### Alternative C: Mandatory Deliberation Step

**Description:** Add a numbered "Decision Fork Enumeration" step before Q-block generation. For every identified fork the AI must tag it `ask | resolve-autonomously` and write the tag plus rationale to the Decision Points Catalog. Q-blocks are generated for all `ask`-tagged forks.

**Trade-offs:**
- Benefits: Makes the decision process fully visible and auditable; addresses root cause 3 (silent defaults).
- Drawbacks: Adds cognitive load; may produce verbose catalog for simple requests.

**Codebase impact:** New numbered step in the standard flow section of `aib-analysis.md`; updated Decision Points Catalog format.

**Note:** Alt A and Alt C are complementary. Combining them (philosophy inversion + mandatory deliberation) yields the strongest guarantee and is the recommended approach.

---

### Decision Points Catalog

| # | Decision Point | Tag | Resolution |
|---|---|---|---|
| 1 | Combine Alt A + Alt C vs. Alt A only | resolve-autonomously | Both are additive and complementary; combining yields stronger guarantees with limited additional complexity. |
| 2 | Decision Points Catalog: subsection of `## Implementation Alternatives` vs. new top-level section | resolve-autonomously | Assumption A3 in request.md and the 8-section convention rule out a new top-level section. |
| 3 | `## Decisions` format: preserve existing Q-block format (question + chosen `[x]`) vs. new format | resolve-autonomously | Assumption A4 in request.md specifies existing Q-block format; no new format needed. |
| 4 | Scope of mandatory pre-check tightening: "explicitly stated" vs. full removal | resolve-autonomously | Full removal would prevent the AI from using valid context; "explicitly stated" tightening is the right calibration. |

---

## AI Copilot Suggestions

- **Root cause vs. symptom:** The prior analysis run focused on adding a Decision Points Catalog (symptom-level fix — making suppression visible). The developer's amended input correctly identifies the root cause: the prompt philosophy defaults to autonomous resolution. Both the structural rewrite and the philosophy inversion are now in scope. The combined rewrite carries significant regression risk because test-assertion strings must be preserved verbatim. Consider treating the structural pass (numbered steps, preamble) and the behavioral pass (philosophy inversion, mandatory deliberation step) as logically separate sub-tasks within Task 1 — this makes it easier to isolate regression causes if tests fail.

- **Pre-check tightening needs precise wording:** The fix to the mandatory pre-check should be precise: "The pre-check passes only when the answer is *explicitly and unambiguously stated* in a named, specific section of context.md or the convention files — not merely inferable or consistent with what the files say." Without this precision, the AI will continue to treat inference as explicit knowledge and suppress Q-blocks.

- **Decision Points Catalog rationale column is critical:** As designed, the catalog table has a "Resolution" column. This column should require a rationale for *every* `resolve-autonomously` entry, not just a description of what was decided. The auditable value comes from the "why I did not ask" statement, not the "what I decided" statement. Consider making the rationale mandatory in the catalog format definition.

- **Scope of the Decisions section rename:** The rename from `## Questions & Decisions` to `## Decisions` affects `request-convention.md`. Existing closed requests have the old heading. Since tools do not parse this heading, backward compatibility is safe at the code level. However, documenting a backward-compatibility note in `request-convention.md` (e.g., "Closed requests created before v1.2.X may use `## Questions & Decisions`; this is equivalent to `## Decisions`.") would prevent confusion during future request audits. This note is optional but high-value.

- **Scope size assessment:** The request scope is proportionate to its goal. Four coordinated file changes (prompt rewrite, convention rename, cross-reference update, test additions) plus the Q-block philosophy change is significant but bounded. The highest-risk item is the prompt rewrite, which must preserve multiple exact test strings while changing the behavioral logic. The plan is well-structured. No scope reduction is recommended.
One-sentence description: Rewrite `aib-analysis.md` entirely using a new section template (Preamble → External Dependencies → Preflight → Procedure Branches → Output Contract) without preserving any of the current prose wording.

Trade-offs:
- Benefits: Maximum clarity improvement; no legacy wording retained.
- Drawbacks: High regression risk — exact test-assertion strings must be replanted deliberately. Any missed string causes immediate test failure. High effort to validate equivalence of all edge cases (Q&A re-run, stub-equivalence guard, Amend Request detection, etc.).

Expected codebase impact: Changes only `.aib_brain/prompts/aib-analysis.md` and cross-reference files. No script changes.

### Alternative B: Progressive restructuring (recommended)
One-sentence description: Keep all existing content and logic, add structural formatting (numbered steps, explicit preamble table for external deps, section breaks, Decision Points Catalog subsection), and make targeted wording improvements while preserving all test-assertion strings verbatim.

Trade-offs:
- Benefits: Near-zero regression risk; every behavior preserved by construction; test strings preserved; easier review.
- Drawbacks: The result may still feel somewhat verbose because existing rule prose is preserved; purely cosmetic restructuring may feel insufficient to some reviewers.

Expected codebase impact: Changes `.aib_brain/prompts/aib-analysis.md`, `.aib_brain/conventions/request-convention.md`, `.aib_brain/conventions/analysis-convention.md`. No script changes.

**Recommendation: Alternative B.** The goal explicitly states "do not exclude anything from the current prompt, but change the format and wording." Progressive restructuring satisfies this exactly and avoids regression risk from inadvertently dropping exact-match test strings.

### Decision Points Catalog

All decision-point categories eligible for Q-block generation in an `aib-analysis.md` run:

| Category | Trigger condition | Q-block generated? |
|---|---|---|
| Implementation alternative choice | Two or more named alternatives with materially different codebase impacts | Yes — one Q-block per pair of materially different alternatives |
| Scope ambiguity | Input text has multiple valid scope interpretations with different implementation outcomes | Yes — if not resolvable from `context.md` or conventions |
| Constraint conflict | Two constraints or success criteria are mutually exclusive | Yes — user must choose which to prioritize |
| Missing required input | A decision cannot be made without a value only the developer knows | Yes — only if the answer is not in any workspace doc or internet research |
| External dependency version / approach | Multiple valid library/tool versions or integration approaches with non-trivial trade-offs | Yes — if not answerable from `context.md` or project constraints |
| Non-applicable case (autonomously resolved) | Any other ambiguity where one option is clearly superior from existing workspace docs | No — apply directly and document in Assumptions |

---

## AI Copilot Suggestions

**Observation 1 — The `## Questions & Decisions` backward-compatibility note is now a source of confusion, not safety.**
The current section header and its note ("Q-blocks are NO LONGER written here… kept for backward compatibility with existing closed requests") creates cognitive overhead: a reader must understand that the section exists but is intentionally empty and serves no active purpose. The rename to `## Decisions` and its redefinition as a resolved-Q&A log eliminates this confusion entirely. The risk of broken backward compatibility with existing closed requests is low because archived `request.md` files are read-only and not processed by any active tool. **Suggestion:** Proceed with the rename without hesitation; add a note in the convention that `## Questions & Decisions` in pre-rename archives is treated as equivalent to `## Decisions` for human review purposes only.

**Observation 2 — The Decision Points Catalog adds audit value but risks becoming a checkbox formality if not implemented with clear exit criteria.**
The new requirement to list all Q-block-eligible cases in the analysis document is valuable for auditability. However, without a clear format and pass/fail criterion, an AI agent may generate a vague list rather than a structured catalog that helps the developer understand why questions were or were not raised. **Suggestion:** Define the Decision Points Catalog as a table (as designed in this analysis) with four columns: Category, Trigger condition, Example, Q-block generated (Y/N). Require the implementing agent to fill in every row for each analysis run, even when Q-blocks are 0.

**Observation 3 — The prompt's two execution branches (auto-request and standard flow) share most of their steps but are currently described sequentially in a way that makes their divergence point hard to find.**
The branch decision (Active request exists vs. not) happens in preflight step 1, but the auto-request procedure is described as a long embedded sub-section many paragraphs later. A reader scanning the prompt for "what happens if no active request exists" must find the one-sentence trigger label and then trace a non-linear path. **Suggestion:** In the rewrite, represent the branch as an explicit routing diagram or decision table near the top of the document: `[Active request exists] → Standard Analysis Flow (Section 3); [No active request + non-empty input.md] → Auto-Request Creation Branch (Section 4); [No active request + empty input.md] → Error halt.` This makes the flow scannable in seconds.

**Observation 4 — Scope note:** The scope is appropriately sized. The rewrite touches three files in `.aib_brain/` and one test file. It does not require script changes, CI changes, or context regeneration during implementation (context.md will be refreshed after). No scope creep risk identified.

**Note: This section is a reasoning artifact only. `aib-implement.md` MUST NOT read or act on AI Copilot Suggestions.**
