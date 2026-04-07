Purpose
Define a strict, AI-friendly and human-verifiable convention for the “ARCH-07 — Resource catalog” product document so teams can register, validate, and maintain an authoritative inventory of all technology resources used by the product.

Scope
This convention applies to the single documentation file that fulfills ARCH-07 (Resource catalog). It specifies filename, location, structure, required fields, allowed values, validation rules, and operational behaviors (create, edit, review).

Normative Language
The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119 / RFC 8174.

Target File
- File name: ARCH-07.md

Document Goals (from requirement intent)
- Provide a complete catalog of product resources with unique identifiers, locations/regions, types/SKUs, purposes, and application/functionality association.
- Enable deterministic automation for checks, inventory exports, and drift detection.

Content Structure (top-level headings)
1. Overview
2. Registry
3. Conventions and Allowed Values
4. Validation Rules
5. Operations (Create, Edit, Review)
6. Quality Checks (Checklist)
7. Change Log

1. Overview
- Short text explaining that the file is the single source of truth for the resource inventory of the product across all environments.

2. Registry
- The registry MUST be expressed as one GitHub-Flavored Markdown table with the exact columns below and in the same order.
- Each row represents exactly one provisioned resource (or one declarative resource target if tracked before creation).

Required Table Columns (exact headers)
- resource_id — Stable unique ID for this catalog (format: RES-0001, RES-0002, …; lexical ascending; immutable once assigned).
- name — Human-readable resource name.
- cloud — One of: azure | aws | gcp | onprem | other.
- account_subscription — Cloud account/subscription/project identifier (free text; e.g., sub GUID, AWS account ID).
- environment — One of: dev | test | stage | prod | shared.
- region — Provider region/zone (e.g., westeurope, us-east-1, europe-west1; on-prem: site/city/DC code).
- resource_group_namespace — Grouping construct (e.g., Azure RG, Kubernetes namespace, on-prem service group). Use "-" if not applicable.
- service_type_sku — Canonical service/type and SKU or tier (e.g., Azure Cosmos DB / Serverless; AWS RDS / db.t3.large).
- purpose — Concise statement of what the resource is used for.
- application_function — Product application or function the resource supports (e.g., ingestion, serving-api, analytics-jobs).
- criticality — One of: C1 (critical) | C2 (high) | C3 (medium) | C4 (low).
- data_classification — One of: Public | Internal | Confidential | Restricted.
- dependencies — Comma-separated list of resource_id values this resource depends on; "-" if none.
- tags — Comma-separated business/ops tags (key=value pairs are allowed).
- cost_center — Internal cost attribution code; "-" if not applicable.
- owner_role — Responsible role/team for this resource (not an individual).
- operational_sla — Key SLO/SLA applicable to this resource (e.g., 99.5% availability, latency <= 200ms).
- backup_recovery — One of: N/A | Scheduled | Continuous | Provider-Managed; notes after a semicolon are allowed (e.g., Scheduled; daily 02:00 UTC).
- dr_class — One of: DR0 (none) | DR1 (manual) | DR2 (warm) | DR3 (hot).
- monitoring — Reference label to monitoring dashboard/log view (human-friendly label only; actual links managed elsewhere).
- iac_source — Path or identifier of the IaC module/template if managed as code; "-" if not under IaC.
- lifecycle_state — One of: planned | active | deprecated | decommissioned.
- created_at — ISO 8601 date (YYYY-MM-DD) of initial provisioning (or catalog entry if planned).
- last_changed — ISO 8601 date of last material change to the resource or its contract.
- decommission_plan — "-" if none; otherwise a short plan ID or note.
- notes — Optional free text for constraints or special handling.

Registry Formatting Rules
- The table MUST appear once under a heading named “Registry”.
- Column order MUST be exactly as listed above.
- Every row MUST populate all columns; use "-" where not applicable.
- Rows MUST be sorted lexically by resource_id ascending.
- No duplicate resource_id values are allowed.
- If a physical resource is replaced, the old row’s lifecycle_state MUST become “decommissioned”; do not delete the row.

3. Conventions and Allowed Values
3.1 Identifiers
- resource_id format: ^RES-[0-9]{4}$ with zero-padded integers starting at RES-0001 and increasing without gaps where possible.
- name: concise human-readable label; avoid secrets.
- dependencies: only other resource_id values listed in this file.

