# Analysis - Iteration 01

## Executive Summary
- The request aims to (1) make the mapping explicit between each `product-doc` entry in `.aib_memory/references.md` and its corresponding convention file under `.aib_brain/conventions/`, and (2) update `.aib_brain/prompts` so that per-document convention rules are followed whenever a product doc is edited.
- Evidence indicates that per-document convention files already exist (for example, `.aib_brain/conventions/arch-01-convention.md`) and a mapping list already exists in `.aib_brain/conventions/product-documentation-convention.md`, but edit workflows do not consistently require reading the per-document conventions.
- The immediate gap is in editing prompts (notably `implement` and `update-documentation`) which currently require reading product docs but do not explicitly require reading the corresponding per-doc convention(s) before making edits.
- This iteration should resolve a key design decision: where the “explicit relationship” should live (mapping rule vs explicit mapping table vs embedding convention path in `references.md` notes) and how prompts should deterministically load conventions.
- Recommended direction: prefer keeping `.aib_memory/references.md` schema unchanged and implement a deterministic “doc -> convention” mapping rule based on requirement IDs (with fallback to the explicit list in `product-documentation-convention.md`), then require prompts to read the applicable convention files before editing. A schema change remains an allowed fallback if the team wants the mapping embedded in `references.md`.
- Key decision points: (D1) mapping source of truth; (D2) whether to update prompts to read all per-doc conventions up front or only for the target-edit set; (D3) how strictly to fail when a convention file is missing.

## Request Context Snapshot
- Request ID: R-20260320-1837
- Request title (folder slug): issue-19
- Iteration ID: 01 (Active)
- High-level purpose: improve determinism and compliance of documentation-editing workflows by binding each product doc to its governing convention and ensuring prompts apply those conventions.
- Constraints inherited from `request.md`:
  - The relationship MAY require changing the schema of `.aib_memory/references.md`.
  - The request currently provides no additional constraints.
- Scope delta since prior iteration: N/A (initial iteration).
- References context: `.aib_memory/references.md` lists 27 `product-doc` documentation files (seed placeholders) and per-document convention files exist for each corresponding requirement ID.
- Request validity note (per `.aib_brain/conventions/request-convention.md`): the current `request.md` contains only `## Goal` and is missing required sections (`## Background`, `## Scope`, `## Out of scope`, `## Constraints`, `## Success criteria`). This makes scope boundaries and acceptance criteria under-specified.

## Scope Interpretation
- In scope: Define an explicit relationship between each `product-doc` referenced in `.aib_memory/references.md` and its related convention file under `.aib_brain/conventions/`.
- In scope: Modify prompts under `.aib_brain/prompts` to ensure that, when a `product-doc` is edited, the relevant convention file’s instructions are read and followed.
- Potentially in scope: If required to make the relationship explicit and tool-actionable, change `.aib_memory/references.md` schema and update `.aib_brain/conventions/references-convention.md` accordingly (the request explicitly allows schema change).
- Out of scope: Editing the content of the product documentation files themselves (for example, filling ARCH/DATA docs with project content) unless required to implement the relationship/prompt behavior.
- Out of scope: Introducing additional UX/features beyond the relationship mapping and prompt enforcement.
- Implicitly in scope: Update any related convention documentation to keep the workflow deterministic and auditable (implicit rule - AIB framework).

## Domain Knowledge Essentials
- Product documentation set: the curated set of “product-doc” artifacts that define the product across domains (ARCH/CMP/DATA/KNW/RQT/OBS/SEC, etc.).
- Governance intent: per-document conventions define the expected structure and editing rules for each product doc so humans can validate and tools can generate deterministically.
- Roles impacted:
  - Documentation owners/reviewers who expect consistent structure.
  - Developers/maintainers using AIB prompts to update docs.
  - Tooling maintainers responsible for deterministic prompt behavior.
- Business acceptance: the “explicit relationship” must be discoverable and enforceable so updates to docs remain consistent with the standards.

## Technical Knowledge & Terms
- `product-doc`: a reference type in `.aib_memory/references.md` representing a product documentation file seeded from `.aib_brain/conventions/Product_Documentation.md`.
- Per-document convention: a file under `.aib_brain/conventions/` (for example, `arch-01-convention.md`) defining the exact structure/rules for a specific product doc.
- Editing prompt: an instruction file under `.aib_brain/prompts/` that governs how agents read inputs and make edits (notably `aib-implement.md` and `aib-update-documentation.md`).
- Deterministic mapping: a stable rule that maps a requirement/document ID (e.g., `ARCH-01`) to the convention file that governs it.

