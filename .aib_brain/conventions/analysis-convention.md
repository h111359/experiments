# analysis Convention

# Analysis Document Convention

**Scope:** Normative  
**Applies to:** All files named `<ITERATION_ID>-analysis.md` generated under `.aib_memory/requests/<request-folder>/`.

***

## 1. Purpose

The **Analysis document** describes the AI's structured reasoning about the user request during a specific iteration.  
It ensures that assumptions, impacts, decisions, and unknowns are explicit, traceable, and consistent across iterations.

The analysis serves as the foundation for:

*   the *questionnaire* (what must still be clarified),
*   the *plan* (how work will be executed),
*   and, ultimately, *implementation*.

It must be decision-ready for mixed stakeholders (business, product, and technical), so a human decision-maker can take correct, timely, and confident decisions.

***

## 2. Scope & Normative Language

This convention applies only to analysis artifacts for a single iteration:

*   Target files: `<ITERATION_ID>-analysis.md`
*   Location: `.aib_memory/requests/<request-folder>/`
*   Out of scope: plan, and implementation records (defined by their own conventions)

Normative keywords **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, and **MAY** are interpreted per BCP 14 (RFC 2119 / RFC 8174).

***

## 3. File Naming & Location (Normative)

*   File name **must** follow:
    <ITERATION_ID>-analysis.md
  where `<ITERATION_ID>` is exactly two digits matching regex `^[0-9]{2}$` (for example: `01`, `02`).

*   File **must** be placed in the respective request folder:
    .aib_memory/requests/<request-folder>/<ITERATION_ID>-analysis.md

*   Exactly one analysis file per iteration ID **MAY** exist at a time.

*   Regeneration **must** replace the same file path atomically.

*   Version metadata (for example: version/author/status headers) **must not** be embedded in the analysis file. Versioning is handled by VCS.

***

## 4. Mandatory Structure

Each analysis file **must** contain the following sections in the exact order:

1.  **Executive Summary** (legacy-compatible with *Summary*) **[REQ]**
2.  **Scope Interpretation** **[REQ]**
3.  **Domain Knowledge Essentials** **[REQ]**
4.  **Technical Knowledge & Terms** **[REQ]**
5.  **Assumptions** **[REQ]**
6.  **Impact Assessment** **[REQ]**
7.  **Research Plan and Findings** **[REQ]**
8.  **Rewrite Proposal of the Request** **[REQ]**
9. **Solution Options** **[REQ]**
10. **Affected Documentation** **[REQ]**
11. **Operational & Documentation Implications** **[REQ]**
12. **Risks** **[REQ]**
13. **Open Questions & Next Actions** **[REQ]**

### Section descriptions & rules:

***

### 4.1 Executive Summary

A concise overview in 5-10 bullets or sentences answering:

*   Request ID
*   Request title
*   Iteration ID
*   High-level purpose

The summary must reference:

*   The `request.md` content
*   Earlier iterations (if any)
*   Conflicts resolved per iteration precedence rule (latest iteration overrides earlier ones)
  
After each bullet keep an empty line for readability.

***

### 4.2 Scope Interpretation

A line-by-line interpretation of the request that includes:

*   Items explicitly in scope
*   Items explicitly out of scope (if user-provided)
*   Items implicitly in scope according to AIB rules (for example, documentation updates when related code is touched), labeled exactly as:
    (implicit rule - AIB framework)

Must be written in bullet-list form. Add extra empty line between bullets.

***

### 4.3 Domain Knowledge Essentials

Describe the minimum domain context required for correct decisions.

Include:

*   Business terminology and one-line definitions
*   Impacted roles/personas
*   Business processes touched
*   Relevant metrics/KPIs and IDs (if defined)
*   Acceptance impact from a business/product perspective

***

### 4.4 Technical Knowledge & Terms

Describe the minimum technical context required for correct decisions.

Include:

*   Technologies, components, modules, and environments involved
*   Data models/assets and runtime constraints
*   Non-functional attributes (reliability, performance, security, operations)
*   One-line definition for each key term/acronym on first use