3.2 Environments
- dev: developer-facing; test: automated QA; stage: pre-prod; prod: production; shared: cross-env shared infra.

3.3 Regions
- Use the provider’s official region/zone code. For on-prem, use an agreed site/city/DC code (e.g., SOF-DC1).

3.4 Service Type and SKU
- Prefer “Provider Service / SKU-or-Tier” (examples: “Azure Storage / GRS”, “AWS S3 / Standard”).

3.5 Classification & Criticality
- Map to enterprise standards if available; otherwise use the enumerations defined above.

4. Validation Rules
- Table presence: Exactly one “Registry” table MUST exist.
- Headers: All required columns MUST be present with exact spelling and order.
- Unique keys: resource_id values MUST be unique.
- Referential integrity: dependencies MUST reference existing resource_id values (case-sensitive match).
- Allowed values: cloud, environment, criticality, data_classification, backup_recovery, dr_class, lifecycle_state MUST use only allowed values.
- Dates: created_at and last_changed MUST be valid ISO 8601 dates (YYYY-MM-DD) and last_changed MUST be >= created_at.
- Sorting: rows MUST be sorted by resource_id ascending.
- Deletion: catalog rows MUST NOT be deleted; use lifecycle_state to mark retirement.

5. Operations (Create, Edit, Review)
5.1 Create
- Assign the next resource_id (RES-XXXX) by scanning existing rows and choosing the next integer.
- Add a complete row with all required fields.
- If the resource is not yet provisioned, set lifecycle_state=planned and created_at as the entry date.

5.2 Edit
- Update fields as needed; bump last_changed to today’s local date.
- Material changes include: environment, region, service_type_sku, purpose, application_function, criticality, data_classification, dependencies, operational_sla, backup_recovery, dr_class, iac_source, lifecycle_state.

5.3 Review
- At least quarterly, run automated validation and review exceptions.
- Changes that alter risk/cost SHOULD be accompanied by an ADR or equivalent decision in the Architecture domain and referenced in notes.

6. Quality Checks (Checklist)
- [ ] Single “Registry” table present with exact headers and order.
- [ ] resource_id values unique and correctly formatted (RES-####).
- [ ] Rows sorted by resource_id ascending.
- [ ] dependencies reference existing resource_id values only.
- [ ] Allowed-value columns use only enumerated values.
- [ ] created_at and last_changed valid; last_changed ≥ created_at.
- [ ] No deleted historical rows; retired ones marked decommissioned.
- [ ] iac_source provided or explicitly “-”.
- [ ] Purpose and application_function are concise and clear.

7. Change Log
- Keep a simple dated list of notable catalog-wide changes (schema adjustments, mass updates).
- Format: YYYY-MM-DD — short description.

Appendix A — Minimal Worked Example (illustrative)
| resource_id | name                | cloud | account_subscription | environment | region      | resource_group_namespace | service_type_sku           | purpose                    | application_function | criticality | data_classification | dependencies | tags                          | cost_center | owner_role     | operational_sla      | backup_recovery            | dr_class | monitoring     | iac_source                         | lifecycle_state | created_at  | last_changed | decommission_plan | notes |
|-------------|---------------------|-------|----------------------|------------|------------|---------------------------|----------------------------|----------------------------|---------------------|------------|--------------------|-------------|-------------------------------|------------|----------------|----------------------|----------------------------|---------|----------------|-------------------------------------|-----------------|------------|-------------|-------------------|-------|
| RES-0001    | ingestion-storage   | azure | SUB-1234             | prod       | westeurope | rg-prod-ingestion         | Azure Storage / GRS        | Raw files landing zone     | ingestion           | C1         | Confidential       | -           | owner=dataplatform,env=prod   | CC-OPS     | Data Platform  | 99.5% availability    | Scheduled; daily 02:00 UTC | DR2     | mon-ing-storage | iac/azure/storage/ingestion.bicep | active          | 2026-03-05 | 2026-03-08  | -                 | -     |
| RES-0002    | serving-api-db      | aws   | 123456789012         | prod       | eu-central-1 | app-prod                  | AWS RDS / db.t3.large      | Transactional API storage  | serving-api         | C1         | Confidential       | RES-0001    | app=api,owner=appteam         | CC-APP     | App Team       | p99 latency ≤ 200ms   | Continuous                  | DR3     | mon-api-db     | iac/aws/rds/serving.tf             | active          | 2026-03-06 | 2026-03-08  | -                 | -     |
``