## Purpose
Define a strict, AI-friendly and human-verifiable convention for the **Data archiving & deletion policy** document that standardizes how to specify criteria, processes, evidence, and controls for archiving and securely deleting data at end-of-life.

## Scope
This convention governs the single product documentation file that satisfies requirement **DATA-08 — Data archiving & deletion policy**.
It applies to the full lifecycle of that file: creation, editing, validation, and ongoing maintenance.

## Target File
- **File Name:** DATA-08.md
- **Uniqueness:** Exactly one `DATA-08.md` file per product.
- **Edit policy:** Human-editable; AI MAY propose edits when explicitly requested by the user or automation, respecting repository guardrails.

## Audience
- Data Platform Owners, Security & Privacy Officers, Product Engineering, Operations, and Audit.

## Normative Language
The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in BCP 14 (RFC 2119/8174).

## Document Structure (Required Sections & Fields)
The document MUST contain the sections below in the exact order. Each section lists its required fields and formatting rules.

### 1. Overview
- **Purpose:** (2–5 sentences) Why archiving/deletion are needed for this product.
- **Scope:** Systems, data domains, and environments covered.
- **Regulatory Context:** Short bullets listing applicable regulations/standards (e.g., GDPR, CCPA, SOX) without external links.
- **Policy Statement:** One paragraph stating the product’s commitment to archival and secure deletion.

### 2. Data Classification & Retention
- **Classification Scheme:** Table of classification levels used by the product (e.g., Public, Internal, Confidential, Restricted).
- **Default Retention Schedule:** Table mapping **Data Category** → **Classification** → **Authoritative Source** → **Retention Period** → **Legal/Business Rationale**.
- **Overrides:** List of exceptions with justification and approval owner.
- **Time Reference:** Define whether retention starts from *ingestion*, *last access*, *business event*, or *record close*.

### 3. Archiving Policy
- **Archiving Criteria:** Bullet list of triggers (e.g., inactivity threshold, state changes, lifecycle events).
- **Archival Destination(s):** Table with **Target Store**, **Storage Class/Tier**, **Region/Residency Constraints**, **Encryption**, **Expected Cost Profile**.
- **Format & Packaging:** Allowed serialization (e.g., Parquet, CSV), compression, and manifest requirements.
- **Indexing & Discoverability:** How archived data is cataloged and located (metadata, tags, catalog entries).
- **Access Controls:** Roles permitted to access archives; read patterns; break-glass policy (if applicable).
- **Performance & Cost Considerations:** Guidance and thresholds (e.g., retrieval latency expectations, cold vs. deep-cold tiers).

### 4. Secure Deletion Policy
- **Deletion Criteria:** Conditions under which data MUST be deleted (end of retention, subject requests, contractual end).
- **Deletion Methods:** Approved methods by storage type:
  - **Object Storage:** logical purge + lifecycle rules; ensure all versions and replicas are covered.
  - **Relational/Columnar DB:** delete statements + vacuum/compaction; index rebuild where applicable.
  - **File Systems:** secure wipe strategy compatible with the platform (logical delete + underlying block retirement where supported).
  - **Backups/Replicas:** coordinated deletion or cryptographic erasure via key retirement.
- **Cryptographic Controls:** How encryption keys are managed; process for crypto-erasure when physical overwrite isn’t feasible.
- **Propagation:** How deletions are propagated to downstream systems, caches, derived datasets, and analytics extracts.

### 5. Data Subject Rights (DSR) Handling
- **Request Types:** Access, Rectification, Deletion (Right to be Forgotten), Restriction, Portability.
- **Verification & Logging:** Identity verification steps; request logging fields (request id, identity proof method, timestamps).
- **Fulfillment Workflow:** SLA targets, responsible roles, evidence artifacts, and communication templates.
- **Scope Resolution:** Rules to identify all locations (raw, curated, aggregates, backups) where the subject’s data might exist.

### 6. Evidence, Audit & Traceability
- **Audit Trails:** What MUST be logged for archiving/deletion (who, what, when, where, result, record counts).
- **Evidence Artifacts:** Required artifacts (job run reports, control dashboards screenshots, signed approvals).
- **Tamper Resistance:** Storage requirements for logs/evidence (append-only, retention).
- **Sampling & Periodic Reviews:** Cadence and method for independent checks.

### 7. Operational Controls & Automation
- **Schedulers & Orchestrators:** Named jobs/pipelines that enforce archiving/deletion with frequency and ownership.
- **Preconditions & Safety Checks:** Dry-run counts, protected datasets list, approval steps for bulk deletions.
- **Failure Handling:** Retries, back-off, and escalation paths; quarantine procedures for partial failures.
- **Monitoring & Alerting:** Metrics and thresholds (e.g., overdue items, job success rate, deletion backlog size).

