# Questionnaire — R-20260404-0823 / Iteration 01

Request: Create `aib-context.md` prompt for unified workspace context document

---

## 1. Business & Functional Questions

### QID-BF-001 — Scope of `.aib_brain/` in `context.md`
**Intent:** Decide whether the `aib-context.md` prompt should include `.aib_brain/` content (framework prompts, tools, conventions) in the generated `context.md`, or remain exclusively limited to workspace-specific artifacts.

**Rationale:** The request explicitly excludes `.aib_brain/` from exploration. However, the success criterion states "the product can be recreated by AI just from this file." Since `.aib_brain/` contains the AIB framework definition (prompts, tools, conventions) that drives all AIB behaviour, an AI reading only `context.md` would not know how AIB works. This creates a potential tension between the stated exclusion and the stated success criterion. This question resolves which interpretation should take precedence.

**Impact Areas:** Scope, Requirements, User Experience

**Assumptions:**
- The current request text says "excluding `.aib_brain`" as an explicit out-of-scope item.
- "Recreatable" may mean recreating the product/data/configuration state, not the framework itself.

**Answer Type:** single-select

**Options:**
- [ ] A) Exclude `.aib_brain/` as stated — `context.md` captures workspace-specific state only; a note is added that framework assets live in `.aib_brain/` (recommended)
- [ ] B) Include `.aib_brain/` content — extend exploration to include prompts, conventions, tools so `context.md` is truly self-contained for full recreation
- [ ] C) Include only `.aib_brain/prompts/` and `.aib_brain/conventions/` (skip tools) — partial inclusion for richer context without full framework duplication
- [ ] Other — (describe below):

**Constraints & Guards:** Selecting B or C requires updating the Out of Scope section of request.md; selecting A requires a preamble note in context.md explaining the limitation.

---

## 2. Architecture & Technical Questions

### QID-AT-001 — Level of detail in `context.md` sections
**Intent:** Decide whether each section of `context.md` should contain full verbatim content from source product-doc files, or concise summaries (key IDs, component names, critical decisions).

**Rationale:** "Full content reproduction" makes `context.md` very large (potentially 50–100KB with all docs), increasing context-window pressure for AI agents reading it. "Concise summaries" produce a more manageable, brainstorming-friendly document but may omit critical details needed for full product recreation. The right balance depends on the primary intended use.

**Impact Areas:** Architecture, User Experience, Requirements

**Assumptions:**
- The primary stated use is "brainstorming and simplicity."
- The secondary use is "product recreation by AI."

**Answer Type:** single-select

**Options:**
- [ ] A) Concise summaries per section — key IDs, component names, critical facts; 1–3 paragraphs per domain (recommended)
- [ ] B) Full verbatim content — embed complete product-doc content into relevant sections
- [ ] C) Adaptive — include full content for populated docs; summaries for stub/sparse docs
- [ ] Other — (describe below):

**Constraints & Guards:** Selecting B may make `context.md` too large for efficient use in AI sessions; selecting A may be insufficient for the "full recreation" criterion.

---

## 3. Appendix — Answer Encoding Rules

**Checkbox state:**
- Unchecked: `- [ ]`
- Checked: `- [x]`

**Single-select validation:**
- Exactly one option MUST be checked per question. `Other` counts if checked.

**Other answer box (if Other is selected):**
- Write your free-text answer on the line immediately below the `Other` option.

**Examples:**
```
- [x] A) Option label — impact hint
- [ ] B) Option label — impact hint
```

```
- [ ] A) Option label — impact hint
- [x] Other — (describe below):
  My custom answer here
```
