Purpose
Define a clear, portable, and machine-checkable convention for the “Use Cases & Personas” document associated with requirement KNW-03. This convention standardizes the file name, structure, allowed content, validation rules, and operating (edit) procedures so both AI and humans can create, read, and verify the document consistently.

Scope
This convention applies to a single document containing:
- A catalog of use cases supported by the product
- A catalog of personas interacting with the product
- A mapping between personas and use cases, including goals and pain points per persona
It governs formatting, allowed fields, validation, and maintenance workflows. 

File Naming
- Document ID: KNW-03
- Default file name: KNW-03.md
- Character set: UTF-8
- Line endings: LF
- One file per product

Authoring Principles
- Audience: business stakeholders, product managers, analysts, architects, and AI assistants
- Language: English
- Clarity: short sentences, unambiguous terms
- Determinism: follow the exact field names and orders below so automation can parse it reliably
- No external links inside the document body unless explicitly required by a field definition

Document Structure (Top-Level Headings in this exact order)
1. Summary
2. Personas
3. Use Cases
4. Persona–Use Case Mapping
5. Assumptions & Constraints
6. Risks & Mitigations
7. Change Log

Section 1 — Summary
Goal: Provide a brief orientation to the content and its intended use.
Required fields (in order):
- Purpose: one short paragraph describing why this document exists
- Scope: one short paragraph describing what this document covers
- Out-of-Scope: bullet list of items that are not covered

Section 2 — Personas
Goal: Define who interacts with the product.
Representation: persona entries as a level-3 heading per persona.
Ordering: by persona_id ascending.
Required fields per persona:
- persona_id: stable identifier using upper snake case; regex ^[A-Z0-9_]+$
- name: short human-readable label
- description: 1–3 sentences describing the persona
- goals: bullet list; each bullet is a single, testable goal statement
- pain_points: bullet list; each bullet is a concise pain/friction statement
- responsibilities: bullet list describing typical duties related to the product
- success_metrics: bullet list; how success is measured for this persona
- primary_tools: bullet list; key tools/systems used by this persona
- interaction_frequency: one of Rare, Occasional, Regular, Heavy
- notes: optional bullet list for clarifications

Example persona block (structure only; replace with actual content):
### <PERSONA_ID>
- persona_id: <PERSONA_ID>
- name: <Persona Name>
- description: <1–3 sentences>
- goals:
  - <goal 1>
  - <goal 2>
- pain_points:
  - <pain 1>
  - <pain 2>
- responsibilities:
  - <resp 1>
  - <resp 2>
- success_metrics:
  - <metric 1>
  - <metric 2>
- primary_tools:
  - <tool 1>
  - <tool 2>
- interaction_frequency: <Rare|Occasional|Regular|Heavy>
- notes:
  - <optional note>

Section 3 — Use Cases
Goal: Define the set of product use cases with enough detail for alignment and automation.
Representation: use case entries as a level-3 heading per use case.
Ordering: by uc_id ascending.
Required fields per use case:
- uc_id: stable identifier; format UC-### with zero-padded number; regex ^UC-[0-9]{3}$
- title: short, action-oriented label (imperative mood preferred)
- description: 1–4 sentences describing the user intent and outcome
- primary_actor: persona_id of the main actor
- secondary_actors: bullet list of persona_id values or “None”
- triggers: bullet list of events that initiate the use case
- preconditions: bullet list of conditions that must hold true
- main_flow: numbered list of the primary steps (5–12 steps typical)
- alternate_flows: bullet list referencing step numbers and explaining variations
- postconditions: bullet list of state changes and outputs
- business_value: 1–3 bullets capturing the tangible benefit
- frequency: one of Ad-hoc, Daily, Weekly, Monthly, Quarterly, Yearly
- criticality: one of Low, Medium, High, Critical
- data_assets: bullet list naming important data objects/entities
- systems: bullet list naming systems/components touched
- metrics: bullet list of success/health metrics related to this use case
- non_functional_needs: bullet list (e.g., performance, security, compliance)
- open_questions: bullet list of known gaps
- notes: optional bullet list for clarifications

Example use case block (structure only; replace with actual content):
### <UC_ID> — <Title>
- uc_id: <UC_ID>
- title: <Short title>
- description: <1–4 sentences>
- primary_actor: <PERSONA_ID>
- secondary_actors:
  - <PERSONA_ID or None>
- triggers:
  - <trigger 1>
- preconditions:
  - <precondition 1>
- main_flow:
  1. <step 1>
  2. <step 2>
- alternate_flows:
  - <refers to step N: description>
- postconditions:
  - <post 1>
- business_value:
  - <value 1>
