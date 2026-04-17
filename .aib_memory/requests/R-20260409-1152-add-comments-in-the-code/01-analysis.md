# 01-analysis — R-20260409-1152 — Add Comments in the Code

## 1. Executive Summary

- **Request ID**: R-20260409-1152

- **Request title**: Add Comments in the Code

- **Iteration ID**: 01 (Active, created 2026-04-09)

- **High-level purpose**: Extend the AIB implementation workflow so that every code file generated or edited during `implement` is required to contain comments following consistent coding conventions. Achieve this by (a) creating a general coding-principles convention file and (b) creating language-specific coding convention files for Python, DAX, SQL, HTML, JavaScript, CSS, React, Flask, Django, C#, Scala, and UI/UX design. The implement prompt (`aib-implement.md`) is updated to unconditionally load the general convention and conditionally load the relevant language-specific convention based on the file type(s) being created or edited.

- **Earlier iterations**: None — this is iteration 01.

- **Conflicts**: None detected.

---

## 2. Scope Interpretation

- **Explicitly in scope**:

  - Creation of a general coding-principles convention file covering commenting requirements and code quality best practices that applies across all languages.

  - Creation of language-specific convention files for each of the following: Python, DAX, SQL, HTML, JavaScript, CSS, React, Flask, Django, C#, Scala, UI/UX design.

  - Modification of `.aib_brain/prompts/aib-implement.md` to unconditionally reference the general coding convention and conditionally reference the appropriate language-specific convention based on the file type(s) involved in any given implementation run.

- **Explicitly out of scope**: None stated by the user.

- **Implicitly in scope** (implicit rule - AIB framework):

  - If coding convention files are added to `.aib_brain/conventions/`, the product documentation (`CMP-01`, `CMP-02`, `ARCH-01`) may need to reference their existence as framework artifacts; however, since these are brain assets and not product-docs, no `references.md` updates are required.

  - Existing code already in the repository is **not** in scope for retroactive comment enforcement.

  - Testing of the modified implement prompt behaviour (by verifying it loads the correct convention) is implicitly required.

---

## 3. Domain Knowledge Essentials

- **AIB (AI Builder)**: A model-agnostic, file-system-first framework that drives AI-assisted development via prompt + convention files stored in `.aib_brain/`. Workspace-specific artifacts live in `.aib_memory/`.

- **Coding convention**: A normative document describing required style, structure, commenting, and quality rules for a specific programming language or technology. In AIB, conventions reside in `.aib_brain/conventions/` and are referenced by prompts.

- **Implement prompt** (`aib-implement.md`): The AIB prompt that directs the AI to execute the active request scope and apply code/documentation changes. It is the central enforcement point for coding standards.

- **Impacted roles/personas**:
  - *Repository Developer*: Creates and tracks requests; benefits from consistently commented, readable generated code.
  - *AIB Maintainer*: Owns brain assets; responsible for keeping conventions accurate and complete.
  - *AI Automation Agent*: Executes the implement prompt; must read and follow the conventions.

- **Business processes touched**: Implementation workflow (step 4 of the AIB canonical workflow).

- **Acceptance impact**: Developers receive generated code that is self-documenting and maintainable. Code reviews are faster because intent is captured inline.

---

## 4. Technical Knowledge & Terms

- **`.aib_brain/conventions/`**: Directory holding all AIB normative convention files. Adding new files here extends the framework without breaking existing behavior, provided prompts are updated to reference them.

- **Conditional convention loading**: The pattern in which a prompt reads a language-specific convention file only when the implementation touches files of that language. Implemented via natural-language instructions in the prompt (e.g., "if creating or editing `.py` files, read `.aib_brain/conventions/coding-python-convention.md`").

- **General coding convention**: A language-agnostic file establishing comment requirements (file header, function/class docstrings, inline comments for non-obvious logic), naming rules, and quality hygiene (no dead code, no magic numbers).

- **Language-specific coding convention**: A focused normative file for one language/framework that extends the general convention with idiomatic rules (e.g., Python docstring format, SQL block headers, DAX measure annotations).

- **Safety constraint in implement prompt**: The line `"Do not modify .aib_brain/ assets during implementation work"` exists to prevent accidental framework corruption during normal feature development. This request is explicitly modifying framework assets; however, since the request arises from a deliberate AIB-framework-evolution intent (not a product feature), the conventional safety rule requires the implementer to acknowledge and override it in the plan.

- **DAX (Data Analysis Expressions)**: Formula language used in Microsoft Power BI, Power Pivot, and SSAS Tabular for calculations and measures.

