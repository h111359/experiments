# 01-questionnaire — R-20260409-1152 — Add Comments in the Code

> Generated from `01-analysis.md` section 13 — Open Questions & Next Actions.
> Answer questions by placing `x` inside the brackets: `- [x]`.
> For "Other" selections, fill the Answer Box below the options.

---

## 1. Business & Functional Questions

---

### QID-BF-001 — Comment format depth

**Intent:** Decide how prescriptive the language-specific conventions should be regarding the exact format of comments and docstrings.

**Rationale:** The required depth determines whether convention files contain minimal rules ("add a comment to every function") or detailed idiomatic rules (e.g., NumPy docstrings for Python, JSDoc `@param`/`@returns` tags for JavaScript, XML `///` doc-comments for C#). Prescriptive conventions produce more consistent output but require more maintenance; a baseline-only approach is faster to implement and easier to evolve.

**Impact Areas:** Requirements, Scope, Architecture, Timeline

**Assumptions:**
- The user wants generated code to be self-documenting.
- The AI model can apply style-specific formats if explicitly instructed.

**Answer Type:** single-select

**Options:**
- [x] A) Baseline only — mandate that comments exist (file header, function description, inline for non-obvious logic); allow any format. (recommended)
- [ ] B) Idiomatic formats — mandate language-standard formats (e.g., NumPy for Python, JSDoc for JavaScript, XML `///` for C#, KDoc for Scala).
- [ ] C) Both — baseline format for all languages, with idiomatic format also specified per language as SHOULD (recommended where applicable).
- [ ] Other — (describe here):

**Constraints & Guards:** — If B or C is selected, each convention file will require a "Comment Format" section with examples, adding ~10–20 lines per file.

---

## 2. Architecture & Technical Questions

---

### QID-AT-001 — Permission to create files inside `.aib_brain/` during `implement`

**Intent:** Confirm whether the AI Automation Agent is permitted to create files under `.aib_brain/conventions/` and edit `.aib_brain/prompts/aib-implement.md` during the `implement` step of this request.

**Rationale:** The current safety rule in `aib-implement.md` states: `"Do not modify .aib_brain/ assets during implementation work."` This request IS a framework-evolution change deliberately targeting `.aib_brain/`. Without explicit confirmation, the implement step could self-block. Knowing the answer here determines whether the plan includes a direct `implement` step or instructs the user to place files manually.

**Impact Areas:** Architecture, Scope, Timeline

**Assumptions:**
- The safety rule was added to prevent accidental framework changes during product-feature implementations, not to prevent evolution of the framework itself.

**Answer Type:** single-select

**Options:**
- [x] A) Yes — the AI agent may create convention files under `.aib_brain/conventions/` and edit `aib-implement.md` for this request only. (recommended)
- [ ] B) No — the user will place the convention files manually using the scaffolded content produced by the AI.
- [ ] Other — (describe here):

**Constraints & Guards:** — If A, the implementation plan must include a one-time explicit override note. If B, the plan output must include ready-to-paste file content as the deliverable.

---

### QID-AT-002 — Flask and Django convention structure

**Intent:** Decide whether Flask and Django each get a standalone convention file or are covered as sub-sections within the Python convention file.

**Rationale:** Flask and Django are Python web frameworks; their file extensions (`.py`) overlap with standard Python. If they are sub-sections of `coding-python-convention.md`, the conditional loading in `aib-implement.md` becomes simpler (detecting `.py` files loads Python rules including Flask/Django). If they are separate files, the implement prompt must also detect framework-specific patterns (e.g., `views.py`, `urls.py`, `app.py`) to load the correct file, which adds complexity but allows more focused convention evolution.

**Impact Areas:** Architecture, Scope, Requirements

**Assumptions:**
- Flask and Django files always have `.py` extension.
- Detecting framework context from file names is feasible within a prompt instruction.

**Answer Type:** single-select

**Options:**
- [x] A) Separate files — `coding-flask-convention.md` and `coding-django-convention.md`, loaded conditionally when framework-specific patterns are detected. (recommended)
- [ ] B) Sub-sections — Flask and Django rules are sections inside `coding-python-convention.md`; no separate files.
- [ ] C) Hybrid — separate files but they import (by reference) the Python convention as the baseline.
- [ ] Other — (describe here):

**Constraints & Guards:** — If B, the Python convention file grows significantly; if A, the conditional loading logic in `aib-implement.md` requires a framework-detection rule (e.g., by file name pattern or directory structure).

---

### QID-AT-003 — React convention file scope (file extensions covered)

**Intent:** Define which file extensions trigger loading of `coding-react-convention.md` during `implement`.

**Rationale:** React code can appear in `.jsx`, `.tsx`, `.js`, and even `.ts` files in modern projects. If the React convention only applies to `.jsx`/`.tsx`, simpler JavaScript/TypeScript files in the same project are covered only by the JavaScript convention. If it applies more broadly, there may be overlap with the JavaScript convention for `.js` files.

**Impact Areas:** Architecture, Scope

**Assumptions:**
- JavaScript convention (`coding-javascript-convention.md`) covers `.js` and `.mjs` files generally.
- TypeScript is not in the explicitly requested language list, but `.tsx` is implied by React.

**Answer Type:** single-select

**Options:**
- [x] A) `.jsx` and `.tsx` only — pure React component files; `.js` and `.ts` use the JavaScript convention. (recommended)
- [ ] B) `.jsx`, `.tsx`, `.js`, `.ts` — all files in a React project use the React convention when a React context is detected.
- [ ] C) `.jsx` only — exclude TypeScript React files from the React convention scope for now.
- [ ] Other — (describe here):

**Constraints & Guards:** — If B, there is potential overlap with the JavaScript convention for `.js` files; the plan must specify precedence rules (React convention overrides JavaScript convention when both match).

---

## 3. Appendix — Answer Encoding Rules

| Symbol | Meaning |
|--------|---------|
| `- [ ]` | Unchecked / not selected |
| `- [x]` | Selected (lowercase x or uppercase X both accepted) |
| `(recommended)` | Suggested default choice |

**Single-select validation**: Exactly one option must be `- [x]`. Selecting `Other` requires a non-empty answer in the space provided.

**Multi-select validation**: Any number of options may be `- [x]`; zero is treated as unanswered.

**Free-text answers**: Place text directly below the "Other" option line after checking it.

**QID key rules**: Each `QID-BF-###` and `QID-AT-###` is a stable identifier for this iteration. If this questionnaire is regenerated, QIDs remain unchanged.

---

--- I am done with the questionnaire ---
