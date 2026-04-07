Purpose
-------
Define a clear, minimal, and verifiable convention for documenting the **Secrets management & rotation policy** for a product. The convention ensures the file is AI-friendly for generation/updates and human-friendly for validation and audits.

Scope
-----
This convention applies to the single document that specifies how secrets are **stored, accessed, injected, rotated, expired, audited, and evidenced** across environments and systems used by the product.

Audience & Roles
----------------
- **Security Owner** — accountable for policy completeness and compliance checks.
- **Engineering Lead** — responsible for technical feasibility and implementation mapping.
- **Operations Lead** — responsible for run-time enforcement and evidence capture.
- **Auditor/Reviewer** — validates adherence and signs off on reviews.

File Name
---------
- **Exact file name:** `SEC-03.md`
- **Location:** As defined by the documentation register (outside of this convention). Do not include paths here.

Document Structure (Headings & Order)
-------------------------------------
Use the exact headings below and keep the order. Sub-bullets may be added when needed, but headings must remain verbatim.

1. **Overview**
   - Short summary of secrets management approach (3–5 sentences).
   - In-scope environments (e.g., dev, test, stage, prod).

2. **Secrets Inventory & Ownership**
   - Table listing secrets categories and examples.
   - For each category: owner role, usage scope, environment applicability.

3. **Storage & Tooling**
   - Chosen secrets management solution(s) and storage mechanisms.
   - Namespace/segmentation strategy (per app, per env).
   - Key management approach (e.g., KMS/HSM responsibility split).

4. **Access Control Model**
   - Role-to-secret access mapping (principle of least privilege).
   - Human vs. machine identities; MFA requirements for human access.
   - Review cadence and approval workflow.

5. **Rotation & Expiration Policy**
   - Rotation frequency per secret category.
   - Expiry rules and conditions for immediate rotation (e.g., suspected exposure).
   - Coordinated rollout strategy to avoid downtime.

6. **Secret Injection & Consumption**
   - Injection mechanisms (runtime, CI/CD pipeline, sidecar/agent).
   - Transport security and format (env vars, files, mounts, parameters).
   - Redaction rules for logs and error messages.

7. **Evidence & Auditability**
   - Required evidence artifacts (rotation logs, approvals, automated checks).
   - Retention duration for evidence; audit trail expectations.
   - How to retrieve evidence on demand.

8. **Monitoring & Alerting**
   - Signals that indicate misuse or policy drift (e.g., access anomalies).
   - Alert thresholds, channels, and escalation paths.

9. **Emergency Response**
   - Runbook for suspected secret exposure.
   - Steps: containment, rotation blast radius, verification, post-incident review.

10. **Testing & Validation**
    - Non-prod validation of rotation procedures.
    - Periodic drills and pass/fail criteria.

11. **Change Management**
    - When policy updates are required (new systems, scope change).
    - Approval and communication process.

Normative Content Requirements
------------------------------
The document **MUST** address the following items in a clear, testable way:

- **Secrets management solution & storage mechanisms** (names, purpose, where secrets live).
- **Types of secrets managed** (e.g., API keys, DB credentials, tokens, certificates), grouped into categories with examples.
- **Access control model for secrets** (roles, permissions, inheritance rules, least-privilege guardrails, MFA for humans, service principals for workloads).
- **Rotation & expiration policies** (frequency by category, triggers for forced rotation, key/cert renewal timelines).
- **Injection mechanism** (runtime vs. pipeline; secure distribution channel; no plaintext storage; redaction rules).
- **Audit evidence requirements** (what artifacts exist, how they are produced, where they are stored, retention, retrieval).

Authoring & Formatting Rules
----------------------------
- Language: English, concise, and unambiguous.
- Use Markdown only. Prefer tables for registers and matrices.
- Keep paragraphs short (≤5 lines). Use lists where possible.
- Do **not** include external hyperlinks or footnotes in this document.
- Use present tense and normative keywords (MUST/SHOULD/MAY) when defining rules.

Validation Checklist (Copy/Paste)
---------------------------------
Use this checklist for creation and reviews. Every item MUST be satisfied before approval:

