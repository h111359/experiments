## Executive Summary
- This iteration analyzes request R-20260320-1837 (issue-19) for making the association between `product-doc` entries in `.aib_memory/references.md` and per-document convention files under `.aib_brain/conventions/` explicit and enforceable.
- The repository already contains an explicit, reviewable mapping list in `.aib_brain/conventions/product-documentation-convention.md` that associates each `product-doc` title to a convention file path.
- The current gaps are enforcement and determinism in edit workflows: `.aib_brain/prompts/aib-implement.md` and `.aib_brain/prompts/aib-update-documentation.md` do not require reading the applicable per-document convention(s) prior to editing, while other workflows (plan/questionnaire) already reference `product-documentation-convention.md`.
- A key conflict to resolve is that `aib-implement.md` includes a safety rule “Do not modify `.aib_brain/` assets”, but the user request explicitly requires updating `.aib_brain/prompts/*` to enforce convention reading.
- The product documentation files listed in references are currently seeded placeholders; the work is primarily governance + prompt behavior, not filling product docs.
- This iteration is expected to clarify and lock decisions on (1) mapping source of truth, (2) missing convention behavior (fail vs warn), and (3) whether/how to allow `.aib_brain/` prompt changes within the “implement” workflow.
- Key decisions required:
  - D1: Authoritative mapping location (rule vs mapping list vs embedding in `.aib_memory/references.md`).
  - D2: Enforcement scope (conventions read only for target-edit set vs for all product-docs).
  - D3: Failure mode when a convention is missing/unreadable.
  - D4: Workflow rule for editing `.aib_brain/` (permitted in this request or handled via separate governance action).

## Request Context Snapshot
- Request ID: R-20260320-1837
- Request title (folder slug): issue-19
- Iteration ID: 03 (Active)
- High-level purpose: ensure every `product-doc` in `.aib_memory/references.md` has an explicit association to a per-document convention under `.aib_brain/conventions/`, and ensure editing prompts enforce reading/following that convention before editing.
- Constraints inherited from `request.md`:
  - Changing the schema of `.aib_memory/references.md` is approved.
  - Enforcement must occur in `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md`.
  - Failure behavior for missing convention must be defined deterministically (error vs warning).
- Scope delta since prior iteration(s):
  - Iterations 01 and 02 are marked Completed; 03 is Active.
  - An `01-analysis.md` exists; no `02-analysis.md` is present in the request folder.
  - No updated scope text is present in `request.md` beyond `## Goal`.
- References context (current state):
  - `.aib_memory/references.md` currently lists 27 `product-doc` rows, all with `edit_allowed=Y` and `source=default`.
  - `.aib_brain/conventions/references-convention.md` states seeded rows SHOULD be `edit_allowed=N` and notes SHOULD mention “Seeded from Product_Documentation.md”, so the current register state appears either user-modified or inconsistent with the seeding convention.

## Scope Interpretation
- In scope:
  - Make the association between every `product-doc` row in `.aib_memory/references.md` and its per-document convention under `.aib_brain/conventions/` explicit and reviewable.
  - Define a deterministic mapping method (or explicit authoritative list) from requirement ID (e.g., `ARCH-01`) to convention file path (e.g., `.aib_brain/conventions/arch-01-convention.md`).
  - Update `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md` so that when a product documentation file is eligible to be edited (`edit_allowed=Y`) and is being edited, the corresponding convention file is read first and its rules are enforced.
  - Define deterministic failure behavior when a convention is missing or cannot be resolved/read.
- Out of scope (explicit in request):
  - Filling out seeded product docs with project-specific content.
- In scope (implicit rule - AIB framework):
  - If schema or behavior changes affect parsing/validation conventions, update the relevant conventions to keep the workflow deterministic (for example, `.aib_brain/conventions/references-convention.md`).
  - If prompts rely on mappings, ensure mapping source-of-truth is stable and auditable.

## Domain Knowledge Essentials
- Product documentation governance: a set of “product-doc” artifacts (ARCH/CMP/DATA/KNW/RQT/OBS/SEC) intended to be consistently structured and edited under documented conventions.
- Requirement ID: an identifier like `ARCH-01` used as a stable key across registers, documentation, and conventions.
- Roles/personas impacted:
  - Tooling maintainers (own AIB prompt + convention determinism).
  - Documentation reviewers (validate docs against conventions).
  - Contributors using prompts to update documentation.
