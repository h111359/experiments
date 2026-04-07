Purpose
-------
Define a concise, deterministic convention for the **Infrastructure Data Protection** document. The convention ensures consistent authoring and automated validation of content that demonstrates how infrastructure protects data from unauthorized access across environments.

Scope
-----
This convention governs a single markdown file intended to capture infrastructure-level data protection controls, evidences, and decisions. It covers data at rest, data in transit, key management, data minimization/masking, DLP, data residency, and applicable privacy/regulatory alignment for the product or workload.

File Naming
-----------
- **File name:** `SEC-02.md`
- **Format:** UTF-8, Markdown (.md)
- **One file per product/workload.** Do not split content across multiple files.

Document Structure (Mandatory Sections)
---------------------------------------
Each top-level heading listed below is **mandatory** and must appear exactly once, in the order shown.

1) Overview
   - **Objective**: one paragraph explaining the strategy for protecting data handled by the infrastructure.
   - **Protection Scope Matrix (table)**: enumerate protection domains and whether they apply.

     | Domain                         | Applies (Y/N) | Notes (short)              |
     |--------------------------------|---------------|----------------------------|
     | Data at rest                   |               |                            |
     | Data in transit                |               |                            |
     | Key management                 |               |                            |
     | Data masking/anonymization     |               |                            |
     | Data loss prevention (DLP)     |               |                            |
     | Data residency                 |               |                            |
     | Privacy regulations compliance |               |                            |

2) Data at Rest
   - **Encryption Mechanisms**: product technologies/features used (e.g., storage-level encryption, database-native encryption, filesystem encryption).
   - **Cipher & Policy**: algorithm family, key length, rotation policy, default-on enforcement.
   - **Scope & Exceptions**: covered stores (object storage, block, DBs, caches), justified exceptions with compensating controls.
   - **Evidence**: references to configs, policies, or screenshots names (filenames only).

3) Data in Transit
   - **Transport Encryption**: protocols/versions (e.g., TLS), termination points, mTLS usage, minimum protocol/cipher standards.
   - **Ingress/Egress Paths**: user-to-edge, service-to-service, data pipeline channels; include a concise path table.

     | Path                         | Termination Point | AuthN/AuthZ | Min TLS | mTLS (Y/N) | Notes |
     |------------------------------|-------------------|-------------|---------|------------|-------|

   - **Downgrade/Legacy Handling**: policy for non-compliant clients or endpoints.
   - **Evidence**.

4) Key Management
   - **Ownership Model**: who controls keys (platform/key vault/HSM vs application), separation of duties.
   - **Generation & Storage**: KMS/HSM usage, key classes (DEK/KEK), wrap/unwrap process.
   - **Rotation & Expiry**: rotation cadence, automated vs manual triggers, decommission process.
   - **Access Control**: RBAC/ABAC for key usage, audit requirements.
   - **Evidence**.

5) Data Masking & Anonymization
   - **Classification Link**: which data classes are subject to masking/anonymization/pseudonymization.
   - **Techniques**: rule-based masking, tokenization, format-preserving encryption, hashing, generalization.
   - **Execution Points**: ingestion, storage, query, export.
   - **Effectiveness & Re-identification Risk**: brief rationale.
   - **Evidence**.

6) Data Loss Prevention (DLP)
   - **Scope**: channels covered (storage, endpoints, e-mail, data egress).
   - **Controls**: prevent/exfiltrate rules, content inspection, allowed/blocked patterns.
   - **Monitoring & Alerting**: thresholds, notification targets, workflow.
   - **Evidence**.

7) Data Residency & Sovereignty
   - **Locations**: regions/data centers used; pin-to-region policies.
   - **Constraints**: residency restrictions, cross-border transfer conditions.
   - **Backup/DR Residency**: confirm alignment for replicas and backups.
   - **Evidence**.

8) Privacy & Regulatory Alignment
   - **Applicable Regulations**: name the laws/standards in scope (e.g., GDPR, CCPA) and the data classes affected.
   - **Technical Enablers**: how infra controls support lawful bases, data minimization, storage limitation, subject rights enablement.
   - **Evidence**.

9) Control-to-Evidence Traceability (Mandatory Table)
   Provide a many-to-one mapping from each declared control to at least one tangible evidence item.

   | Control Area          | Control ID | Control Summary                          | Evidence Ref(s)                |
   |-----------------------|------------|-------------------------------------------|--------------------------------|
   | Data at rest          | DAR-001    | Storage encryption default-on             | `policy-storage.json`, ...     |
   | Data in transit       | DIT-001    | TLS 1.2+ enforced at all edges            | `ingress-gateway.yaml`, ...    |
   | Key management        | KM-001     | Keys in HSM; rotation 180 days            | `kms-policy.md`, `audit.csv`   |
   | Masking/Anonymization | DM-001     | PII tokenized in analytics zone           | `masking-rules.md`            |
   | DLP                   | DLP-001    | Exfiltration rules on egress gateway      | `egress-policy.yaml`          |
   | Residency             | RES-001    | Single-region storage for subject data    | `region-map.csv`              |
   | Privacy alignment     | PRV-001    | Technical enablers for data subject rights| `dsar-process.md`             |

10) Risks, Exceptions & Compensating Controls
    - **Known Risks**: top N with short impact/likelihood.
    - **Exceptions**: ID, description, owner, review-by date.
    - **Compensating Controls**: mapped to the exception IDs.

11) Operational Processes
    - **Reviews**: cadence for crypto standards review, key rotation audits, TLS baseline updates.
    - **Change Management Hooks**: what triggers re-validation (new region, new data class, new exposure).
    - **Incident Response Link**: where infra/security incident runbooks reside (file names only).

12) Acceptance Criteria
    - All mandatory sections present and non-empty.
    - **At rest** and **in transit** controls explicitly documented with ciphers/protocol minima.
    - Key rotation policy defined with cadence and responsibilities.
    - Masking/anonymization techniques tied to data classes.
    - DLP scope and rules enumerated.
    - Residency statement includes primary and backup/DR posture.
    - Privacy/regulatory mapping present.
    - Control-to-evidence table includes at least one evidence per control area.

Authoring Guidance
------------------
- Prefer short, verifiable statements over prose.
- Use tables for lists of controls, paths, and mappings.
- Evidence must reference **workspace-relative file names** only (no external links).
- If a section **does not apply**, keep the heading and state `Not applicable` with a one-line justification.

Validation Rules (Machine-Checkable)
------------------------------------
- Headings: exact names and order as defined above.
- Required tables:
  - Protection Scope Matrix in **Overview**.
  - Path table in **Data in Transit**.
  - Control-to-Evidence Traceability.
- Evidence items must use valid filename characters and relative paths; do not use URLs.
- At least one control defined for each of the seven domains in the Protection Scope Matrix when “Applies = Y”.

Editorial Conventions
---------------------
- English language.
- Use present tense and active voice.
- Acronyms expanded on first use within the document.
- Do not include document-level metadata blocks (title, version, owner, status, location).

Change Log
----------
Maintain a simple, append-only list at the end of the document.

- `YYYY-MM-DD` – Short change summary.