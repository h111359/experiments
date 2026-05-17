# Analysis: R-20260508-0036 — Move analysis questions to input.md with answers

## Executive Summary

- **Request ID:** R-20260508-0036

- **Title:** Move analysis questions to input.md with answers

- **Purpose:** Consolidate all developer–AI interaction into `input.md` as the single touchpoint. Currently, AI-generated Q-blocks land in `request.md`, requiring the developer to navigate away from their primary input file. This request moves questions to `input.md` and removes the `Question threshold` configurability, delegating that judgment entirely to the AI.

- **High-level scope:** Changes touch `aib-analysis.md` (core logic rewrite of Q&A section), `initialize.py` and `close-request.py` (seed template update), `.aib_brain/README.md` (documentation), and the automated test suite. `request-convention.md` is NOT changed — `## Questions & Decisions` is retained as section 10 (Q001 resolved: Option B).

- **`request.md` updates this run:** Sections replaced: `## Assumptions`, `## Plan`, `## Documentation`. Q001 answer applied (Option B selected): `## Questions & Decisions` retained as an always-empty section 10 in `request.md`; AI no longer writes Q-blocks there.

- **Key risk:** The change is a breaking behavioral shift in how developers interact with the analysis workflow. Any deviation in parsing logic for answered questions in `input.md` will silently drop answers or incorrectly apply them to `request.md` sections.

- **All questions resolved.** Q001 was answered (Option B — retain `## Questions & Decisions` as always-empty section 10). Implementation may proceed.


## Domain Knowledge Essentials

- **AIB (AI Builder):** A file-based, model-agnostic framework for specification-driven development. All workflow state lives in the filesystem; there is no database or server component.

- **`input.md`:** The primary developer-to-AI communication file. Currently structured with `## Active request`, `## Options`, and `## Input` sections. After this request, it will also support a `## Questions` section populated by the AI and answered by the developer.

- **`request.md`:** The authoritative specification document for an active request. Contains 10 mandatory sections including `## Questions & Decisions`. Currently receives AI-generated Q-blocks during analysis.

- **Q-block:** The structured question format used by AIB — `**Q<nnn>**: <text>`, checkbox options with a `*(recommended)*` marker, and a `> Answer:` field. Currently written to `request.md`; this request moves them to `input.md`.

- **Question threshold:** A configurable severity level (`[x] 3` by default) in `input.md ## Options` that controls whether a decision point is raised as a Q-block or resolved autonomously. This feature is being removed entirely.

- **Developer (primary actor):** Writes intent to `input.md`, reviews `request.md` and `analysis.md`, answers questions, triggers prompt actions. Friction in this workflow has a direct impact on adoption.

- **Single-touchpoint principle:** The design goal of reducing developer context-switching. `input.md` is already the entry point; centralizing questions there avoids requiring the developer to also monitor `request.md` during the Q&A phase.

- **Recommended answer:** A pre-filled AI preference on each Q-block option, marked `*(recommended)*`. If the developer provides no answer on re-run, the recommended option is treated as chosen.

- **One-cycle Q&A:** The intent that one round of question-generation followed by one round of answering is sufficient to resolve all ambiguity; no iterative question-asking is expected.


## Technical Knowledge & Terms

- **`aib-analysis.md`:** The analysis prompt. Largest and most complex of the three AIB prompt files. Contains: preflight steps, toggle detection, auto-request creation branch, analysis generation logic, `request.md` update logic, and the `input.md` reset step. The Q-block generation and threshold decision logic live here and are the primary targets of change.

- **`initialize.py`:** Seeds the `.aib_memory/` workspace on first use. Contains a hardcoded `input_seed` string that defines the initial `input.md` content, including the `Question threshold` row to be removed.

- **`close-request.py`:** Closes an active request. Also contains a hardcoded `input_seed` string (identical to `initialize.py`) that is written to `input.md` after close. Must be updated in sync with `initialize.py`.

- **`request-convention.md`:** Defines the normative 10-section schema for `request.md`. Declares `## Questions & Decisions` as section 10. Whether this section remains mandatory after the change is an open design question (Q001).

- **`test_initialize.py::test_input_md_has_threshold_scale_labels`:** An existing automated test that asserts the seeded `input.md` contains `1 (all)` and `5 (mandatory only)` — the threshold scale labels. This test MUST be updated as part of this request since those strings will no longer appear in the seed.

- **`## Questions` section in `input.md`:** The new AI-generated section. Present only when the analysis identifies questions; absent from the seed template. Format reuses the Q-block structure. Each Q-block gains an additional `> **Why this matters:** <impact explanation>` sub-element.

- **Re-run answer application:** When `aib-analysis.md` is re-run and finds a `## Questions` section in `input.md` with answered Q-blocks (any `[x]` checkbox or non-empty `> Answer:` line), it applies each answer to the matching `request.md` section (Goal, Scope, Constraints, etc.), then clears the `## Questions` section before proceeding with normal analysis.