## Assumptions
- Assumption A1: “Make explicit relationship” means the relationship must be expressed in a place that is both human-readable and tool-actionable (not only implied by naming).
  - Rationale: the request explicitly asks for the relationship to be explicit, and prompts need to use it.
  - Risk if false: changes may be implemented in the wrong artifact (e.g., only documentation prose) and fail to improve tooling behavior.
  - Falsification method: confirm desired “source of truth” location with stakeholder (convention doc vs references notes vs mapping rule).
- Assumption A2: The per-document convention set is intended to be complete and authoritative for the current `product-doc` set.
  - Rationale: convention files exist for each current requirement ID in `.aib_memory/references.md`.
  - Risk if false: prompts may read and apply conventions that are incomplete or not intended for enforcement.
  - Falsification method: spot-check additional convention files and confirm they’re normative and in-use.
- Assumption A3: Prompts are the primary enforcement mechanism (rather than a separate script/validator) for ensuring convention compliance during edits.
  - Rationale: the request explicitly targets modifying `.aib_brain/prompts`.
  - Risk if false: prompt changes alone may not guarantee compliance if other tooling writes docs.
  - Falsification method: identify all doc-writing entry points (scripts/tools) and confirm prompts are used for edits.
- Assumption A4: A `references.md` schema change is allowed but not required; the team will prefer the least disruptive approach unless a first-class field is explicitly desired.
  - Rationale: the request explicitly allows schema change, while the existing conventions define a strict schema and tooling likely assumes it.
  - Risk if false: the chosen solution may be rejected if stakeholders require the mapping to live directly inside `references.md` (as structured data).
  - Falsification method: confirm Decision D1 with the tooling owner and confirm whether any downstream parsers would break on a schema change.
- Assumption A5: When editing documentation, reading the convention file should be a hard preflight requirement (fail closed) rather than best-effort.
  - Rationale: without a hard requirement, convention compliance remains optional and inconsistent.
  - Risk if false: strict failures may reduce usability for partial doc sets or early scaffolds.
  - Falsification method: agree on failure behavior (error vs warning) when convention file is missing.

- Assumption A6: Because `request.md` is missing required sections, this analysis treats scope boundaries and success criteria as unknown and focuses on the minimal interpretation of the stated Goal.
  - Rationale: per request convention, missing sections reduce determinism; analysis should not invent missing scope/criteria.
  - Risk if false: later clarification may shift scope (e.g., requiring schema changes) and invalidate parts of the analysis.
  - Falsification method: update `request.md` to the full required structure and regenerate analysis for the iteration.

## Impact Assessment
### Affected Components / Areas
- `.aib_brain/prompts/aib-implement.md`
- `.aib_brain/prompts/aib-update-documentation.md`
- Potentially `.aib_brain/prompts/aib-create-plan.md` and `.aib_brain/prompts/aib-create-questionnaire.md` (only if they need to reference the explicit mapping for traceability; they do not edit docs directly).
- `.aib_brain/conventions/product-documentation-convention.md` (may be updated to be the explicit mapping source-of-truth and to define deterministic mapping rules).
- `.aib_memory/references.md` (may remain unchanged; alternatively could be enhanced via `notes` text, but schema must remain as-is).

### Change Type and Dependencies
- Prompts: modify
  - Dependency: rely on `.aib_memory/references.md` to enumerate product-docs and determine edit targets.
  - Dependency: rely on the presence and stability of per-document convention files in `.aib_brain/conventions/`.
  - Sequencing: define mapping rule/source-of-truth first, then update prompts to require reading and applying the right convention(s).
- Conventions: modify
  - Dependency: keep consistent with existing per-doc convention files and with `.aib_brain/conventions/references-convention.md` schema constraints.

### Domain Impacts
- DOMAIN (ARCH): No impact detected (content not being updated; governance enforcement only).
- DOMAIN (CMP): No impact detected.
- DOMAIN (DATA): No impact detected.
- DOMAIN (DEV): Governance/tooling improvement affecting how docs are edited.
- DOMAIN (DSR): No impact detected.
- DOMAIN (FNL): No impact detected.
- DOMAIN (KNW): No impact detected.
- DOMAIN (RQT): Governance/tooling improvement affecting requirements-related docs edit workflow.
- DOMAIN (OBS): No impact detected.
- DOMAIN (OPR): No impact detected.
- DOMAIN (SEC): No impact detected.