- Business acceptance intent:
  - The mapping and enforcement must reduce ambiguity and rework by making “what rules apply to this doc” explicit and ensuring edits are compliant by design.

## Technical Knowledge & Terms
- `.aib_memory/references.md`: canonical register of referenced assets, including product docs and edit authorization (`edit_allowed`).
- `product-doc`: a reference row type representing a product documentation file seeded from `Product_Documentation.md`.
- Per-document convention file: a convention file under `.aib_brain/conventions/` named like `<req_id-lower>-convention.md` (e.g., `arch-01-convention.md`) that defines the required structure for a specific product doc.
- `.aib_brain/conventions/product-documentation-convention.md`: an explicit mapping list from product-doc titles to convention file paths.
- `target-edit set`: the subset of product-doc paths where `edit_allowed=Y` (as used by `aib-update-documentation.md`).
- Fail-closed vs fail-open:
  - Fail-closed: do not proceed with edits when required convention cannot be resolved/read.
  - Fail-open: proceed with warnings, accepting potential non-compliance.

## Assumptions
- Assumption A1: “Explicit association” must be both human-reviewable and tool-actionable (not merely implied by naming conventions).
  - Rationale: the request requires prompts to enforce convention rules, which requires deterministic resolution.
  - Risk if false: the solution may over-engineer mapping storage and create unnecessary migration work.
  - Falsification method: confirm with stakeholder whether a human-readable mapping list alone is sufficient.
- Assumption A2: The existing mapping list in `.aib_brain/conventions/product-documentation-convention.md` is intended to be authoritative (or can be made authoritative) for all `product-doc` entries.
  - Rationale: it already enumerates each product doc title with a per-doc convention file path.
  - Risk if false: prompts might enforce a mapping source that stakeholders do not accept.
  - Falsification method: verify whether any other “source of truth” is specified (e.g., in `.aib_brain/Concepts.md`) and get confirmation.
- Assumption A3: Enforcement should be applied only to the documents being edited (target-edit set), not all product-docs on every run.
  - Rationale: it keeps preflight bounded and aligns enforcement cost with actual edits.
  - Risk if false: stakeholders may require reading conventions for all docs every time to increase rigor.
  - Falsification method: confirm the intended trade-off for performance vs strictness.
- Assumption A4: Missing convention should be handled deterministically as an error for documentation edits (fail-closed) unless explicitly overridden.
  - Rationale: without fail-closed behavior, convention compliance is optional and drift remains.
  - Risk if false: strict behavior could block urgent edits in early bootstrap states.
  - Falsification method: define and approve an explicit exception policy (e.g., “warn only when user explicitly requests”).
- Assumption A5: Updating `.aib_brain/prompts/*` is acceptable within this request, even though `aib-implement.md` currently states “Do not modify `.aib_brain/` assets during implementation work.”
  - Rationale: the request explicitly targets prompt files inside `.aib_brain/`.
  - Risk if false: implementation cannot be executed via the standard implement workflow without changing that safety rule or creating a new dedicated governance workflow.
  - Falsification method: decide whether `.aib_brain/` changes are allowed for this request (and if so, under what guardrails).
- Assumption A6: The current `request.md` is intentionally minimal and is accepted for this workflow despite not matching the full request convention.
  - Rationale: `request.md` currently contains only `## Goal`; missing sections reduce determinism but the goal is still actionable.
  - Risk if false: future tooling may reject analysis/plan generation due to request format validation.
  - Falsification method: update `request.md` to the full required heading structure and re-run analysis generation.

## Impact Assessment
### Affected Components / Areas
- `.aib_brain/prompts/aib-update-documentation.md` (enforcement: resolve convention(s) for target-edit docs and require reading them)
- `.aib_brain/prompts/aib-implement.md` (enforcement: if it edits a product-doc, resolve and read convention(s) first)
- `.aib_brain/conventions/product-documentation-convention.md` (possible: clarify as authoritative mapping, normalize path conventions)
- `.aib_memory/references.md` (possible: schema change or additional structured mapping, if chosen)
- `.aib_brain/conventions/references-convention.md` (only if `references.md` schema changes)
- Product docs themselves (ARCH/CMP/DATA/KNW/RQT/OBS/SEC): impacted by governance enforcement, but not necessarily content-edited.

### Change Type and Dependencies
- Prompt changes (modify):
  - Change type: modify
  - Dependencies: `.aib_memory/references.md` row correctness; convention mapping source-of-truth; convention files existence.
  - Sequencing implications: mapping resolution approach must be defined before prompt changes can be deterministic.
