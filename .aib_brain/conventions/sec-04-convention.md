# Purpose
Define a clear, deterministic convention for creating and maintaining the **Infrastructure Network Security** document that captures how network access is segmented, controlled, and protected across environments.

# Scope
This convention applies to the single documentation file that fulfills the “Infrastructure network security” requirement. It covers file naming, structure, required sections and fields, editing rules, quality checks, and examples. It does not define where the file is stored.

# Normative Language
The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in this document are to be interpreted as described in RFC 2119/RFC 8174.

# File Name
- **MUST** use the exact file name: `SEC-04.md`.

# Audience & Usage
- Primary readers: security architects, platform/network engineers, product architects, operations.
- The document **MUST** be written for quick AI parsing and human verification.
- Keep wording concise, avoid redundancy, and use the required tables and checklists below.

# Document Structure (Top-Level Sections)
The document **MUST** include the following sections in this exact order and with the exact headings:

1. **Summary**
2. **Network Architecture & Segmentation**
3. **Ingress/Egress Controls**
4. **Public vs Private Exposure**
5. **Network-Level Encryption**
6. **Monitoring & Detection**
7. **Change Management**
8. **Exceptions & Compensating Controls**
9. **Verification Checklist**
10. **Appendix: Diagrams & References**

---

## 1. Summary
**Purpose:** One short paragraph (max 120 words) describing the network security posture.

**Required fields (table):**

| Field | Description |
|---|---|
| scope_summary | One sentence stating which environments and components are covered. |
| last_reviewed | Local date in `YYYY-MM-DD`. |
| reviewers | Roles or teams who reviewed the last version. |

Validation:
- `last_reviewed` **MUST** be a valid date.
- `scope_summary` **MUST** be non-empty.

---

## 2. Network Architecture & Segmentation
**Intent:** Describe VPC/VNet layout, subnets, and trust boundaries.

**Required artifacts:**
- **Text overview:** 2–5 short paragraphs explaining zones and boundaries.
- **Table – Segmentation Map (REQUIRED):**

| Segment_ID | Segment_Name | Zone/Trust_Level | Purpose | Allowed_EastWest | Notes |
|---|---|---|---|---|---|
| SEG-001 | example-segment | Restricted | e.g., data processing | Allowed list or “None” | Optional clarifications |

Rules:
- `Segment_ID` **MUST** match `^SEG-[0-9]{3}$`.
- **MUST** explicitly state isolation between user-facing, application, and data layers.
- **MUST** identify management/bastion segments if used.

**Diagram:**
- **SHOULD** include one high-level network diagram (ASCII or embedded image) showing segments and trust boundaries.

---

## 3. Ingress/Egress Controls
**Intent:** Enumerate controls at the perimeter and between segments.

**Required table – Controls Register:**

| Control_ID | Type | Scope | Technology | Policy/Rule_Summary | Direction | Logging | Owner |
|---|---|---|---|---|---|---|---|
| CTRL-001 | Firewall / SG / NACL / WAF | Env / Segment / Endpoint | e.g., Azure NSG, AWS SG | Human-readable rule summary | Ingress/Egress | Where logs land | Role/team |

Rules:
- `Control_ID` **MUST** match `^CTRL-[0-9]{3}$`.
- Each control **MUST** indicate whether it applies at Internet edge, private edge, or intra-segment.
- Policy summaries **MUST** avoid ambiguous “any/any” unless explicitly justified in **Exceptions**.

**Port/Protocol Matrix (REQUIRED):**

| Source_Segment | Destination_Segment | Protocol | Port/Range | AuthN/AuthZ Method | Justification |
|---|---|---|---|---|---|

Rules:
- Every open port **MUST** include a justification.
- If dynamic ports are used, the negotiation mechanism **MUST** be documented.

---

## 4. Public vs Private Exposure
**Intent:** Make public exposure deliberate and minimal.

**Required table – Public Endpoints:**

| Endpoint_ID | DNS/Address | Purpose | Exposure (Public/Private) | Protection (WAF/CDN/Rate Limit) | Data Sensitivity | Owner |
|---|---|---|---|---|---|---|

Rules:
- Public endpoints **MUST** list upstream protections (e.g., WAF/CDN, rate limiting).
- Private endpoints **MUST** indicate access path (e.g., VPN, Private Link, bastion).

---

## 5. Network-Level Encryption
**Intent:** Describe encryption in transit and TLS termination points.

**Required table – TLS & Key Management:**

| Flow_ID | Source → Destination | TLS_Version/Policy | Termination_Point(s) | mTLS (Y/N) | Cipher Policy | Key Management (KMS/HSM/Other) |
|---|---|---|---|---|---|---|

Rules:
- External-facing TLS **MUST** be ≥ TLS 1.2 (or stricter per enterprise policy).
- Termination points (edge, service mesh, ingress controller, app) **MUST** be explicit.
- If mTLS is not used where feasible, provide rationale in **Exceptions**.

---

## 6. Monitoring & Detection
**Intent:** Ensure visibility and rapid detection.

**Required content:**
- Logging coverage for firewalls/SGs/NACLs/WAFs (what, where, retention).
- Network telemetry sources (flow logs, packet capture, IDS/IPS).
- Alert rules (thresholds, owners, response expectations).