- **Files read for this analysis:**
  - `.aib_memory/input.md` — request content
  - `.aib_memory/context.md` — product context
  - `.aib_memory/instructions.md` — workspace directives
  - `.aib_memory/requests_register.md` — register state
  - `.aib_brain/prompts/aib-analysis.md` — current prompt logic
  - `.aib_brain/conventions/analysis-convention.md` — analysis structure
  - `.aib_brain/conventions/request-convention.md` — request structure
  - `.aib_brain/tools/initialize.py` — seed template source
  - `.aib_brain/tools/close-request.py` — seed template source
  - `.aib_brain/README.md` — documentation source
  - `tests/test_initialize.py` — affected test
  - `tests/test_analysis_prompt_structure.py` — reference for test patterns


## Research Results

- **Pattern: Questions-in-input vs. questions-in-spec.** Across similar AI-assisted developer workflow systems (GitHub Copilot Workspace, Cursor AI, Devin), all user-facing clarification Q&A occurs in the primary input interface, not in derived specification documents. Writing questions into `request.md` is an AIB-specific deviation from this norm that this request corrects.

- **Pattern: Recommended defaults.** Pre-selecting a recommended answer and treating it as chosen when the user provides no input is a well-established UX pattern (e.g., CLI tool defaults, form pre-fills). It reduces friction without removing user agency.

- **Pattern: One-cycle disambiguation.** Design goal aligns with the principle of "front-loading ambiguity resolution" — all clarifying questions are asked once, answered once, and the system proceeds. This reduces total round-trips.

- **Seed template synchronization risk.** The `input_seed` string appears in two Python files (`initialize.py` and `close-request.py`). Currently these are duplicated strings. This is a pre-existing technical debt that this request does not eliminate but must not worsen — both strings must be updated consistently.

- **Test coverage gap identified.** No test currently asserts the structure of the `## Questions` section that the analysis prompt generates. New tests must be added to cover SC-1 through SC-4.


## External Benchmarking

- **GitHub Issues / PR review cycle:** GitHub places reviewer questions directly in the PR thread (the primary interaction surface), not in a separate specification document. This mirrors the intent of this request: keep questions where the developer already is. Takeaway: validated pattern; high applicability.
  - The convention of "one comment thread = one question + recommended fix" maps well to the Q-block format with a `*(recommended)*` option.
  - Rejection of any GitHub-specific tooling: AIB is model-agnostic and file-only.

- **Linear / Jira "clarification" workflows:** Both platforms surface clarifying questions as comments on the ticket (the single interaction record), not as amendments to a separate spec document. Takeaway: further validation of the single-touchpoint principle; no direct adoption needed since AIB is file-based.

- **Wizard-style progressive disclosure pattern:** UX research shows that presenting all questions in one page with defaults pre-selected (progressive disclosure with smart defaults) results in faster completion and fewer abandonment events than multi-step wizards without defaults. This supports the "one-cycle Q&A with recommended answers" design.
  - Applicability: directly applicable to the `## Questions` section design — all questions appear at once, each with a pre-marked recommended option.
  - Adaptation needed: the format must be text-only Markdown to remain tool-agnostic.

- **Conventional Commits / RFC processes:** Both use a "comment period" model where all stakeholder questions are gathered in one phase and resolved before implementation begins. This validates the one-cycle Q&A assumption in the request scope.
  - Rejection: the full RFC ceremony is overkill for a single-developer, AI-assisted workflow. The lightweight Q-block format is the right adaptation.


## Minimal Spikes and Experiments

- **Spike: Parsability of answered Q-blocks in `input.md`**
  - Hypothesis: The existing Q-block format (`[x]` checkbox, non-empty `> Answer:` line) can be reliably parsed by prompt logic to determine whether a question is answered and which option was selected.
  - Approach: Reviewed the Q-block format as defined in `request-convention.md` and as used in prior closed requests. Checked that `[x]` appears exactly once per answered question and `> Answer:` is uniquely identifiable.
  - Outcome: Format is deterministically parseable. A question is answered if at least one checkbox is `[x]` OR the `> Answer:` line has non-empty text after the colon. The existing re-run merging rules in `aib-analysis.md` already implement this logic for `request.md`.
  - Conclusion: No format changes are needed. The existing Q-block structure can be reused in `input.md` without modification.

- **Spike: Impact of removing threshold row on existing tests**
  - Hypothesis: Removing `Question threshold` from the `input.md` seed breaks at least one existing test in `tests/test_initialize.py`.
  - Approach: Searched `tests/` for `threshold` keyword. Found `test_input_md_has_threshold_scale_labels` in `test_initialize.py` (lines 336–345) which explicitly asserts `"1 (all)"` and `"5 (mandatory only)"` appear in the seeded `input.md`. This assertion will fail after the seed is changed.
  - Outcome: Confirmed one test requires update. No other test in `tests/` references threshold directly.
  - Conclusion: The test must be replaced with an assertion that the threshold row is ABSENT from the seeded `input.md`.