- Mapping storage choice:
  - Change type: add/modify (depending on whether mapping is embedded in `references.md` or kept in `product-documentation-convention.md`)
  - Dependencies: any tooling parsing `.aib_memory/references.md` or using `product-documentation-convention.md`.
  - Sequencing implications: if schema change is chosen, update `references-convention.md` and any validators before changing `references.md`.

### Domain Impacts
- DOMAIN (ARCH): governance enforcement applies to ARCH docs (no content change implied).
- DOMAIN (CMP): governance enforcement applies to CMP docs (no content change implied).
- DOMAIN (DATA): governance enforcement applies to DATA docs (no content change implied).
- DOMAIN (DEV): prompt/convention governance changes (primary implementation domain).
- DOMAIN (DSR): No impact detected based on current context.
- DOMAIN (FNL): No impact detected based on current context.
- DOMAIN (KNW): governance enforcement applies to KNW docs (no content change implied).
- DOMAIN (RQT): governance enforcement applies to RQT docs (no content change implied).
- DOMAIN (OBS): governance enforcement applies to OBS docs (no content change implied).
- DOMAIN (OPR): No impact detected based on current context.
- DOMAIN (SEC): governance enforcement applies to SEC docs (no content change implied).

### Constraints
- The request explicitly allows changing `.aib_memory/references.md` schema, but any schema change must be coordinated with `.aib_brain/conventions/references-convention.md` and any tooling that reads/validates it.
- `aib-implement.md` currently forbids modifying `.aib_brain/` assets during implementation, but the request requires prompt changes under `.aib_brain/`.
- Path normalization consistency: `.aib_memory/references.md` uses `/` separators; `.aib_brain/conventions/product-documentation-convention.md` currently uses `\` separators.

### Required Documentation Updates
- ARCH-01 - High-level architecture
  Required update? NO
  Reason: governance and prompt enforcement do not require changing doc content.
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
- Decision D1: Where should the authoritative mapping live?
  - Option 1: Treat `.aib_brain/conventions/product-documentation-convention.md` as authoritative mapping list.
    - Implications: no `references.md` schema change required; prompts read this mapping.
  - Option 2: Deterministic naming rule from requirement ID to convention file path (e.g., `ARCH-01` -> `.aib_brain/conventions/arch-01-convention.md`) and use mapping list only as audit/reference.
    - Implications: simpler resolution; still needs a documented rule and defined failure behavior.
  - Option 3: Embed convention association in `.aib_memory/references.md` (either in `notes` or by adding a `convention_path` column).
    - Implications: makes mapping colocated with reference rows; but may require schema change + migration and updating validators.
  - Recommended: Option 1 + Option 2 combined (mapping list is explicit and reviewable; naming rule provides deterministic resolution and simplifies enforcement).
- Decision D2: Enforcement scope in prompts
  - Option A: Resolve and read conventions only for the documents being edited (target-edit set).
  - Option B: Resolve and read conventions for all product-docs on every run.
  - Recommended: Option A.
- Decision D3: Missing convention behavior
  - Option A: Fail-closed for edits (error and do not edit that doc).
  - Option B: Warn and proceed with best-effort structure.
  - Recommended: Option A by default; Option B only when explicitly requested by a human with an audit note.
- Decision D4: How to handle `.aib_brain/` modifications
  - Option A: Add a dedicated governance prompt/workflow for `.aib_brain/` changes, leaving `aib-implement.md` safety rule intact.
  - Option B: Update `aib-implement.md` to permit `.aib_brain/` edits for this class of governance requests, with guardrails.
  - Recommended: Option A if strict separation is desired; otherwise Option B with explicit scope exceptions.

### Estimated Implementation Complexity
- Medium
  - Rationale: changes touch multiple prompts and require deterministic resolution and failure behavior; schema change is optional but increases complexity if chosen.
  - Confidence: Medium (depends on chosen mapping storage and governance workflow decision).

## Research Plan and Findings
- Methodology used:
  - Request artifact review: `request.md`, `iterations.md`, existing iteration artifacts.
  - Register + docs scan: `.aib_memory/references.md` and every referenced `product-doc` file.
  - Convention + prompt scan: read analysis/request/references/product-documentation conventions; inspect prompts for required-read logic and safety rules.
- Evidence summary:
  - The mapping between product docs and conventions already exists as an explicit list in `.aib_brain/conventions/product-documentation-convention.md`.
  - `aib-create-plan.md` and `aib-create-questionnaire.md` already include `product-documentation-convention.md` as an input convention.
  - `aib-implement.md` and `aib-update-documentation.md` currently do not require per-doc conventions to be read/enforced before editing.
  - All referenced product-doc files are seeded placeholders, implying governance/prompt changes do not require content editing of those docs.
  - `.aib_memory/references.md` appears inconsistent with `.aib_brain/conventions/references-convention.md` seeding rules (seeded rows are marked editable and notes differ).
- Gaps and unknowns:
  - Whether any automated validator or tooling currently relies on the existing `references.md` schema and would break with schema changes.
  - Whether the mapping list’s backslash path formatting is acceptable cross-platform or must be normalized.
  - Whether request validation (per request convention) is enforced in tooling for analysis/plan generation.
- Evidence -> implication log:
  - Evidence: explicit mapping list exists in `product-documentation-convention.md` -> Implication: the request’s “explicit and reviewable mapping” can be satisfied without changing `references.md` schema.
  - Evidence: update/implement prompts omit convention reading -> Implication: enforcement gap remains; prompt changes are required to meet acceptance criteria.
  - Evidence: implement prompt disallows `.aib_brain/` edits -> Implication: governance changes may not be executable via the standard implement workflow without an exception or separate workflow.
  - Evidence: references register differs from its seeding convention -> Implication: eligibility semantics (`edit_allowed=Y`) may be broader than intended; enforcement should be careful not to unintentionally edit many docs.
- Proposed validation actions:
  - Add or run a deterministic check that every `product-doc` requirement ID resolves to an existing per-doc convention file.
  - Add a prompt-level self-check step: before editing a doc, confirm the resolved convention file was read and its required headings are being followed.
  - If schema change is chosen, add a migration checklist and an updated validation rule in `references-convention.md`.

## Rewrite Proposal of the Request
- Update documentation governance so that for every `product-doc` row in `.aib_memory/references.md` there is an explicit, tool-actionable association to a per-document convention file under `.aib_brain/conventions/`.
- Define the authoritative mapping method as:
  - Primary: convention path resolved deterministically from requirement ID (e.g., `ARCH-01` -> `.aib_brain/conventions/arch-01-convention.md`).
  - Secondary (audit list): `.aib_brain/conventions/product-documentation-convention.md` MUST list every product-doc title and its convention path; the list MUST be kept complete.
- Update `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md` so that for any product documentation file being edited:
  - the applicable per-document convention file MUST be resolved and read before edits,
  - edits MUST conform to the convention’s required structure,
  - if the convention cannot be resolved/read, the workflow MUST fail-closed for that document (unless explicitly overridden with a documented warning).
- Acceptance criteria:
  - For any edit of a `product-doc` file, the prompt contains an explicit instruction to read the resolved convention file first and enforce its required structure.
  - Mapping is explicit and reviewable (auditable list) and deterministic (resolvable rule).
  - Missing convention behavior is deterministic and documented.
- Out of scope:
  - Do not add project-specific content to seeded product docs.
  - Do not introduce new documentation domains or new product-docs unrelated to the mapping/enforcement change.

## Solution Options
- Option A: Use `product-documentation-convention.md` as authoritative mapping list (no `references.md` schema change)
  - Overview: prompts read `.aib_brain/conventions/product-documentation-convention.md` and locate the convention path matching a product-doc title.
  - Benefits: mapping is explicit and reviewable; minimal disruption; already present.
  - Trade-offs: requires robust parsing; depends on title matching staying stable.
  - Constraints: must normalize path separators and ensure titles exactly match references titles.
  - Risks: drift if mapping list is not updated when references change.
  - Expected effort: Medium.
  - Acceptance-test ideas: for a target doc, prompt explicitly reads the mapped convention and outputs a compliant structure.
- Option B: Deterministic naming rule from requirement ID (no `references.md` schema change)
  - Overview: prompts derive convention path from requirement ID (e.g., lowercase + `-convention.md`) and read that file.
  - Benefits: simplest deterministic mapping; no list parsing required.
  - Trade-offs: requires extracting requirement ID reliably from title/path.
  - Constraints: convention file naming must remain consistent.
  - Risks: breaks if naming deviates or requirement IDs change.
  - Expected effort: Low-Medium.
  - Acceptance-test ideas: for any `REF-xxxx` product-doc row, convention path resolves and file exists.
- Option C: Add explicit `convention_path` field to `.aib_memory/references.md` (schema change)
  - Overview: extend register schema to include `convention_path` per row.
  - Benefits: most tool-friendly; colocates mapping with reference rows.
  - Trade-offs: requires schema migration and convention/tooling updates.
  - Constraints: must update `.aib_brain/conventions/references-convention.md` and any validators/parsers.
  - Risks: backward compatibility issues; partial migration risks.
  - Expected effort: High.
  - Acceptance-test ideas: schema validation passes; prompts use `convention_path` directly.
- Recommendation: Option A + Option B combined.
  - Rationale: mapping remains explicit and reviewable (Option A) while the runtime resolution can be deterministic and simple (Option B) with a clear fail-closed rule.

## Suggested Implementation Approach
1. Decide and document D1–D4 in the iteration plan (`03-plan.md`).
2. Normalize and clarify mapping governance:
   - Confirm titles in `.aib_brain/conventions/product-documentation-convention.md` match `.aib_memory/references.md` titles exactly.
   - Normalize convention paths to use `/` in documentation (platform-neutral) or explicitly document allowed path separators.
3. Update `.aib_brain/prompts/aib-update-documentation.md`:
   - After building target-edit set, resolve the per-doc convention for each target doc and read it before editing.
   - Define deterministic failure behavior when convention is missing/unreadable.
4. Update `.aib_brain/prompts/aib-implement.md`:
   - If it edits any `product-doc`, require resolving and reading the corresponding convention before editing.
   - Resolve the governance conflict: either permit `.aib_brain/` edits for this request class (guarded) or move prompt updates to a dedicated governance workflow.
5. Add a lightweight validation step (script or documented manual check) ensuring:
   - every `product-doc` row has a resolvable convention file,
   - missing convention behavior is deterministic.
6. Record outcomes in `implementation.md` with an entry for iteration 03.

## Suggested Testing Approach
- Prompt-level verification (manual, deterministic):
  - For a chosen small set of product docs (e.g., one each from ARCH/DATA/SEC), simulate an “edit” scenario and verify the prompt instructions explicitly require reading the resolved convention first.
  - Negative test: remove/rename a convention path (in a controlled test branch) and verify fail-closed behavior is triggered deterministically.
- Static checks (automatable, low effort):
  - Validate every product-doc requirement ID resolves to an existing convention file under `.aib_brain/conventions/`.
  - Validate mapping list completeness: every product-doc title in `.aib_memory/references.md` has a corresponding entry in `product-documentation-convention.md`.
- Regression guardrail:
  - Ensure `aib-create-plan.md` and `aib-create-questionnaire.md` continue to function with the chosen mapping approach (especially if schema changes are made).

## Affected Documentation
| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0002 | ARCH-02 - Topology/network description | .aib_memory/docs/04 Technology/Architecture/ARCH-02.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0003 | ARCH-03 - Capacity model | .aib_memory/docs/04 Technology/Architecture/ARCH-03.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0004 | ARCH-04 - ADRs repository | .aib_memory/docs/04 Technology/Architecture/ARCH-04.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0005 | ARCH-06 - Runtime interaction sequences | .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0006 | ARCH-07 - Resource catalog | .aib_memory/docs/04 Technology/Inventory/ARCH-07.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0008 | CMP-02 - Algorithm specification register | .aib_memory/docs/04 Technology/Compute/CMP-02.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0009 | DATA-01 - Source data catalog and data ingestion strategy | .aib_memory/docs/04 Technology/Data Sources/DATA-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0010 | DATA-02 - Data models (logical & physical) | .aib_memory/docs/04 Technology/Data Models/DATA-02.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0011 | DATA-03 - Data lineage | .aib_memory/docs/04 Technology/Data Workspace/DATA-03.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0012 | DATA-04 - Data storage strategy & patterns | .aib_memory/docs/04 Technology/Data Workspace/DATA-04.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0013 | DATA-05 - Data consumption & access patterns | .aib_memory/docs/04 Technology/Data Workspace/DATA-05.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0014 | DATA-06 - Metrics catalog | .aib_memory/docs/04 Technology/Analytics/DATA-06.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0015 | DATA-07 - Data quality rules, monitoring & reporting | .aib_memory/docs/04 Technology/Data Workspace/DATA-07.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0016 | DATA-08 - Data archiving & deletion policy | .aib_memory/docs/04 Technology/Data Workspace/DATA-08.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0017 | DATA-09 - Dashboard inventory | .aib_memory/docs/04 Technology/Analytics/DATA-09.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0019 | KNW-02 - Business process catalog | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0020 | KNW-03 - Use cases & personas | .aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0021 | OBS-01 - Logging | .aib_memory/docs/04 Technology/Observability/OBS-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0022 | RQT-01 - Product charter | .aib_memory/docs/01 Product Management/Product Charter/RQT-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0024 | SEC-01 - Access management | .aib_memory/docs/04 Technology/Access and Security/SEC-01.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0025 | SEC-02 - Infrastructure data protection | .aib_memory/docs/04 Technology/Access and Security/SEC-02.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0026 | SEC-03 - Secrets management & rotation policy | .aib_memory/docs/04 Technology/Access and Security/SEC-03.md | Governance mapping and convention enforcement applies to this doc when edited. |
| REF-0027 | SEC-04 - Infrastructure network security | .aib_memory/docs/04 Technology/Access and Security/SEC-04.md | Governance mapping and convention enforcement applies to this doc when edited. |

## Operational & Documentation Implications
- Operational workflow implications:
  - Documentation edits become stricter: convention resolution/read becomes a hard preflight step for any product-doc edit, which may increase failure rate but improves determinism.
  - If fail-closed is adopted, missing conventions become blockers that must be resolved before editing proceeds.
- Documentation governance implications:
  - The mapping list must be kept complete and consistent with `.aib_memory/references.md` titles and paths.
  - If `references.md` remains broadly editable (`edit_allowed=Y` for all product-docs), prompt changes could make it easier to unintentionally edit many docs; additional guardrails may be needed (e.g., only edit docs explicitly required by request scope).
- Observability/documentation implications:
  - Add an audit note to `implementation.md` entries indicating which convention files were applied for each edited doc.

## Risks
- Risk R1: Governance conflict prevents execution of required prompt updates.
  - Probability: Medium
  - Impact: High
  - Mitigation: Decide D4 explicitly; either permit `.aib_brain/` edits for this request class or create a dedicated governance workflow for `.aib_brain/` modifications.
  - Owner (role): Tooling maintainer
- Risk R2: Mapping drift between `.aib_memory/references.md` titles and `product-documentation-convention.md` entries.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Add a deterministic validation check that every product-doc row matches exactly one mapping entry and that its convention file exists.
  - Owner (role): Documentation governance owner
- Risk R3: `references.md` schema change breaks existing tooling/parsers.
  - Probability: Low
  - Impact: High
  - Mitigation: Prefer no schema change (Option A+B). If schema change is chosen, update `references-convention.md` first and add a migration plan with rollback.
  - Owner (role): Tooling maintainer
- Risk R4: Path separator inconsistency (`/` vs `\`) causes non-deterministic resolution across environments.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Normalize to `/` in conventions and prompts or implement a normalization rule in mapping resolution.
  - Owner (role): Tooling maintainer

## Dependencies / Externalities
- Stakeholder decision on mapping source-of-truth (D1).
- Stakeholder decision on failure mode (D3).
- Governance decision on allowing `.aib_brain/` edits in the implement workflow or providing an alternative workflow (D4).
- Confirmation whether request validation (per request convention) is enforced by tooling; if enforced, the request must be expanded to include required sections.

## Open Questions & Next Actions
1. (Owner: Tooling maintainer; Due: before creating `03-plan.md`) Decide D4: are `.aib_brain/prompts/*` edits allowed under this request via `aib-implement`, or must a separate governance workflow be used?
2. (Owner: Documentation governance owner; Due: before implementing prompt changes) Decide D1/D2: will mapping be resolved via naming rule, mapping list parsing, or a `references.md` schema change?
3. (Owner: Product/Tech lead; Due: before any doc edits) Decide D3: should missing convention block edits (fail-closed) or allow warnings (fail-open) and under what override policy?
4. (Owner: Tooling maintainer; Trigger: if schema change is selected) Identify all consumers of `.aib_memory/references.md` and confirm compatibility/migration steps.
5. (Owner: Request author; Trigger: if tooling enforces request format validation) Expand `request.md` to the full required heading structure to avoid tool rejections.

## Appendices
### Appendix A: Current mapping evidence (summary)
- `.aib_brain/conventions/product-documentation-convention.md` already lists each `product-doc` title with a per-document convention file path, matching the intent of the request’s “explicit mapping” requirement.