### Constraints
- `.aib_memory/references.md` schema is defined by `.aib_brain/conventions/references-convention.md`; changing it requires updating the convention and any tooling that parses/validates the file.
- Analysis/plan/questionnaire prompts already require reading all `product-doc` files; extending preflight to also read conventions must remain deterministic and bounded.
- Implementation prompt currently forbids modifying `.aib_brain/` assets during implementation; prompt updates are therefore a separate workflow (not part of `implement`).

### Required Documentation Updates
- ARCH-01 - High-level architecture
  Required update? NO
  Reason: Relationship/enforcement changes do not require editing the product doc content.
- ARCH-02 - Topology/network description
  Required update? NO
- ARCH-03 - Capacity model
  Required update? NO
- ARCH-04 - ADRs repository
  Required update? NO
- ARCH-06 - Runtime interaction sequences
  Required update? NO
- ARCH-07 - Resource catalog
  Required update? NO
- CMP-01 - Notebook/script catalog
  Required update? NO
- CMP-02 - Algorithm specification register
  Required update? NO
- DATA-01 - Source data catalog and data ingestion strategy
  Required update? NO
- DATA-02 - Data models (logical & physical)
  Required update? NO
- DATA-03 - Data lineage
  Required update? NO
- DATA-04 - Data storage strategy & patterns
  Required update? NO
- DATA-05 - Data consumption & access patterns
  Required update? NO
- DATA-06 - Metrics catalog
  Required update? NO
- DATA-07 - Data quality rules, monitoring & reporting
  Required update? NO
- DATA-08 - Data archiving & deletion policy
  Required update? NO
- DATA-09 - Dashboard inventory
  Required update? NO
- KNW-01 - Domain glossary
  Required update? NO
- KNW-02 - Business process catalog
  Required update? NO
- KNW-03 - Use cases & personas
  Required update? NO
- OBS-01 - Logging
  Required update? NO
- RQT-01 - Product charter
  Required update? NO
- RQT-02 - Requirements document
  Required update? NO
- SEC-01 - Access management
  Required update? NO
- SEC-02 - Infrastructure data protection
  Required update? NO
- SEC-03 - Secrets management & rotation policy
  Required update? NO
- SEC-04 - Infrastructure network security
  Required update? NO

### Decision Points
- Decision D1: Where should the explicit mapping live?
  - Option 1: Mapping rule (by requirement ID) + explicit list in `product-documentation-convention.md` as authoritative.
    - Implication: No changes to `references.md` schema; prompts deterministically resolve conventions.
  - Option 2: Embed convention path in `.aib_memory/references.md` `notes` for each `product-doc` row.
    - Implication: Requires editing many rows and defining parsing rules; still schema-compliant.
  - Option 3: Add a new column to `references.md` (e.g., `convention_path`).
    - Implication: Requires changing `.aib_brain/conventions/references-convention.md` and migrating tooling.
  - Recommended: Option 1 (least disruptive; still explicit if the mapping is stated normatively and listed).
- Decision D2: Prompt loading strategy for per-doc conventions during edits
  - Option A: Read conventions only for target-edit docs (`edit_allowed=Y`).
    - Implication: Efficient and directly tied to editing.
  - Option B: Read conventions for all `product-doc` entries every time.
    - Implication: More robust but potentially wasteful; increases preflight cost.
  - Recommended: Option A.
- Decision D3: Missing convention behavior
  - Option A: Fail closed (do not edit doc) if convention is missing.
  - Option B: Warn and proceed with `product-documentation-convention.md` only.
  - Recommended: Option A for `update-documentation`; Option B may be acceptable for emergencies if explicitly requested.

### Estimated Implementation Complexity
- Medium
  - Rationale: Changes span multiple prompts and require a deterministic mapping approach with clear failure behavior.
  - Confidence: Medium (depends on how the explicit relationship is expected to be surfaced and whether any downstream parsers assume current prompt text).

## Research Plan and Findings
- Methodology:
  - Internal docs scan: read `.aib_memory/references.md` and all referenced `product-doc` files.
  - Convention scan: inspected `.aib_brain/conventions/` and representative per-doc convention content.
  - Prompt scan: inspected `.aib_brain/prompts/` for preflight and editing requirements.
