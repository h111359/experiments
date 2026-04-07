### Repository Overview

This file records Architecture Decision Records (ADRs) for AIB in a single append-preferred ledger. Governing rules are in `.aib_brain/conventions/arch-04-convention.md`.

### Architectural Principles

- Determinism for state resolution and file generation.
- Safety via explicit edit scope (references register).
- Replaceable brain assets with workspace-specific memory.
- Vendor/model agnostic prompt design.
- Fail-closed on missing conventions.

### ADR Index

| adr_id | title | status | decided_at | supersedes | superseded_by |
| --- | --- | --- | --- | --- | --- |
| ADR-0001 | Single SemVer marker file for version | Proposed |  | - | - |
| ADR-0002 | Fail-closed convention enforcement | Proposed |  | - | - |

### ADR Entries

#### ADR-0001 — Single SemVer marker file for version

Context
The framework needs deterministic version detection without package managers.

Decision
Represent active version as exactly one empty file in `.aib_brain/` named `vMAJOR.MINOR.PATCH`.

Status
- Proposed

Consequences
- (+) Tool-agnostic and easy to validate.
- (–) Requires strict enforcement to avoid multiple markers.

Alternatives Considered
- Version JSON file — higher merge conflict risk.
- Git tags only — less discoverable in workspace-only contexts.

References
- Development and deployment specification

Audit Trail
- 2026-03-22 — Created ADR as Proposed.

#### ADR-0002 — Fail-closed convention enforcement

Context
Missing mapping or convention files can cause malformed docs or drift.

Decision
If mapping row or convention file cannot be resolved deterministically, do not edit the product-doc and record a blocker.

Status
- Proposed

Consequences
- (+) Prevents accidental corruption.
- (–) Can block until conventions repaired.

Alternatives Considered
- Best-effort edits with warnings — too risky.

References
- product-documentation-convention mapping

Audit Trail
- 2026-03-22 — Created ADR as Proposed.
