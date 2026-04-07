# Summary

- Purpose: Describe who interacts with AI Builder (AIB) and which use cases the workflow supports.
- Scope: Personas plus core lifecycle use cases (initialize, request/iteration management, implement, release bookkeeping).
- Out-of-Scope:
	- Deep infrastructure provisioning.
	- External workspace validation beyond this repo.

# Personas

### AI_AGENT
- persona_id: AI_AGENT
- name: AI Automation Agent
- description: Executes prompt-driven workflows to implement requests and draft documentation.
- goals:
	- Apply changes only within explicitly allowed scope.
	- Produce convention-compliant artifacts.
- pain_points:
	- Missing conventions must fail closed.
	- Large workspaces exceed context limits.
- responsibilities:
	- Read references and conventions before edits.
	- Record verifications and blockers.
- success_metrics:
	- Deterministic updates with minimal cleanup.
- primary_tools:
	- Chat agent interface
	- Workspace file tools
- interaction_frequency: Regular
- notes:
	- Vendor/model should be interchangeable.

### DEVELOPER
- persona_id: DEVELOPER
- name: Repository Developer
- description: Maintains the repository and uses AIB tooling to manage structured work items.
- goals:
	- Create and track requests and iterations deterministically.
	- Keep documentation consistent with conventions.
- pain_points:
	- Manual documentation is error-prone.
	- Large diffs are hard to review.
- responsibilities:
	- Run tools and review generated artifacts.
	- Approve changes to conventions/docs.
- success_metrics:
	- Requests completed with clear audit trail.
	- Product docs remain convention-compliant.
- primary_tools:
	- VS Code
	- Local terminal with Python
- interaction_frequency: Heavy
- notes:
	- None

### MAINTAINER
- persona_id: MAINTAINER
- name: AIB Maintainer
- description: Owns `.aib_brain` assets and enforces conventions and deterministic behavior.
- goals:
	- Keep prompts/tools stable and backward compatible.
	- Enforce deterministic validation and fail-closed policies.
- pain_points:
	- Small changes can break deterministic parsing.
- responsibilities:
	- Review changes to `.aib_brain`.
	- Maintain version marker rules and workflow.
- success_metrics:
	- Tool scripts remain runnable; docs stay valid.
- primary_tools:
	- Git
	- GitHub Actions
- interaction_frequency: Occasional
- notes:
	- None

# Use Cases

### UC-001 — Initialize workspace
- uc_id: UC-001
- title: Initialize workspace
- description: Seed `.aib_memory` registers and product-doc stubs from `.aib_brain` assets.
- primary_actor: DEVELOPER
- secondary_actors:
	- AI_AGENT
- triggers:
	- AIB installed into a repository.
- preconditions:
	- `.aib_brain` exists.
	- Python is available.
- main_flow:
	1. Run initialize.
	2. Seed `.aib_memory` structure.
	3. Create registers and doc stubs.
	4. Verify baseline artifacts exist.
- alternate_flows:
	- refers to step 2: if `.aib_memory` exists, validate and keep deterministic state.
- postconditions:
	- Workspace has registers and doc stubs.
- business_value:
	- Standardized, auditable setup.
- frequency: Ad-hoc
- criticality: High
- data_assets:
	- `.aib_memory/references.md`
	- `.aib_memory/requests_register.md`
- systems:
	- Local terminal
- metrics:
	- Init succeeds without partial writes.
- non_functional_needs:
	- Determinism.
- open_questions:
	- None
- notes:
	- None

### UC-002 — Create request and iteration
- uc_id: UC-002
- title: Create request and iteration
- description: Create an Active request folder and default Active iteration 01.
- primary_actor: DEVELOPER
- secondary_actors:
	- AI_AGENT
- triggers:
	- New work item.
- preconditions:
	- Workspace initialized.
	- No other Active request exists.
- main_flow:
	1. Run create-request.
	2. Seed request artifacts.
	3. Register request Active.
	4. Register iteration 01 Active.
- alternate_flows:
	- refers to step 1: if request already Active, fail and do not write.
- postconditions:
	- One Active request exists.
- business_value:
	- Deterministic tracking.
- frequency: Ad-hoc
- criticality: High
- data_assets:
	- `.aib_memory/requests_register.md`
- systems:
	- Local terminal
- metrics:
	- active_request_count == 1.
- non_functional_needs:
	- Safety: fail on invalid state.
- open_questions:
	- None
- notes:
	- None