- Findings:
  - Per-document convention files exist for the current product-doc set (evidence: `arch-01-convention.md` and many peers).
  - An explicit list-style mapping of document titles to convention file paths exists in `product-documentation-convention.md`.
  - Editing prompts do not currently require reading per-document conventions before editing product docs; `aib-implement.md` and `aib-update-documentation.md` notably omit `product-documentation-convention.md` and any per-doc convention requirement.
- Evidence -> Implication log:
  - Evidence: `product-documentation-convention.md` lists each product doc with a convention file path -> Implication: mapping can be treated as explicit without changing `references.md` schema.
  - Evidence: `aib-update-documentation.md` builds required-read and target-edit sets but does not mention conventions -> Implication: doc updates can drift from required structure unless conventions are mandated.
  - Evidence: per-doc conventions contain normative required section orders/headings -> Implication: prompts must instruct writers to conform to these exact structures when editing.
- Gaps/unknowns:
  - Whether the “explicit relationship” must be stored in `.aib_memory/references.md` itself (vs a convention doc).
  - Whether any automation parses `product-documentation-convention.md` today (or it is informational only).
  - Whether missing per-doc conventions should be treated as an error globally.
- Proposed validation actions:
  - Add a lightweight validation step (manual or scripted) that ensures every `product-doc` requirement ID has a corresponding `<id>-convention.md` file.
  - Confirm prompt consumers (agents/scripts) do not rely on the older minimal analysis template structure.

## Rewrite Proposal of the Request
- Update the documentation governance so that for every `product-doc` entry listed in `.aib_memory/references.md`, there is an explicitly documented association to a per-document convention file under `.aib_brain/conventions/`.
- Define a deterministic mapping method (or an explicit authoritative list) for resolving `product-doc` requirement IDs (e.g., `ARCH-01`) to convention files (e.g., `.aib_brain/conventions/arch-01-convention.md`).
- Update `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md` so that when a product documentation file is eligible to be edited (`edit_allowed=Y`) and is being edited, the corresponding convention file is read first and its rules are enforced.
- Acceptance criteria:
  - For any edit of a `product-doc` file, the prompt explicitly requires reading the corresponding convention file and following its required structure.
  - The mapping is explicit and reviewable without inference.
  - Failure behavior on missing convention is defined (error vs warning) and is deterministic.
- Out of scope:
  - Filling out the seeded product docs with project-specific content.
  - Changing the schema of `.aib_memory/references.md` unless explicitly approved.

## Solution Options
- Option A: Deterministic mapping rule + authoritative list in `product-documentation-convention.md` (no `references.md` changes)
  - Overview: Treat requirement IDs as the key; resolve convention path via a standard naming rule and/or a curated mapping list.
  - Benefits: Minimal disruption; no register schema changes; mapping is explicit in a single normative place.
  - Trade-offs: Requires prompts (and any tools) to implement mapping resolution behavior.
  - Constraints: Must define behavior when a requirement has no convention file.
  - Risks: Mapping drift if new product docs are added but the mapping list isn’t updated.
  - Expected effort: Medium (prompt edits + documentation updates).
  - Acceptance-test ideas: Given a target-edit doc with ID `ARCH-01`, the workflow reads `arch-01-convention.md` and produces a compliant structure.
- Option B: Embed convention path in `.aib_memory/references.md` `notes` for each product-doc row
  - Overview: Store “convention=…” text in the existing `notes` field for each `product-doc` row.
  - Benefits: Keeps mapping colocated with the referenced document; no schema changes required.
  - Trade-offs: Requires mass-editing register rows; requires defining a parsing convention for notes text.
  - Constraints: Notes is free-text; consistency must be enforced by additional rules.
  - Risks: Tools may not parse notes reliably; humans may edit notes inconsistently.
  - Expected effort: Medium-High (row edits + parsing rules + validation).
  - Acceptance-test ideas: Parser extracts convention path from notes for all product-doc rows deterministically.
- Option C: Extend `.aib_memory/references.md` schema with a `convention_path` column
  - Overview: Make mapping first-class in the register schema.
  - Benefits: Most explicit and tool-friendly.
  - Trade-offs: Requires updating `.aib_brain/conventions/references-convention.md` and migrating tooling.
  - Constraints: Any existing parsers/validators may break.
  - Risks: Backwards-compatibility issues.
  - Expected effort: High.
  - Acceptance-test ideas: Schema validation and all prompts/tools continue to work with the new column.
