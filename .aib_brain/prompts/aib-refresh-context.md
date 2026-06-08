# Prompt: aib-refresh-context

## Goal:
Produce or modify `.aib_memory/context.md` — a unified, structured synthesis of all workspace-specific product knowledge, structured according to `.aib_brain/conventions/context-convention.md`. This prompt also serves the reverse-engineering use case: when no prior `context.md` content exists, the workspace scan in Phase 2 becomes the primary synthesis source.

## Workspace instructions pre-read (MUST):
- Read `.aib_memory/instructions.md`. If the file exists and is non-empty, treat its content as persistent workspace-level instructions that MUST be observed throughout this prompt's execution. If the file is absent or empty, proceed normally.

## Core requirements (normative):
- MUST be workspace/tool/model/vendor agnostic.
- MUST handle large repos (chunked inventory + selective deep reads).
- MUST produce full content replacement of `.aib_memory/context.md` on each execution (not append, prepend, or partially edit).
- Re-execution with unchanged sources MUST produce semantically equivalent output.

## Non-goals:
- Do not modify any existing file in the workspace other than `.aib_memory/context.md`.
- Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md` and tool script invocations listed in this prompt.
- Do not explore `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`.
- Do not remove content in `.aib_memory\context.md` unless you find evidence it is incorrect.

---

## Phase 1 — Preflight

1. Read `.aib_brain/conventions/context-convention.md`. This is the authoritative source for the required section structure, content guidance, formatting rules, and quality gates for `context.md`.
2. If `.aib_memory/instructions.md` lists additional file paths the developer wants AIB to treat as supplementary product-doc inputs, collect those paths into the supplementary read set. Otherwise the supplementary read set is empty.
3. If the supplementary read set is not empty, read every file in the supplementary read set.
4. **Format detection:** Read `.aib_memory/context.md` (if it exists). Determine whether the file is in the new atomic format by checking for the presence of `## 2. Statements` as a section heading and atomic statement lines matching the pattern `- <AREA>-<TYPE>-<HASH>: <text>`. Set internal variable [format-is-atomic] accordingly.
   - If the file is in the OLD format (12-section prose): treat existing content as informational input alongside workspace files for generating atomic statements. The old content informs synthesis but is not preserved structurally.
   - If the file is in the NEW format (3-section atomic): existing atomic statements serve as the baseline. Add, modify, or remove statements as needed based on workspace evidence.
   - If the file does not exist: proceed with full generation in atomic format.

---

## Phase 2 — Supplementary read (workspace sources)

In addition to the supplementary read set, this phase is the **primary synthesis source** (reverse-engineering mode). Apply the traceability and evidence-collection rules from the Reverse-Engineering Evidence Collection section below.

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
   - For directories containing three or more items that share a repeating naming pattern, apply the grouping rule defined in `context-convention.md` Section 12: provide a single summary bullet for the directory rather than listing individual items.
   - Sort by workspace-relative path ascending.
2. Read `README.md` (if it exists at workspace root).
3. Read files under `scripts/` (purpose, inputs, outputs per script).
4. Read files under `tests/` (test coverage areas, key test targets).
5. Read root configuration files (e.g., `.gitignore`, `pyproject.toml`, `setup.cfg`, `requirements.txt`, `package.json`) if they exist.

---

## Reverse-Engineering Evidence Collection

Apply the following additional evidence-collection rules during Phase 2.

### A. Deterministic file inventory

- MUST produce (internally, for reasoning) a deterministic inventory of workspace files:
- Sort by workspace-relative path ascending.

Notes for large repos:
- Prefer a two-pass approach:
  1. Fast inventory from metadata only.
  2. Deep reads only for a small set of relevant files per section.
- If context is limited, summarize and defer deep reads; never invent content.

- Use `.aib_brain/tools/file-inventory.py` to emit a JSONL inventory and compare with the existing list in `.aib_memory/context.md`

### B. Traceability requirement

For each mandatory section of `.aib_memory/context.md` synthesized from workspace sources:
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

Produce or modify the content of `.aib_memory/context.md` as follows.

Apply the formatting rules defined in the `## Formatting Rules` section of `.aib_brain/conventions/context-convention.md`.

### Content currency rule

All content MUST reflect the current state of the product only.
MUST NOT include version history annotations such as "introduced in vX.Y.Z", "added in vX", "deprecated as of vX", "removed as of", or "(Deprecated)" labels.
Describe what currently exists and is active; historical change information belongs in changelogs and version logs, not in context.md.

### 4.1 Preamble

Write the preamble exactly as specified in the `context-convention.md` Preamble Format section. Replace the timestamp placeholder with the actual generation timestamp in local project time.

### 4.2 Section 1 — Product Identity

Write `## 1. Product Identity` with free-form prose content following the Section 1 content guidance in `context-convention.md`. Synthesize from all available workspace sources and supplementary files.

### 4.3 Section 2 — Statements

Write `## 2. Statements` containing atomic statements organized into the 22 subsections defined in `context-convention.md`.

For each subsection area:
1. Identify all relevant facts, requirements, constraints, decisions, and information from workspace sources that belong to this area.
2. For each fact, compose a single-sentence atomic statement.
3. Compute the 8-character hash using `hashlib.sha256(text.encode('utf-8')).hexdigest()[:8]` where `text` is the statement text.
4. Assign the appropriate statement type letter (N, R, C, E, L, U, A, D, I).
5. Format as: `- <AREA>-<TYPE>-<HASH>: <text>`
6. Add optional `{Related to: <id1>, <id2>}` suffix where relationships between statements exist.

