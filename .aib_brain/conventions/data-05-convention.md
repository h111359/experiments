## Purpose
Define the normative format, file operations, and editing rules for **DATA-05 — Data consumption & access patterns** so documentation is deterministic for AI tools and easy for human validation.

## Scope
- Applies to the single document describing how data is exposed and accessed by consumers of the product (datasets, connections, APIs, direct query, subscriptions, exports).
- This convention governs the **content structure**, **field definitions**, **naming**, **location**, **edit workflow**, and **validation rules** for the DATA-05 document.

## File Identity
- **Canonical document ID:** DATA-05
- **Document name:** Data consumption & access patterns

## Relationship to the Product Documentation System
- DATA-05 is a **[H] High** priority document within the **Data** domain, Technology → Data Workspace. It complements DATA-01 (sources), DATA-02 (models), DATA-03 (lineage), DATA-04 (storage strategy), DATA-06 (metrics), DATA-07 (quality), and DATA-09 (dashboards). Consistency across these is **required**.

## Authoring Principles
- Be concise, unambiguous, and implementation-oriented.
- Prefer tables for registries and checklists, bullet lists for guidelines, and short paragraphs for rationales.
- Write in English. Use consistent terminology across documents.
- Every statement that is normative for the product **must** be captured in the structured fields, not only in free text.

## Document Structure (normative)
The DATA-05 document **MUST** follow this exact structure and heading order. Sections marked **(Table)** must be Markdown tables with the specified columns and semantics.

1. **Overview**
   - Purpose (2–4 sentences)
   - Scope of consumers (personas, teams, external/internal)
   - Access principles (e.g., least privilege, governed interfaces first)

2. **Exposed Datasets (Table)**
   - Columns (exact order):
     1. `dataset_id` — Stable ID, format `DS-0001`, `DS-0002`, …
     2. `name` — Human-friendly dataset name
     3. `description` — What the dataset provides
     4. `data_domain` — Business domain (e.g., Sales, Finance)
     5. `schema_ref` — Link/slug to the authoritative schema location (e.g., `DATA-02:SalesFact`)
     6. `freshness_slo` — e.g., `<= 2h`, `daily 06:00`
     7. `rls_ols` — Row/Object level security policy summary (e.g., `RLS by BU`)
     8. `quality_status` — `Green|Amber|Red` (roll-up from DATA-07)
     9. `owner_role` — Accountable role/team
     10. `consumption_channels` — `API|DirectQuery|BI|Export`
     11. `status` — `Active|Deprecated|Planned`
   - **Rules:**
     - `dataset_id` is unique within the document.
     - Any dataset referenced by API, Direct Query, BI, or Export **MUST** have a row here.

3. **Database Connections (Table)**
   - Columns:
     1. `conn_id` — `DB-0001`, `DB-0002`, …
     2. `engine` — e.g., `PostgreSQL 14`, `SQL Server 2022`, `Databricks SQL`
     3. `host_or_endpoint` — DNS or platform endpoint (mask secrets)
     4. `port` — Numeric or `managed`
     5. `db_or_catalog` — Database/catalog name
     6. `schema` — Default schema or `varies`
     7. `auth_mode` — e.g., `AAD SSO`, `Service Principal`, `User+MFA`
     8. `access_policy` — Who may use, link to IAM policy name
     9. `allowed_operations` — `READ|WRITE|DDL` (subset)
     10. `latency_target` — e.g., `p95 < 300 ms`
     11. `notes` — Constraints/quotas/special routing

4. **Data APIs (Table)**
   - Columns:
     1. `api_id` — `API-0001`, …
     2. `style` — `REST|GraphQL|gRPC|ODATA`
     3. `base_path_or_route` — Path or route name; no secrets
     4. `authz` — How authorization is enforced (scope/role)
     5. `rate_limits` — Per consumer/app if applicable
     6. `contracts` — Schema/versioning approach (e.g., `OpenAPI 3.1`, `GraphQL SDL v2`)
     7. `backed_by` — Dataset(s) or view(s) powering the API (reference `dataset_id`)
     8. `change_policy` — Breaking change protocol (e.g., `sunset >= 90d`)
     9. `availability_slo` — e.g., `99.5%`
     10. `observability` — Logs/metrics traces location or label

5. **Direct Query Access (Guidelines + Table)**
   - **Guidelines (bullets, normative):**
     - Use governed interfaces (APIs/semantic layers) **first**; direct DB access is **exceptional** and **time-bound**.
     - For ad-hoc exploration, read-only roles with RLS **MUST** be used.
     - Long-running ad-hoc queries **MUST NOT** impact production SLAs; use replicas or designated compute.
   - **Entitlements (Table):**
     1. `entitlement_id` — `DQ-0001`, …
     2. `role_or_group` — Consumer role/group
     3. `target_conn_id` — From the **Database Connections** table
     4. `scope` — Schemas/tables/views allowed
     5. `rls_ols_applied` — Yes/No + brief
     6. `expiry` — Date or `no-expiry`
     7. `approver_role` — Accountable gatekeeper

6. **Subscription Models (Table)**
   - Columns:
     1. `subscription_id` — `SUB-0001`, …
     2. `type` — `Push|Pull|Event`
     3. `delivery_channel` — e.g., `Event Hub`, `Kafka`, `S3`, `Email`
     4. `format` — `Parquet|CSV|JSON|Excel`
     5. `schedule_or_trigger` — Cron, SLA-based, or event
     6. `target_audience` — Persona/app
     7. `retention` — For delivered artifacts
     8. `backed_by` — `dataset_id` or API powering it
     9. `ownership` — Accountable role/team