***

### 4.5 Assumptions

Every assumption must follow this strict pattern:

  - Assumption A<n>: <text>
    - Rationale: <why AI considers this reasonable>
    - Risk if false: <short impact statement>
    - Falsification method: <how to validate/refute>

Rules:

*   Do not include obvious facts already stated in the request.
*   Only include assumptions that directly affect plan/implementation/decision.
*   Prefix assumption lines with `Assumption A<n>:` exactly.
*   Max 10 assumptions; if more are needed, summarize additional assumptions.

***

### 4.6 Impact Assessment

This is the most important section for downstream artifacts. It must contain all sub-sections below.

#### 4.6.1 Affected Components / Areas

List all affected architecture components, data assets, code modules, environments, dashboards, and runbooks.

If none are known, explicitly state:

  No directly identifiable components based on current context.

#### 4.6.2 Change Type and Dependencies

For each affected area include:

*   Change type: add / modify / deprecate / remove
*   Dependencies: internal/external, upstream/downstream
*   Sequencing implications

#### 4.6.3 Domain Impacts

This section aligns directly with `Product_Documentation.md` domains.

For each domain (ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC):

  - DOMAIN (<ACRONYM>): impact description
    - Relevant requirement IDs (if identifiable)

If no impact:

  - DOMAIN (ARCH): No impact detected.

#### 4.6.4 Constraints

List business, regulatory, technical, and operational constraints that shape delivery choices.

#### 4.6.5 Required Documentation Updates

Map specific requirements from `Product_Documentation.md` to required updates.

Example:

  - ARCH-01 - High-level Architecture
    Required update? YES
    Reason: New component introduced

#### 4.6.6 Decision Points

List explicit choices required from stakeholders with options and implications.

Each decision point must include:

*   options
*   implications of each option
*   recommended option (or why no recommendation yet)

***

### 4.7 Research Plan and Findings

Must contain:

*   Methodology used (for example: internal docs scan, repository scan, pattern scan)
*   Evidence summary (what was found and why it matters)
*   Gaps and unknowns (what remains unverified)
*   Proposed validation actions (spikes/experiments/SME input)
*   **Files Read** — a bullet list of every file read during the research phase. Each bullet must state the file path (workspace-relative) and a one-line note on what was found or confirmed. If a product-doc was skipped due to scope filtering or context-window management, mark it as `[SKIPPED — context limit]` or `[SKIPPED — domain out of scope]`.

Rules:

*   Summarize findings and implications; do not embed external links.
*   If live web research was used, mention outcomes only, not URLs.
*   Include a concise evidence log mapping `evidence -> implication`.
*   The Files Read bullet list is required; omitting it is a convention violation.

***

### 4.8 Solution Options

Provide at least 2 options (A/B; C optional). For each option include:

*   Overview
*   Benefits
*   Trade-offs
*   Constraints
*   Risks
*   Expected effort/lead-time
*   High-level acceptance-test ideas

Conclude with a recommendation and rationale.
Separate options with empty line for readability.

***

### 4.9 Affected Documentation

This section **must** refer to `.aib_memory/references.md`.

Structure:

  | ref_id | document_title | path | reason_for_inclusion |
  |--------|----------------|------|----------------------|

Rules:

*   Include only documents actually affected.
*   If none are identified, the table must still appear with a single row containing:
    No affected documents identified at this stage.

***

### 4.10 Operational & Documentation Implications

Describe changes expected in:

*   Runbooks
*   SLAs/SLOs
*   Monitoring/observability/logging/alerts/dashboards
*   Data quality rules
*   Product documentation artifacts and requirement sections

***

### 4.11 Risks

Risks must follow this format:

  - Risk R<n>: <short description>
    - Probability: Low/Medium/High
    - Impact: Low/Medium/High
    - Mitigation: <text>
    - Owner (role): <role>

Every risk must correspond to at least one of:

*   scope uncertainty
*   assumption
*   technical dependency
*   domain requirement