- **React**: JavaScript library for building UI components. Relevant for `.jsx` and `.tsx` files.

- **Flask** and **Django**: Python web frameworks. Their convention files extend the Python convention with web-specific patterns (routes, views, templates).

- **UI/UX design convention**: Targets design-related markup and layout code; covers HTML/CSS accessibility, component naming, and visual comment standards.

---

## 5. Assumptions

- Assumption A1: The new coding convention files will reside inside `.aib_brain/conventions/` under the naming pattern `coding-<language>-convention.md`.
  - Rationale: All existing conventions follow the `<slug>-convention.md` naming pattern in that folder; language-specific conventions are a natural extension.
  - Risk if false: Naming drift causes the implement prompt to be unable to resolve files deterministically.
  - Falsification method: Inspect the final file listing in `.aib_brain/conventions/` after implementation.

- Assumption A2: The implement prompt (`aib-implement.md`) is the single enforcement point and the only file that needs modification to load coding conventions.
  - Rationale: `aib-implement.md` is the prompt that executes code generation; no other prompt generates code directly.
  - Risk if false: If other prompts (e.g., `aib-documentation.md`) also produce code snippets, they would bypass commenting enforcement.
  - Falsification method: Scan all `.aib_brain/prompts/*.md` for code-generating instructions.

- Assumption A3: The safety rule `"Do not modify .aib_brain/ assets during implementation work"` is intentionally scoped to prevent accidental changes during product-feature implementations, and does not prohibit deliberately scheduled framework-evolution requests.
  - Rationale: The request itself is a framework-evolution change; blocking it entirely would make AIB unable to evolve. All other AIB lifecycle rules confirm humans may update `.aib_brain/` directly.
  - Risk if false: The implement step would be blocked; a manual override instruction must be added to the plan.
  - Falsification method: Ask the AIB Maintainer (user) to confirm intent in questionnaire Q1.

- Assumption A4: Language-specific conventions are loaded conditionally based on file extensions found in the active changeset.
  - Rationale: Loading all 12 language conventions on every implement would increase context usage even when only Python files are touched.
  - Risk if false: If the AI miss-detects file types, wrong or no convention is applied.
  - Falsification method: Test the implement prompt on a Python-only change and verify only the Python convention is loaded.

- Assumption A5: UI/UX design convention applies to HTML, CSS, and component files collectively, rather than as a separate tech-stack convention.
  - Rationale: UI/UX spans multiple file types and is primarily a design philosophy layer; separate from the individual HTML/CSS language conventions.
  - Risk if false: Overlap or contradiction between HTML/CSS conventions and the UI/UX convention.
  - Falsification method: Review both HTML-convention and UI/UX-convention for conflicting rules after creation.

---

## 6. Impact Assessment

### 6.1 Affected Components / Areas

- `.aib_brain/conventions/` — 13 new convention files to be created (1 general + 12 language-specific).

- `.aib_brain/prompts/aib-implement.md` — modified to enforce general convention loading and conditional language-specific convention loading.

- Test suite (`.../tests/`) — test(s) validating that the implement prompt includes convention references, or smoke-test fixture that verifies file presence.

### 6.2 Change Type and Dependencies

- `.aib_brain/conventions/coding-general-convention.md`: **add** — no dependencies; foundation for all language conventions.

- `.aib_brain/conventions/coding-python-convention.md` (and 11 similar): **add** — depends on `coding-general-convention.md` being written first (for cross-reference).

- `.aib_brain/prompts/aib-implement.md`: **modify** — depends on all convention files existing before the prompt is finalized, so that paths are correct.

- No upstream or downstream integration partners affected; changes are entirely within the workspace filesystem.

### 6.3 Domain Impacts

- DOMAIN (ARCH): No structural change to the architecture. New convention files are an extension of the existing brain asset pattern. `ARCH-01` component map may optionally be updated to note coding conventions as a sub-category of brain assets.
  - Relevant requirement IDs: ARCH-01

- DOMAIN (CMP): CMP-01 (Notebook/script catalog) and CMP-02 (Algorithm specification register) are unaffected in structure; however, new scripts generated after this change will conform to the commenting conventions.
  - Relevant requirement IDs: CMP-01, CMP-02

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): This is the primary Domain impact. The Product Documentation currently has no `DEV` domain document registered in references. The coding conventions fill the gap that `DEV` (SDLC / code practices) normally describes. If a `DEV-01` document is ever created, it would reference these conventions.
  - Relevant requirement IDs: None currently registered.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (KNW): No impact detected.