7. **Export Capabilities (Table)**
   - Columns:
     1. `export_id` — `EXP-0001`, …
     2. `source` — `dataset_id`/API/BI
     3. `format` — `CSV|Parquet|XLSX|PDF`
     4. `limits` — Row/file size, frequency
     5. `destination` — Folder/bucket/workspace (no secrets)
     6. `privacy_controls` — Masking/PII handling
     7. `retention` — Days or policy reference
     8. `request_process` — How users request/enable exports

8. **Security & Compliance Controls**
   - Map consumption modes to: authentication, authorization model (RBAC/ABAC), encryption in transit, data classification handling, data residency, and audit logging expectations.
   - Reference the specific controls from Security documents (SEC-01, SEC-02, SEC-03, SEC-04) by ID only.

9. **Performance & Cost Guardrails**
   - Provide p95 latency/freshness targets per channel (APIs, direct query, BI, exports).
   - Document quotas (requests/minute, concurrency, dataset size limits).
   - Provide guidance for cost-aware usage (e.g., off-peak exports, cache/semantic models for BI).

10. **Operational Considerations**
    - Incident routing & ownership for each channel.
    - Change management: how consumers are notified about deprecations/breaking changes (sunset periods).
    - Observability hooks: logs/metrics dashboards identifiers; how consumers report issues.

11. **Changelog (Append-only)**
    - Date, change summary, impacted sections, author role/team.

## Field Specifications (normative)
- **Identifiers:** All registries use zero-padded ascending IDs per type: `DS-0001`, `DB-0001`, `API-0001`, `DQ-0001`, `SUB-0001`, `EXP-0001`. IDs are immutable once published.
- **Status values:** `Active|Deprecated|Planned`. Deprecations **must** include a final date in the affected row’s notes.
- **SLO fields:** Use explicit units (e.g., `p95 < 300 ms`, `<= 2h freshness`).
- **Security fields:** Avoid secrets; store only policy names, roles, scopes, and redacted endpoints.
- **Cross-references:** Use document IDs or local identifiers (`dataset_id`, `conn_id`) rather than URLs.

## Naming Rules
- Dataset names: `Domain_DataSubject[_Grain][_Region]` (Camel_Snake acceptable), e.g., `Sales_Fact_Daily_EU`.
- API routes: kebab-case nouns with versioning prefix, e.g., `/v1/sales-orders`.
- Connection IDs: reflect engine and purpose where useful, e.g., `DB-0003` (`engine=PostgreSQL 14`, purpose: `analytics-ro`).

## Validation Rules (normative)
Automations reading DATA-05 **MUST** validate:
1. Required sections and tables exist and are in the exact order specified.
2. All registry ID columns are unique within their respective tables.
3. Every `backed_by` reference resolves to an existing `dataset_id` in **Exposed Datasets**.
4. Every `target_conn_id` in **Direct Query Access** resolves to an existing `conn_id`.
5. Status values, SLO formats, and allowed operation enumerations are valid.
6. No secrets or credentials appear anywhere in the document (endpoints redacted, tokens absent).
7. If any dataset is marked `Deprecated`, a deprecation note with final date exists.

## Editing Workflow
- **Creation:** Seeded empty tables/sections per this convention.
- **Updates:** Append rows for new interfaces; update existing rows in-place; record changes in **Changelog**.
- **Deprecation:** Mark `status=Deprecated` and maintain until sunset passes; remove only after final date and consumer migration complete.
- **Change Impact:** When changing datasets/APIs impacting schemas or contracts, update DATA-02/DATA-03 references accordingly.

## Minimal Examples (illustrative)
> Replace placeholder values before publishing.

### Exposed Datasets
| dataset_id | name                      | description                              | data_domain | schema_ref              | freshness_slo | rls_ols | quality_status | owner_role     | consumption_channels       | status |
|---|---|---|---|---|---|---|---|---|---|---|
| DS-0001 | Sales_Fact_Daily_EU         | Daily fact table for EU sales            | Sales       | DATA-02:SalesFact       | <= 2h         | RLS by BU | Green        | Analytics Team | API, BI, Export            | Active |
| DS-0002 | Customer_Dimensional_Master | Golden customer attributes and segments  | Sales       | DATA-02:CustomerDim     | daily 06:00   | OLS on PII | Amber       | Data Steward   | DirectQuery, BI            | Active |

### Database Connections
| conn_id | engine          | host_or_endpoint      | port | db_or_catalog | schema | auth_mode  | access_policy | allowed_operations | latency_target | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| DB-0001 | PostgreSQL 14   | `analytics-ro.example`| 5432 | salesdw       | public | AAD SSO    | Analytics-RO  | READ               | p95 < 300 ms   | Read-only replica |
| DB-0002 | Databricks SQL  | `dbc-xxxxx.cloud`     | managed | hive_metastore | bronze | Service Principal | Eng-ELT | READ, WRITE | p95 < 800 ms | ETL only |

### Data APIs
| api_id | style | base_path_or_route | authz          | rate_limits | contracts       | backed_by | change_policy  | availability_slo | observability |
|---|---|---|---|---|---|---|---|---|---|
| API-0001 | REST | /v1/sales-orders   | role:sales-api | 600 rpm     | OpenAPI 3.1 v1  | DS-0001   | sunset >= 90d  | 99.5%            | api-logs:sales |

## Deviation Policy
- Any deviation from this convention **MUST** be explicitly justified in a short paragraph at the end of the affected section, prefixed with `Deviation:` and reviewed in the next governance cycle.

## Acceptance Criteria (for reviewers)
- Structure and tables match this convention exactly.
- All cross-references resolve; no placeholders remain.
- Security constraints are specified without secrets.
- Guardrails (performance, cost) are concrete and measurable.
- Changelog updated for substantive changes.