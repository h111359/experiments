# Iteration Questionnaire — Iteration 03

## Business & Functional Questions

### QID-BF-001 — Authoritative mapping location
**Intent:** Select where the authoritative association between each `product-doc` and its per-document convention is stored.
**Rationale:** This choice determines whether changes are limited to prompts/conventions or require schema migration and tooling updates. It also affects how reviewers audit the mapping.
**Impact Areas:** Scope, Requirements, Compliance, Timeline
**Assumptions:**
- The mapping must be explicit and reviewable without inference.
**Answer Type:** single-select
**Options:**
- [x] A) Keep mapping in `.aib_brain/conventions/product-documentation-convention.md` — Explicit list stays the source of truth. (recommended)
- [ ] B) Use deterministic naming rule only (ID → convention path) — Minimal docs, rely on naming stability.
- [ ] C) Store mapping in `.aib_memory/references.md` `notes` — No schema change, but parseable convention text.
- [ ] D) Add a `convention_path` column to `.aib_memory/references.md` — Strongest structure, requires schema migration.
- [ ] Other — (describe below)
**Constraints & Guards:** If D is selected, `references-convention.md` MUST be updated before any migration.
**Answer Box (required if Other selected):**
```text

```

### QID-BF-002 — Missing convention behavior
**Intent:** Decide the deterministic behavior when the applicable per-document convention cannot be resolved or read.
**Rationale:** The acceptance criteria requires deterministic failure behavior (error vs warning). This decision directly affects reliability and operator expectations.
**Impact Areas:** Requirements, Compliance, Timeline, Operations
**Assumptions:**
- Convention enforcement is required whenever a product-doc is edited.
**Answer Type:** single-select
**Options:**
- [x] A) Fail-closed — do not edit the doc; emit an error explaining the missing convention. (recommended)
- [ ] B) Warn and proceed — continue editing using best-effort structure.
- [ ] C) Fail-closed only for `aib-update-documentation`, warn for `aib-implement`.
- [ ] D) Ask an interactive question at runtime — block until a human chooses fail vs warn.
- [ ] Other — (describe below)
**Constraints & Guards:** If B is selected, the prompt MUST record a clear non-compliance warning in `implementation.md`.
**Answer Box (required if Other selected):**
```text

```

### QID-BF-003 — Workflow for editing `.aib_brain/` prompts
**Intent:** Choose how prompt changes under `.aib_brain/prompts/` should be executed, given `aib-implement.md` currently forbids `.aib_brain/` edits.
**Rationale:** The request explicitly requires updates to `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md`. This is blocked unless the governance rule is clarified.
**Impact Areas:** Scope, Timeline, Compliance
**Assumptions:**
- The current safety rule is intended to protect the framework from unintended changes.
**Answer Type:** single-select
**Options:**
- [ ] A) Allow `.aib_brain/` edits for this request class (with explicit guardrails) — unblock prompt updates. (recommended)
- [ ] B) Create a separate “governance update” workflow to modify `.aib_brain/`, keeping `aib-implement` unchanged.
- [x] C) Temporarily override the safety rule only for iteration 03 (document the exception).
- [ ] D) Do not change `.aib_brain/`; instead change only `.aib_memory/*` and accept reduced enforcement.
- [ ] Other — (describe below)
**Constraints & Guards:** If A/C is selected, changes MUST be limited strictly to the files named in the request scope.
**Answer Box (required if Other selected):**
```text

```

### QID-BF-004 — Scope of documentation edits for this request
**Intent:** Decide whether this request is allowed to change any `product-doc` content, or only the governance/prompt artifacts.
**Rationale:** `.aib_memory/references.md` currently marks all product-docs as `edit_allowed=Y`, which could enable broad edits unless the scope is constrained. The request also states “Filling out seeded product docs” is out of scope.
**Impact Areas:** Scope, Timeline, Compliance
**Answer Type:** single-select
**Options:**
- [ ] A) Governance-only — modify only mapping/conventions/prompts; do not edit product-doc content. (recommended)
- [ ] B) Limited doc edits allowed — only edit product-docs if required to implement mapping/enforcement.
- [ ] C) Allow doc edits for target-edit set, but only structural conformance (no content additions).
- [x] D) Full doc edits allowed for all `edit_allowed=Y` rows.
- [ ] Other — (describe below)
**Constraints & Guards:** If B/C/D is selected, require an explicit per-doc reason in `implementation.md`.
**Answer Box (required if Other selected):**
```text

```

