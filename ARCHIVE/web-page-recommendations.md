# GDATD Connect Page — Recommendations (Executive-ready)

Source reviewed: `team-presentation/connect-page-rough.txt`

## 1) Top issues to address

### A. Executive-readiness gaps (CDO audience)
- **No “at-a-glance” summary**: Missing team size, scope, portfolio breadth, coverage model, and measurable impact.
- **Outcomes are not framed as business value**: Achievements list activities, but not the “why it mattered” (risk reduced, cycle time improved, cost avoided, adoption, uptime, compliance).
- **Acronyms and internal shorthand are unexplained**: NSR, CCL, CoE, RED, UDP, DX, SCOT, RGM, CuDa, QSRP, OU, PVP, WoW, SR, UAT, POS, SBS, TCCC, CEE, WE, LATAM.
- **Engagement model is missing**: How stakeholders request work, prioritization approach, lead time expectations, and ownership boundaries.
- **Who we are section is empty**: “Who are the people in the team?” is a placeholder.

### B. Structure and formatting issues
- **Inconsistent heading hierarchy** (some headings look like body text).
- **Bullets are not consistently formatted** (lists are plain lines; long paragraphs mixed with list items).
- **Extra whitespace and empty lines** break readability.
- **Inconsistent capitalization** (e.g., “DevOps Model”, “Web UI”, “Current NSR Web App”).

### C. Language/grammar issues (high impact)
- “**Be technical owner** …” → should be “**We are the technical owners** …” or “**Serve as technical owner** …”.
- “**Leading of vendor teams** …” → should be “**We lead vendor teams** …”.
- “**data clearance**” likely intended as **data cleansing**.
- “**deployment to productive**” → **deployment to production**.
- “**wholistic**” → **holistic**.
- “identify weaknesses and threats, find improvement opportunities” → can be tightened.

### D. Consistency and terminology
- “Data Clearance and Validation” vs “Data Validation” elsewhere: choose one phrase.
- “Programming with” list mixes languages and “AI” (not a language). Suggest “Languages & tools” and list separately.
- “Azure SQL Server” is often referred to as **Azure SQL Database** (unless you truly mean SQL Server on VM).
- “PBI” appears; for exec-facing material use “Power BI” and optionally “(PBI)”.

## 2) Concrete copy edits (typos + rewrites)

You can apply these edits directly to the page copy.

### Quick replacements
- Replace “Data Clearance” → “Data Cleansing”
- Replace “deployment to productive” → “deployment to production”
- Replace “wholistic” → “holistic”
- Replace “PBI” → “Power BI” (or “Power BI (PBI)” on first mention)

### Sentence rewrites
- Current: “Translation of business needs and change requests related to data and analytics area into trustworthy and predictable solutions”
  - Suggested: “We translate business needs and change requests into reliable, predictable data & analytics solutions.”

- Current: “Design, develop, and deploy end-to-end Data and Analytics solutions and especially:”
  - Suggested: “We design, build, and run end-to-end data & analytics products, including:”

- Current: “Be technical owner of data and analytics products ensuring quality standards and best practices, alignment with enterprise architecture and information security requirements”
  - Suggested: “We serve as technical owners of data & analytics products, ensuring quality standards, best practices, enterprise architecture alignment, and information security compliance.”

- Current: “Maintain, troubleshoot, monitor, stabilize and optimize our products, ensure technical strengths, identify weaknesses and threats, find improvement opportunities in data and analytics solutions.”
  - Suggested: “We operate and continuously improve our products: monitoring, incident response, stabilization, performance optimization, and proactive risk reduction.”

- Current: “Leading of vendor teams and contributors as integral extension to our internal team”
  - Suggested: “We lead vendor teams and external contributors as an integrated extension of our internal team.”

### Consistent naming suggestions
- Standardize “NSR 2.0” vs “NSR2.0” (pick one; “NSR 2.0” is more readable).
- Standardize “Web UI” vs “Web App” (define once and use consistently).

## 3) Suggested page structure (CDO-friendly)

This keeps your content but presents it in an executive-consumable format.

### Proposed outline
1. **Title + one-line value proposition**
2. **At a glance** (3–6 bullets)
   - Location, time zone coverage, team size (or range), core roles
   - Portfolio: #products owned, #platforms supported (if you can share)
   - Engagement: intake channel and how you prioritize
3. **Mission & principles** (short)
4. **What we do (capabilities)** (bullet list)
   - Product ownership & operations
   - Data engineering & integration
   - Semantic modeling & analytics engineering
   - Reporting & BI
   - Web tools for data operations/admin
   - Quality, governance, and security alignment
5. **Where we create impact** (initiatives / domains)
   - Group initiatives by business domain (NSR / CCL D&A CoE / DX & UDP)
6. **Outcomes & achievements** (by year)
   - Convert each year to 5–8 concise bullets with value framing
7. **Technology stack**
   - Platforms, orchestration, storage, BI, languages (separate “AI” as “AI/ML tooling”) 
8. **Team & ways of working**
   - Team composition summary
   - Operating model (Agile, DevOps, ownership, vendor management)
9. **Contact / how to engage**
   - A mailbox/Teams channel + who to contact (names optional; role is fine)

## 4) Make achievements “outcome-led” (rewrite pattern)

For executive readability, use a consistent template:
- **Outcome** (what improved) + **what we delivered** (how) + **scope** (where) + **metric** (if available).

Example rewrite patterns (use your real numbers if you can share):
- “Reduced operational effort by ~X% by automating [process], improving month-end close reliability.”
- “Improved platform resilience by introducing self-healing for pipeline/cube failures, reducing incident MTTR.”
- “Enabled faster onboarding/migrations by standardizing CI/CD for Synapse and WebApp components.”