- frequency: <Ad-hoc|Daily|Weekly|Monthly|Quarterly|Yearly>
- criticality: <Low|Medium|High|Critical>
- data_assets:
  - <asset 1>
- systems:
  - <system 1>
- metrics:
  - <metric 1>
- non_functional_needs:
  - <nfr 1>
- open_questions:
  - <question 1>
- notes:
  - <optional note>

Section 4 — Persona–Use Case Mapping
Goal: Provide a deterministic mapping for impact analysis and planning.
Representation: a single table with the exact columns and constraints below.
Columns (in this order):
- persona_id
- uc_id
- role: one of Primary, Secondary, Reviewer, Approver, Observer
- frequency: one of Ad-hoc, Daily, Weekly, Monthly, Quarterly, Yearly (may differ from use case global frequency to reflect persona-specific cadence)
- importance: one of Low, Medium, High, Critical (persona-specific)
- notes: optional short text

Validation rules for this section:
- persona_id must exist in Section 2 Personas
- uc_id must exist in Section 3 Use Cases
- Each pair (persona_id, uc_id, role) must be unique
- At least one row must exist where role = Primary for each uc_id

Section 5 — Assumptions & Constraints
Goal: Capture key assumptions and constraints to reduce ambiguity.
Content:
- Assumptions: bullet list; each bullet includes potential impact if false
- Constraints: bullet list; each bullet includes rationale

Section 6 — Risks & Mitigations
Goal: Identify risks related to personas and use cases and how they are managed.
Content:
- Risk entries as bullets with the following inline fields:
  - id: R-###
  - description: short risk statement
  - impact: Low, Medium, High, Critical
  - likelihood: Low, Medium, High
  - mitigation: short description
  - owner_role: optional short role label

Section 7 — Change Log
Goal: Track meaningful edits for auditability and context.
Representation: reverse-chronological bullet list.
Entry format:
- [YYYY-MM-DD] <short description of change> — <author or team>

Formatting Rules
- Use only the specified headings and field names; do not invent new top-level sections
- Lists are hyphen bullets or ordered lists as specified
- Tables use standard Markdown syntax with a header row
- Values for enumerations must match exactly one of the allowed literals
- Keep examples placeholder-like and remove them in the final maintained document

Quality Rules (Document Must Satisfy)
- Completeness:
  - At least one persona and one use case
  - Each use case has one primary_actor that maps to an existing persona
  - Section 4 contains at least one mapping row per defined use case
- Consistency:
  - Every persona referenced in Use Cases and Mapping exists in Section 2
  - Every use case referenced in Mapping exists in Section 3
  - Enumerated fields use only allowed literals
- Clarity:
  - Sentences are concise and unambiguous
  - No contradictory statements across sections
- Testability:
  - Preconditions and postconditions are concrete and checkable
  - Main flow steps are sequenced and outcome-oriented

Edit & Operation Rules
- Editing order recommendation:
  1) Draft personas
  2) Draft use cases
  3) Complete persona–use case mapping
  4) Fill assumptions, constraints, risks
- When adding a new use case:
  - Create a complete use case block in Section 3
  - Update Section 4 with at least one Primary role mapping
- When modifying a persona_id or uc_id:
  - Update all references across Sections 2, 3, and 4
  - Ensure uniqueness and validation rules remain satisfied
- Deletions:
  - If removing a persona, first remove its mapping rows and secondary_actor mentions
  - If removing a use case, first remove mapping rows; ensure downstream documents that depend on it are updated
- Change Log:
  - Add an entry for any structural or semantic change, not for trivial wording fixes

Validation Checklist (for humans or automation)
- Summary present and informative
- All personas satisfy required fields and regex rules
- All use cases satisfy required fields and regex rules
- Mapping table present and passes uniqueness and existence checks
- Assumptions & Constraints present with impact/rationale
- Risks have id, impact, likelihood, and mitigation
- Enumerations use allowed values only
- Change Log updated

Enumeration Reference (exact allowed values)
- interaction_frequency (persona): Rare, Occasional, Regular, Heavy
- frequency (use case & mapping): Ad-hoc, Daily, Weekly, Monthly, Quarterly, Yearly
- criticality (use case): Low, Medium, High, Critical
- role (mapping): Primary, Secondary, Reviewer, Approver, Observer
- impact (risk): Low, Medium, High, Critical
- likelihood (risk): Low, Medium, High

Naming Rules
- persona_id: uppercase letters, digits, and underscores only; must be stable across document updates
- uc_id: UC-### with zero-padded integer starting from 001; never reuse retired IDs

Maintenance Guidance
- Prefer incremental edits over large rewrites to preserve ID stability
- If a persona splits or merges, record the change in the Change Log and update mappings atomically
- Review this document at each significant release or scope change