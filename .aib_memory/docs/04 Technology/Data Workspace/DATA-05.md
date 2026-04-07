# Overview

AI Builder (AIB) exposes operational “datasets” as structured Markdown registers and request artifacts. Consumers are developers and AI agents reading these files to understand workspace state and documentation requirements.

# Exposed Datasets (Table)

| dataset_id | name | description | data_domain | schema_ref | freshness_slo | rls_ols | quality_status | owner_role | consumption_channels | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-0001 | AIB_Requests_Register | Request lifecycle register (Active/Closed) | IT | DATA-02:REQUEST | on-demand | N/A | Green | Product Team | DirectQuery, Export | Active |
| DS-0002 | AIB_References_Register | Registry of referenced files and edit permissions | IT | DATA-02:REFERENCE | on-demand | N/A | Green | Product Team | DirectQuery | Active |

# Database Connections (Table)

| conn_id | engine | host_or_endpoint | port | db_or_catalog | schema | auth_mode | access_policy | allowed_operations | latency_target | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DB-0001 | Filesystem | local-workspace | managed | repo | varies | OS login | workspace ACLs | READ, WRITE | p95 < 50 ms | File-based; no database engine. |

# Data APIs (Table)

| api_id | style | base_path_or_route | authz | rate_limits | contracts | backed_by | change_policy | availability_slo | observability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| API-0001 | N/A | N/A | N/A | N/A | N/A | DS-0001; DS-0002 | N/A | N/A | N/A |

# Direct Query Access (Guidelines + Table)

- Use tool scripts to modify registers; avoid manual edits.
- Parse stable IDs and tables deterministically.

| entitlement_id | role_or_group | target_conn_id | scope | rls_ols_applied | expiry | approver_role |
| --- | --- | --- | --- | --- | --- | --- |
| DQ-0001 | Repository Contributors | DB-0001 | `.aib_memory/*` | No | no-expiry | Repository Maintainers |

# Subscription Models (Table)

| subscription_id | type | delivery_channel | format | schedule_or_trigger | target_audience | retention | backed_by | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SUB-0001 | Pull | Filesystem | Markdown | on-demand | Developer, AI Agent | git | DS-0001 | Product Team |

# Export Capabilities (Table)

| export_id | source | format | limits | destination | privacy_controls | retention | request_process |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EXP-0001 | DS-0001 | CSV | best-effort | local file | none | git | manual export |

# Security & Compliance Controls

- Refer to SEC-01..SEC-04; do not embed credentials.

# Performance & Cost Guardrails

- Keep registers small.

# Operational Considerations

- Primary visibility via CI outcomes and implementation logs.

# Changelog (Append-only)

- 2026-03-22 — Populated AIB consumption patterns — AI Agent
