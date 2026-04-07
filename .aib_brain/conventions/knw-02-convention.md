## Purpose
Define a clear, portable, and AI-friendly convention for the **Business Process Catalog** document that ensures a consistent, verifiable description of business processes relevant to a product or program.

## Scope
This convention applies **only** to the Business Process Catalog file associated to requirement **KNW-02** and governs its **file naming**, **document structure**, **field semantics**, **editorial rules**, **validation rules**, and **operational guidance**.

## File Naming
- **File name:** `KNW-02.md`
- **Rationale:** Stable mapping to requirement identifier; short, predictable, and tool-friendly.
- **Character set:** ASCII; avoid spaces (use hyphens only if needed).
- **Case:** Uppercase for the prefix; remainder as shown.

## Document Structure (Top-level Headings)
The document MUST follow the headings and order below:

1. **Overview**
2. **Catalog Schema**
3. **Process Entries**
4. **Diagrams (Optional)**
5. **Cross-Mappings**
6. **Governance & Maintenance**
7. **Change Log**

> Do not add or reorder top-level sections. Use the prescribed subheadings within each section as defined below.

---

### 1) Overview
**Purpose:** Briefly explain what the catalog is and how it is used.
- **Contents (2–5 short paragraphs):**
  - What a “business process” means in this context.
  - How the catalog supports product understanding, onboarding, analysis, and impact assessment.
  - Relationship to glossary/terms (without duplicating definitions).
  - Editorial scope of this file vs. other knowledge documents.

### 2) Catalog Schema
Define the **canonical fields** for each process entry. Use the table below and keep field names **exactly** as written.

| Field | Type | Requirement | Description | Allowed values / Format | Examples |
|---|---|---|---|---|---|
| `process_id` | String | MUST | Stable ID, unique within the file. | `BP-0001`, `BP-0002`, … | `BP-0012` |
| `name` | String | MUST | Human-readable process name. 3–60 chars. | Free text | “Monthly Sales Forecasting” |
| `description` | Text | MUST | Concise description of what the process achieves and why it exists. | 1–3 paragraphs | — |
| `triggers` | List | SHOULD | Events or conditions that start the process. | Bullet list | “End of month close” |
| `inputs` | List | MUST | Business/technical inputs required. | Bullet list | “POS daily sales”, “Calendar” |
| `outputs` | List | MUST | Outcomes/artifacts produced. | Bullet list | “Forecast vX”, “Approval record” |
| `steps` | Ordered list | MUST | End-to-end steps, numbered; each step 1–2 sentences; avoid tool-specific jargon. | `1. … 2. …` | — |
| `roles` | List | MUST | Roles involved (not individuals). | Bullet list (RACI tags optional) | “Demand Planner (A/R)”, “Finance Analyst (C)” |
| `dependencies` | List | SHOULD | Other processes or external prerequisites. | Bullet list with `process_id` refs where applicable | “BP-0003” |
| `policies` | List | MAY | Policy or compliance constraints that shape execution. | Bullet list | “Quarterly SOX review inputs” |
| `metrics` | List | SHOULD | KPIs or health metrics to assess process quality. | Bullet list with formula/owner | “Forecast MAPE (Owner: FP&A)” |
| `systems` | List | SHOULD | Systems/platforms typically used (descriptive, not infra detail). | Bullet list | “BI Portal”, “Planning Tool” |
| `frequency` | Enum | SHOULD | Typical cadence. | `ad-hoc` \| `daily` \| `weekly` \| `monthly` \| `quarterly` \| `yearly` | `monthly` |
| `owner_role` | String | SHOULD | Accountable role (RACI “A”). | Free text | “Product Owner” |
| `notes` | Text | MAY | Any clarifications that improve understanding. | Free text | — |

**Field conventions**
- Lists use `-` bullets; ordered lists use `1.` numbering.
- Role tags may optionally include RACI in parentheses `(R/A/C/I)`.
- Keep steps outcome-oriented; avoid vendor or tool-dependent commands.

### 3) Process Entries
Each entry MUST use the exact subheading `#### <process_id> — <name>` followed by the fields in the order below, using the shown labels and formats.

Example scaffold (copy and reuse):

#### BP-0001 — Monthly Sales Forecasting
- **description:**  
  Short paragraph (1–3) explaining scope, boundaries, success criteria.
- **triggers:**  
  - …
- **inputs:**  
  - …
- **outputs:**  
  - …
- **steps:**  
  1. …  
  2. …  
  3. …
- **roles:**  
  - …
- **dependencies:**  
  - …
- **policies:**  
  - …
- **metrics:**  
  - *Metric name:* definition/formula; owner
- **systems:**  
  - …
