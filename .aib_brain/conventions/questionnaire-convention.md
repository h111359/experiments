# questionnaire Convention
Purpose
-------
Define a deterministic, user-friendly convention for generating, structuring, and operating iteration questionnaires so that all questions whose answers can materially change design, implementation, or delivery outcomes are asked early, answered easily, and traceably acted upon.

Scope
-----
This convention applies to every questionnaire file created per iteration of an Active request under:
- `.aib_memory/requests/<request-folder>/<ITERATION_ID>-questionnaire.md`
- `<ITERATION_ID>` is a two-digit token (`01`, `02`, …).
- The request folder, iteration register, and other artifacts follow the AIB lifecycle and file rules.
Questionnaires produced outside this path or naming scheme are out of scope.

Location and File Naming (Normative)
------------------------------------
- File path (relative): `.aib_memory/requests/<request-folder>/<ITERATION_ID>-questionnaire.md`
- `<ITERATION_ID>` format: two digits, regex: `^[0-9]{2}$`
- Exactly one questionnaire file **MAY** exist per iteration. If regenerated, it **MUST** overwrite the same file deterministically.

Operational Contract (Normative)
--------------------------------
- Generation:
  - The questionnaire **MUST** be generated only when a request and an active iteration are resolved.
  - The content **MUST** derive from the current request context + analysis (if present) + project documentation domains (Architecture, Data, Development, Security, etc.).
- Idempotency:
  - With identical inputs, regeneration **SHOULD** converge to identical content and question ordering.
- Safety:
  - On missing active iteration or unresolved request, generation **MUST** fail without writes.
- Supersession:
  - If multiple iterations exist, the questionnaire with the highest `<ITERATION_ID>` is considered authoritative for conflicting answers.
- Editing:
  - Human edits are expected and supported. The format **MUST** make selecting answers trivial (checkboxes) and adding free-text answers safe.
- Consumption:
  - Answers from the active iteration’s questionnaire **MUST** be the canonical source for plan generation and subsequent implementation notes.
- Traceability:
  - Each question **MUST** carry a stable `QID` to persist across regenerations within the same iteration. If text changes but intent remains, `QID` remains unchanged.

Document Structure (Normative)
------------------------------
Questionnaires **MUST** follow the structure and heading order below:

1. Business & Functional Questions
2. Architecture & Technical Questions
3. Appendix — Answer Encoding Rules

Section Content Rules
---------------------

### 1) Business & Functional Questions
- Questions organized by functional themes relevant to product scope (e.g., Objectives, Success Metrics, Users & Personas, Use Cases, Governance, Compliance, Rollout, Support).
- Each question block MUST use the canonical **Question Block** format (defined below).
- Include only questions whose answers can materially alter scope, acceptance criteria, or delivery sequencing.
- Business and Functional Questions **MUST** ensure enough information is collected for fulfillment of the **Business & Functional Documents** documents described in `.aib_brain\conventions\product-documentation-convention.md` and located as per `.aib_memory\references.md` file

### 2) Architecture & Technical Questions
- Questions organized by technical/architectural themes (e.g., Runtime Architecture, Data Strategy, Storage, Interfaces & APIs, Security & Access, Dev/Test/Release, Observability, Operations, DR/BCP, Cost).
- Each question block MUST use the canonical **Question Block** format.
- Include only questions whose answers can materially alter system design, build, or operational posture.
- Architecture and Technical Questions **MUST** ensure enough information is collected for fulfillment of the **Architecture & Technical** documents described in `.aib_brain\conventions\product-documentation-convention.md` and located as per `.aib_memory\references.md` file


### 3) Appendix — Answer Encoding Rules
- Define exact symbols and validation rules for checkboxes and answer blocks.
- Provide examples for each answer type and how tools should parse them.

Canonical Question Block Format (Normative)
-------------------------------------------
Every question **MUST** follow this exact structure and field order. Fields marked **(Req.)** are required.

**QID** (Req.):  
- Stable ID with domain prefix and numeric suffix:  
  - Business/Functional: `QID-BF-###` (e.g., `QID-BF-001`)  
  - Architecture/Technical: `QID-AT-###`
- Once emitted for an iteration, the QID **MUST NOT** change unless the question is deleted.

**Intent** (Req.):  
- One sentence describing the decision being solicited (what trade-off or configuration is selected).

**Rationale** (Req.):  
- 1–3 sentences explaining *why* this question matters and where it impacts downstream artifacts (plan, docs, code, infra).

