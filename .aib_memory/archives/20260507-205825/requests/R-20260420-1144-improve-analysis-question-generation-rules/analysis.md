## Executive Summary

- **Request ID:** R-20260420-1144

- **Request title:** Improve analysis question generation rules

- **High-level purpose:** Extend the `aib-analysis.md` prompt and related framework assets to: (1) introduce a 5-level configurable severity threshold for Q-block generation; (2) add a mandatory documentation pre-check that suppresses Q-blocks answerable from existing workspace docs; (3) add a new mandatory "AI Copilot Suggestions" section to analysis documents; (4) move `## Testing`, `## Minimal Spikes and Experiments`, and `## Multi-Perspective Stakeholder Review` from `request.md` into `analysis.md`, updating both conventions; (5) require mandatory plan tasks for automated testing and for context/docs update in every generated plan; (6) create `UAT_scenarios.md` when manual testing is needed.

- **Trigger:** Standard analysis flow re-run — request R-20260420-1144 is Active; scope expanded from previous analysis run based on new content in `input.md`.

- **Scope of change:** Seven files modified — `.aib_brain/prompts/aib-analysis.md`, `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`, `.aib_brain/tools/initialize.py`, `.aib_brain/README.md`, `.aib_memory/context.md` (runtime), `.aib_memory/input.md` (runtime). `UAT_scenarios.md` created conditionally in request folders.

- **No questions raised:** All decision points in this request are resolvable from workspace documentation or qualify as Level-1/Level-2 decisions resolved autonomously below the default threshold of 3.

- **`request.md` sections updated in this run:** `## Goal`, `## Background`, `## Scope`, `## Out of scope`, `## Constraints`, `## Success criteria`, `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`. `## Questions & Decisions` has no content (no open questions). `## Multi-Perspective Stakeholder Review` is retained in this `request.md` under the current convention; new convention places it in `analysis.md` from the next request onward.

- **Analysis document is a reasoning artifact only.** `implement` reads `request.md` exclusively.


## Domain Knowledge Essentials

**Business terminology:**

- **AIB (AI Builder):** A minimal, model-agnostic framework for specification-driven development in a repository workspace. Orchestrates developer intent through a structured request → analysis → implementation → close lifecycle.

- **Q-block (Question block):** A structured entry in `## Questions & Decisions` of `request.md`, formatted as `**Q<nnn>**` with checkbox options and a `> Answer:` field. Raised when the AI identifies a decision fork requiring user input.

- **Severity threshold:** A numeric value (1–5) set by the developer that determines the minimum severity level at which a decision fork is surfaced to the user as a Q-block. Decisions below the threshold are resolved autonomously with inline reasoning.

- **Documentation pre-check:** A mandatory verification step performed before generating any Q-block, confirming the answer is not already present in `context.md`, convention files, or any required-read file from `references.md`.

- **AI Copilot Suggestions:** A new mandatory section in `analysis.md` providing a sincere, expert-level critical review of the request — improvement opportunities, pitfalls to avoid, quality assessment of scope and success criteria. It is a reasoning artifact; `implement` does not consume it.

- **Autonomous decision:** A choice made by the AI without raising a Q-block. Used for decisions rated below the active threshold. The chosen option and reasoning are documented inline in the relevant `request.md` section.

- **Question threshold row:** A checkbox line in `input.md ## Options`: `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5`. The checked value is the active threshold. Reset to `[x] 3` by the analysis prompt on input.md reset.

- **UAT_scenarios.md:** An optional file created in the request folder by `aib-analysis.md` when the request requires manual testing scenarios that cannot be expressed as automated assertions.

- **Section relocation:** Moving mandatory sections (`## Testing`, `## Minimal Spikes and Experiments`, `## Multi-Perspective Stakeholder Review`) from `request.md` to `analysis.md`. This keeps `request.md` focused on specification content and `analysis.md` as the full reasoning and quality-assurance artifact.

**Impacted roles/personas:**

- **Developer:** Benefits from tunable Q-block volume, suppressed redundant questions, expert-quality feedback on requests via AI Copilot Suggestions, and visible testing and stakeholder analysis in `analysis.md`.

- **AI Automation Agent:** Must read the threshold from `input.md`, apply severity levels, execute the pre-check, generate AI Copilot Suggestions, generate Testing and Multi-Perspective Stakeholder Review in `analysis.md`, and include mandatory plan tasks on every analysis run.

