Purpose
The purpose of this convention is to define a precise, portable, and AI-friendly format for the Product Charter document. It standardizes naming, content structure, field semantics, and editing/validation rules so both humans and AI tools can create, read, and verify the document consistently.

Scope
This convention applies only to the Product Charter document that captures the high‑level overview of a product: its name and definition, the stakeholders affected, and the mandatory roles assigned to real people. It does not prescribe where the file is stored.

Outcomes
- Deterministic file name and single-file format
- Clear, minimal sections with normative field definitions
- Machine-checkable constraints for each field
- Human-verifiable checklists for completeness and quality

File Naming
- File name: RQT-01.md
- Character set: ASCII letters, digits, dash, and dot only
- Exactly one file per product; duplicates are not allowed

Document Structure (Headings and Order)
1. Product Name
2. Product Definition
3. Stakeholders
4. Roles and Assignments
5. Acceptance Checklist

Section Specifications
1. Product Name
   - Content: A concise name, preferably no longer than 5 words.
   - Constraints:
     - Must be a single line
     - Max 60 characters
     - Avoid internal abbreviations unless widely recognized

2. Product Definition
   - Content: Short description explaining what the product is and why it exists.
   - Constraints:
     - Prefer 1 to 5 short paragraphs
     - Each paragraph up to 3 sentences
     - Avoid marketing language; be factual and outcome-oriented

3. Stakeholders
   - Content: List of stakeholder groups or specific stakeholders affected by the product.
   - Format:
     - Unordered list; one stakeholder per bullet
   - Constraints:
     - Each item must be a clear noun phrase (e.g., Sales Leadership, Data Governance Council)
     - Avoid duplications and ambiguous labels

4. Roles and Assignments
   - Content: Mandatory roles and their assigned real persons.
   - Mandatory roles:
     - Business Owner (budget holder and decision taker)
     - Data Owner (if different from Business Owner)
     - Product Owner
     - Technical Owner
     - Technical Team
     - Known Subject Matter Experts
   - Format:
     - One sublist item per role with fields:
       - Person or Team: Full name(s) or team name
       - Title: Official job title
       - Contact: Corporate email or preferred channel
       - Notes: Optional clarifications
   - Constraints:
     - Business Owner must be specified
     - If Data Owner differs from Business Owner, specify explicitly; otherwise note "Same as Business Owner"
     - At least one Technical Team entry is required
     - Contacts must be reachable corporate channels

5. Acceptance Checklist
   - A machine- and human-verifiable checklist confirming required content is present and unambiguous.
   - Required checklist items:
     - Product Name present and within limits
     - Product Definition present and within limits
     - Stakeholders listed with no duplicates
     - Business Owner assigned with contact
     - Data Owner handled (different person specified or "Same as Business Owner")
     - Product Owner assigned with contact
     - Technical Owner assigned with contact
     - Technical Team identified with contact
     - SMEs listed or "None"
     - Document reviewed by Product Owner

General Formatting Rules
- Language: English
- Tone: Clear, factual, and concise
- Lists: Use simple bullet lists; avoid nested lists deeper than one level
- Tables: Avoid unless strictly necessary; prefer lists for readability
- IDs, links, and paths: Do not include file system paths or external links
- Avoid placeholders like TBD; use "None" if truly not applicable

Editing Rules
- Single-source-of-truth: Maintain exactly one Product Charter per product
- Replace vs. append: Edits may replace sections in full; keep the structure and order intact
- Change tracking: Capture rationale for material changes in the commit message or adjacent change log, not inside the document body

Validation Rules (for Automation)
- File name equals RQT-01.md (case-sensitive)
- Required sections and order must match "Document Structure"
- Role completeness:
  - Business Owner, Product Owner, Technical Owner, and Technical Team must be present with contacts
  - Data Owner rule respected (different person specified or explicitly "Same as Business Owner")
- Length limits respected (Product Name and Definition)
- No disallowed content:
  - No storage locations
  - No external links
  - No confidential secrets or tokens

Quality Guidance (Non‑Normative)
- Ensure Product Definition states intended outcomes and primary users
- Keep stakeholder list focused; avoid generic "All employees"
- Use consistent job titles and organization naming
- Prefer distribution lists for team contacts when applicable

Example Skeleton (Illustrative Only)
# Product Name
Acme Demand Signals

# Product Definition
A concise description of the product's purpose and scope written in 1–3 short paragraphs.

# Stakeholders
- Sales Leadership
- Revenue Growth Management
- Data Governance Council

# Roles and Assignments
- Business Owner:
  - Person or Team: Jane Doe
  - Title: VP, Commercial Excellence
  - Contact: jane.doe@example.com
  - Notes: Budget holder
- Data Owner:
  - Person or Team: Same as Business Owner
  - Title: —
  - Contact: —
  - Notes: —
- Product Owner:
  - Person or Team: John Smith
  - Title: Senior Product Manager
  - Contact: john.smith@example.com
  - Notes: —
- Technical Owner:
  - Person or Team: Priya Patel
  - Title: Engineering Manager
  - Contact: priya.patel@example.com
  - Notes: —
- Technical Team:
  - Person or Team: Data Platform Team
  - Title: —
  - Contact: dataplatform@example.com
  - Notes: —
- Known Subject Matter Experts:
  - Person or Team: Alex Chen; Maria Rossi
  - Title: Domain SME; Analytics Lead
  - Contact: alex.chen@example.com; maria.rossi@example.com
  - Notes: —

# Acceptance Checklist
- [ ] Product Name present and within limits
- [ ] Product Definition present and within limits
- [ ] Stakeholders listed without duplicates
- [ ] Business Owner assigned with contact
- [ ] Data Owner handled (different specified or "Same as Business Owner")
- [ ] Product Owner assigned with contact
- [ ] Technical Owner assigned with contact
- [ ] Technical Team identified with contact
- [ ] SMEs listed or "None"
- [ ] Reviewed by Product Owner