- DOMAIN (RQT): RQT-02 (Requirements document) currently has no requirement for code comments; this request adds an implicit non-functional requirement (NFR for code quality). RQT-02 may optionally be updated with a new NFR entry.
  - Relevant requirement IDs: RQT-02

- DOMAIN (OBS): No impact detected.

- DOMAIN (OPR): No impact detected.

- DOMAIN (SEC): No impact detected.

### 6.4 Constraints

- `.aib_brain/` assets must not be modified by tool scripts (Concepts.md, safety rule). They can be modified by the AI agent in an explicit framework-evolution request such as this one, with explicit acknowledgment.

- New convention files must not break the deterministic convention resolution path used by `aib-implement.md`: coding conventions are NOT product-doc conventions (they are not in `references.md` and do not require a mapping in `product-documentation-convention.md`). They are auxiliary prompt support files.

- Content in convention files must use normative language (MUST/SHOULD/MAY) per BCP 14 to remain consistent with all other AIB conventions.

### 6.5 Required Documentation Updates

- ARCH-01 — High-level architecture
  - Required update? OPTIONAL — The component description for "AIB Brain Assets" could mention coding conventions as a new convention sub-category.
  - Reason: Minor completeness improvement; not blocking.

- RQT-02 — Requirements document
  - Required update? OPTIONAL — Add a new NFR entry for code quality/commenting.
  - Reason: Keeps requirements traceable to this change.

No other product-doc updates are required.

### 6.6 Decision Points

- Decision Point DP-1: Naming convention for the new files.
  - Option 1: `coding-<language>-convention.md` (e.g., `coding-python-convention.md`) — keeps all coding conventions grouped by prefix.
  - Option 2: `<language>-coding-convention.md` — language-first naming.
  - Recommendation: **Option 1** — `coding-<language>-convention.md`. Aligns with alphabetical ordering, groups all coding conventions together in directory listings, and makes shell globs (`coding-*.md`) easy.

- Decision Point DP-2: Should the general convention be a standalone file or embed the language-specific content?
  - Option 1: One general file + 12 separate language files (federated model).
  - Option 2: One omnibus coding convention file covering all languages.
  - Recommendation: **Option 1** — federated model. Keeps each file focused and loadable independently. Reduces context usage per implement run. Easier to evolve individual language conventions without touching the general one.

- Decision Point DP-3: Does the safety rule override need to be noted in the plan, or is it acceptable to handle it via an explicit annotation in the analysis?
  - Option 1: Add an override note in the plan for the implement step.
  - Option 2: Have the user explicitly confirm in a questionnaire.
  - Recommendation: **Option 1** — document the override in the plan; it is a known, intentional case. No user input required.

---

## 7. Research Plan and Findings

- **Methodology**: Internal docs scan (`.aib_brain/`, `.aib_memory/`, `tests/`) + pattern scan of existing conventions.

- **Evidence summary**:
  - The `.aib_brain/conventions/` folder contains 36 convention files; ALL are either product-doc conventions or AIB structural conventions. Zero coding-style or commenting conventions exist today.
  - The `aib-implement.md` prompt has no reference to code quality, commenting, or language conventions. The only safety rule about code is "Do not create Python virtual environment".
  - The `Product_Documentation.md` has no `DEV` domain entries under Standard Requirements; the Development domain is listed in the domain table but has no mandatory or recommended requirements defined.
  - All tests in `tests/` check lifecycle behavior (requests, iterations, menu, lifecycle e2e). No test checks that generated code contains comments.