- **AIB Maintainer:** Approves changes to `.aib_brain/` assets, including the updated `aib-analysis.md`, `analysis-convention.md`, `request-convention.md`, `initialize.py`, and `README.md`.

**Business processes touched:**

- **Execute analysis workflow:** Primary process changed — question generation logic, analysis.md structure, request.md section structure, and input.md options processing are all updated.

- **Execute implement workflow:** Indirectly improved — every plan now includes a mandatory context/docs update task, ensuring `context.md` is always synchronized after implementation.


## Technical Knowledge & Terms

**Technologies and components:**

- **`aib-analysis.md`:** Markdown prompt file executed by an AI coding assistant. Controls the full analysis workflow including Q-block generation, `analysis.md` creation, and `request.md` optional section updates. Model-agnostic.

- **`analysis-convention.md`:** Normative convention file defining the required structure, section order, and content rules for `analysis.md` artifacts. Adding new mandatory sections here makes them required in every future `analysis.md`.

- **`request-convention.md`:** Normative convention file defining the mandatory sections of `request.md`. Removing sections here changes the required structure for all future `request.md` files.

- **`initialize.py`:** Python 3.10+ script that seeds `.aib_memory/` on first use. The `input_seed` string hardcoded in this file determines the initial content of `input.md`, including the `## Options` section.

- **`input.md`:** Ephemeral Markdown file used as the user-agent communication channel. Read by `aib-analysis.md` to extract threshold value and user intent. Reset to the seed template at the end of each analysis run.

- **`context.md`:** The authoritative product knowledge artifact for the workspace, fully replaced on each `aib-context.md` execution. Must be updated after implementation to reflect framework changes.

- **`UAT_scenarios.md`:** Optional file in the request folder. Created when the AI determines that some test cases require manual execution (e.g., UI interactions, end-user workflows, visual validation).

- **`## Options` section (input.md):** A Markdown checkbox list in `input.md` that controls analysis behavior. Extended by this request to include the `Question threshold` row alongside the two existing toggles.

**Data models and runtime constraints:**

- Threshold value: integer in range [1, 5]; extracted from the checked checkbox in the `Question threshold` row; default 3 when absent or unparseable.
- `input.md` is reset to the seed template as the last action of each analysis run; threshold resets to `[x] 3`.
- All tool script changes must use Python 3.10+ standard library only.

**Non-functional attributes:**

- Model-agnostic: all prompt instructions must be interpretable by any AI model without vendor-specific capabilities.
- Fail-safe: missing threshold row defaults to 3 without crashing or halting the analysis.
- Backward compatibility: existing closed `request.md` files retain their old section structure; no migration required.

**Evidence log:**

- `context.md` (FR-004): `aib-analysis.md` generates `analysis.md` and updates `request.md` optional sections → after this request, Testing and Multi-Perspective Stakeholder Review move from `request.md` to `analysis.md`.
- `context.md` (FR-007): `input.md` supports two opt-in toggles → extended to three (adding `Question threshold` row).
- `request-convention.md` (section 9): `## Testing` is currently mandatory in `request.md` → removed by this request.
- `request-convention.md` (section 14): `## Multi-Perspective Stakeholder Review` is currently mandatory in `request.md` → removed by this request.
- `analysis-convention.md` (section 4): currently defines 6 mandatory sections → extended to 9 mandatory sections.

**Files read for this analysis:**
- `.aib_memory/context.md`
- `.aib_brain/Concepts.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/tools/initialize.py`
- `.aib_brain/README.md`
- `.aib_memory/references.md`
- `.aib_memory/requests/R-20260420-1144-improve-analysis-question-generation-rules/request.md`


## Research Results

**Pattern scan against prior requests and workspace conventions:**

1. **Q-block filtering precedent:** Prior requests (R-20260409-1322 "39-decision-points-vs-questionnaire") already addressed the distinction between genuine decision forks and informational unknowns. The current request adds a numeric scale and a pre-check gate, consistent with the trajectory of that prior work. No conflict.

2. **Section relocation pattern:** The analysis-convention.md currently defines 6 sections for `analysis.md`. The `request-convention.md` defines 14 sections for `request.md`. The relocation of 3 sections from `request.md` to `analysis.md` is architecturally consistent with the stated purpose of each artifact — no prior request has relocated sections between these two documents.

3. **Seed template synchronization:** Two files contain the `input.md` seed template: `initialize.py` and `aib-analysis.md`. This dual-point-of-change pattern was identified in prior analysis runs as an implementation risk. Both must be updated together (Tasks 2 and 7).