### 8. Risk Management
- **Risks List:** At minimum: over-retention, under-retention (premature deletion), orphaned replicas, compliance gaps, cross-region copies, cost spikes.
- **Mitigations:** Concrete measures for each risk.
- **Residual Risk Acceptance:** When applicable, responsible owner and review cadence.

### 9. Change Management
- **Triggers for Update:** New regulation, storage change, region move, schema evolution affecting identification of data subjects.
- **Approval Workflow:** Required approvers (roles) and evidence.
- **Backward Compatibility:** How existing archives/deletions are handled when policies change.

### 10. Appendices
- **Glossary:** Product-specific terms.
- **References (Internal Only):** Filenames/paths to internal documents or registers in the repo (no external links).
- **Templates:** Inline minimal templates for tables (retention schedule, destinations, logs).

## Formatting Rules
- **Language:** English.
- **Style:** Short, declarative sentences; bullets and tables preferred over long prose.
- **Tables:** Use GitHub-flavored Markdown; include headers; no merged cells.
- **Identifiers:** Use stable names for jobs/pipelines; include version or hash where applicable.
- **No External Links:** Reference internal paths only.

## Quality Gates (Validation Rules)
Automation MUST validate:
1. **Section presence & order** exactly as defined above.
2. **Retention Schedule Table** has at least one row per **Data Category** in scope.
3. **Archival Destinations Table** specifies encryption, region, and storage class for each destination.
4. **Deletion Methods** enumerate all in-scope storage types used by the product.
5. **DSR Workflow** defines SLA and identity verification steps.
6. **Audit Trails** specify required fields and storage requirements.
7. **Monitoring Metrics** include at least: overdue items, success rate, backlog size, last-run timestamp.
8. **No External URLs** present in the file.

## Naming & File Rules
- **Document Title (first H1):** `# DATA-08 — Data archiving & deletion policy`
- **Headings:** Use `##` for sections and `###` for sub-sections exactly as in this convention.
- **File Name:** `DATA-08.md` (uppercase prefix) at the target path defined above.

## Editing Rules
- **Human Authority:** Changes to retention, DSR process, or deletion methods MUST be reviewed by Security/Privacy roles before merge.
- **AI Assistance:** AI MAY refactor formatting, expand tables, and add clarifying text, but MUST NOT relax controls or SLAs without explicit human instruction.
- **Changelogs:** Summarize material changes at the top under an **Unreleased Changes** note (keep concise; no dates required by this convention).

## Minimal Seed Template (Copy-Paste)
Below is a minimal, valid skeleton the tools SHOULD seed:

# DATA-08 — Data archiving & deletion policy

## Overview
- **Purpose:** …
- **Scope:** …
- **Regulatory Context:** - …
- **Policy Statement:** …

## Data Classification & Retention
**Classification Scheme**

| Level | Description | Examples |
|---|---|---|
| Public |  |  |
| Internal |  |  |
| Confidential |  |  |
| Restricted |  |  |

**Default Retention Schedule**

| Data Category | Classification | Authoritative Source | Retention Period | Legal/Business Rationale |
|---|---|---|---|---|
|  |  |  |  |  |

**Overrides**
- ID: … — Rationale: … — Approved by: …

**Time Reference:** …

## Archiving Policy
**Archiving Criteria**
- …

**Archival Destinations**

| Target Store | Storage Class/Tier | Region/Residency | Encryption | Expected Cost Profile |
|---|---|---|---|---|
|  |  |  |  |  |

**Format & Packaging:** …
**Indexing & Discoverability:** …
**Access Controls:** …
**Performance & Cost Considerations:** …

## Secure Deletion Policy
**Deletion Criteria:** …
**Deletion Methods**
- Object Storage: …
- Relational/Columnar DB: …
- File Systems: …
- Backups/Replicas: …

**Cryptographic Controls:** …
**Propagation:** …

## Data Subject Rights (DSR) Handling
**Request Types:** …
**Verification & Logging:** …
**Fulfillment Workflow:** …
**Scope Resolution:** …

## Evidence, Audit & Traceability
**Audit Trails — Required Fields:** …
**Evidence Artifacts:** …
**Tamper Resistance:** …
**Sampling & Periodic Reviews:** …

## Operational Controls & Automation
**Schedulers & Orchestrators:** …
**Preconditions & Safety Checks:** …
**Failure Handling:** …
**Monitoring & Alerting — Metrics:** Overdue items, Success rate, Backlog size, Last-run timestamp.

## Risk Management
**Risks & Mitigations:** …
**Residual Risk Acceptance:** …

## Change Management
**Triggers for Update:** …
**Approval Workflow:** …
**Backward Compatibility:** …

## Appendices
**Glossary:** …
**References (Internal Only):** …
**Templates:** …