## Purpose
Define a simple, stable structure for the Requirements Document so AI tools can generate, read, and update it reliably with minimal parsing complexity.

## File Name
RQT-02.md

## Required Sections
The document MUST contain exactly these sections in the following order:

1. **Summary**
2. **Functional Requirements**
3. **Non-Functional Requirements**
4. **Acceptance Criteria**
5. **Assumptions**
6. **Constraints**

No other top‑level sections are allowed.

---

## Section Rules

### 1. Summary
Short free text (1–3 paragraphs).  
Explains what the product should achieve overall.

### 2. Functional Requirements
A flat list.  
Each line is one requirement in this exact pattern:

`FR-###: <short requirement text>`

- ID is numeric, zero‑padded (001, 002, 003…).  
- Text is a single sentence.  
- No sub‑bullets, no additional fields.

Example:  
`FR-002: The system exports filtered records to CSV.`

### 3. Non-Functional Requirements
Same pattern as functional requirements:

`NFR-###: <short requirement text>`

Short single sentence per requirement.

Example:  
`NFR-003: P95 latency must stay under 300 ms under normal load.`

### 4. Acceptance Criteria
A numbered list of short criteria.

Example:  
1. The export reflects active filters.  
2. CSV contains header row.

### 5. Assumptions
Simple bullet list.  
Each bullet is one sentence.

### 6. Constraints
Simple bullet list.  
Each bullet is one sentence.

---

## Writing Rules
- All requirements MUST fit on one line each.  
- No tables, no nested lists, no multi‑paragraph fields.  
- No rationale, owner, priority, or metadata fields.  
- Use clear, verifiable statements.  
- IDs MUST NOT change once created.

---

## Maintenance Rules
- New requirements are appended at the end of the respective list.  
- Deleting a requirement is not allowed (mark it as: `FR-005: (Deprecated) <old text>`).  
- Section order must remain unchanged.  
- Empty sections are allowed but must be present.