## 5) Specific content gaps to fill (high priority)

Add (even if approximate):
- **Team size** (e.g., “~N people” or “N–M range”).
- **Service footprint**: #business units supported, #countries, #data products.
- **Operating SLAs / support model**: e.g., business hours + on-call (if applicable).
- **Intake & governance**: where requests go, how priorities are set, who approves.
- **Security & compliance posture**: a single sentence is enough (“aligned with enterprise architecture and InfoSec requirements; least privilege; audited pipelines; etc.”).

## 6) Acronyms: add a glossary (must-have)

Add a short glossary at the bottom (or hover definitions if the web platform supports it). At minimum define:
- NSR, CCL, CoE, RED, UDP, DX, SCOT, RGM, CuDa, QSRP
- OU, PVP, WoW, SR, UAT
- POS, SBS, TCCC, CEE, WE, LATAM

## 7) Technologies section: normalize and de-duplicate

Suggested grouping (edit to match your reality):
- **Azure**: Synapse Analytics, Data Factory, Databricks, Storage (ADLS), Functions, Logic Apps, Azure SQL Database, Azure DevOps
- **Analytics**: Analysis Services, Power BI
- **Languages**: Python, SQL, DAX, C#
- **AI**: (specify what you mean—e.g., “GenAI-assisted development”, “ML experimentation”, “document processing”, etc.)

## 8) Proposed “polished” version (ready-to-paste draft)

Below is a cleaned-up draft based on your content. Replace bracketed items with your specifics.

---

## Global Data Technologies Delivery Team (GDATD)

**Mission**
We deliver end-to-end, high-quality data & analytics products and future-ready platforms that empower business growth. We own and evolve these products as one global team, with passion, accountability, and craftsmanship.

**At a glance**
- Location: Sofia, Bulgaria (Global Delivery Center Sofia)
- Roles: Data & Analytics Solution Architects, Data Engineers, Data Analysts, Agile Project Managers
- Scope: End-to-end product ownership, delivery, and operations for global and regional data & analytics initiatives
- Engagement: [intake channel / governance]

**Principles**
Empowerment, tolerance, inclusion, continuous improvement, and agility.

### What we do
- Translate business needs into reliable and predictable data & analytics solutions
- Explore and analyze data to inform solution design
- Design, build, and run end-to-end data & analytics products, including:
  - Data cleansing and validation
  - Data integration and matching
  - ELT/ETL development and automation
  - Semantic layer and analytical modeling
  - Visualization and reporting
  - Web interfaces for data processing and product administration
- Serve as technical owners: quality standards, best practices, enterprise architecture alignment, and information security compliance
- Operate and continuously improve products (monitoring, incident response, stabilization, performance optimization)
- Lead vendor teams and external contributors as an integrated extension of our team

### Key initiatives
**Global D&A Engineering**
- NSR 2.0: technical ownership, development, and support

**Customer & Commercial D&A Center of Excellence**
- RED Certification
- Metro Surveys
- Sodexo Surveys
- Metro SCOT Reporting
- RGM Template Generator
- Customer Data (CuDa): Carrefour, Metro, QSRP

**Contributions to platforms owned by other teams**
- DX 1.0 (Data Exchange) platform
- UDP engineering and integration

### Technology stack
Azure Synapse Analytics, Azure Storage Services, Azure Functions, Logic Apps, Azure Analysis Services, Azure Databricks, Azure Data Factory, Azure SQL Database, Azure DevOps, Power BI

Languages: Python, SQL, DAX, C#

### Achievements (selected)
**2025**
- NSR Web Migration
- NSR Japan Migration
- RED Assessments Application launch
- Customer Success (Metro Survey) Application launch
- RGM Africa OU PVP template refresh automation
- DX Rule Engine contribution; UDP streaming solution; UDP operations support

**2024**
- Implemented self-healing mechanisms in NSR for cube and pipeline failures
- Completed EME & Africa mergers
- Delivered full Web UI migration (production target: end of Jan 2025)
- Simplified and automated the audit process
- Advanced NSR Global v2 technology
- Fine-tuned the DevOps model, reducing operational effort
- Built CI/CD workflows for Synapse and WebApp components
- Automated service requests via Data Steward Panel (target: 80% reduction of upload/sync SRs)
- NSR Japan integration kick-off: scope, feasibility, migration plan, and post-go-live ways of working
- Took over Coke&GO Analytics technical ownership and development
- Delivered Customer Data (CuDa) analytics and dashboards (Carrefour shoppers KPIs; POS/SBS enhancements)
- Delivered shared Power BI dashboards for Sodexo and Metro Surveys
- Delivered RED Certification web app infrastructure in UAT; kicked off Metro application infrastructure

**2023**
- Established the NSR DevOps model
- NSR 2.0 go-live (April) and stabilization within one year, supporting month/half-year/full-year closes
- Migrated error reporting for NSR Data Governance anomaly detection
- Transitioned reporting model from CEE/WE business units to one Europe OU
- Enhanced Profit Center functionality and regional hierarchies
- Increased processing concurrency through batching
- Expanded self-service capabilities and automation to reduce operational effort
- Contributions: BEACH data migration in UDP; Smart OPEX report rewiring to Finance HUB

---

## 9) Final checklist before sending to the CDO
- Add a 3–5 bullet **impact summary** (with metrics if permitted).
- Add an **engagement model** (how to request + prioritization).
- Add a **glossary** for acronyms.
- Ensure each section is consistently formatted (headers + bullets).
- Remove placeholders (“Who are the people in the team?”) or replace with a short team composition summary.