When converting from old format:
- Map content from old `## Domain Knowledge` to areas DO, CO.
- Map content from old `## Concepts` to area CO.
- Map content from old `## Constraints & Assumptions` to appropriate areas with type C or A.
- Map content from old `## Requirements` to area FN with type R.
- Map content from old `## Architecture & Decisions` to areas TD, TS with types D, I.
- Map content from old `## Technical Design` to area TD.
- Map content from old `## Data Architecture` to area DS, DF.
- Map content from old `## Security & Compliance` to area SC.
- Map content from old `## Operations` to area OP.
- Map content from old `## Development Practices` to area DV.
- Use best judgment for placement when content spans multiple areas.

### 4.4 Section 3 — Workspace File Inventory

Write `## 3. Workspace File Inventory` listing all non-excluded files and directories discovered in Phase 2. Follow the format defined in `context-convention.md` Section 3.

For each entry:

- **File entries:** Write `- \`path\` — description.` where description is one sentence derived from knowledge synthesized in earlier sections or from direct file content read in Phase 2.

- **Directory entries:** Write `- \`dir/\` — description.` for every directory and subdirectory present in the workspace (using a trailing slash). Derive the description from the folder's evident role.

- **Repetitive items:** Apply the grouping rule for directories containing three or more items with repeating naming patterns.

- Sort all entries (files and directories together) ascending by path.

---

## Phase 4b — Enrichment Verification Passes

After synthesis, execute the following enrichment passes to ensure completeness:

### Pass 1 — Analysis decisions verification

Read `.aib_memory/analysis-<request_id>.md` for the active request (if it exists, check `requests_register.md` for the Active request). Verify all decisions from the Decision Register section are reflected as statements (type D) in the appropriate area subsection of `## 2. Statements`. Add missing decision statements.

### Pass 2 — Plan results verification

Read `.aib_memory/plan-<request_id>.md` for the active request (if it exists). Verify all completed task outcomes and architectural decisions from the plan are reflected in context statements. Add missing statements.

### Pass 3 — Modified files verification

Compare workspace file state against context statements. Verify that any new files, removed files, or renamed files since the last context generation are reflected in `## 3. Workspace File Inventory`. Verify that significant functional changes to existing files are reflected as updated or new statements in `## 2. Statements`.

---

## Phase 5 — Write output

1. **Statement uniqueness verification pass (MUST complete before writing):** Scan all generated atomic statements in Section 2. For each statement, extract the index (area+type+hash). If any duplicate index is found, resolve by adjusting the statement text (which changes the hash) or removing the duplicate. Only after zero uniqueness violations remain may you proceed to write the file.
2. Write the complete synthesized content to `.aib_memory/context.md`, replacing any existing content entirely.
3. Do NOT append — full replacement on every execution.
4. Do NOT modify any other file.
5. Confirm at the very end of the conversation with the text "--- I am done with the context update ---" that all your activities are finished

---

## Phase 6 — Post-write Validation

1. Re-read `.aib_memory/context.md` as written.
2. Extract all level-2 headings from the document in order.
3. Compare the extracted list against the mandatory section list from `.aib_brain/conventions/context-convention.md` (exact heading text: `## 1. Product Identity`, `## 2. Statements`, `## 3. Workspace File Inventory` — in that order).
4. If any heading is non-compliant — wrong name, wrong order, or missing — identify each correction needed.
5. For each non-compliant section, rewrite it (heading and content) to match the convention; do not alter compliant sections.
6. Verify all atomic statements in Section 2 have unique indices and match the required format.
7. After all corrections are applied, confirm the written file is compliant.

---

## Phase 7 — Format Verification

1. Invoke `python .aib_brain/tools/verify-context.py --workspace .` to run automated format checks against the written `context.md`.
2. If the script exits with code 0 (all checks pass), proceed to completion.
3. If the script exits with code 1 (one or more checks fail), review the reported failures and correct the deviations in `context.md`. Re-run the verification script until all checks pass.

---

## Safety

- The only permitted write target is `.aib_memory/context.md`.
- Do NOT edit any existing workspace file.
- Do NOT create files other than `.aib_memory/context.md`.
- Do NOT explore or read `.aib_brain/` contents except `.aib_brain/conventions/context-convention.md`.
- Do NOT install packages, create virtual environments, or run tools.
- MAY read `.aib_memory/analysis-<request_id>.md` and `.aib_memory/plan-<request_id>.md` for the active request only (needed for enrichment passes in Phase 4b).
- MUST NOT read analysis or plan files for Closed requests.

---

## Done criteria

- `.aib_memory/context.md` exists and is valid Markdown.
- It contains the preamble as defined in `context-convention.md`, including the auto-generation notice and timestamp.
- It contains all 3 mandatory sections in the order specified by `context-convention.md` (`## 1. Product Identity`, `## 2. Statements`, `## 3. Workspace File Inventory`), using the exact headings.
- Section 1 has concise prose content synthesized from workspace sources.
- Section 2 contains atomic statements in the correct format with unique indices across all subsections.
- Section 3 lists all non-excluded workspace files in the required format.
- No content is derived from excluded directories.
- No files other than `.aib_memory/context.md` were modified.