- **frequency:** monthly
- **owner_role:** …
- **notes:**  
  Optional clarifications.

**Authoring rules**
- Prefer short sentences; 8–18 words per sentence.
- Avoid acronyms unless already defined in the glossary; otherwise expand once.
- Keep steps at the business level; implementation specifics belong in technical documents.

### 4) Diagrams (Optional)
When diagramming, use text-first description plus an embedded image or a link to a local repository path. Acceptable diagram types:
- **Process flow** (BPMN/UML Activity style)
- **Swimlane** with roles
- **State transitions** (if helpful)

If included, add under each process as `##### Diagram` with a short caption. Store images alongside documentation in a predictable, repo-relative path.

### 5) Cross-Mappings
Provide simple linkages to other knowledge artifacts to keep the catalog discoverable:
- **Glossary terms:** reference canonical term keys used in the process (`terms:` bullet list).
- **Use cases & personas:** reference use-case IDs or persona IDs when the process explicitly serves them.
- **Data/Reports:** name the metrics or dashboards the process produces or feeds.

**Format**

```
- terms:
  - <TERM_ID> - <Term Name>
- use_cases:
  - <UC-0001> - <Use case short title>
- personas:
  - <P-ROLE-1> - <Persona title>
- data_products:
  - <ID or Name>
- dashboards:
  - <ID or Name>
```

### 6) Governance & Maintenance
- **Stewardship:** Declare the stewarding role(s) responsible for the catalog’s integrity.
- **Update triggers:** Add/change processes when scope, outcomes, or controls change.
- **Review cadence:** At least quarterly; document outcomes in the Change Log.
- **Quality gates (pre-merge):**
  - All **MUST** fields present.
  - `process_id` unique; no gaps required but recommended.
  - Steps are numbered and outcome-oriented.
  - Inputs/Outputs are concrete and testable.
  - Roles are role-based (no personal names).
- **Deprecation policy:** Mark entries as *Deprecated* with rationale and effective date; keep until no references remain, then remove in next review.

### 7) Change Log
Maintain an append-only log at the end of the file.

| date (YYYY-MM-DD) | change_type | process_ids | summary | editor |
|---|---|---|---|---|
| 2026-03-09 | created | BP-0001..BP-0003 | Initial catalog scaffold | <role> |

---

## Validation Rules (Machine-Checkable)
- **File name** equals `KNW-02.md`.
- **Top-level sections** present and in order as specified.
- Every process entry:
  - Heading matches regex: `^#### BP-\d{4} — .+$`
  - Contains all **MUST** fields from the schema.
  - `frequency` value, if present, is in the allowed enum.
  - `roles` list contains role names (no emails or personal names).
- **IDs**
  - `process_id` format: `BP-` + four digits.
  - Uniqueness of `process_id` across file.
- **Links/Refs**
  - Cross-mappings, if used, only reference IDs that exist in their respective documents.

## Editorial Style
- English language.
- Use active voice; avoid future tense unless necessary.
- Keep paragraphs <= 5 lines; prefer bullets for lists.
- Avoid tool/vendor names unless essential to understanding the business outcome.

## Examples (Non-Normative)
Add 1–3 example processes as templates to accelerate authoring; remove them once real content is added.

#### BP-0002 — Customer Return Handling
- **description:** Handles customer product returns from initiation to refund/credit note completion.
- **triggers:**  
  - Customer initiates return
- **inputs:**  
  - Return request, proof of purchase
- **outputs:**  
  - Approved/Rejected decision, refund/credit note
- **steps:**  
  1. Validate request and eligibility.  
  2. Determine disposition (restock, scrap).  
  3. Issue refund/credit note and notify customer.
- **roles:**  
  - Customer Support (R)  
  - Warehouse Supervisor (C)  
  - Finance Analyst (A)
- **dependencies:**  
  - BP-0007
- **metrics:**  
  - Return cycle time (Owner: Ops)  
  - % returns resolved < 5 business days (Owner: Ops)
- **systems:**  
  - Ticketing, ERP
- **frequency:** daily
- **owner_role:** Operations Lead
- **notes:** None.

## Operational Guidance
- Start by listing processes that directly produce product outcomes or key business artifacts.
- Prioritize high-impact, high-frequency processes.
- Keep language accessible for non-technical stakeholders.

## Acceptance Checklist (for Reviewers)
- [ ] File name is `KNW-02.md`.
- [ ] All top-level sections are present and correctly ordered.
- [ ] Each process entry includes all **MUST** fields and passes regex/enum checks.
- [ ] Steps are numbered, concise, and outcome-focused.
- [ ] Roles are roles, not individuals.
- [ ] Cross-mappings (if present) use valid IDs.
- [ ] Change Log updated for this revision.