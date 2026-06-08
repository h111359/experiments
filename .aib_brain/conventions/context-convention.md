# Convention: context.md

## Purpose

This convention defines the required structure, atomic statement format, formatting rules, and quality gates for `.aib_memory/context.md`. It is the single authoritative source for the structure of `context.md` and MUST be referenced by the `aib-refresh-context.md` prompt.

This convention is product-agnostic and MUST NOT embed assumptions about any specific product's domain taxonomy or folder structure.

## Applicability

This convention applies to every `.aib_memory/context.md` file in every workspace that uses the AIB framework, regardless of product domain, industry, or technology stack.

## Normative Language

The key words MUST, MUST NOT, SHALL, SHOULD, MAY, and OPTIONAL in this document are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174).

## Document Identity

- **Canonical file path:** `.aib_memory/context.md`
- **Encoding:** UTF-8
- **Format:** Markdown only. No HTML tags, no images, no external hyperlinks.
- **Authoring model:** Generated or modified by the `aib-refresh-context.md` prompt. Also modified by `edit-context.py` for individual statement CRUD operations. Human edits are not expected but possible.
- **Replacement semantics:** Full-file replacement applies during `aib-refresh-context.md` execution. Individual statement operations via `edit-context.py` use targeted line-level insert/delete.

---

## Section Structure

### Mandatory Section Order

The document MUST contain the following sections, in order:

1. `## 1. Product Identity` — product name, purpose, primary actors.
2. One `## <AREA>` section per active knowledge area (H2, two-letter area code only — e.g., `## FN`, `## PO`). Include only areas with at least one statement.
3. `## Files` — workspace file inventory in indented tree format.

### Optional: Aliases Block

An optional `Aliases:` line MAY appear before `## 1. Product Identity`. Format:

```
Aliases: SHORT=Long Name, SHORT2=Another Long Name
```

Use short aliases exclusively in all statements when a long name repeats frequently.

### Empty Area Sections

If an area has no statements, omit the section entirely. Do NOT output empty headings or stub notices explaining missing data.

### No Wrapper Headings

The document MUST NOT contain `## 2. Statements` or `## 3. Workspace File Inventory` wrapper headings. Area sections appear directly at H2 level.

---

## Section 1 — Product Identity

Establish product identity: name, purpose, audience.

MUST include:
- Product name.
- One-paragraph purpose statement.
- Primary actors/users.

SHOULD include:
- Key business outcome.
- Scope boundaries (what product does NOT cover).

MUST NOT include:
- Technical implementation details (belong in TD or TS).
- Marketing copy or aspirational language.
- Version/status metadata — rely on Git for versioning.

Format:
- Atomic statements where possible, free-form prose if not.
- No bold, italic, or backtick formatting.

---

## Area Sections (H2)

### Valid Area Codes

The following 22 two-letter codes are valid area identifiers:

| Code | Area |
|------|------|
| PO | Project overview |
| CM | Change Management |
| DO | Domain |
| CO | Concepts |
| BP | Best Practices |
| FN | Functionality |
| TD | Technical Design |
| TS | Technology Stack |
| NW | Networking and Connectivity |
| DS | Data structures |
| DF | Data flow |
| PR | Processes |
| AN | Analytics |
| UI | User Interface |
| SC | Security |
| PF | Performance |
| OP | Operations |
| DV | Development |
| DP | Deployment |
| DR | Durability |
| OB | Observability |
| DM | Documentation |

### Atomic Statement Format

Each statement is a single Markdown bullet line:

```
- <TYPE>: <text>
```

Where:
- `<TYPE>` — Single-letter statement type identifier (see Statement Types below).
- `<text>` — Statement content in concise, telegraphic phrasing.

**Example:**

```
- R: User auth uses JWT tokens with 1h expiry.
- D: Flat Markdown files used instead of db for max portability.
- N: Request lifecycle: create -> analyze -> plan -> implement -> close.
```

### Statement Types

| Letter | Type | Description |
|--------|------|-------------|
| N | Definition | Defines a concept, entity, or term. |
| R | Requirement | A functional or non-functional requirement. |
| C | Constraint | A limitation or boundary condition. |
| E | Reference | Points to an external resource or artifact. |
| L | Relationship | Describes a connection between entities. |
| U | Rule | A business or technical rule. |
| A | Assumption | Something assumed to be true. |
| D | Decision | An architectural or design decision. |
| I | Information | General factual information. |

Note: Open/unresolved questions MUST NOT be stored in context.md. Use input.md for open questions.

### Statement Addressing