**Required table – Alerts Catalog:**

| Alert_ID | Source | Condition | Severity | Action/Runbook |
|---|---|---|---|---|

---

## 7. Change Management
**Intent:** Keep rules controlled and auditable.

**Required content:**
- Approval workflow (who can change network rules).
- Rollback strategy for control changes.
- Evidence requirements (e.g., change ticket ID, diff of policy).

**Required checklist:**
- [ ] Change is peer-reviewed.
- [ ] Impact analysis documented.
- [ ] Monitoring updated (logs/alerts).
- [ ] Rollback tested or documented.

---

## 8. Exceptions & Compensating Controls
**Intent:** Track justified deviations.

**Required table – Exceptions Register:**

| EXC_ID | Description | Risk | Expiry | Compensating_Control | Approval |
|---|---|---|---|---|---|

Rules:
- `EXC_ID` **MUST** match `^EXC-[0-9]{3}$`.
- Each exception **MUST** have an expiry date and a compensating control.

---

## 9. Verification Checklist
**Purpose:** Enable fast reviews by security and operations.

**Required checklist (keep as-is, tick when satisfied):**
- [ ] Segmentation map present with clear trust boundaries.
- [ ] All controls listed with logging destinations.
- [ ] Port/Protocol matrix complete with justifications.
- [ ] Public endpoints enumerated with protections.
- [ ] TLS termination points explicit; versions/ciphers stated.
- [ ] Monitoring & alerts defined with owners and runbooks.
- [ ] Change management workflow and evidence defined.
- [ ] Exceptions documented with expiry and compensating controls.

---

## 10. Appendix: Diagrams & References
**Diagrams:**
- **SHOULD** include at least one current logical network diagram.
- **MAY** include per-environment overlays if it improves clarity.

**References:**
- **MAY** list internal document IDs or filenames (no external links required by this convention).

---

# Editing Rules
- Keep sentences short. Prefer tables for enumerations.
- Use stable IDs (`SEG-xxx`, `CTRL-xxx`, `EXC-xxx`, `Flow_ID`) and do not reuse them.
- If a section is not applicable, include the section heading with a single line: `Not applicable – rationale: <one sentence>.`
- Do not include document-level metadata headers (title, version, status, owner, applies-to, last-updated).

# Quality Gates (Machine-Verifiable)
An automated linter **SHOULD** verify:
1. Presence and order of all top-level sections.
2. ID formats for `SEG-`, `CTRL-`, `EXC-`.
3. Non-empty mandatory tables: Segmentation Map, Controls Register, Port/Protocol Matrix, Public Endpoints, TLS & Key Management, Alerts Catalog, Exceptions Register.
4. At least one TLS flow defined when any public endpoint exists.
5. `last_reviewed` is ≤ 180 days old; otherwise flag **OUTDATED**.

# Minimal Starter Template (Copy into the file and fill)
> The backticks below are standard Markdown fences and are allowed by this convention.

```
# Summary
| Field | Description |
|---|---|
| scope_summary |  |
| last_reviewed | YYYY-MM-DD |
| reviewers |  |

# Network Architecture & Segmentation
(2–5 short paragraphs)
| Segment_ID | Segment_Name | Zone/Trust_Level | Purpose | Allowed_EastWest | Notes |
|---|---|---|---|---|---|

# Ingress/Egress Controls
| Control_ID | Type | Scope | Technology | Policy/Rule_Summary | Direction | Logging | Owner |
|---|---|---|---|---|---|---|---|

## Port/Protocol Matrix
| Source_Segment | Destination_Segment | Protocol | Port/Range | AuthN/AuthZ Method | Justification |
|---|---|---|---|---|---|

# Public vs Private Exposure
| Endpoint_ID | DNS/Address | Purpose | Exposure (Public/Private) | Protection (WAF/CDN/Rate Limit) | Data Sensitivity | Owner |
|---|---|---|---|---|---|---|

# Network-Level Encryption
| Flow_ID | Source → Destination | TLS_Version/Policy | Termination_Point(s) | mTLS (Y/N) | Cipher Policy | Key Management (KMS/HSM/Other) |
|---|---|---|---|---|---|---|

# Monitoring & Detection
(brief narrative)
| Alert_ID | Source | Condition | Severity | Action/Runbook |
|---|---|---|---|---|

# Change Management
- Approval workflow:
- Rollback strategy:
- Evidence requirements:

- [ ] Change is peer-reviewed.
- [ ] Impact analysis documented.
- [ ] Monitoring updated (logs/alerts).
- [ ] Rollback tested or documented.

# Exceptions & Compensating Controls
| EXC_ID | Description | Risk | Expiry | Compensating_Control | Approval |
|---|---|---|---|---|---|

# Verification Checklist
- [ ] Segmentation map present with clear trust boundaries.
- [ ] All controls listed with logging destinations.
- [ ] Port/Protocol matrix complete with justifications.
- [ ] Public endpoints enumerated with protections.
- [ ] TLS termination points explicit; versions/ciphers stated.
- [ ] Monitoring & alerts defined with owners and runbooks.
- [ ] Change management workflow and evidence defined.
- [ ] Exceptions documented with expiry and compensating controls.

# Appendix: Diagrams & References
- Diagrams:
- References:
```