- Recommendation: Option A.
  - Rationale: It is explicit (via authoritative list + mapping rule), preserves `references.md` schema, and aligns with the existing convention file layout.

## Suggested Implementation Approach
- Update/clarify `product-documentation-convention.md` to be explicitly normative for the mapping (if it is not already treated as such), including:
  - A deterministic mapping rule for requirement ID to convention filename.
  - A completeness rule: every `product-doc` requirement ID must have a convention file.
- Update `.aib_brain/prompts/aib-update-documentation.md` preflight to:
  - After computing the target-edit set, resolve and read each applicable per-doc convention file before editing.
  - Define fail-closed behavior if a convention is missing.
- Update `.aib_brain/prompts/aib-implement.md` documentation reading requirements to:
  - Include reading `product-documentation-convention.md`.
  - For any documentation file it is about to edit (authorized via `references.md`), require reading the matching per-doc convention first.
- Capture execution detail in the iteration plan artifact (`01-plan.md`) once produced.

## Suggested Testing Approach
- Static validation:
  - Verify every `product-doc` in `.aib_memory/references.md` has a corresponding convention file under `.aib_brain/conventions/`.
  - Verify each modified prompt includes explicit steps requiring convention reads before edits.
- Behavioral checks (manual):
  - Mark a single doc as `edit_allowed=Y`, run the update-documentation workflow, and confirm the prompt requires and applies the per-doc convention structure.
- Regression checks:
  - Ensure prompts that do not edit docs (analysis/questionnaire/plan) remain deterministic and do not gain unnecessary scope.

## Affected Documentation
| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| N/A | No affected documents identified at this stage. | N/A | This request targets conventions and prompts; it does not require editing referenced `product-doc` files. |

## Operational & Documentation Implications
- Documentation governance becomes stricter: edits to product docs must conform to per-doc conventions, improving consistency and reviewability.
- Operationally, doc-edit operations may fail earlier (by design) if convention files are missing or unread, which reduces silent drift but requires clear error messaging in the prompt text.
- Long-term, onboarding and maintenance improves because each document has an explicit governing standard and edit workflows enforce it.

## Risks
- Risk R1: The “explicit relationship” requirement is interpreted differently (e.g., must be stored in `.aib_memory/references.md`), causing rework.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Decide and document the single source of truth for mapping (Decision D1).
  - Owner (role): Product owner / tooling owner
- Risk R2: Prompts become too strict (fail-closed) and block legitimate early-stage edits.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Define a controlled escape hatch (explicit instruction required to proceed without per-doc convention).
  - Owner (role): Tooling owner
- Risk R3: Mapping drift when new product-doc requirements are added but convention files/mapping list are not updated.
  - Probability: Medium
  - Impact: High
  - Mitigation: Add a validation checklist/step that compares `references.md` product-doc IDs to convention files.
  - Owner (role): Maintainers / CI owner

- Risk R4: `request.md` is non-compliant with the request convention, so downstream tools may be forced to guess or fail (and success criteria are currently undefined).
  - Probability: High
  - Impact: Medium
  - Mitigation: Update `request.md` to include all required sections and measurable success criteria, then regenerate iteration artifacts.
  - Owner (role): Request author / product owner

## Dependencies / Externalities
- Human input: confirm mapping source of truth and failure behavior for missing conventions.
- Process: agree whether `product-documentation-convention.md` is normative and must be updated with new requirements.
- Tooling: any scripts/parsers consuming `.aib_brain/prompts` must tolerate the updated prompt text.

## Open Questions & Next Actions
1. Confirm where the explicit mapping must be stored (Owner: Tooling owner; Trigger: before prompt edits; Resolution: pick Decision D1 and document it).
2. Confirm strictness of missing convention handling (Owner: Tooling owner; Trigger: before implementing fail-closed behavior; Resolution: pick Decision D3).
3. Identify whether any tooling currently parses `product-documentation-convention.md` (Owner: Maintainer; Trigger: before relying on it as authoritative; Resolution: search code/scripts for references and document findings).
4. Update `request.md` to include the required sections and success criteria (Owner: Request author; Trigger: before implementing prompt changes; Resolution: add `## Background`, `## Scope`, `## Out of scope`, `## Constraints`, `## Success criteria` per the request convention).

## Appendices
- Appendix A: Current observed state
  - `.aib_memory/references.md` contains 27 `product-doc` rows.
  - The referenced product-doc files currently contain seeded placeholder text.
  - Per-document convention files exist for each referenced requirement ID.