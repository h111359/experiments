# DATA-08 — Data archiving & deletion policy

## Overview

- **Purpose:** Define how AIB repo artifacts are retained, archived, and deleted in an auditable way.
- **Scope:** `.aib_brain`, `.aib_memory`, `logs/`, scripts.
- **Regulatory Context:**
	- None explicitly identified; treat artifacts as Internal engineering documentation.
- **Policy Statement:** Retain via source control history; deletions must be intentional, reviewed, and auditable.

## Data Classification & Retention

| Level | Description | Examples |
| --- | --- | --- |
| Public | Safe for public distribution | README excerpts |
| Internal | Engineering docs and workflows | `.aib_memory/*`, `.aib_brain/*` |
| Confidential | Not expected in this repo | N/A |
| Restricted | Not expected in this repo | N/A |

| Data Category | Classification | Authoritative Source | Retention Period | Legal/Business Rationale |
| --- | --- | --- | --- | --- |
| AIB brain assets | Internal | git history | until decommission | Maintain framework integrity. |
| AIB memory artifacts | Internal | git history | until decommission | Preserve request/doc traceability. |
| Release logs | Internal | git history | until decommission | Audit trail across releases. |

**Overrides**
- ID: OV-001 — Rationale: remove accidental secrets if ever committed — Approved by: Repository Maintainers

**Time Reference:** retention starts from commit date.

## Archiving Policy

**Archiving Criteria**
- Snapshot releases via tags and preserve version logs.

| Target Store | Storage Class/Tier | Region/Residency | Encryption | Expected Cost Profile |
| --- | --- | --- | --- | --- |
| Git remote | Provider-managed | global | provider-managed | low/managed |

**Format & Packaging:** Markdown and source files.
**Indexing & Discoverability:** request ids, version headings, Git history.
**Access Controls:** repository permissions.
**Performance & Cost Considerations:** retrieval via git clone/fetch.

## Secure Deletion Policy

**Deletion Criteria:** end-of-life, incident response, or repo decommission.

**Deletion Methods**
- Object Storage: Not applicable – rationale: no object store provisioned.
- Relational/Columnar DB: Not applicable – rationale: no DB provisioned.
- File Systems: delete via reviewed PR; avoid history rewrite unless explicitly approved.
- Backups/Replicas: follow provider guidance for sensitive removals.

**Cryptographic Controls:** provider-managed.
**Propagation:** handle forks/mirrors per org policy.

## Data Subject Rights (DSR) Handling

Repository is not intended to store personal data. If discovered, treat as incident and remove with audit.

## Evidence, Audit & Traceability

- Audit trails: PR history and commit history.
- Evidence artifacts: CI logs, release logs.

## Operational Controls & Automation

- CI validates marker state and generates logs.

## Risk Management

- Risk: accidental secret commit; mitigation: PR review and scanning.

## Change Management

- Update on new storage backends or policy changes.

## Appendices

- References (Internal Only): `.aib_memory/references.md`, `logs/versions_log.md`.