Rules:

*   Minimum 2 risks, maximum 10.
*   High-impact risks must include explicit contingency.

***

### 4.12 Disambiguation Questionnaire

 Provide the minimal but sufficient answers to the canonical disambiguation questions (see “Canonical Disambiguation Questionnaire” later). Each answered item MUST state:
   - **Question**
   - **Chosen Answer / Value**
   - **Rationale**
   - **Evidence / Reference** (internal file/section names only)
   - **Impact if changed**

  Compactness rules (Normative):
  - Answers SHOULD be concise. Long-form reasoning belongs in `<ITERATION_ID>-analysis.md`; in the plan, the rationale MAY be a short reference to the analysis/questionnaire section.
  - If multiple canonical questions are `N/A` for the same reason, they MAY be bundled into a single gate entry as long as every question number is explicitly listed (for example: `Q4, Q5, Q6`).

### 4.13 Open Questions & Next Actions

Provide a numbered list of unresolved items.

Each item must include:

*   owner (role)
*   due date or trigger condition
*   resolution path

***

## 5. Authoring Rules (Normative)

*   Audience targeting: write for mixed business/product/technical stakeholders.
*   Signal-to-noise: use concise, information-dense bullets and short sentences.
*   Traceability: reference affected artifacts by stable IDs/names (for example: `ARCH-01`, `DATA-02`), and state expected change.
*   Assumptions vs facts: mark assumptions explicitly and include falsification method.
*   Decisions: if a decision is already taken during analysis, mark as `DECISION:` with one-line rationale.
*   Numbers: prefer concrete ranges or point estimates with confidence when relevant.
*   Security/privacy: redact sensitive values; do not include secrets, credentials, tokens, or sensitive PII.
*   No document-level metadata headers inside analysis files (for example: Title/Version/Status/Owner/Last-Updated).

***

## 6. Research Method (Process Convention)

This section defines the required research process for analysis generation.

1.  Internal-first review of `request.md`, `iterations.md`, and relevant docs from `.aib_memory/references.md`.
2.  Code and asset scan for components implicated in impact assessment (repos, pipelines, scripts/notebooks, IaC, dashboards, runbooks).
3.  Pattern scan against organizational standards and prior similar solutions.
4.  Optional external benchmarking when needed; summarize takeaways without links.
5.  Minimal spikes/experiments where uncertainty is high.
6.  Evidence log that maps evidence to decision implications.

***

## 7. Rewrite Quality Rubric (Normative)

The **Rewrite Proposal of the Request** is compliant only if all are met:

*   Specificity: named actors/systems/data/triggers; ambiguous terms removed.
*   Measurability: acceptance criteria are testable with thresholds.
*   Feasibility: conforms to known constraints and architecture, or states required exceptions.
*   Completeness: includes functional and non-functional expectations plus explicit out-of-scope.
*   Traceability: references affected artifact IDs/names.
*   Clarity: no nested ambiguity; keep sentences concise.

***

## 8. Interaction With Other Conventions

### 8.1 Questionnaire Convention

Questions generated must correspond directly to:

*   missing assumptions
*   ambiguous interpretations in scope
*   gaps in dependent documentation
*   unclear affected domains
*   unresolved decision points from analysis

### 8.2 Plan Convention

The plan depends deterministically on:

*   documented impacts
*   accepted assumptions
*   resolved questionnaire answers
*   selected solution option and decision outcomes

### 8.3 Implementation Convention

Implementation must not diverge from the accepted analysis. If implementation needs scope/decision changes:

*   create a new iteration
*   generate a new analysis for that iteration

`implementation.md` should later capture what was actually done.

***

## 9. Creation Workflow (Normative)

1.  Pre-checks:
  * ensure a resolved request and active iteration exist in `iterations.md`
  * confirm `<ITERATION_ID>` exists and is active
2.  Seed:
  * create/overwrite `.aib_memory/requests/<request-folder>/<ITERATION_ID>-analysis.md`