Statements are addressed by type letter and text content. Tool scripts use text-based line matching for CRUD operations. Statement text MUST be unique within its area section to allow unambiguous addressing.

### Uniqueness Invariant (Normative)

Statement text MUST be unique within each area section (case-insensitive). Duplicate statement texts within the same area are PROHIBITED. The `edit-context.py` tool validates this invariant on every insert operation.

### Telegraphic Language

Statements MUST use concise, telegraphic phrasing. Omit unnecessary articles (a, an, the) and helper verbs (is, are, must be). Always use standard abbreviations: req, res, auth, db, env, config, err, msg, btn.

### Granularity Principle

Each statement SHOULD express exactly one fact. Exception: tightly coupled properties of a single named entity MAY be grouped into one statement using an inline list (e.g., `- R: User table columns: email (unique), password_hash`).

### Completeness Principle

Statements MUST be detailed enough that the full workspace context can be reconstructed from them alone (in combination with Section 1 and Files). A competent developer reading only `context.md` must understand what the product does, why key decisions were made, and how the system works.

### Logic Notation

For logic and flow statements, prefer pseudo-code and logic operators (`->`, `&&`, `||`, `==`, `!=`) over natural language when the expression is shorter.

---

## Files Section

### Format

Use an indented tree format:

```
## Files

.aib_memory/
  context.md — product context synthesis
  requests_register.md — all requests with state
.aib_brain/tools/
  verify-context.py — validates context.md format
scripts/
  release_bookkeeping.py — SemVer bump and log generation
```

### Inclusion Rules

Only list directories and core architectural files. Ignore tests, config files, assets, and minor utilities unless they contain critical business logic.

When a directory contains three or more items sharing a repeating naming pattern (e.g., per-request subfolders, versioned logs), provide a single summary line:

```
logs/ — Contains N versioned log files following pattern version_vX.Y.Z_log.md.
```

---

## Formatting Rules

1. The document MUST be UTF-8 encoded Markdown.
2. The document MUST NOT contain HTML tags.
3. The document MUST NOT contain images.
4. References to external sources MUST be plain text only.
5. Heading levels MUST follow this hierarchy:
   - `# Product Context` — document title (H1, exactly one).
   - `## 1. Product Identity`, `## <AREA>`, `## Files` — top-level sections (H2).
   - `### <Sub-area Name>` — MAY be used for sub-areas (H3).
   - H4 and deeper MUST NOT be used.
6. Statements MUST NOT use bold, italic, or inline code formatting (backticks). Plain text only.
7. Statement lines MUST use Markdown bullet syntax (`- `) followed by the type letter, colon, and text.
8. Traceability references MUST be plain text, not hyperlinks.
9. Markdown tables MUST NOT appear anywhere in the document.
10. Each atomic statement MUST occupy exactly one line (no line wrapping or continuation lines).
11. Heading nesting MUST NOT exceed H3 (`###`) in any section.
12. No preamble or version metadata is required. Version tracking is via Git.

---

## Pruning Rules

Aggressively delete historical context, past design iterations, and resolved open questions. Do not retain deprecated features. context.md must represent only the CURRENT state of the application.

---

## No Negative Space

Do not state standard defaults (e.g., API returns JSON, uses REST). Do not document negative space (e.g., No caching implemented) unless it overrides a standard expectation. Document only custom business logic and deviations.

---

## Quality Gates

A generated `context.md` passes quality review if and only if all of the following are true:

1. **Title present:** Document begins with `# Product Context`.
2. **Product Identity present:** `## 1. Product Identity` section is present.
3. **Area headings valid:** Every H2 heading (except `## 1. Product Identity` and `## Files`) uses a recognized two-letter area code.
4. **At least one area section:** At least one valid area section is present.
5. **Area sections non-empty:** Every area section that appears has at least one statement.
6. **Statement format compliance:** Every statement line in area sections matches `- <TYPE>: <text>` with a valid single-letter type.
7. **Statement uniqueness:** No two statements in the same area section have identical text (case-insensitive).
8. **No external hyperlinks:** The file contains no `http://` or `https://` strings.
9. **No HTML tags:** The file contains no HTML tags.
10. **No tables:** The file contains no Markdown table syntax.
11. **Product Identity non-empty:** `## 1. Product Identity` has at least 3 lines of substantive content.

---

## Relationship to Other Conventions

- This convention governs ONLY `.aib_memory/context.md`.
- It does NOT govern any `.aib_brain/` framework files.
- The `aib-refresh-context.md` prompt MUST reference this convention as the sole structural authority for `context.md`.
