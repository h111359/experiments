# Prompt: context

Goal:
Produce or fully replace `.aib_memory/context.md` — a unified, structured synthesis of all workspace-specific product knowledge, structured according to `.aib_brain/conventions/context-convention.md`.

Non-goals:
- Do not modify any existing file in the workspace other than `.aib_memory/context.md`.
- Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md`.
- Do not explore `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`.
- Do not add entries to `.aib_memory/references.md`.

Core requirements (normative):
- MUST be workspace/tool/model/vendor agnostic.
- MUST handle large repos (chunked inventory + selective deep reads).
- MUST produce full content replacement of `context.md` on each execution (not append).
- Re-execution with unchanged sources MUST produce semantically equivalent output.

---

## Phase 1 — Preflight

1. Read `.aib_brain/conventions/context-convention.md`. This is the authoritative source for the required section structure, content guidance, formatting rules, and quality gates for `context.md`.
2. Read `.aib_memory/references.md`.
3. Build the product-doc read set: every `path` where `type = product-doc`.
4. Verify the read set is non-empty. If empty, STOP and report an error.

---

## Phase 2 — Primary read (product documentation)

1. Read every file in the product-doc read set from `.aib_memory/docs/`.
2. For each file, determine whether it contains real content or is a stub (seeded placeholder text only with no substantive information beyond template headings).
3. Record per-file status: `populated` or `stub`.

---

## Phase 3 — Supplementary read (workspace sources)

1. Build a deterministic file inventory of the workspace root.
   - Include all files and directories.
   - Exclude these directories and their contents:
     - `.aib_brain/`
     - `.aib_memory/`
     - `.venv/`
     - `venv/`
     - `node_modules/`
     - `__pycache__/`
     - `.pytest_cache/`
     - `.mypy_cache/`
     - `.git/`
   - Sort by workspace-relative path ascending.
2. Read `README.md` (if it exists at workspace root).
3. Read files under `scripts/` (purpose, inputs, outputs per script).
4. Read files under `tests/` (test coverage areas, key test targets).
5. Read root configuration files (e.g., `.gitignore`, `pyproject.toml`, `setup.cfg`, `requirements.txt`, `package.json`) if they exist.

---

## Phase 4 — Synthesis

Produce the complete content of `.aib_memory/context.md` as follows.

### 4.1 Preamble

Write the preamble exactly as specified in the `context-convention.md` Preamble Format section. Replace the timestamp placeholder with the actual generation timestamp in local project time.

### 4.2 Mandatory sections

Write all mandatory sections in the exact order and with the exact headings defined in `context-convention.md`. For each section:

- Synthesize relevant content from all populated product-doc files and workspace sources.
- Apply the content guidance defined for the section in `context-convention.md`.
- Include traceability references (e.g., `per ARCH-01`) where applicable — plain text only, no hyperlinks.
- If no source content is available for a section, write the stub notice exactly as specified in `context-convention.md`.
- Do NOT reproduce verbatim content from source files. Summarize and synthesize.

When mapping product documentation to sections:
- Use all product-doc content as source material. Map each document's content into the most relevant mandatory section(s) as defined in `context-convention.md`.
- A single product-doc may contribute to multiple sections.
- A single mandatory section may draw from multiple product-docs and workspace sources.

### 4.3 Workspace file inventory

Write the final mandatory section (`## Workspace File Inventory`) listing all non-excluded files discovered in Phase 3. Follow the format defined in `context-convention.md` Section 12.

---

## Phase 5 — Write output

1. Write the complete synthesized content to `.aib_memory/context.md`, replacing any existing content entirely.
2. Do NOT append — full replacement on every execution.
3. Do NOT modify any other file.
4. Confirm at the very end of the conversation with the text "--- I am done with the context update ---" that all your activities are finished

---

## Context-window management

If the aggregate size of all files to be read (product-docs + workspace sources) exceeds 80% of available context:

1. Prioritize source files in this order (highest priority first): product-docs with `populated` status, `README.md`, `scripts/`, `tests/`, root configuration files.
2. For deprioritized files, read only file headers and first section, then summarize.
3. In the preamble of `context.md`, add a note listing which files were summarized due to context-window limits.

---

## Safety

- The only permitted write target is `.aib_memory/context.md`.
- Do NOT edit any existing workspace file.
- Do NOT create files other than `.aib_memory/context.md`.
- Do NOT explore or read `.aib_brain/` contents except `.aib_brain/conventions/context-convention.md`.
- Do NOT install packages, create virtual environments, or run tools.

---

## Done criteria

- `.aib_memory/context.md` exists and is valid Markdown.
- It contains the preamble as defined in `context-convention.md`, including the auto-generation notice and timestamp.
- It contains all mandatory sections in the order specified by `context-convention.md`, using the exact headings.
- Populated sections have concise, non-empty key-fact summaries sourced from workspace content.
- Sections with no available source content contain the stub notice as defined in `context-convention.md`.
- Workspace source artifacts (`scripts/`, `tests/`) are synthesized under the applicable mandatory sections.
- No content is derived from excluded directories.
- No files other than `.aib_memory/context.md` were modified.
