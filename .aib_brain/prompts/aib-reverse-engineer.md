# Prompt: reverse-engineer

Goal:
Reverse engineer the current workspace to populate documentation files listed in `.aib_memory/references.md` where `type=product-doc` and `edit_allowed=Y`, using per-document conventions and explicit traceability to workspace sources.

Non-goals:
- Do not change product code unless explicitly requested.
- Do not edit any file not permitted by `.aib_memory/references.md`.

Core requirements (normative):
- MUST be workspace/tool/model/vendor agnostic.
- MUST handle large repos (chunked inventory + selective deep reads).
- MUST fail-closed if product-doc convention mapping is incomplete (no partial edits).
- MUST provide traceability for material claims (cite source paths and brief excerpts/anchors).

---

## Input resolution

- Resolve active request from `.aib_memory/requests_register.md` unless an explicit request id is provided.
- Resolve active iteration from the request `iterations.md`.
- Use newest iteration artifacts as truth when conflicts exist.

---

## Mandatory preflight (fail-closed)

1. Read `.aib_brain/Concepts.md` for normative lifecycle and safety rules.
2. Read `.aib_memory/references.md`.
2. In a single pass through references, build:
   - required-read set: every `path` where `type=product-doc`
   - target-edit set: every `path` where `type=product-doc` and `edit_allowed=Y`
3. Read every file in the required-read set before editing anything.
4. Read `.aib_brain/conventions/product-documentation-convention.md` (authoritative mapping).
5. Convention enforcement preflight (fail-closed):
   - For every product-doc in the required-read set:
     - Derive requirement ID from the document filename (e.g., `ARCH-01.md` -> `ARCH-01`).
     - Resolve the per-document convention file path deterministically:
       `.aib_brain/conventions/<requirement-id-lower>-convention.md`.
     - Verify the mapping row exists in `product-documentation-convention.md` for the doc title and resolved convention path.
     - Read the resolved convention file.
   - If any mapping row is missing or any convention file cannot be read, STOP:
     - Do NOT edit any product-docs.
     - Record the blocker and required remediation in the active request `implementation.md`.

Editing permissions:
- Only modify files listed in `.aib_memory/references.md` with `edit_allowed=Y`.
- Do not edit files listed with `edit_allowed=N` unless the user explicitly instructs otherwise.

---

## Workspace reverse engineering (evidence collection)

### A. Deterministic file inventory

MUST produce (internally, for reasoning) a deterministic inventory of workspace files:
- Inventory includes all files under workspace root.
- Exclude typical noise directories unless explicitly needed:
  - `.git/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- Sort by workspace-relative path ascending.

Notes for huge repos:
- Prefer a two-pass approach:
  1) fast inventory from metadata only
  2) deep reads only for a small set of relevant files per document
- If context is limited, summarize and defer deep reads; never invent content.

Optional helper tool:
- You MAY use `.aib_brain/tools/reverse-engineer.py` to emit a JSONL inventory.
- The prompt must still work without that tool.

### B. Traceability requirement

For each product-doc you edit:
- Include an explicit “Traceability” or “Sources” section if the convention allows it.
- Provide:
  - source path(s)
  - what you took from each source (one line)
  - any assumptions and why they were necessary

If a claim cannot be supported:
- Mark it as an assumption with a clear confidence level.
- Prefer leaving a TODO/question over guessing.

---

## Document population rules

For each product-doc in target-edit set:
- Follow its per-document convention file exactly (section order, required tables, IDs).
- Keep content consistent with workspace evidence.
- Prefer concise, deterministic wording.
- Avoid adding new sections that the convention does not permit.

If a convention requires a table and the workspace lacks data:
- Keep the table with the correct headers and leave cells blank or as `N/A` as allowed by the convention.

---

## Validation & completion

1. Run convention mapping validation (if available in the workspace) and record results.
2. Run lightweight python validation where relevant (e.g., `python -m compileall -q .`) and record results.
3. Append a new dated entry to the active request `implementation.md`:
   - iteration id
   - summary of edited docs
   - evidence sources
   - validation commands + results
   - blockers/follow-ups
4. Confirm at the very end of the conversation with the text "--- I am done with the reverse engineering ---" that all your activities are finished

Done criteria:
- All `product-doc` paths with `edit_allowed=Y` are convention-compliant and evidence-backed.
- No edits were made outside the allowed target set.
- Implementation log updated with validations and traceability summary.

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

