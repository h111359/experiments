Purpose
Define a single-file Architecture Decision Records (ADR) repository convention that enables compact, reviewable, and automation-friendly capture of architectural decisions for the product. The convention ensures consistent naming, structure, lifecycle, and editing rules so both AI and humans can efficiently read, write, and verify ADRs.

## File Naming
- **File name:** `ARCH-04.md`
- **One file only** for the complete glossary (no per-term files).
- **Character set:** UTF-8, Unix line endings (`\n`).

Scope
This convention applies to the documentation artifact for requirement ARCH-04 — ADRs repository. It governs:
- Where the ADR repository file lives and how it is named.
- How the repository file is structured (sections, tables, entries).
- How ADRs are created, updated, superseded, and referenced.
- How automation (AIB tools/prompts) reads and writes ADR content.

Canonical Location & File Name
- Single-file repository: exactly one file hosts all ADRs (no per-ADR files in subfolders).
- If the project relocates documentation, references.md MUST point to the new path; the structure in this convention remains unchanged.

Design Principles
- Single source of truth: one file contains the ADR index and all decisions.
- Append-preferred: new decisions are appended; changes to past ADRs are limited to corrections (typos/format) or status transitions with explicit rationale.
- Deterministic parsing: headings, tables, and tokens follow strict patterns to support automation.
- Human-verifiable: short, readable sections with clear status and rationale.
- Traceable: each ADR has a stable ID; supersessions are recorded explicitly.

Document Structure (strict)
The repository file MUST follow the section order below and use the exact section headings:

1. Repository Overview
2. Architectural Principles
3. ADR Index
4. ADR Entries

Section Specifications
1) Repository Overview
   - Brief description of what ADRs represent for this product and how to use them (2–6 sentences).
   - Include a one-line reference to this convention file name so humans know the governing rules (text only; no link required).

2) Architectural Principles
   - Bullet list of core engineering principles guiding decisions (e.g., security-by-design, scalability, resilience, cost-effectiveness, observability, extensibility, data sovereignty).
   - Keep each principle to one line. Principles here are stable and rarely changed.

3) ADR Index
   - A register table listing all ADRs with the following columns in this exact order:
     | adr_id | title | status | decided_at | supersedes | superseded_by |
   - Column rules:
     - adr_id: "ADR-0001", "ADR-0002", … zero-padded to 4 digits.
     - title: short human-readable name (≤ 100 chars).
     - status: one of Proposed | Accepted | Rejected | Superseded | Deprecated.
     - decided_at: local date in YYYY-MM-DD when status first became Accepted/Rejected/Deprecated (empty for Proposed).
     - supersedes: adr_id this ADR replaces (or "-" if none).
     - superseded_by: adr_id that supersedes this ADR (or "-" if none).
   - Rows are ordered by adr_id ascending and MUST be unique on adr_id.
   - Exactly one row per ADR entry in Section "ADR Entries".

4) ADR Entries
   - Each ADR entry is a sub-section with the exact heading format:
     #### ADR-#### — <Title>
   - For each ADR, include the following fixed subheadings in the order shown:
     - Context
     - Decision
     - Status
     - Consequences
     - Alternatives Considered
     - References
     - Audit Trail
   - Content rules for subheadings:
     - Context: concise background and drivers.
     - Decision: the chosen option; keep it normative and explicit.
     - Status: a single line matching the status in the index; if Superseded, name the successor.
     - Consequences: positive/negative outcomes; include operational and cost impact when relevant.
     - Alternatives Considered: bullet list; one line per alternative with brief rationale.
     - References: bullet list of internal document IDs or file paths; avoid external links.
     - Audit Trail: bullet list of dated notes (YYYY-MM-DD — <note>), including transitions (e.g., Proposed→Accepted) and material edits.

Lifecycle & State Transitions (normative)
- Proposed → Accepted: upon approval by designated architecture authority (process external to this file).
- Proposed → Rejected: if evaluated and declined.
- Accepted → Superseded: when a new ADR replaces it.
- Accepted → Deprecated: when no longer recommended but still in use somewhere.
- Rejected/Deprecated/Superseded are terminal for decision intent (content remains for history).
- Supersession rules:
  - The newer ADR MUST set "supersedes" in the index to the prior adr_id.
  - The prior ADR MUST set "superseded_by" to the new adr_id and set Status to Superseded.
  - The "Audit Trail" of both ADRs MUST include a dated note of the transition.