### UC-003 — Generate iteration artifacts
- uc_id: UC-003
- title: Generate iteration artifacts
- description: Generate analysis/questionnaire/plan artifacts for the Active iteration.
- primary_actor: AI_AGENT
- secondary_actors:
	- DEVELOPER
- triggers:
	- Developer requests artifacts.
- preconditions:
	- Active request and iteration exist.
- main_flow:
	1. Resolve active request and iteration.
	2. Generate requested artifact files.
	3. Developer reviews and answers questionnaire if present.
- alternate_flows:
	- refers to step 1: if no Active iteration exists, fail.
- postconditions:
	- Artifacts exist to guide execution.
- business_value:
	- Improves execution quality.
- frequency: Ad-hoc
- criticality: Medium
- data_assets:
	- request folder artifacts
- systems:
	- VS Code chat
- metrics:
	- Artifacts follow conventions.
- non_functional_needs:
	- Deterministic naming.
- open_questions:
	- None
- notes:
	- None

### UC-004 — Implement request scope
- uc_id: UC-004
- title: Implement request scope
- description: Apply scoped changes, update allowed product-docs, and append implementation evidence.
- primary_actor: AI_AGENT
- secondary_actors:
	- DEVELOPER
- triggers:
	- Implement instruction is issued.
- preconditions:
	- Active request exists.
	- references register identifies editable files.
- main_flow:
	1. Resolve active request and iteration.
	2. Read references and conventions.
	3. Apply changes only to edit_allowed=Y targets.
	4. Run validations.
	5. Append implementation log.
- alternate_flows:
	- refers to step 2: if convention mapping missing, stop and record blocker.
- postconditions:
	- Changes applied and auditable.
- business_value:
	- Faster iteration with controlled risk.
- frequency: Ad-hoc
- criticality: Critical
- data_assets:
	- `.aib_memory/docs/*`
- systems:
	- Workspace filesystem
- metrics:
	- forbidden_writes_count == 0.
- non_functional_needs:
	- Fail-closed.
- open_questions:
	- None
- notes:
	- None

### UC-005 — Run release bookkeeping workflow
- uc_id: UC-005
- title: Run release bookkeeping workflow
- description: Bump patch marker and generate per-version log in PR workflows.
- primary_actor: MAINTAINER
- secondary_actors:
	- DEVELOPER
- triggers:
	- PR events.
- preconditions:
	- Exactly one marker file exists.
- main_flow:
	1. Validate marker.
	2. Compute patch+1 from base ref.
	3. Rotate marker and write log.
	4. Push changes to PR branch.
- alternate_flows:
	- refers to step 1: marker invalid -> fail with explicit error.
- postconditions:
	- Marker and logs updated.
- business_value:
	- Removes manual bookkeeping errors.
- frequency: Ad-hoc
- criticality: High
- data_assets:
	- `.aib_brain/vMAJOR.MINOR.PATCH`
	- `logs/version_vX.Y.Z_log.md`
- systems:
	- GitHub Actions
- metrics:
	- idempotent reruns.
- non_functional_needs:
	- Safety against loops.
- open_questions:
	- None
- notes:
	- None

# Persona–Use Case Mapping

| persona_id | uc_id | role | frequency | importance | notes |
| --- | --- | --- | --- | --- | --- |
| DEVELOPER | UC-001 | Primary | Ad-hoc | High | Initializes workspace. |
| DEVELOPER | UC-002 | Primary | Ad-hoc | High | Creates tracked work items. |
| AI_AGENT | UC-003 | Primary | Ad-hoc | Medium | Generates artifacts on demand. |
| AI_AGENT | UC-004 | Primary | Ad-hoc | Critical | Executes implementation within guardrails. |
| MAINTAINER | UC-005 | Primary | Ad-hoc | High | Owns release process. |

# Assumptions & Constraints

- Assumptions:
	- `.aib_brain` exists at repo root.
	- Python 3.10+ is available.
- Constraints:
	- Only one Active request exists.
	- Only one Active iteration per request.
	- Only edit files allowed by references.

# Risks & Mitigations

- id: R-001; description: Agent edits disallowed files; impact: High; likelihood: Medium; mitigation: enforce references gating; owner_role: Product Team
- id: R-002; description: Workspace exceeds context limits; impact: High; likelihood: Medium; mitigation: chunk inventory and reads; owner_role: AI Agent

# Change Log

- [2026-03-22] Populated AIB personas and use cases — AI Agent
