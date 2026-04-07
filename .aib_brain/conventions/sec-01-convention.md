## Purpose
Define a precise, machine- and human-friendly convention for the **Access Management** document that governs how identities, roles, and permissions are specified, reviewed, and evidenced for an analytics/software product. The convention standardizes the file’s structure, allowed content, validation rules, and update workflow so the document can be authored consistently and verified quickly.

## Scope
This convention applies to the standalone **Access Management** document that describes identity and access control policy for application functionalities, data assets (raw, processed, aggregated), and dashboards, including human and non-human identities and their permissions across environments.

## Outcomes
- A deterministic document structure with labeled sections and required fields.
- A clear register of roles, permissions, and review cadences.
- Evidence points for audits and access reviews.
- Unambiguous editing and validation rules enabling automated checks.

## File Naming
- **File name:** `SEC-01.md`
- **Encoding:** UTF-8
- **Format:** GitHub-flavored Markdown (GFM)
- **One-file rule:** All access management content resides in this single file.

## Document Structure (Top-level Headings)
The document **MUST** contain the sections below in the exact order. Subsections are allowed where specified.

1. **Overview**
2. **Identity Model**
3. **Role Catalog**
4. **Permission Matrix**
5. **Access Assignment Rules**
6. **Authentication & MFA**
7. **Reviews & Certification**
8. **Service & Machine Identities**
9. **Provisioning & Deprovisioning**
10. **Evidence & Audit Artifacts**
11. **Exceptions & Temporary Access**
12. **Change Log**

### 1. Overview
**Goal:** Summarize the access control approach and coverage.
**Required fields:**
- **Purpose (1–3 sentences)**
- **In-scope systems** (bulleted list)
- **Out-of-scope systems** (bulleted list, if any)
- **Environments covered:** e.g., Dev, Test, Prod

### 2. Identity Model
Describe identity sources and classification.
**Required fields:**
- **Identity sources:** (e.g., corporate IdP/SSO, external partners)
- **Identity types:** Human users, Service principals/Apps, Automation agents
- **Namespaces:** How identities are named (pattern examples)
- **Joiner–Mover–Leaver mapping:** Brief reference to Section 9

### 3. Role Catalog
Define all roles and their responsibilities at a stable abstraction level.
**Required table columns (in this order):**
- `role_id` (stable key, e.g., `ROLE_DASHBOARD_VIEWER`)
- `role_name` (human-readable)
- `description` (concise responsibility statement)
- `scope` (application/data area; may list multiple)
- `risk_level` (`Low` | `Medium` | `High`)
- `owner` (function/team name, not a person)
- `review_cadence` (`Quarterly`, `Semiannual`, `Annual`)
- `mfa_required` (`Yes` | `No`)
- `least_privilege_notes` (how the role is minimized)

**Rules:**
- Roles **MUST NOT** embed user-specific information.
- Overlapping roles **SHOULD** be merged or justified in Section 11.

### 4. Permission Matrix
Map roles to operations on resources.
**Required table columns (in this order):**
- `resource_id` (stable ID, e.g., `RPT_SALES_PERF`)
- `resource_type` (e.g., dashboard, dataset, table, API)
- `environment` (`Dev` | `Test` | `Prod` | `All`)
- `role_id`
- `operations` (comma-separated verbs; e.g., `view, export`)
- `constraints` (row-level policy, time bounds, condition)
- `evidence_ref` (pointer into Section 10)

**Operation verbs — canonical set:**
`view`, `query`, `export`, `create`, `update`, `delete`, `admin`, `share`, `approve`, `configure`

**Rules:**
- If `operations` includes `admin`, justification **MUST** exist in Section 11.
- Environment-specific differences **MUST** be explicit per row.

### 5. Access Assignment Rules
Define how users obtain roles.
**Required content:**
- **Entitlement policy:** Eligibility criteria per role
- **Segregation of duties (SoD):** Forbidden role combinations (table)
- **Approval workflow:** Steps, approver functions, SLAs
- **Time-bound access:** Defaults for temporary elevation
- **Break-glass:** Emergency access pattern and constraints

### 6. Authentication & MFA
**Required content:**
- **Primary auth method:** (e.g., SSO with IdP)
- **MFA policy:** Factors accepted, enforcement points
- **Session management:** Timeouts, re-auth triggers
- **Service accounts:** Non-interactive auth method summary (tie to Section 8)

### 7. Reviews & Certification
**Required table columns (in this order):**
- `review_id` (e.g., `REV-2026Q1`)
- `scope` (e.g., “All Prod dashboards”)
- `review_cadence` (e.g., `Quarterly`)
- `reviewer_function` (not a person)
- `methodology` (attestation, revalidation steps)
- `status` (`Planned` | `In-Progress` | `Completed`)
- `findings_summary` (link to Section 10 evidence IDs)
- `remediation_due` (date)
- `closure_date` (date or empty)

**Rules:**
- Each role with `High` risk_level **MUST** appear in at least one planned review per year.
- Findings require remediation tracking until closure.

### 8. Service & Machine Identities
**Required fields:**
- **Inventory table columns:** `svc_id`, `owner_function`, `purpose`, `secrets_store` (e.g., KMS/HSM), `rotation_policy`, `network_constraints`, `scopes/permissions`, `non-interactive_auth` (`Yes/No`)
- **Rotation:** Default rotation interval and exceptions handling
- **Secret injection:** (runtime / pipeline; redaction policy)

