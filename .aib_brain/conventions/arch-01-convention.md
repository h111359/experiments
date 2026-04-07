Purpose
Define the exact format, content, and operating rules for the “ARCH-01 — High‑level architecture” document so AI tools can generate it deterministically and humans can verify it quickly.

Applicability
This convention applies to the single documentation file that fulfills requirement ARCH-01 — High‑level architecture. The file provides a product‑level, technology‑agnostic overview that enables independent understanding without additional knowledge transfer.

## File Naming
- **File name:** `ARCH-01.md`
- **One file only** for the complete glossary (no per-term files).
- **Character set:** UTF-8, Unix line endings (`\n`).

Do Not Include
- Marketing statements, vendor pitches, or non-architectural details.
- Deep implementation specifics (move those to component or compute docs).

Document Structure (normative)
Produce the following sections in the exact order and with the exact headings:

1) Summary
   - 1–3 short paragraphs describing the product’s purpose, main capabilities, and architectural stance (e.g., batch/streaming, cloud/on‑prem, modular/monolith).
   - Include a one‑line “Architecture-in-a-sentence”.

2) System Context
   - Provide a concise text description of external actors/systems and how they interact with the product.
   - Include a simple context diagram (ASCII or Mermaid is allowed) that shows the product as a single box with inbound/outbound integrations.
   - Each external integration must be named and referenced in the Data Flows section.

3) Component Inventory (required table)
   Create a table with one row per component. Required columns (use these exact column names):
   - Component name
   - Description
   - Purpose
   - Location (runtime/execution location or repo/subsystem)
   - Group or category (e.g., Ingestion, Processing, Storage, Serving, UI, Security, Orchestration)
   - Component tier (e.g., Presentation, Application, Data, Infrastructure) — leave empty if N/A
   - Connections and dependencies (comma-separated component names)
   Rules:
   - Every component named in any diagram must have a row here.
   - Names must be unique within this file.
   - If a dependency is not in inventory, either add it or justify as external in System Context.

4) Data Flows
   - List major data flows between components and to/from external systems.
   - For each flow specify: Source → Target, transport/protocol (e.g., REST, gRPC, JDBC, file drop, event bus), format (e.g., JSON, Parquet), trigger/cadence (e.g., batch hourly, streaming), and directionality.
   - Keep flows high‑level; implementation detail belongs in compute/pipeline specs.

5) Environments & Topology (high‑level)
   - Identify environments (Dev/Test/Staging/Prod or equivalents).
   - Summarize where components run (e.g., VNet/Subnet/Namespace/Cluster) without deep network specifics.
   - If a component is environment‑specific (exists only in Prod), state it.

6) Quality Attributes (overview)
   - Briefly explain how the architecture supports key attributes: scalability, reliability, performance, security, cost efficiency, observability, and operability.
   - Bullet points only; link to respective domain documents (e.g., DEV/SEC/OBS) via relative paths if available.

7) Assumptions & Constraints (summary)
   - List only those that materially shape the architecture (others live in RQT-04).
   - If a constraint conflicts with any referenced standard, document the exception and rationale.

8) Key Risks & Mitigations (optional but recommended)
   - Top 3–10 architectural risks with a one‑line mitigation each.

9) Traceability
   - Map components and flows to requirements/use‑cases or metrics where relevant (IDs only; detailed content lives in their respective documents).
   - Include a small table with columns: Artifact type, ID, Short note.

10) Change Log (lightweight)
   - Reverse‑chronological bullet list of meaningful architectural changes (date; short description; reference to request/iteration ID).
   - Keep it concise; this is not versioning.

Formatting Rules
- Language: English.
- Use GitHub‑flavored Markdown only.
- Tables: use standard pipes; no HTML tables.
- Diagrams: Prefer Mermaid or compact ASCII; keep node names identical to Component Inventory.
- Wrap lines at ~120 characters for readability.
- Use consistent casing for component names across sections.

Deterministic Generation Hints (for AI tools)
- If inputs are incomplete, generate a “Known gaps” note at the end of the affected section with bullet points of required information.
- Infer sensible defaults conservatively; never invent component names not derivable from context.
- When conflicting inputs exist, prefer the latest iteration inputs (higher iteration ID) and add a one‑line “Conflict resolution” note to Change Log.

Validation Checklist (must pass before accepting)
- [ ] All required sections exist and follow the exact heading names/order.
- [ ] Component Inventory table exists and includes every diagrammed component.
- [ ] No duplicate component names; all dependencies resolve to known components or declared externals.
- [ ] Every external integration in System Context is referenced in Data Flows (and vice versa).
- [ ] Environments section mentions where each critical component runs (at least Prod).
- [ ] Quality Attributes mention observability and security at minimum.
- [ ] Traceability table has valid IDs that exist elsewhere in the docs set (if references.md lists them).
- [ ] No prohibited metadata headers are present.
- [ ] Change Log contains at least one entry after initial creation (on subsequent edits).

Editing Rules
- “Do not change” blocks: A human may wrap any subsection in a fenced code block starting with the literal line: DO_NOT_CHANGE. AI tools must not modify content inside such blocks and should append updates below them.
- Section appends: When AI updates a section, it may replace the whole section (preferred) or append a clearly labeled “Update (YYYY‑MM‑DD)” subsection. Do not interleave edits line‑by‑line.
- Cross‑file links: Use workspace‑relative Markdown links if the target exists in references.md and edit_allowed=Y; otherwise, include the ID as plain text without a link.

Minimal Example (illustrative)
Summary
- Architecture-in-a-sentence: Batch ingestion → curated storage → serving layer with scheduled transformations and APIs.

System Context
- External: Source ERP, CRM, Identity Provider, BI Portal.

Component Inventory

| Component name | Description                      | Purpose                      | Location              | Group or category | Component tier | Connections and dependencies      |
|---|---|---|---|---|---|---|
| Ingestion Agent | Reads source ERP exports         | Land raw files               | Data Lake / raw zone  | Ingestion         | Data           | Scheduler, Raw Storage            |
| Scheduler       | Orchestrates batch pipelines     | Trigger/monitor workloads    | Orchestrator service  | Orchestration     | Application    | Ingestion Agent, Transformer      |
| Transformer     | Applies cleansing & modeling     | Produce curated datasets     | Compute cluster       | Processing        | Application    | Raw Storage, Curated Storage      |
| API Service     | Serves curated datasets          | External consumption         | App service           | Serving           | Presentation   | Curated Storage, Identity Provider|

Data Flows
- ERP → Ingestion Agent (SFTP; CSV; hourly batch)
- Ingestion Agent → Raw Storage (object copy; CSV)
- Transformer → Curated Storage (Spark; Parquet; scheduled)
- API Service → BI Portal (HTTPS/JSON; on-demand)

Operational Notes
- Keep this file high‑level; detailed compute logic belongs to CMP‑01/CMP‑02; network specifics belong to ARCH‑02; capacity belongs to ARCH‑03.

Acceptance Criteria (for reviewers)
- The file enables a new engineer to draw the main system diagram and list core components without external briefings.
- The architecture’s primary data paths are understandable in under 10 minutes of reading.