- **Spike: Whether `## Questions & Decisions` removal from `request.md` is required**
  - Hypothesis: The request scope implies but does not explicitly state whether `## Questions & Decisions` should be removed from the 10-section mandatory schema.
  - Approach: Reviewed `input.md` content, `request-convention.md`, and the 10-section mandate. The request says questions move to `input.md` but does not say to remove the section from the convention. Having an always-empty mandatory section is design noise but removing it changes the convention and breaks existing tooling expectations.
  - Outcome: Ambiguous. Two valid options exist with materially different implementation scope. Raised as Q001; developer answered Option B (retain the section as always-empty; AI no longer writes Q-blocks there).
  - Conclusion: `request-convention.md` is NOT modified. `## Questions & Decisions` remains as section 10 in `request.md` — always empty during AI-driven workflows; available for manual human notes.


## AI Copilot Suggestions

- **Observation 1 — Scope of `aib-analysis.md` changes is larger than it appears.** The Q-block generation and threshold logic is tightly woven into the analysis prompt across multiple sections (preflight, toggle detection, standard flow, auto-request branch, re-run merging rules, final reset). Changing it requires touching every location where threshold is read and where Q-blocks are written. The risk of missing one location is moderate. Suggestion: create a checklist of all locations in `aib-analysis.md` where `Question threshold` is referenced (at least: toggle detection step 5 read, "Threshold read" instruction, 5-Level Severity Scale table, "Decision rule" section, "Q-block format" section, re-run merging rules, seed template in final reset step) and verify each is updated.

- **Observation 2 — The `## Questions & Decisions` section disposition (Q001) has cascading effects (now resolved).** Q001 was answered with Option B: retain `## Questions & Decisions` as always-empty section 10 in `request.md`. This means `request-convention.md` is unchanged, the mandatory section list is unchanged, and no additional test changes are required for convention schema. The implementation scope is now fully determined. Suggestion: verify that `aib-analysis.md`'s Part 2 instructions no longer reference writing Q-blocks to `## Questions & Decisions` in `request.md` — that instruction must be removed as part of Task 4.

- **Observation 3 — Duplicate `input_seed` string in `initialize.py` and `close-request.py` is pre-existing tech debt.** This request requires updating both files. Given they now have a third sync point (the reset in `aib-analysis.md`), consider whether a shared constant or helper is warranted — but this is out of scope for this request. Suggestion: add a comment in both files noting they must be kept in sync, and ensure the `## Documentation` section captures both as affected files.

- **Observation 4 — The new `## Questions` section in `input.md` needs clear sentinel logic.** When `aib-analysis.md` re-runs and finds `## Questions`, it must distinguish between: (a) questions from a prior run that are now answered → apply and clear, (b) questions from a prior run that are still unanswered → apply recommended defaults. If the prompt does not clearly define this detection, partial answers (some `[x]`, some blank) may be mishandled. Suggestion: define the detection rule precisely in the updated `aib-analysis.md`: treat each Q-block independently; for each unanswered block, apply the `*(recommended)*` option as if the developer had selected it.

- **Scope note:** The request scope is well-calibrated. The changes are non-trivial but bounded. The primary risk is in `aib-analysis.md` prompt complexity; the tool script changes (`initialize.py`, `close-request.py`) are straightforward string replacements.


## Testing

- T1 — Seed template has no threshold row: Run `initialize.py` in a temp workspace; read seeded `input.md`. Expected outcome: the string `Question threshold` does NOT appear anywhere in the file.

- T2 — Seed template has correct Options structure: Run `initialize.py` in a temp workspace; read seeded `input.md`. Expected outcome: `## Options` section contains exactly two toggles — `No changes — provide answer only` and `Skip analysis document generation`; no third line in that section.

- T3 — `close-request.py` resets to threshold-free template: Run `close-request.py` in a temp workspace with an active request; read resulting `input.md`. Expected outcome: `Question threshold` does NOT appear in the file.

- T4 — `aib-analysis.md` does not reference threshold reading logic: Read `.aib_brain/prompts/aib-analysis.md` content. Expected outcome: the string `Question threshold` does NOT appear in the seed template blocks; the `Question threshold` row is absent from all `input.md` reset templates defined in the prompt. (Allowable: historical references in comments or context-only paragraphs — but the operational seed strings must not contain it.)

- T5 — `aib-analysis.md` references `## Questions` section in `input.md`: Read `aib-analysis.md`. Expected outcome: the string `## Questions` appears in the prompt, indicating the new Q&A section is referenced.

