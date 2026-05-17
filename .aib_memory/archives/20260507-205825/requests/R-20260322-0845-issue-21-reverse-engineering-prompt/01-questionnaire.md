# Iteration Questionnaire

## Instructions for human
- Review each question and mark your chosen option(s) with `[x]`.
- Use `Other` when none of the provided options fit, and write your answer in the space provided.
- One option marked `(recommended)` reflects the AI's suggestion based on analysis.

---

## Business & Functional Questions

### QID-BF-001
**Intent:** Determine whether the reverse-engineering capability should be a formal AIB action or a standalone prompt.
**Rationale:** If registered as a formal action in `Concepts.md`, it becomes part of the canonical workflow, is discoverable via `run.bat`/`run.sh`, and benefits from lifecycle guardrails. A standalone prompt is simpler but less integrated. This decision shapes the implementation scope and the number of files changed.
**Impact Areas:** Scope, Requirements, Architecture
**Answer Type:** single-select
**Options:**
- [x] A) New formal AIB action (`reverse-engineer`) added to action contract matrix, with optional tool script (recommended)
- [ ] B) Standalone prompt only — user invokes it manually without framework registration
- [ ] C) Extension of the existing `aib-update-documentation` prompt with a new "scan workspace" mode
- [ ] Other — (describe below):

**Constraints & Guards:** If A is selected, `Concepts.md` must be updated; if C is selected, the existing prompt must be reviewed for compatibility.

---

### QID-BF-002
**Intent:** Decide what level of human review is required before writing to product-doc files.
**Rationale:** Fully automated writing is fast but risks overwriting user-curated content or introducing low-quality entries. A two-phase approach (extract → review → populate) is safer but slower. This directly affects the prompt design, number of intermediate artifacts, and user workflow.
**Impact Areas:** Scope, Requirements, User Experience
**Answer Type:** single-select
**Options:**
- [x] A) Fully automated — prompt writes all product-doc files in one pass without human review checkpoint
- [ ] B) Two-phase — first pass generates a review/extraction document; human approves; second pass writes files (recommended)
- [ ] C) Per-document approval — prompt generates a questionnaire for each of the 27 documents before writing
- [ ] D) Write to separate draft files (e.g., `ARCH-01-draft.md`) for human to compare and merge manually
- [ ] Other — (describe below):

**Constraints & Guards:** If C is selected, expect significant user effort (27 approval steps). If A is selected, a rollback mechanism should be considered.

---

### QID-BF-003
**Intent:** Decide whether populated product-doc files should include a confidence/draft indicator.
**Rationale:** Auto-generated content may range from highly accurate (e.g., file catalogs) to speculative (e.g., business process catalog inferred from code). A visible indicator helps human reviewers prioritize their review effort and prevents downstream consumers from treating draft content as verified.
**Impact Areas:** Requirements, User Experience, Scope
**Answer Type:** single-select
**Options:**
- [ ] A) Yes — add a "Draft — auto-generated, pending human review" watermark at the top of each populated file (recommended)
- [ ] B) Yes — add per-section confidence tags (High/Medium/Low) based on source evidence strength
- [x] C) No — write content as-is; rely on VCS diff for review
- [ ] Other — (describe below):

**Constraints & Guards:** If A or B is selected, a convention update may be needed for the watermark/tag format.

---

### QID-BF-004
**Intent:** Identify target brownfield projects for validation testing.
**Rationale:** The approach must be workspace-agnostic. Testing against at least one real brownfield project validates that the design works outside the AI_Builder repo. Without a test target, the only validation is theoretical.
**Impact Areas:** Scope, Timeline
**Answer Type:** free-text
**Constraints & Guards:** Provide the name or path of 1–2 existing projects where AIB could be installed for pilot testing, or state "None available" if testing will be deferred.
**Answer:** The AIB project itself


---

## Architecture & Technical Questions