### 9. Provisioning & Deprovisioning
**Required content:**
- **Joiner workflow:** Steps from request to grant
- **Mover workflow:** Role changes, SoD re-checks
- **Leaver workflow:** Timelines, revocation guarantees
- **SLAs:** Max times for each workflow stage
- **Automation hooks:** Where tickets/scripts/IdP rules apply

### 10. Evidence & Audit Artifacts
Define how proofs are captured and referenced across the document.
**Required table columns (in this order):**
- `evidence_id` (e.g., `E-0007`)
- `type` (screenshot, export, log excerpt, attestation record)
- `description`
- `storage_location` (relative path or repository ref)
- `related_object` (role_id, resource_id, review_id)
- `timestamp` (ISO 8601)

**Rules:**
- Every row in Permission Matrix **SHOULD** reference at least one `evidence_id`.
- Sensitive artifacts **MUST** be stored in restricted locations with audit trail.

### 11. Exceptions & Temporary Access
**Required content:**
- **Exception register table columns:** `exception_id`, `requestor_function`, `justification`, `roles/resources`, `risk_acceptance_owner`, `start`, `end`, `controls`, `status`
- **Temporary elevation:** Max duration and non-renewal policy without new approval
- **Compensating controls:** Monitoring, additional review frequency

### 12. Change Log
A simple, append-only log of meaningful document updates.
**Required table columns:** `date`, `summary`, `initiator_function`

## Validation Rules (Normative)
Automated validators **MUST** enforce:
1. **Presence & order of sections** exactly as defined.
2. **Table schemas** exactly as specified (column headers and order).
3. **Stable keys format:**
   - `role_id` matches `^[A-Z0-9_]{6,}$`
   - `resource_id` matches `^[A-Z0-9_]{3,}$`
   - `review_id` matches `^REV-[0-9]{4}Q[1-4]$`
   - `evidence_id` matches `^E-[0-9]{4}$`
   - `exception_id` matches `^X-[0-9]{4}$`
4. **Operation verbs** limited to the canonical set.
5. **Risk alignment:** Any `admin` operation requires an entry in Section 11 referencing a valid `exception_id` unless the role’s `risk_level=High` and justified in `least_privilege_notes`.
6. **SoD completeness:** All forbidden combinations listed; no user/identity may be assigned both roles in a forbidden pair.
7. **Review coverage:** Every `High` risk role appears in Section 7 at least once per 12 months.
8. **MFA enforcement:** Any role with `admin`, `configure`, or `approve` operations **MUST** have `mfa_required=Yes`.

## Authoring Guidance
- Keep descriptions concise and decision-oriented.
- Prefer function/team names over individuals for ownership fields.
- Use short, stable identifiers that are tooling-friendly.
- Where possible, decompose broad resources into smaller, addressable `resource_id`s to apply least privilege.

## Minimal Example Skeleton (Illustrative)
> Replace sample values. Keep headers and column order unchanged.

### 1. Overview
- **Purpose:** Centralize and enforce least-privilege access to analytics assets.
- **In-scope systems:** BI platform, Analytics DB, Reporting APIs
- **Environments covered:** Dev, Test, Prod

### 3. Role Catalog
| role_id | role_name | description | scope | risk_level | owner | review_cadence | mfa_required | least_privilege_notes |
|---|---|---|---|---|---|---|---|---|
| ROLE_DASHBOARD_VIEWER | Dashboard Viewer | Read-only access to published dashboards | Dashboards | Low | Analytics Ops | Annual | No | No export unless explicitly granted |
| ROLE_DATA_EXPORTER | Data Exporter | Export datasets for approved use cases | Datasets | Medium | Data Governance | Semiannual | Yes | Export limited to aggregated views |
| ROLE_PLATFORM_ADMIN | Platform Admin | Administrative tasks on BI workspace | Platform | High | Platform Eng | Quarterly | Yes | Restricted to non-prod unless justified |

### 4. Permission Matrix
| resource_id | resource_type | environment | role_id | operations | constraints | evidence_ref |
|---|---|---|---|---|---|---|
| RPT_SALES_PERF | dashboard | Prod | ROLE_DASHBOARD_VIEWER | view | RLS: region-by-user | E-0001 |
| DS_ORDERS | dataset | Prod | ROLE_DATA_EXPORTER | query, export | Export only aggregated metrics | E-0002 |
| WS_MAIN | workspace | Prod | ROLE_PLATFORM_ADMIN | admin, configure | Break-glass only | E-0003 |

### 7. Reviews & Certification
| review_id | scope | review_cadence | reviewer_function | methodology | status | findings_summary | remediation_due | closure_date |
|---|---|---|---|---|---|---|---|---|
| REV-2026Q1 | Prod dashboards & datasets | Quarterly | Security Governance | Attestation + sample revalidation | Planned | — | 2026-04-30 |  |

### 10. Evidence & Audit Artifacts
| evidence_id | type | description | storage_location | related_object | timestamp |
|---|---|---|---|---|---|
| E-0001 | screenshot | RPT_SALES_PERF role check | ./evidence/2026Q1/ | ROLE_DASHBOARD_VIEWER | 2026-03-09T09:00:00+02:00 |

## Maintenance & Review Cadence
- **Document steward (function):** Security Governance
- **Recommended review frequency:** Quarterly for High-risk scope; otherwise Semiannual.
- **Archival rule:** Keep at least the last 8 quarters of Change Log entries.