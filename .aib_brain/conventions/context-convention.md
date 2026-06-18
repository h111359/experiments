# Convention: context.md
## Purpose
Defines required structure, statement syntax, formatting rules, quality gates for .aib_memory/context.md; single structural authority for context.md; aib-refresh-context.md MUST reference this convention. Product-agnostic; MUST NOT assume domain taxonomy/folder structure.
## Applicability
Applies to every .aib_memory/context.md in every AIB workspace, any domain/industry/stack.
## Normative Language
Keywords MUST, MUST NOT, SHALL, SHOULD, MAY, OPTIONAL per BCP 14 (RFC 2119 + RFC 8174).
## Document Identity
- Canonical path: .aib_memory/context.md
- Encoding: UTF-8
- Format: Markdown only; NO HTML tags; NO images; NO external hyperlinks.
- Authoring: aib-refresh-context.md full refresh; edit-context.py targeted statement CRUD; human edits possible but not expected.
- Replacement semantics: refresh = full-file replace; edit-context.py = line-level insert/delete.
## Section Structure
### Mandatory Order
1. ## 1. Product Identity
2. One H2 area per active area name: ## <AREA> (full name, example Functionality, Project overview); include only areas with >=1 statement.
3. ## Files
### Optional Aliases Block
May appear before ## 1. Product Identity.
Format: Aliases: SHORT=Long Name, SHORT2=Another Long Name
Rule: if defined, use short aliases consistently for repeated long names.
### Empty Areas
Area with 0 statements: omit section; NO empty headings; NO stubs.
### Wrapper Headings
MUST NOT include ## 2. Statements or ## 3. Workspace File Inventory; areas appear directly as H2.
## Section 1 - Product Identity
Goal: establish product name, purpose, audience.
MUST include: product name; one-paragraph purpose; primary actors/users.
SHOULD include: key business outcome; scope boundaries (what product does NOT cover).
MUST NOT include: impl details (move to TD/TS); marketing/aspirational copy; version/status metadata (Git is source of truth).
Format: atomic statements when possible, prose allowed when needed; no bold/italic/backticks.
## Area Sections (H2)
### Valid Area Names (22)
Project overview; Change Management; Domain; Concepts; Best Practices; Functionality; Technical Design; Technology Stack; Networking and Connectivity; Data structures; Data flow; Processes; Analytics; User Interface; Security; Performance; Operations; Development; Deployment; Durability; Observability; Documentation.
### Atomic Statement Format
Every statement = single Markdown bullet line: - <TYPE>: <text>
TYPE = single-letter statement type; text = concise telegraphic phrasing.
Example:
- R: User auth uses JWT tokens with 1h expiry.
- D: Flat Markdown files used instead of db for max portability.
- N: Request lifecycle: create -> analyze -> plan -> implement -> close.
### Statement Types
N Definition; R Requirement; C Constraint; E Reference; L Relationship; U Rule; A Assumption; D Decision; I Information.
Open/unresolved questions MUST NOT be in context.md; store in input.md.
### Statement Addressing
Address = type letter + text content. Tooling uses text line matching for CRUD. Statement text MUST be unique within area for unambiguous addressing.
### Uniqueness Invariant
Within each area, statement text uniqueness is REQUIRED (case-insensitive). Duplicate text in same area PROHIBITED. edit-context.py enforces on insert.
### Telegraphic Language
Use concise telegraphic phrasing; drop unnecessary articles/helper verbs. Use standard abbreviations: req, res, auth, db, env, config, err, msg, btn.
### Granularity
SHOULD: 1 statement = 1 fact. Exception: tightly-coupled properties of one named entity MAY be grouped in inline list.
### Completeness
Statements MUST let competent dev reconstruct full workspace context (with Section 1 + Files): what product does, why key decisions exist, how system works.
### Logic Notation
For flow/logic, prefer pseudo-code/operators when shorter: ->, &&, ||, ==, !=.
## Files Section
### Format
Use indented tree, example:
## Files
.aib_memory/
  context.md - product context synthesis
.aib_brain/tools/
  verify-context.py - validates context.md format
scripts/
  release_bookkeeping.py - SemVer bump + log generation
### Inclusion Rules
Include only directories + core architectural files. Ignore tests/config/assets/minor utilities unless they carry critical business logic.
Pattern compression: directory with >=3 similarly named items -> one summary line, example: logs/ - Contains N files matching version_vX.Y.Z_log.md.
## Formatting Rules
1. UTF-8 Markdown only.
2. NO HTML tags.
3. NO images.
4. External refs as plain text only.
5. Heading hierarchy only: H1 # Product Context exactly once; H2 limited to ## 1. Product Identity, ## <AREA>, ## Files; H3 optional sub-areas; H4+ forbidden.
6. Statements MUST NOT use bold/italic/backticks; plain text only.
7. Statement syntax MUST be bullet + type letter + colon + text: - <TYPE>: <text>.
8. Traceability refs plain text, not hyperlinks.
9. NO Markdown tables.
10. Each atomic statement occupies exactly one line (no wraps/continuations).
11. Heading depth MUST NOT exceed H3.
12. NO preamble/version metadata; versioning via Git.
## Pruning Rules
Aggressively remove historical context, old iterations, resolved questions, deprecated features; context.md reflects CURRENT app state only.
## No Negative Space
Do not document standard defaults unless overriding expectation. Record only custom business logic/deviations.
## Quality Gates
Pass iff all true:
1. Starts with # Product Context.
2. Has ## 1. Product Identity.
3. Every H2 except Product Identity/Files is a valid area name from the defined list.
4. Contains >=1 area section.
5. Every present area section has >=1 statement.
6. Every area statement matches - <TYPE>: <text> with valid single-letter type.
7. No duplicate statement text within same area (case-insensitive).
8. No http:// or https:// strings.
9. No HTML tags.
10. No Markdown table syntax.
11. Product Identity section has >=3 substantive lines.
## Relationship to Other Conventions
Governs only .aib_memory/context.md. Does NOT govern .aib_brain framework files. aib-refresh-context.md MUST reference this convention as sole structural authority for context.md.