### QID-AT-001
**Intent:** Select the primary workspace-traversal strategy.
**Rationale:** This is the core technical decision. The chosen strategy determines how the prompt handles large workspaces, binary files, and context-window limits. It directly shapes the prompt design, tooling requirements, and execution model. See analysis Solution Options for detailed comparison.
**Impact Areas:** Architecture, Scope, Requirements
**Answer Type:** single-select
**Options:**
- [ ] A) Single-pass monolithic prompt (simple, only for small workspaces)
- [ ] B) Tool-assisted manifest + prompt pipeline (recommended)
- [x] C) Iterative document-by-document prompt chain
- [ ] D) Two-phase extract-then-populate
- [ ] E) Hybrid manifest + chunked extraction with progress state (most robust, most complex)
- [ ] F) Convention-driven targeted scan (lightweight, potentially incomplete)
- [ ] Other — (describe below):

**Constraints & Guards:** Options A and F have known limitations for the "no file missed" requirement. Option E is significantly more complex than B. Consider starting with B and evolving to E if needed.

---

### QID-AT-002
**Intent:** Determine how binary and non-text files should be handled during workspace scanning.
**Rationale:** Brownfield workspaces typically contain binary files (images, compiled artifacts, archives, database files) that LLMs cannot interpret. The manifest/enumeration step must decide whether to skip them entirely, record their existence for documentation (e.g., resource catalog), or attempt metadata extraction (file size, type, date).
**Impact Areas:** Architecture, Data
**Answer Type:** single-select
**Options:**
- [ ] A) Skip binary files entirely — do not include them in any output
- [x] B) Record binary file paths and metadata (size, extension, modified date) in ARCH-07 resource catalog, but do not attempt content extraction (recommended)
- [ ] C) Attempt metadata extraction for known binary formats (e.g., image dimensions, database schema) using Python libraries
- [ ] Other — (describe below):

**Constraints & Guards:** Option C adds Python library dependencies and complexity; only justified if database schemas or image metadata are critical documentation inputs.

---

### QID-AT-003
**Intent:** Decide whether existing (non-placeholder) content in product-doc files should be preserved or overwritten.
**Rationale:** In some scenarios, a user may have partially filled some product-doc files manually before running reverse-engineer. The prompt must decide whether to merge, append, or replace content. This affects data safety and user trust.
**Impact Areas:** Architecture, Data, User Experience
**Answer Type:** single-select
**Options:**
- [ ] A) Always overwrite — replace all content regardless of what exists (simplest but destructive)
- [ ] B) Skip non-placeholder files — only write to files that still contain the seed placeholder text (recommended)
- [x] C) Merge — append extracted content following the respective convention and formatting
- [ ] D) Prompt the user per file — ask before overwriting non-placeholder content
- [ ] Other — (describe below):

**Constraints & Guards:** If A is selected, recommend combining with draft-file approach (QID-BF-002 option D) to avoid data loss.

---

### QID-AT-004
**Intent:** Define the set of file patterns and directories that should be excluded from workspace scanning.
**Rationale:** Most workspaces contain directories that are not useful for documentation extraction (e.g., `node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`). Excluding them reduces noise, speeds up scanning, and avoids token waste. However, the exclusion list must be configurable to avoid missing project-specific important directories.
**Impact Areas:** Architecture, Scope
**Answer Type:** single-select
**Options:**
- [x] A) Hard-coded default exclusion list in the tool script (e.g., `.git`, `node_modules`, `__pycache__`, `dist`, `build`, `.aib_brain`, `.aib_memory`) (recommended)
- [ ] B) Respect `.gitignore` rules for exclusions (plus always exclude `.git/`)
- [ ] C) Configurable exclusion list via a settings file (e.g., `.aib_memory/scan-config.md`)
- [ ] D) No exclusions — scan everything including `node_modules`, `.git`, etc.
- [ ] Other — (describe below):

**Constraints & Guards:** Option D will produce massive manifests and waste tokens. If B is selected, projects without `.gitignore` get no exclusions. Option A is recommended as a starting point, extendable to C in a future iteration.

---

## Appendix — Answer Encoding Rules

- Checkbox unchecked: `- [ ]`
- Checkbox checked: `- [x]`
- Exactly one `(recommended)` marking per question indicates the AI's suggestion.
- Single-select: check exactly one option (including `Other` if used).
- Multi-select: check any number of options.
- Free-text: write your answer in the provided `**Answer:**` block.
- If `Other` is checked, provide a description in the space after the dash.
