## Purpose
Define a strict, AI-friendly, human-verifiable convention for documenting **Dashboard Inventory** artifacts (requirement ID: DATA-09), ensuring consistent naming, structure, editing, and validation across products.

## Applicability
- Applies to the documentation file that fulfills **DATA-09 — Dashboard inventory** under the Product Documentation model.
- Applies to all formats of “dashboard” (reports, dashboards, spreadsheets, visualizations).
- Applies to AI-generated first drafts and human-edited revisions.

## File Naming & Location (Normative)
- **File name:** `DATA-09.md`
- The path MAY be overridden by human via `references.md`; automation MUST respect the active `references.md` record when present.

## Document Structure (Normative)
The document MUST contain the sections below in the exact order and with the exact headings.

1. **Overview**
   - Short description of the scope and intent of the dashboard inventory.
   - Ownership statement for maintaining the inventory (role/team names only).

2. **Conventions Used**
   - Key field formats (ID patterns, date formats, URL format).
   - Environment tags used (e.g., `DEV`, `TEST`, `PROD`) and their meaning.

3. **Inventory Table**
   A single canonical table with one row per dashboard/report. Columns (all normative):

   | Column | Type | Rules |
   |---|---|---|
   | `dashboard_id` | string | **Required.** Stable unique ID. Pattern: `DB-0001`, `DB-0002`, ... Strictly incremental without reuse. |
   | `name` | string | **Required.** Descriptive human-friendly name. |
   | `business_purpose` | text | **Required.** Clear business question(s) or decision(s) it supports. |
   | `primary_audience` | list<string> | **Required.** One or more audience labels (e.g., `Sales Leaders`, `Finance`, `Field Reps`). |
   | `data_sources` | list<string> | **Required.** Source systems or curated datasets (use stable names; avoid URLs). |
   | `created_at` | date | **Required.** ISO 8601 (`YYYY-MM-DD`). |
   | `last_updated_at` | date | **Required.** ISO 8601. |
   | `development_specifics` | text | **Required.** Tooling (e.g., Power BI, Tableau), workspace/project, notable model settings. |
   | `viz_standards` | list<string> | **Required.** Referenced style guides/pattern names (e.g., “Corporate Viz Std v2”, “Color Palette A”). |
   | `interactivity` | text | **Required.** Describe filters, parameters, drill paths, navigation, export options. |
   | `url` | url | **Required.** Canonical dashboard URL (environment-specific if needed; prefer `PROD`). |
   | `refresh_frequency` | string | **Required.** Human-readable, e.g., `Hourly`, `Daily 02:00 UTC`, `On-demand`. |
   | `max_latency` | duration | **Required.** Maximum acceptable data staleness (e.g., `PT2H`, `P1D`). |
   | `performance_sla` | text | **Required.** Render time and query SLAs; specify targets (e.g., “P95 < 5s”). |
   | `testing_strategy` | text | **Required.** Brief of regression checks, visual tests, query tests. |
   | `security` | text | **Required.** Row/Object-level security summary; role names or policy IDs. |
   | `cicd` | text | **Required.** Packaging/release approach; pipeline IDs or paths. |
   | `logging_monitoring` | text | **Required.** Log category, metrics dashboards, alert references. |
   | `associated_compute` | list<string> | **Required.** IDs of upstream compute assets (e.g., `NB-014`, `ALG-003`, pipeline IDs). |
   | `status` | enum | **Required.** One of: `Active` \| `Deprecated` \| `Planned` \| `Retired`. |
   | `notes` | text | Optional. Free-form remarks or caveats. |

4. **ID Management**
   - `dashboard_id` assignment is deterministic and monotonic.
   - IDs MUST NOT be re-used, even if a dashboard is retired.
   - If a dashboard is replaced, add a new row with a new `dashboard_id` and set the old row’s `status=Retired` and `notes="Replaced by <DB-XXXX>"`.

5. **Environments**
   - If multiple environments exist, one row per environment **is NOT allowed**. Keep a **single row** representing the canonical production artifact and include environment details under `development_specifics`, `url`, and `notes` if needed.