## Architecture & Technical Questions

### QID-AT-001 — Convention resolution method in prompts
**Intent:** Choose how prompts should resolve the per-document convention for a product-doc before editing.
**Rationale:** Determinism depends on extracting the correct requirement ID and mapping it reliably to a convention file path across platforms.
**Impact Areas:** Architecture, Operations, Timeline
**Assumptions:**
- Requirement ID is available via product-doc title and/or path (e.g., `ARCH-01`).
**Answer Type:** single-select
**Options:**
- [2] A) Resolve by deterministic file naming rule from requirement ID (e.g., `ARCH-01` → `arch-01-convention.md`). (recommended)
- [1] B) Resolve by parsing `.aib_brain/conventions/product-documentation-convention.md` mapping list.
- [ ] C) Resolve by a new `convention_path` field in `.aib_memory/references.md`.
- [ ] D) Hybrid: naming rule first, fallback to mapping list if missing.
- [ ] Other — (describe below)
**Constraints & Guards:** If B is selected, title matching rules and normalization MUST be defined (case, dash variants, whitespace).
**Answer Box (required if Other selected):**
```text

```

### QID-AT-002 — Path separator normalization
**Intent:** Decide the canonical path separator style for convention paths and prompt parsing.
**Rationale:** `.aib_memory/references.md` mandates `/`, while `product-documentation-convention.md` currently uses `\`. Without normalization rules, cross-platform behavior can become inconsistent.
**Impact Areas:** Architecture, Operations, Compliance
**Answer Type:** single-select
**Options:**
- [x] A) Normalize to `/` everywhere in docs and prompts (platform-neutral). (recommended)
- [ ] B) Allow both `/` and `\` in mapping docs, prompts normalize internally.
- [ ] C) Keep `\` in `.aib_brain/*`, but require prompts to always convert.
- [ ] D) No normalization — require exact string matches.
- [ ] Other — (describe below)
**Constraints & Guards:** If D is selected, mapping resolution MUST specify the exact OS expectation.
**Answer Box (required if Other selected):**
```text

```

### QID-AT-003 — Enforcement scope for reading conventions
**Intent:** Decide whether prompts should read conventions only for documents being edited or for all product-docs every run.
**Rationale:** Reading all conventions increases rigor but may be unnecessary overhead; reading only for edited docs is more efficient but requires clear target selection rules.
**Impact Areas:** Architecture, Timeline, Operations
**Answer Type:** single-select
**Options:**
- [ ] A) Read conventions only for the target-edit docs that will actually be edited. (recommended)
- [x] B) Read conventions for all product-doc entries on every run.
- [ ] C) Read conventions for all `edit_allowed=Y` docs, even if not edited.
- [ ] D) Read only the umbrella product documentation convention (no per-doc conventions).
- [ ] Other — (describe below)
**Constraints & Guards:** If A is selected, prompts MUST explicitly define how “about to edit” is determined.
**Answer Box (required if Other selected):**
```text

```

### QID-AT-004 — Validate `.aib_memory/references.md` state
**Intent:** Decide whether to treat the current `references.md` state (all product-docs `edit_allowed=Y`) as intentional or as something to normalize back to convention defaults.
**Rationale:** Broad edit authorization increases risk of unintended edits. Normalizing may be safer but is a behavior change.
**Impact Areas:** Security, Compliance, Operations, Timeline
**Answer Type:** single-select
**Options:**
- [x] A) Treat as intentional; do not change `references.md`, add prompt guardrails to avoid broad edits. (recommended)
- [ ] B) Normalize seeded rows back to `edit_allowed=N` and require explicit opt-in per doc.
- [ ] C) Keep `edit_allowed=Y`, but add a new field (or notes convention) to constrain edit scope per request.
- [ ] D) Defer decision; proceed with prompt changes first.
- [ ] Other — (describe below)
**Constraints & Guards:** If B/C is selected, specify a migration approach that preserves `ref_id` stability.
**Answer Box (required if Other selected):**
```text

```

## Appendix — Answer Encoding Rules
- Checkboxes:
  - Unchecked: `- [ ]`
  - Checked: `- [x]` (or `- [X]`)
- Single-select questions:
  - Exactly one option MUST be checked.
  - `Other` counts as an option.
- If `Other` is checked:
  - The corresponding **Answer Box** MUST contain non-empty text.
- When answering, keep any additional explanation inside the Answer Box so it remains machine-parseable.