**Impact Areas** (Req.; pick any that apply):  
- `Scope`, `Requirements`, `Architecture`, `Data`, `APIs`, `Security`, `Observability`, `Operations`, `DR`, `Cost`, `Timeline`, `User Experience`, `Compliance`.

**Assumptions** (Opt.):  
- Bullet list of assumptions this question currently relies on.

**Answer Type** (Req.):  
- One of: `single-select`, `multi-select`, `free-text`, `numeric`, `date`, `toggle (Y/N)`.

**Options** (Conditional):  
- Required for `single-select` or `multi-select`.
- 3–6 curated options labeled `A)`, `B)`, `C)`, `D)`, … ordered from most to least likely in this project context.
- Exactly one option **MAY** be tagged with `(recommended)`.
- Each option is followed by a short (≤ 15 words) impact hint.

**Selection UI** (Conditional):  
- For `single-select` or `multi-select`, present as a Markdown checklist, one line per option:
  - `- [ ] A) <label> — <impact hint>`
- Include the final item:
  - `- [ ] Other — (describe below)`

**Constraints & Guards** (Opt.):  
- Short rules about incompatible selections or mandatory follow-ups.

Parsing & Validation Rules (Normative)
--------------------------------------
- Checkbox syntax:
  - Unchecked: `- [ ]`
  - Checked: `- [x]` (lowercase x or uppercase X)
- Single-select validation:
  - Exactly one option **MUST** be checked; `Other` counts as an option if checked.
- Multi-select validation:
  - Any number of options **MAY** be checked; if none are checked, treat as unanswered.
- Free-text/numeric/date:
   - Numeric/date answers **SHOULD** include units or format hints in the box.
- Completion definition:
  - A question is “answered” when its selection state is valid and any required `Answer Box` is non-empty.

Authoring Guidance for Questions (Informative)
----------------------------------------------
- Focus only on forks that significantly change implementation, architecture, or delivery (avoid cosmetic questions).
- Keep the **Intent** crisp; avoid jargon—prefer plain language with business meaning.
- Options must be mutually distinguishable and map to concrete implementation choices (e.g., “SQL DB (Postgres)” vs “Object store (Parquet)”).
- Provide just enough context in **Rationale** so a non-technical owner can answer confidently.
- Limit question blocks to ≤ 13 lines when possible.

Appendix — Answer Encoding Rules (Normative)
--------------------------------------------
- Checkbox:
  - Unchecked: `- [ ]`
  - Checked: `- [x]`
- “Recommended” marking:
  - Exactly one option **MAY** include the literal string `(recommended)`.
- Single-select validation:
  - Exactly one `- [x]` among the listed options (including `Other`).
- Multi-select validation:
  - Any number of `- [x]`; zero is allowed but treated as unanswered.
- “Other”:
  - If `Other` is `- [x]`, the Answer Box **MUST** contain non-empty text.
- Free-text/numeric/date:
  - Answers **MUST** be placed inside the provided fenced block.
- Parser hints:
  - QID is the primary key for question blocks.
  - The first heading line after a blank line indicates a new question block if it matches `^### QID-(BF|AT)-[0-9]{3} —`.
  - Fields appear in the fixed order defined in “Canonical Question Block Format”.

Appendix — Question Templates (Copy/Paste)
------------------------------------------
**Template — Single-Select (with Other)**
```markdown
### QID-XX-###
**Intent:** <one-sentence decision>
**Rationale:** <impact explanation>
**Impact Areas:** <comma-separated>
**Answer Type:** single-select
**Options:**
- [ ] A) <label> (recommended)
- [ ] B) <label>
- [ ] C) <label>
- [ ] D) <label>
- [ ] Other — (describe here):
**Constraints & Guards:** <rules or “—”>
```

**Template — Multi-Select**
```markdown
### QID-XX-###
**Intent:** <one-sentence decision>
**Rationale:** <impact explanation>
**Impact Areas:** <comma-separated>
**Answer Type:** multi-select
**Options:**
- [ ] A) <label> (recommended)
- [ ] B) <label>
- [ ] C) <label>
- [ ] D) <label>
- [ ] Other — (describe here):
**Constraints & Guards:** <rules or “—”>
```

**Template — Free-Text / Numeric / Date**
```markdown
### QID-XX-###
**Intent:** <one-sentence decision>
**Rationale:** <impact explanation>
**Impact Areas:** <comma-separated>
**Answer Type:** <free-text|numeric|date>
**Constraints & Guards:** <rules, instructions for the expected format, units, or example or “—”>
**Answer:**
```