3.  Populate:
  * fill all required sections; include optional appendices when helpful
4.  Sanity review:
  * validate quality gates
  * verify assumptions/decisions/risks are complete and properly formatted
  * verify no sensitive data is present
5.  Save:
  * perform atomic write replacement
  * do not append version headers or author lines

***

## 10. Maintenance Rules (Normative)

*   Idempotence: same memory state and same request should converge to same analysis intent.
*   Iteration supremacy: higher `ITERATION_ID` overrides conflicting earlier iteration guidance.
*   Change drivers: update analysis when scope changes, decisions change, new evidence appears, or risk state changes.
*   Closure: once an iteration is closed in `iterations.md`, analysis remains unchanged except factual corrections.

***

## 11. Quality Gates (Normative)

An analysis is **Ready for Decision** only if all are true:

1.  Coverage: all required sections are present and non-empty.
2.  Decision readiness: at least one explicit decision point exists and recommendation is present.
3.  Risk and mitigation: high-impact risks include mitigation and contingency.
4.  Assumptions: each assumption includes rationale and falsification method.
5.  Testing: testing approach exists when the change affects software/data/operations.
6.  Traceability: affected docs/components are referenced by IDs or stable names.
7.  Language: concise plain English with defined terms and no unexplained acronyms.
8.  Determinism: no speculative creative expansion beyond explicit assumptions.
9.  Disambiguity: all questions in Disambiguation Questionnaire are answered or included in the questionnaire for resolution by the user


***

## 12. Formatting Requirements

*   All headings must use `##` or `###` consistent with this convention.
*   Bullet lists must use `- `.
*   Tables must use standard GitHub Markdown table syntax.
*   No HTML is allowed.
*   No images, diagrams, embeds, or external hyperlinks.
*   The document must be deterministic (same inputs -> same output intent).
*   Separate chapters, bullets with empty lines for readability

***

## 13. Determinism Rules (Normative)

*   Given the same memory state and request input, analysis output intent must be identical.
*   AI must not guess beyond the explicit assumption mechanism.
*   If request ambiguity exists, generate additional questionnaire items instead of creative interpretation.

***

## 14. Templates & Writing Aids (Informative)

Authors may use this skeleton to seed a new file:

*   Executive Summary
*   Request Context Snapshot
*   Scope Interpretation
*   Domain Knowledge Essentials
*   Technical Knowledge & Terms
*   Assumptions
*   Impact Assessment
*   Research Plan and Findings
*   Rewrite Proposal of the Request
*   Solution Options
*   Suggested Implementation Approach
*   Suggested Testing Approach
*   Affected Documentation
*   Operational & Documentation Implications
*   Risks
*   Dependencies / Externalities
*   Open Questions & Next Actions
*   Appendices

***

## 15. Prohibited Content

*   Secrets, private keys, credentials, tokens, or sensitive PII.
*   External hyperlinks.
*   Embedded images or diagrams.
*   In-file version/author/status metadata headers.

***

## 16. Example (Minimal Skeleton)

  # Analysis - Iteration 01

  ## Executive Summary
  - Goal: ...
  - Key decision needed: ...

  ## Request Context Snapshot
  - Request ID: ...
  - Iteration ID: 01

  ## Scope Interpretation
  - In scope: ...
  - Out of scope: ...
  - Implicit: ... (implicit rule - AIB framework)

  ## Domain Knowledge Essentials
  - Term X: ...

  ## Technical Knowledge & Terms
  - Component Y: ...

  ## Assumptions
  - Assumption A1: ...
    - Rationale: ...
    - Risk if false: ...
    - Falsification method: ...

  ## Impact Assessment
  ### Affected Components / Areas
  - ...
  ### Change Type and Dependencies
  - ...
  ### Domain Impacts
  - DOMAIN (ARCH): ...
  ### Constraints
  - ...
  ### Required Documentation Updates
  - ARCH-01 - Required update? YES
  ### Decision Points
  - Decision D1: Option A / Option B ...
  ### Estimated Implementation Complexity
  - Medium - ...

  ## Research Plan and Findings
  - Methodology: ...
  - Evidence -> Implication: ...

  ## Rewrite Proposal of the Request
  - ...

  ## Solution Options
  - Option A: ...
  - Option B: ...
  - Recommendation: ...

  ## Suggested Implementation Approach
  - ...

  ## Suggested Testing Approach
  - ...

  ## Affected Documentation
  | ref_id | document_title | path | reason_for_inclusion |
  |--------|----------------|------|----------------------|
  | REF-0001 | ARCH-01 ... | ... | New component |

  ## Operational & Documentation Implications
  - ...

  ## Risks
  - Risk R1: ...
    - Probability: Medium
    - Impact: High
    - Mitigation: ...
    - Owner (role): ...

  ## Dependencies / Externalities
  - Human input: ...

  ## Open Questions & Next Actions
  1. Question ... (Owner: ..., Trigger: ...)

  ## Appendices
  - Optional backing detail