- **Gaps and unknowns**:
  - Whether the user expects the conventions to define specific comment formats (e.g., JSDoc, NumPy docstrings, XML doc-comments for C#) or just mandate that comments exist.
  - Whether React convention should extend JavaScript convention or HTML convention (or both).
  - Whether Flask and Django conventions should be separate from Python or sub-sections of the Python convention.

- **Proposed validation actions**:
  - After implementation, run a manual implement cycle on a known Python file and verify that the AI loads and applies `coding-python-convention.md`.
  - Inspect the five shortest convention files to validate they are non-trivial and normatively correct.

- **Files Read**:
  - `.aib_brain\prompts\aib-analysis.md` — found the prompt instructions for this analysis.
  - `.aib_memory/requests/R-20260409-1152-add-comments-in-the-code/request.md` — primary input: user's raw request.
  - `.aib_memory/requests/R-20260409-1152-add-comments-in-the-code/iterations.md` — confirmed iteration 01 is Active.
  - `.aib_memory/references.md` — identified all 27 product-doc entries and confirmed no coding-convention references exist.
  - `.aib_brain/Concepts.md` — confirmed safety rules, brain-asset policy, and normative lifecycle rules.
  - `.aib_brain/conventions/analysis-convention.md` — used as the authoritative schema for this file.
  - `.aib_brain/conventions/request-convention.md` — used for the rewrite proposal format.
  - `.aib_brain/conventions/implementation-convention.md` — reviewed to understand implement output requirements.
  - `.aib_brain/prompts/aib-implement.md` — key input for understanding what needs to change and what safety constraints exist.
  - `.aib_brain/conventions/product-documentation-convention.md` — confirmed coding conventions are separate from product-doc conventions.
  - `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — confirmed product charter is not yet populated; no contradictions.
  - `.aib_memory/docs/03 Requirements/RQT-02.md` — reviewed functional and non-functional requirements; confirmed no existing code-quality NFR.
  - `.aib_memory/context.md` — reviewed synthesized product context; confirmed technology stack (Python 3.10+, Markdown, Git, GitHub Actions).
  - `.aib_brain/Product_Documentation.md` — confirmed domain structure; DEV domain has no implemented requirements.
  - `tests/` (directory listing only) — confirmed no test files cover commenting convention enforcement.
  - `.aib_brain/conventions/cmp-01-convention.md` (partial grep) — confirmed `sql`, `python` referenced as script kinds; no comment rules defined.
  - [SKIPPED — domain out of scope]: ARCH-02, ARCH-03, ARCH-05, ARCH-06, ARCH-07, CMP-01, CMP-02, DATA-01 through DATA-09, KNW-01, KNW-02, KNW-03, OBS-01, SEC-01 through SEC-04 — not relevant to the scope of adding coding conventions.

---

## 8. Rewrite Proposal of the Request

> See the rewritten `request.md` produced as a parallel output of this analysis.

**Summary of rewrite**: The original request used ambiguous phrasing ("to be enforsed", "refered in the implement prompt conditionnaly"). The rewrite names specific actors (AI Automation Agent, AIB Maintainer), identifies exact files to be created and modified, defines measurable acceptance criteria with observable thresholds, and explicitly lists scope and out-of-scope items.

---

## 9. Solution Options

### Option A — Federated Convention Files + Implement Prompt Update (Recommended)

- **Overview**: Create 13 new `.aib_brain/conventions/` files (1 general + 12 language-specific). Update `aib-implement.md` to mandate unconditional loading of the general convention and conditional loading of the matching language convention based on the file extension(s) being created or edited.

- **Benefits**: Minimal per-run context overhead (only relevant language convention loaded). Each convention is independently maintainable. The general convention enforces a baseline even when no language match is found.

- **Trade-offs**: 13 new files to maintain; requires periodic review as languages evolve.

- **Constraints**: Convention files must not be registered as product-docs in `references.md` (they are brain assets, not product-docs).

- **Risks**: If the AI fails to detect the correct file extension, the language-specific convention is silently skipped. Mitigated by always loading the general convention as a fallback.

- **Expected effort**: Medium — 13 files × ~30-50 lines each + implement prompt patch. Estimated 1-2 iterations of refinement.

- **Acceptance tests**:
  - Implement a Python script change → verify `coding-python-convention.md` is loaded and docstrings/comments appear.
  - Implement a SQL query change → verify `coding-sql-convention.md` is loaded and block headers appear.
  - Implement a change with no recognized file type → verify general convention still applies.

### Option B — Single Omnibus Coding Convention File

- **Overview**: Create one large `coding-convention.md` covering all languages in sections. Update `aib-implement.md` to always load this single file.

- **Benefits**: Single file to maintain; simpler prompt modification.

- **Trade-offs**: Increased context usage on every implement run regardless of language. Risk of the AI ignoring irrelevant sections. Harder to evolve individual language rules.

- **Constraints**: None beyond Option A constraints.

- **Risks**: Context bloat; large file may be partially parsed by some models.

- **Expected effort**: Low initial — only 1 file + prompt patch. Higher long-term maintenance.

- **Acceptance tests**:
  - Same as Option A, but the single file is always loaded.

### Recommendation

**Option A** is recommended. It is more efficient, more maintainable, and aligns with the modular, fail-closed conventions architecture already established in AIB. The conditional loading pattern is already implicit in AIB's convention enforcement model (per `aib-implement.md` preflight logic for product-docs).

---

## 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0022 | RQT-01 - Product charter | .aib_memory/docs/01 Product Management/Product Charter/RQT-01.md | Optional: document that this request introduced the coding conventions capability. |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | Optional: add a new NFR for code quality and commenting enforcement. |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Optional: update "AIB Brain Assets" component description to mention coding conventions sub-category. |

---

## 11. Operational & Documentation Implications

- **No runbooks, SLAs, SLOs, or monitoring changes** are required. The AIB framework has no runtime observability layer beyond action log files.

- **Product documentation** (`ARCH-01`, `RQT-02`): Minor optional updates only — see Section 10. Not blocking for implementation.

- **Prompt integrity**: After modification, `aib-implement.md` must remain self-consistent; convention loading instructions must not conflict with existing safety rules. The safety rule override for `.aib_brain/` modification during this meta-request must be explicitly documented in the implementation plan.

- **Future maintenance**: When a new language is supported (e.g., TypeScript, Rust), a follow-up request to add a `coding-<language>-convention.md` and update the conditional table in `aib-implement.md` will be required.

---

## 12. Risks

- Risk R1: The safety rule `"Do not modify .aib_brain/ assets during implementation work"` may cause the implement step to block editing convention files in `.aib_brain/`.
  - Probability: Medium
  - Impact: High
  - Mitigation: Explicitly annotate the plan with an override instruction ("This request IS the framework-evolution task; the safety rule exception applies"). The user (AIB Maintainer) can also manually create convention files outside of the implement workflow.
  - Owner (role): AIB Maintainer

- Risk R2: Generated convention files may contain contradictions between the general convention and a language-specific convention.
  - Probability: Low
  - Impact: Medium
  - Mitigation: The general convention states baseline rules; each language convention explicitly notes which general rules it overrides and why.
  - Owner (role): AIB Maintainer

- Risk R3: Some language conventions (Flask, Django) are framework-level extensions of Python; overlapping rules may confuse the AI when both Python and Flask conventions are applicable.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: The implement prompt loads language conventions based on file extension, not framework. Flask/Django conventions are loaded additionally when framework-specific patterns are detected (e.g., `views.py`, `urls.py`). Document this logic explicitly in the implement prompt update.
  - Owner (role): AI Automation Agent (enforced by prompt instructions)

- Risk R4: UI/UX design convention overlaps with HTML and CSS conventions.
  - Probability: Medium
  - Impact: Low
  - Mitigation: UI/UX convention is explicitly scoped to design-philosophy layer (accessibility labels, component naming, layout comments). HTML/CSS conventions cover code structure and syntax. Both are loaded when applicable; conflicts deferred to language-specific convention.
  - Owner (role): AIB Maintainer

---

## 13. Open Questions & Next Actions

1. **Q1 — Safety rule override confirmation**
   - Owner: User (AIB Maintainer)
   - Trigger: Before implementation begins
   - Question: Should the AI Automation Agent be permitted to create files under `.aib_brain/conventions/` and edit `.aib_brain/prompts/aib-implement.md` during the `implement` step of this request, given that this IS a framework-evolution change? Or does the user prefer to manually create the files?
   - Resolution path: If the user confirms the override is acceptable, the plan can include a direct `implement` step. If not, the plan will produce scaffolded content for the user to place manually.

2. **Q2 — Comment format depth**
   - Owner: User (AIB Maintainer)
   - Trigger: Before plan generation
   - Question: Should the conventions mandate specific comment formats (e.g., NumPy docstrings for Python, JSDoc for JavaScript, XML `///` doc-comments for C#), or just mandate that functions/classes/modules have descriptive comments in any format?
   - Resolution path: User selects preferred depth; this determines how prescriptive the convention files need to be.

3. **Q3 — Flask and Django as separate files or sub-sections of Python**
   - Owner: User (AIB Maintainer)
   - Trigger: Before plan generation
   - Question: Should Flask and Django each have their own convention file (`coding-flask-convention.md`, `coding-django-convention.md`) or should they be sub-sections within `coding-python-convention.md`?
   - Resolution path: User's preference determines file structure. Recommendation: separate files for clarity; sub-sections for simplicity.

4. **Q4 — React convention scope**
   - Owner: User (AIB Maintainer)
   - Trigger: Before plan generation
   - Question: Should the React convention cover `.jsx` and `.tsx` files only, or also include JavaScript config files (`.js`, `.mjs`) used in a React project?
   - Resolution path: User defines boundary; default recommendation is `.jsx`/`.tsx` only (pure React component files).

---

--- I am done with the analysis ---