4. **UAT_scenarios.md precedent:** No prior request has defined `UAT_scenarios.md` as an artifact. The concept is industry-standard. The decision to create it conditionally avoids unnecessary file proliferation for fully automated-testable requests.

5. **Mandatory plan tasks:** Prior requests included testing tasks and documentation update tasks on an ad-hoc basis. Mandating them in every plan standardizes the workflow and reduces the risk of missed context updates and untested implementations.

**Autonomous decisions made (below threshold, resolved inline):**

- *Level 2 — Threshold row format:* Single-line checkbox row, consistent with existing toggles. Rationale: minimal diff to input.md structure; consistent parsing pattern.
- *Level 2 — UAT detection rule:* The AI determines from scope whether manual testing is needed (no user Q-block). Rationale: follows the prompt principle of not asking for information the AI can determine from scope.
- *Level 1 — New analysis section numbering:* 7 = AI Copilot Suggestions, 8 = Testing, 9 = Multi-Perspective Stakeholder Review. Minimal Spikes and Experiments stays at 6.
- *Level 2 — menu.py deferred:* Threshold display/control in the menu is out of scope for this request, as `input.md` direct editing is sufficient evidence.


## External Benchmarking

**Reference 1 — Severity/priority scales in issue trackers (industry standard)**

Issue trackers (Jira, Linear, GitHub Issues) routinely use 4–5 level priority scales (P0–P4 or Critical/High/Medium/Low/Minimal) to gate escalation behavior. The AIB 5-level threshold mirrors this pattern, applied to Q-block generation rather than issue escalation.

- Takeaway: 5-level scales are well-understood by developers and provide sufficient granularity without cognitive overload.
- Applicability: adopted — Level 1 (cosmetic), Level 2 (minor structural), Level 3 (implementation detail — default), Level 4 (functional/behavioral), Level 5 (architectural).

**Reference 2 — "Pre-flight checks" pattern in CI/CD and specification-driven tools**

Modern CI systems (GitHub Actions, GitLab CI) require explicit pre-flight checks before executing expensive or irreversible steps. Specification-driven tools (OpenAPI validators) perform a "known-answer check" before surfacing issues. The `aib-analysis.md` documentation pre-check follows this exact pattern.

- Takeaway: Pre-checks that gate on available information produce more signal and less noise.
- Applicability: adopted — the pre-check reads `context.md` and convention files before raising a Q-block.

**Reference 3 — Architecture Decision Records (ADRs) and expert review artifacts**