***

## 17. Effective Rule

This convention is effective immediately for newly generated analysis files and supersedes prior informal guidance for analysis content and format.


## 18. Canonical Disambiguation Questionnaire (Normative)
--------------------------------------------------
Before finalizing the plan, the following questions MUST be answered **explicitly** in section “Decision Gates”. These are designed to prevent materially different implementations:

**A. Scope & Outcome**
1. What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded?
2. Which user-visible changes (if any) MUST be demonstrable at iteration end?
3. What are the non-functional targets applicable to this iteration (latency, throughput, availability, data freshness, cost ceiling)?

**B. Data & Contracts**
4. What input data sources and schemas are authoritative (include versions) and what happens if a field is missing/extra?
5. What serialization formats, partitioning, and retention policies apply to new/changed datasets?
6. What are the error handling rules for ingestion/processing (retry policy, dead-letter, alerts, human-in-the-loop)?

**C. Compute & Algorithms**
7. Which algorithm/specification variant is in scope (if multiple exist), including parameters and defaults?
8. What accuracy/quality thresholds or benchmarks must be met (and the measurement method)?
9. Are there hardware/compute constraints (local vs. remote execution, concurrency caps, cost limits)?

**D. Interfaces & Integration**
10. Which API endpoints, message topics, or files are produced/consumed (names, versions, SLAs)?
11. What compatibility must be preserved (backward/forward) and what is the deprecation plan if breaking changes are needed?

**E. Security, Privacy, and Compliance**
12. What identities/roles may access the new/changed assets (least privilege)?
13. What data classifications are involved, and what masking/anonymization is required?
14. How are secrets injected at runtime, and what rotation policy is assumed?

**F. Observability & Operations**
15. Which metrics/logs/traces prove the change is healthy (names and thresholds)?
16. What alerts must be configured or updated and who responds?
17. What runbook/SOP updates are required, if any?

**G. Documentation & Governance**
18. Which product docs must be created or updated (paths), and is editing permitted (per references)?
19. What acceptance evidence will be recorded and where?
20. What is the rollback strategy if acceptance fails?

Answer Format (Normative)
-------------------------
Each question in the “Decision Gates” section MUST be recorded using this mini-schema:

```
**Question:** <verbatim from the questionnaire>
**Chosen Answer / Value:** <single value or structured selection>
**Rationale:** <short justification>
**Evidence / Reference:** <file/section names or iteration artifacts>
**Impact if changed:** <1–3 lines on scope/test/doc implications>
```

Allowed compact format (Normative)
---------------------------------
A gate entry MAY be represented as a single bullet as long as it still includes all fields:

- Q<N>: <Question verbatim> | Chosen Answer / Value: ... | Rationale: ... | Evidence / Reference: ... | Impact if changed: ...

For bundled `N/A` entries, list all question numbers explicitly:

- Q4, Q5, Q6: <short label or verbatim> | Chosen Answer / Value: N/A — <justification> | Rationale: ... | Evidence / Reference: ... | Impact if changed: ...
