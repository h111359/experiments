# Prompt: context

Goal:
Produce or fully replace `.aib_memory/context.md` — a unified, structured synthesis of all workspace-specific product knowledge, structured according to `.aib_brain/conventions/context-convention.md`. This prompt also serves the reverse-engineering use case: when no prior `context.md` content exists, the workspace scan in Phase 3 becomes the primary synthesis source.

Workspace instructions pre-read (MUST):
- Read `.aib_memory/instructions.md`. If the file exists and is non-empty, treat its content as persistent workspace-level instructions that MUST be observed throughout this prompt's execution. If the file is absent or empty, proceed normally.

Non-goals:
- Do not modify any existing file in the workspace other than `.aib_memory/context.md`.
- Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md`.
- Do not explore `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`.

Core requirements (normative):
- MUST be workspace/tool/model/vendor agnostic.
- MUST handle large repos (chunked inventory + selective deep reads).
- MUST produce full content replacement of `context.md` on each execution (not append).
- Re-execution with unchanged sources MUST produce semantically equivalent output.

---

## Phase 1 — Preflight

1. Read `.aib_brain/conventions/context-convention.md`. This is the authoritative source for the required section structure, content guidance, formatting rules, and quality gates for `context.md`.
2. If `.aib_memory/instructions.md` lists additional file paths the developer wants AIB to treat as supplementary product-doc inputs, collect those paths into the supplementary read set. Otherwise the supplementary read set is empty.
3. If the supplementary read set is empty, skip Phase 2 and proceed directly to Phase 3.

---

## Phase 2 — Primary read (supplementary product documentation)

> **Note:** This phase is skipped when the supplementary read set is empty (proceed directly to Phase 3).

1. Read every file in the supplementary read set.
2. For each file, determine whether it contains real content or is a stub (placeholder text only with no substantive information beyond template headings).
3. Record per-file status: `populated` or `stub`.

---

## Phase 3 — Supplementary read (workspace sources)

When the supplementary read set is empty, this phase is the **primary synthesis source** (reverse-engineering mode). Apply the traceability and evidence-collection rules from the Reverse-Engineering Evidence Collection section below.

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

## Reverse-Engineering Evidence Collection

When operating in reverse-engineering mode (product-doc read set is empty), apply the following additional evidence-collection rules during Phase 3.

### A. Deterministic file inventory

MUST produce (internally, for reasoning) a deterministic inventory of workspace files:
- Inventory includes all files under workspace root.
- Exclude typical noise directories unless explicitly needed:
  - `.git/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- Sort by workspace-relative path ascending.

Notes for large repos:
- Prefer a two-pass approach:
  1. Fast inventory from metadata only.
  2. Deep reads only for a small set of relevant files per section.
- If context is limited, summarize and defer deep reads; never invent content.

Optional helper tool:
- You MAY use `.aib_brain/tools/reverse-engineer.py` to emit a JSONL inventory.
- The prompt must still work without that tool.

### B. Traceability requirement

For each mandatory section of `context.md` synthesized from workspace sources:
- Provide explicit traceability references (source path and brief note of what was found).
- Mark claims that cannot be directly supported from workspace evidence as assumptions with a confidence level.
- Prefer leaving a stub notice over guessing.

### C. Evidence-backed synthesis rules

- Keep content consistent with workspace evidence.
- Prefer concise, deterministic wording.
- Do NOT reproduce verbatim content from source files. Summarize and synthesize.
- If a section has no workspace evidence, write the stub notice exactly as specified in `context-convention.md`.

---

## Phase 4 — Synthesis

Produce the complete content of `.aib_memory/context.md` as follows.

### 4.1 Preamble

Write the preamble exactly as specified in the `context-convention.md` Preamble Format section. Replace the timestamp placeholder with the actual generation timestamp in local project time.

### 4.2 Mandatory sections

Write all mandatory sections in the exact order and with the exact headings defined in `context-convention.md`. For each section:

- Synthesize relevant content from all populated supplementary files (if any) and workspace sources.
- Apply the content guidance defined for the section in `context-convention.md`.
- Include traceability references (e.g., `per ARCH-01`) where applicable — plain text only, no hyperlinks.
- If no source content is available for a section, write the stub notice exactly as specified in `context-convention.md`.
- Do NOT reproduce verbatim content from source files. Summarize and synthesize.

When mapping documentation to sections:
- Use all populated supplementary content as source material. Map each document's content into the most relevant mandatory section(s) as defined in `context-convention.md`.
- A single supplementary document may contribute to multiple sections.
- A single mandatory section may draw from multiple supplementary documents and workspace sources.

### 4.3 Workspace file inventory

Write the final mandatory section (`## Workspace File Inventory`) listing all non-excluded files and directories discovered in Phase 3. Follow the format defined in `context-convention.md` Section 12.

For each entry:
- **File entries:** Write `- \`path\` — description.` where description is one sentence derived from knowledge synthesized in earlier sections (Sections 1–11) or from direct file content read in Phase 3.
- **Directory entries:** Write `- \`dir/\` — description.` for every directory and subdirectory present in the workspace (using a trailing slash). Derive the description from the folder's evident role (e.g., contents and purpose inferred from earlier synthesis). Add a directory entry for every folder and subfolder; do not omit any directory that contains listed files.
- **Repetitive request artifact files** (`request.md`, `implementation.md`, `analysis.md` within `.aib_memory/requests/<request-folder>/`): use a formulaic description based on the request folder slug (e.g., "Request definition for <human-readable-slug>.", "Implementation log for <human-readable-slug>.", "Analysis artifact for <human-readable-slug>.").
- Sort all entries (files and directories together) ascending by path.

---

## Phase 5 — Write output

1. Write the complete synthesized content to `.aib_memory/context.md`, replacing any existing content entirely.
2. Do NOT append — full replacement on every execution.
3. Do NOT modify any other file.
4. Confirm at the very end of the conversation with the text "--- I am done with the context update ---" that all your activities are finished

---

## Context-window management

If the aggregate size of all files to be read (supplementary docs + workspace sources) exceeds 80% of available context:

1. Prioritize source files in this order (highest priority first): supplementary docs with `populated` status, `README.md`, `scripts/`, `tests/`, root configuration files.
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