- [ ] **Overview** precisely describes solution, env scope, and rationale.
- [ ] **Inventory** table lists all secret categories with owner roles and env scope.
- [ ] **Storage & Tooling** specifies the exact secret store(s) and namespaces.
- [ ] **Access Model** details role-based access, least-privilege, and MFA rules.
- [ ] **Rotation Policy** defines frequency per category and emergency triggers.
- [ ] **Injection** clearly states mechanisms, no plaintext, and redaction rules.
- [ ] **Evidence** defines artifacts, retention, and retrieval steps.
- [ ] **Monitoring** defines signals, thresholds, and escalation.
- [ ] **Emergency Response** runbook exists and is actionable.
- [ ] **Testing** covers rotation drills with pass/fail criteria.
- [ ] **Change Management** defines update and approval flow.
- [ ] Document adheres to headings/order and formatting rules.

Tables — Prescribed Schemas
---------------------------
**Secrets Inventory & Ownership**

| secret_category | examples                         | owner_role       | environments            | notes                |
|-----------------|----------------------------------|------------------|-------------------------|----------------------|
| api_keys        | serviceA_public, maps_api        | Engineering Lead | dev,test,stage,prod     | rotate every 90 days |
| db_credentials  | app_db_rw, app_db_ro             | Engineering Lead | dev,test,stage,prod     | rotate every 60 days |
| tokens          | oauth_client_secret, pat_generic | Security Owner   | dev,test,stage,prod     | rotate every 30 days |
| certificates    | tls_app_cert, mTLS_client_cert   | Security Owner   | stage,prod              | renew 30 days before |

**Access Control Matrix (example)**

| role              | human/machine | secret_category | permission     | constraints                         |
|-------------------|---------------|-----------------|----------------|-------------------------------------|
| Ops Engineer      | human         | api_keys        | retrieve       | MFA required; ticketed approval     |
| CI/CD Runner      | machine       | tokens          | inject-only    | no read at rest; ephemeral scopes   |
| Service Identity  | machine       | db_credentials  | retrieve/use   | namespace-bound; least privilege    |

Evidence & Audit Artifacts (Required)
-------------------------------------
List each artifact with how it is produced and stored.

- **Rotation log** — automated record containing: secret_category, scope, initiator (human/machine), timestamp, outcome, evidence pointer.
- **Approval record** — request/ticket ID, approver identity, timestamp, change summary.
- **Access review** — periodic report of access lists vs. policy; exceptions and remediations.
- **Drill report** — test execution details, pass/fail results, remediation actions.

Rotation & Expiration Policy (Template)
---------------------------------------
Define policy per category using this format:

- **Category:** `<name>`
- **Frequency:** `<e.g., every 60 days>`
- **Max Age/Expiry:** `<e.g., 90 days>`
- **Early Rotation Triggers:** `<compromise suspected, role change, vendor request>`
- **Coordination Steps:** `<announce window, stage rollout, verify, promote>`
- **Post-Rotation Validation:** `<connectivity checks, error-rate monitors, dashboard OK>`

Monitoring & Alerting (Minimum Signals)
---------------------------------------
- Unexpected read attempts or spikes on secret categories.
- Access outside allowed time windows or from unapproved identities.
- Secrets used from non-permitted environments.
- Secrets nearing expiry without scheduled rotation.

Emergency Response (Minimum Steps)
----------------------------------
1. Contain: revoke or disable affected credentials/tokens.
2. Rotate: generate and distribute new secret versions.
3. Validate: confirm system health and absence of leakage.
4. Audit: capture timeline, actions, and evidence.
5. Improve: document root causes and preventive measures.

Change Management
-----------------
- Update this document when adding/removing systems, changing stores, or modifying rotation cadences.
- All changes require review by **Security Owner** and **Engineering Lead**.
- Communicate downstream impacts to delivery and operations teams.

AI Editing Rules
----------------
- AI tools MAY add, update, or reorder list items/tables **only within** the defined headings.
- AI tools MUST NOT remove required headings.
- AI tools MUST keep tables aligned to the prescribed schemas.
- On missing mandatory fields, AI tools MUST add placeholder rows with `TBD` and flag them.

Appendix: Terms
---------------
- **Secret** — any credential or confidential value granting access or trust.
- **Rotation** — replacement of a secret with a new version and invalidation of the old one.
- **Injection** — secure provisioning of secrets to workloads at runtime or during pipelines.