6. **Quality & SLAs**
   - `max_latency` MUST be specific and enforceable.
   - `performance_sla` MUST define at least one percentile-based target (e.g., P95 render time).

7. **Security**
   - Summarize RLS/OLS in `security`. Detailed policies live in Security docs; reference policy names, not inline policy code.

8. **Change Control**
   - Any edit that changes `name`, `business_purpose`, `primary_audience`, `data_sources`, `url`, or SLA fields requires:
     - A short entry in the product’s `implementation.md` (iteration-scoped) referencing the change.
     - Updating `last_updated_at` to the date of change.

9. **Validation Rules (Normative)**
   - Table MUST exist exactly once under **Inventory Table**.
   - Columns MUST match the schema above exactly (names, order recommended).
   - `dashboard_id` MUST be unique.
   - `url` MUST be present and reachable by authorized users (manual/verifiable).
   - `refresh_frequency` and `max_latency` MUST be consistent (e.g., `max_latency` not shorter than the refresh cadence unless justified in `notes`).
   - `status` MUST be one of the allowed enum values.

10. **Editing Workflow**
    - AI MAY add new rows using available context; humans SHOULD verify before commit.
    - Humans MAY edit any field; AI SHOULD preserve unmodified fields verbatim.
    - Deletions are NOT allowed; instead, set `status=Retired` with rationale in `notes`.

11. **Examples (Illustrative)**
    - Example row (compact):

      | dashboard_id | name | business_purpose | primary_audience | data_sources | created_at | last_updated_at | development_specifics | viz_standards | interactivity | url | refresh_frequency | max_latency | performance_sla | testing_strategy | security | cicd | logging_monitoring | associated_compute | status | notes |
      |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
      | DB-0023 | Weekly Sales Performance | Track weekly sales vs target by channel and region | Sales Leaders; Finance | POS_Sales; ProductMaster | 2025-10-12 | 2026-03-09 | Power BI (Prod Workspace: SalesOps); Dataset: `SalesPerf_v3` | Corporate Viz Std v2; Palette A | Filters: Week, Region, Channel; Drill: Region→Market→Store; Export: CSV | https://bi.company.com/groups/…/reports/… | Daily 02:00 UTC | P1D | P95 render < 5s; P99 < 8s | Visual diffs on key pages; query regression suite nightly | RLS: `SalesRegionRole`, OLS on detail pages | Pipeline: `sales-perf-release` | Logs: `sales-perf` category; Alerts: freshness, render time | NB-014; ALG-003; PIPE-201 | Active | Replaces legacy report RPT-778 |

12. **Glossary (Local)**
    - **Dashboard**: Any user-facing data visualization artifact (e.g., BI reports, dashboards, spreadsheet models shared as source of truth).
    - **RLS/OLS**: Row/Object-Level Security.
    - **P95/P99**: 95th/99th percentile metric across user render times.

## Machine-Checkable Constraints (For Automation)
- Regex:
  - `dashboard_id`: `^DB-\d{4}$`
  - `created_at` / `last_updated_at`: `^\d{4}-\d{2}-\d{2}$`
  - `max_latency`: ISO 8601 duration `^P(T?\d+[HMSD])?[\w\dPT]*$` (e.g., `PT2H`, `P1D`)
- Enums:
  - `status`: `{Active, Deprecated, Planned, Retired}`
- Non-empty requirements:
  - `name`, `business_purpose`, `primary_audience`, `data_sources`, `url`, `refresh_frequency`, `max_latency`, `performance_sla`, `testing_strategy`, `security`, `cicd`, `logging_monitoring`, `associated_compute`.

## Determinism & Idempotence
- Re-generating the document MUST preserve existing rows and only append or update rows deterministically based on source-of-truth references and explicit instructions.
- Sorting order of rows SHOULD be by `dashboard_id` ascending unless the human specifies otherwise.

## Human Verification Checklist
- [ ] Inventory table present once; schema matches exactly.
- [ ] Every row has unique `dashboard_id`.
- [ ] URLs resolve for authorized users.
- [ ] SLA fields are specific and aligned with operational monitoring.
- [ ] Security summary is present and consistent with security documentation.
- [ ] Changes recorded in `implementation.md` when mandated.