- T6 — `.aib_brain/README.md` has no `## Question Threshold` section: Read `.aib_brain/README.md`. Expected outcome: the string `## Question Threshold` does NOT appear.

- T7 — `.aib_brain/README.md` documents `input.md` Q&A flow: Read `.aib_brain/README.md`. Expected outcome: the phrase `## Questions` or equivalent new-flow documentation appears in the README.

- T8 — Full test suite passes: Run `pytest tests/` from workspace root. Expected outcome: all tests pass with exit code 0; specifically `test_input_md_has_threshold_scale_labels` (or its replacement) does not fail.

- T9 — Re-run idempotency: In a scenario where `input.md` has no `## Questions` section, running the analysis prompt twice produces equivalent `analysis.md` output. Expected outcome: no `## Questions` section is injected into `input.md` when no ambiguity exists in the request.

See UAT_scenarios.md — UAT-01 (Q&A round-trip in `input.md`).

See UAT_scenarios.md — UAT-02 (unanswered questions use recommended default).


## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The request replaces a configurable threshold mechanism with AI-autonomous judgment about when to raise questions. This simplifies the public API surface of `input.md` at the cost of removing a developer control point. The architectural risk is low: the change is confined to prompt logic and string constants; no new data structures or file types are introduced. The seed template synchronization between `initialize.py` and `close-request.py` remains a latent fragility — two files must change in lockstep, and there is no compile-time check. The introduction of a `## Questions` section in `input.md` (absent from the seed, injected by analysis) is a clean ephemeral-state pattern consistent with how `## Input` already works.

- The 5-Level Severity Scale logic in `aib-analysis.md` becomes dead code once threshold reading is removed; the entire scale table and decision rule block must be removed or repurposed.
- The `Q001` question about `## Questions & Decisions` disposition in `request.md` is the highest-risk architectural decision in this request — getting it wrong forces rework across convention, prompt, and test files.
- Recommend a clear "questions present" detection heuristic: check for `## Questions` section in `input.md` before any other logic in the analysis prompt, not after toggle detection.

### Product Owner

The business value is clear: reducing developer friction in the Q&A phase improves workflow adoption. The current pattern of writing questions to `request.md` requires developers to open a second file, which is counter-intuitive when `input.md` is already open. Moving questions to `input.md` closes this gap. Acceptance criteria SC-1 through SC-7 are measurable and testable. The scope is narrow and well-defined. One concern: the request does not define what happens when a developer manually edits answered questions between runs — this edge case should be addressed in the prompt's re-run logic.

- SC-6 (test suite passes) is essential; any regression in existing behavior would negate the value of the simplification.
- The "one-cycle Q&A" assumption is a deliberate product decision that constrains the design appropriately.
- Documentation update (SC-5 and SC-7) is correctly scoped as part of the request rather than deferred.

### User

From a developer perspective, this change is a clear improvement: all interaction with the AI analysis happens in one file (`input.md`). The current pattern of opening `request.md` to answer questions, then returning to `input.md` to re-run is an unnecessary context switch. The recommended-answer default reduces the cognitive load for non-critical questions — a developer can accept all defaults by simply re-running without making any selections. The impact explanation added to each Q-block (the `> **Why this matters:**` element) is a significant usability enhancement that helps developers make informed choices rather than guessing at option consequences.

- Risk: if questions appear in `input.md` but the developer doesn't notice the new section, they may re-run without answering — but this is gracefully handled by the recommended-default behavior.
- The removal of `Question threshold` eliminates a configuration option that most developers likely left at default anyway; removing it reduces decision fatigue.
- The format of the `## Questions` section must be clearly distinguished from the `## Input` section to avoid confusion.

### Security Officer

This request involves no changes to authentication, authorization, credential handling, or data exposure. All changes are confined to Markdown prompt files, Python tool scripts (standard library only, no network calls), and test files. The `input.md` file is workspace-local and not transmitted over any network. No new file types, external dependencies, or execution permissions are introduced. The recommended-answer default mechanism cannot be exploited to inject malicious content since it reads from the same file the developer controls.

- No security concerns identified for this request.
- The `instructions.md` directive (maintaining `logs/next_version_changes.md`) remains in effect and is not impacted.

### Data Governance Officer

All artifacts modified by this request are Internal engineering documentation with no PII, regulated data, or external data dependencies. The `input.md` file contains developer intent text; its content is no more sensitive than a code comment. Archiving behavior (`input-archive-*.md` in request folders) is unchanged — the archive captures `input.md` state including any `## Questions` section that was present, providing a complete audit trail of Q&A interactions. No data lineage, retention, or classification changes are required.

- The removal of `Question threshold` eliminates one configuration data point from the `input.md` archive; this is acceptable since the threshold was internal-operational, not business-data.
- No compliance implications identified.