ID & Naming Rules (normative)
- adr_id generation: strictly increasing numeric IDs with zero-padding to 4 digits (ADR-0001, ADR-0002, …).
- Exactly one ADR entry per adr_id.
- Title must be unique; if a duplicate topic exists, either merge or create a new ADR that supersedes the prior one.

Editing & Automation Rules (normative)
- File is single-source and MUST remain a valid Markdown document with the structure defined above.
- AIB tools MAY:
  - Append new ADR index rows and new ADR entry sections.
  - Update "status", "decided_at", "supersedes", "superseded_by" fields in the index during lifecycle changes.
  - Insert corresponding "Audit Trail" lines in ADR entries.
  - Correct typos/formatting without changing meaning (must add a dated Audit Trail note).
- AIB tools MUST NOT:
  - Split ADRs into multiple files or create subfolders for ADRs.
  - Reorder sections outside the prescribed structure.
  - Remove historical ADR entries or delete Audit Trail notes.
- Human edits SHOULD follow the same rules; any manual change SHOULD add an "Audit Trail" entry.

Quality Bar & Review Hints
- Keep each ADR Decision section ≤ ~200 words; move extended details to References.
- Prefer precise, testable statements (e.g., "MUST encrypt at rest with KMS-managed keys").
- Capture non-functional impacts (security, performance, cost, operability) under Consequences.

Minimal Working Skeleton (copy/paste)
Below is a seed structure for a new repository file conforming to this convention. Use it when initializing ARCH-04.md.

---
### Repository Overview
This file records Architecture Decision Records (ADRs) for the product. ADRs capture the context, decision, and consequences of architectural choices. They are maintained as a single, append-preferred ledger to preserve history and enable automation. 

### Architectural Principles
- Security-by-design
- Scalability
- Resilience
- Cost-effectiveness
- Observability
- Extensibility
- Data sovereignty

### ADR Index
| adr_id  | title                                    | status    | decided_at | supersedes | superseded_by |
|---------|-------------------------------------------|-----------|------------|------------|---------------|
| ADR-0001 | Example: Choose cloud storage tiering    | Proposed  |            | -          | -             |

### ADR Entries

#### ADR-0001 — Example: Choose cloud storage tiering
Context
- Data volumes fluctuate by season; need predictable costs and performance across hot/warm/cold data.

Decision
- Adopt a three-tier storage strategy (hot/warm/cold) with lifecycle policies transferring objects based on access patterns; enforce encryption at rest and at transit boundaries.

Status
- Proposed

Consequences
- (+) Cost optimization via lifecycle transitions.
- (+) Predictable performance for interactive workloads in hot tier.
- (–) Operational complexity for lifecycle policies and rehydration.

Alternatives Considered
- Single premium tier for all data — simpler, higher cost.
- Two-tier model (hot/cold) — lower complexity, less cost granularity.

References
- ARCH-01 High-level architecture
- DATA-04 Data storage strategy & patterns

Audit Trail
- 2026-03-08 — Created ADR as Proposed.

---

Consistency & Validation (automated checks)
- Index and Entries MUST be in sync (same adr_id set and statuses).
- adr_id formatting and uniqueness MUST pass validation.
- Status transitions MUST follow lifecycle rules and add Audit Trail notes.
- "References" values SHOULD point to internal documentation IDs or paths managed via references.md.
- Linting: headings, tables, and tokens are case-sensitive as specified.

Operating Instructions
- Create a new ADR:
  1) Allocate next adr_id.
  2) Append an Index row with status=Proposed.
  3) Append a new ADR entry with the skeleton subsections.
- Accept/Reject an ADR:
  1) Update status in the Index and "Status" subsection.
  2) Set decided_at (YYYY-MM-DD).
  3) Add an Audit Trail note.
- Supersede an ADR:
  1) Create a new ADR with the new decision.
  2) Set supersedes (new ADR) and superseded_by (old ADR).
  3) Update both "Status" subsections and Audit Trail notes.

Change Control
- Historical correctness outweighs stylistic consistency; never delete history.
- Substantial edits MUST be explained in Audit Trail with date and short rationale.
- Renaming titles is allowed; update Index and the ADR entry heading accordingly.