ADR frameworks (MADR, Michael Nygard's template) separate the decision-recording artifact from the implementation specification. The "AI Copilot Suggestions" section follows this pattern — expert-level design critique separated from the implementation plan, clearly labeled as advisory.

- Takeaway: Expert review artifacts are most useful when clearly labeled as advisory/non-prescriptive and not consumed by automated tools.
- Applicability: adopted — the section is explicitly marked as a reasoning artifact that `implement` MUST NOT read.

**Reference 4 — UAT artifact patterns in agile teams**

Agile teams produce User Acceptance Test (UAT) scripts as a separate artifact from automated test suites. Creating `UAT_scenarios.md` as a conditional artifact follows this pattern while keeping it lightweight (Markdown format, request-scoped).

- Takeaway: UAT artifacts should be created only when needed. Triggering condition: non-automatable test cases.
- Applicability: adopted — `UAT_scenarios.md` is created conditionally, not unconditionally.


## Minimal Spikes and Experiments

**Spike 1 — Threshold row parsing reliability**

*Question:* Can the AI reliably extract the checked value from the `Question threshold` row?

*Finding:* The checkbox format `[x]` vs `[ ]` is unambiguous. The checked value is the digit immediately following `[x]`. Fallback to 3 when no `[x]` is found is straightforward. The format is identical to existing option toggles in `input.md`, which have been reliably parsed in all prior analysis runs.

*Risk mitigated:* Low — fallback default of 3 covers all edge cases.

**Spike 2 — Section relocation impact on `implement`**

*Question:* Does `aib-implement.md` or any other prompt read `## Testing` or `## Multi-Perspective Stakeholder Review` from `request.md` directly?

*Finding:* `context.md` states: "`implement` MUST rely on `request.md` as the sole implementation specification. MUST NOT read analysis, questionnaire, or plan iteration artifacts." No reference to consuming these sections from `request.md` was found. The relocation does not break `implement`.

*Risk mitigated:* Confirmed safe.

**Spike 3 — UAT detection determinism**

*Question:* Can the AI reliably determine whether `UAT_scenarios.md` should be created without asking the user?

*Finding:* The rule "create `UAT_scenarios.md` if any test case cannot be expressed as a script assertion" is deterministic for requests involving UI interactions, visual validation, or end-user workflow steps. For infrastructure or algorithmic requests, all test cases are automatable.

*Risk mitigated:* Medium — when uncertain, the AI should default to creating `UAT_scenarios.md` (false positive is preferable to false negative).


## Testing

- T1 — 5-level severity scale in prompt: Inspect `.aib_brain/prompts/aib-analysis.md` after Task 1. Expected outcome: File contains definitions for all 5 levels with examples, the pre-check rule, and the threshold read step.

- T2 — Seed template threshold row in aib-analysis.md: Inspect all hardcoded seed template occurrences in `aib-analysis.md` after Task 2. Expected outcome: Each occurrence contains `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5`.

- T3 — AI Copilot Suggestions in analysis.md: Run `aib-analysis.md` on any request after Tasks 3 and 5. Expected outcome: `analysis.md` contains a non-empty `## AI Copilot Suggestions` section.

- T4 — Testing section in analysis.md (not in request.md): Run `aib-analysis.md` after Task 3. Expected outcome: `analysis.md` contains `## Testing`; `request.md` does NOT contain a `## Testing` section.

- T5 — Multi-Perspective Stakeholder Review in analysis.md: Run `aib-analysis.md` after Tasks 3 and 5. Expected outcome: `analysis.md` contains `## Multi-Perspective Stakeholder Review`; `request.md` does NOT contain this section.

- T6 — Mandatory plan tasks present: Run `aib-analysis.md` on any request. Expected outcome: `request.md ## Plan` includes a task for automated testing and a task for updating `context.md` and editable docs.

- T7 — UAT_scenarios.md created when manual testing required: Run `aib-analysis.md` on a request that includes UI or user-interaction changes. Expected outcome: `UAT_scenarios.md` is created in the request folder.

- T8 — Threshold reset after analysis: Run analysis with threshold set to 4 in `input.md`. Expected outcome: After analysis resets `input.md`, `input.md ## Options` contains `[x] 3` in the `Question threshold` line.

- T9 — initialize.py seed includes threshold: Run `initialize.py` on a fresh workspace. Expected outcome: `.aib_memory/input.md ## Options` contains `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5`.

- T10 — request-convention.md updated: Inspect `request-convention.md` after Task 6. Expected outcome: `## Testing` and `## Multi-Perspective Stakeholder Review` are not listed as mandatory sections; Plan schema references mandatory testing and context-update tasks.

- T11 — README threshold documentation: Inspect `.aib_brain/README.md` after Task 4. Expected outcome: All 5 threshold levels are documented with definitions, AI behavior, and at least one concrete example each.

- T12 — context.md regenerated: Run `aib-context.md` after Tasks 1–7. Expected outcome: `context.md` references the threshold row, `UAT_scenarios.md`, and the relocated analysis sections.


## Multi-Perspective Stakeholder Review

**Senior Solution Architect**

The expanded scope spans five convention/prompt files and touches the fundamental section structure of both `request.md` and `analysis.md`. The design decisions are architecturally sound: section relocation to `analysis.md` clarifies the purpose of each artifact; the threshold stored in `input.md` reuses the existing ephemeral channel without adding persistent config; the mandatory plan tasks standardize workflow without adding new tools. The primary architectural risk remains seed template synchronization between `initialize.py` and `aib-analysis.md`.

- Five files changed across conventions, prompts, and tool scripts — no new files created other than conditional UAT_scenarios.md.
- Section relocation is additive to `analysis-convention.md` and subtractive from `request-convention.md`; both operations are low-risk.
- Mandatory plan tasks (testing + context update) address a known gap: context drift after implementation.
- UAT_scenarios.md as a conditional artifact is a clean extension — no structural changes to existing artifacts.
- Renumbering `request-convention.md` sections after removing two must be done carefully to avoid reference drift.

**Product Owner**

This request delivers measurable improvements across five dimensions: Q-block noise reduction, Q-block false positive suppression, expert feedback quality, artifact clarity, and workflow completeness. The trade-off is implementation complexity (8 tasks, 5 files). Success criteria are expanded and objectively testable (T1–T12).

- High business value: developers get cleaner analysis output with less noise and better expert review.
- Section relocation improves artifact purpose clarity: `request.md` = specification; `analysis.md` = reasoning + QA.
- Mandatory context update task directly reduces the known problem of stale `context.md` after implementation.
- Risk: developers accustomed to finding Testing and Multi-Perspective Stakeholder Review in `request.md` will need to look in `analysis.md` instead.

**User (Developer)**

The developer experiences improvements: fewer or more questions based on threshold; expert feedback in every `analysis.md`; `analysis.md` is now the complete QA artifact including testing scenarios and stakeholder perspectives; `request.md` is leaner and more focused; `UAT_scenarios.md` makes manual testing explicit and traceable.

- `request.md` becomes a cleaner specification document — easier to review and approve before implementation.
- `analysis.md` becomes the comprehensive reasoning and QA artifact — stakeholder perspectives, testing, and AI advice in one place.
- Threshold control via `input.md` editing is sufficient; menu control is deferred.
- UAT_scenarios.md provides a clear contract for manual testing, previously undefined.

**Security Officer**

No new network calls, authentication paths, or secret handling are introduced. The threshold value is stored in plaintext Markdown — acceptable for developer preference configuration. All new artifacts (`UAT_scenarios.md`, "AI Copilot Suggestions") contain developer notes only — no credentials, PII, or security-sensitive data. No change to file permission model or `edit_allowed` gating.

- No new attack surface introduced.
- All new artifacts are local filesystem Markdown files.
- `UAT_scenarios.md` and `analysis.md` remain classified as Internal engineering documentation.
- No change to access control model.

**Data Governance Officer**

All artifacts remain within the repository workspace. `UAT_scenarios.md`, if created, is committed to VCS as Internal engineering documentation, consistent with `analysis.md`. The threshold row in `input.md` is transient (reset after each analysis run) and contains no personal or business-sensitive data. No new data retention, lineage, or compliance obligations are introduced.

- No new data types or data flows.
- `UAT_scenarios.md` follows the same VCS retention policy as other request artifacts.
- Threshold row in `input.md` is ephemeral — no persistent configuration accumulation.
- No regulatory or compliance impact identified.


## AI Copilot Suggestions

**Improvement opportunities:**

- **Threshold discoverability:** The threshold row in `input.md` is not visible to the developer unless they open the file. The `README.md` update (Task 4) should explicitly document that the threshold can be changed by editing `input.md ## Options` directly — this is the primary access method while menu control is deferred.

- **UAT_scenarios.md format convention:** No format is defined for `UAT_scenarios.md`. A lightweight stub convention (scenario ID, preconditions, steps, expected outcome) should be included in either `analysis-convention.md` (section 8) or `README.md` to ensure consistency across requests. This is low effort and high value.

- **Mandatory plan task templates:** The two new mandatory plan tasks (testing task, context/docs update task) will be AI-generated on each run. To ensure consistency, the `request-convention.md` update (Task 6) should provide a template snippet for each task, not just a prose description. This reduces variation across analysis runs.

- **"Editable documents" scope clarification:** The plan task for updating `context.md` and editable docs from `references.md` should explicitly scope to documents where `edit_allowed = Y` and `type = product-doc`. Without this, `references.md` itself (which is a register, not a product-doc) might be incorrectly included. This clarification must appear in the `aib-analysis.md` rule text.

**Pitfalls to avoid:**

- **Seed template drift:** `input_seed` appears in both `initialize.py` and `aib-analysis.md`. If only one is updated, threshold parsing will fail after initialization. Tasks 2 and 7 must be implemented and reviewed as a pair. The Done Criteria for both tasks should cross-reference each other.

- **Convention backward-compatibility confusion:** Removing `## Testing` and `## Multi-Perspective Stakeholder Review` from `request-convention.md` will cause existing closed `request.md` files to appear non-conformant if the convention is used to validate them retroactively. The updated convention must explicitly state: "This change applies to requests created after this convention version. Historical `request.md` files are not required to conform."

- **analysis-convention section count in context.md:** After this request, `context.md` will reference the analysis convention section count as 9. If `aib-context.md` is not run immediately after implementation, the stale `context.md` will cause the documentation pre-check to apply outdated information. Task 8 (context.md regeneration) is the final implementation task and must not be skipped.

- **UAT_scenarios.md location:** The prompt must specify that `UAT_scenarios.md` is created in `<request-folder>/`, not in `.aib_memory/` root or `.aib_brain/`. This must be explicit in the updated `aib-analysis.md` rule text.
