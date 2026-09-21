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
- Do not modify any existing product-content file except `.aib_memory/context.md` and extensions dispatched through convention-registered Prompt metadata. Normal AIB log and verification-result writes are permitted.
- Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md`, `.aib_brain/prompts/aib-context-read.md`, convention-registered extension Convention and Prompt paths, and tool script invocations listed in this prompt.
- Do not explore `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`.
- Do not remove content in `.aib_memory\context.md` unless you find evidence it is incorrect.
- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.

---

## Phase 1 — Preflight

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 1 started"`.

1. Read `.aib_brain/conventions/context-convention.md`. This is the authoritative source for the required section structure, content guidance, formatting rules, and quality gates for `context.md`.
2. If `.aib_memory/instructions.md` lists additional file paths the developer wants AIB to treat as supplementary product-doc inputs, collect those paths into the supplementary read set. Otherwise the supplementary read set is empty.
3. If the supplementary read set is not empty, read every file in the supplementary read set.
4. **Format detection:** Read `.aib_memory/context.md` (if it exists). Determine whether the file is in the current format by checking for the presence of the section heading.
   - If the file has the current section format as per `.aib_brain/conventions/context-convention.md`; use existing statements as baseline and update based on workspace evidence.
   - If the file does not have the current section format as per `.aib_brain/conventions/context-convention.md`; generate fresh content in the format of the convention.
   - If the file does not exist: proceed with full generation in the format of the convention.
5. Execute `.aib_brain/prompts/aib-context-read.md` with the current refresh goal and treat its returned extension contents as supplementary context. Do not independently parse or load Reference entries.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 1 complete"`.

---

## Phase 2 — Supplementary read (workspace sources)

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 2 started"`.

In addition to the supplementary read set, this phase is the **primary synthesis source** (reverse-engineering mode). Apply the traceability and evidence-collection rules from the Reverse-Engineering Evidence Collection section below.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 2 complete"`.

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
3. Read script and program code files (purpose, inputs, outputs per script).
4. Read test files (test coverage areas, key test targets).
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

## Phase 3 — Cross-Reference

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 3 started"`.

1. Read files under `tests/` to identify test coverage areas and key test targets that should inform context.md content.
2. Read any script files under `scripts/` that were not covered in Phase 2.
3. Note any additional architectural facts, constraints, or decisions discovered in this phase that are relevant to the 6 sections of context.md.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 3 complete"`.

---

## Phase 4 — Synthesis

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 4 started"`.

Produce or modify the content of `.aib_memory/context.md` as follows.

Apply the formatting rules defined in the `## Formatting Rules` section of `.aib_brain/conventions/context-convention.md`.

Use atomic statement format for each bullet line as specified in context-convention.md.

### Content currency rule

All content MUST reflect the current state of the product only.
MUST NOT include version history annotations such as "introduced in vX.Y.Z", "added in vX", "deprecated as of vX", "removed as of", or "(Deprecated)" labels.
Describe what currently exists and is active; historical change information belongs in changelogs and version logs, not in context.md.

### Non-repeating information rule

CLI argument names and function signatures MUST NOT be included in `context.md` because they are derivable by reading the tool scripts directly. High-level tool purpose, behaviour, and architectural facts are retained. All other facts may still be included.

### 4.1 Context Convention Reference

Refer to the valid sections definition in `context-convention.md` for the required section structure, content guidance, formatting rules, and quality gates.

### 4.2 Six-Section Synthesis

Write the content of `.aib_memory/context.md` following the convention defined in `context-convention.md`.

### 4.3 Managed References Reconciliation

Write every convention-defined extension entry to `## References` in convention-defined order. Restore each managed heading, Location, Summary, Convention, and Prompt exactly. Preserve existing valid Read and Update choices case-insensitively and normalize them to lowercase; use convention defaults when a valid prior choice is unavailable. Do not retain bibliographic or unknown entries.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 4 complete"`.

---

## Phase 5 — Enrichment Verification Passes

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 5 started"`.

After synthesis, execute the following enrichment passes to ensure completeness:

### Pass 1 — Analysis decisions verification

Read `.aib_memory/analysis-<request_id>.md` for the active request (if one is active). Verify all decisions from the Decision Register section are reflected as statements in the appropriate section of the current 7-section `context.md` format (Product, Concepts, Requirements, Solution, File Structure, References, or Issues). Add missing statements.

### Pass 2 — Plan results verification

Read `.aib_memory/plan-<request_id>.md` for the active request (if it exists). Verify all completed task outcomes and architectural decisions from the plan are reflected in context statements. Add missing statements.

### Pass 3 — Modified files verification

Compare workspace file state against context statements. Verify that any new files, removed files, or renamed files since the last context generation are reflected in `## File Structure`. Verify that significant functional changes to existing files are reflected as updated or new statements in the appropriate sections.

### Pass 4 — [PLANNED] entry preservation

Preserve every `[PLANNED]` entry verbatim across Product, Concepts, Requirements, and Solution. Automated workspace scanning MUST NOT remove its prefix. A transition to current state is allowed only through the explicit plan-driven `edit-context.py` delete plus insert pair required by `context-convention.md`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 5 complete"`.

---

## Phase 6 — Write output

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 6 started"`.

1. **Statement uniqueness verification pass (MUST complete before writing):** Scan all generated atomic statements in Section 2. For each statement, extract the index (area+type+hash). If any duplicate index is found, resolve by adjusting the statement text (which changes the hash) or removing the duplicate. Only after zero uniqueness violations remain may you proceed to write the file.
2. Write the complete synthesized content to `.aib_memory/context.md`, replacing any existing content entirely.
3. Do NOT append — full replacement on every execution.
4. Do NOT modify any other product-content file in this phase; registered extensions are handled only in Phase 9, and normal logging and verification-result writes remain permitted.
5. Confirm at the very end of the conversation with the text "--- I am done with the context update ---" that all your activities are finished

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 6 complete"`.

---

## Phase 7 — Post-write Validation

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 7 started"`.

1. Re-read `.aib_memory/context.md` as written.
2. Extract all level-2 headings from the document in order.
3. Compare the extracted list against the mandatory section list from `.aib_brain/conventions/context-convention.md` (required headings: `## Product`, `## Concepts`, `## Requirements`, `## Solution`, `## File Structure` — in that order; `## References` is optional).
4. If any heading is non-compliant — wrong name, wrong order, or missing — identify each correction needed.
5. For each non-compliant section, rewrite it (heading and content) to match the convention; do not alter compliant sections.
6. Verify all statements in Product, Concepts, and Solution sections use plain-bullet format, and all statements in Requirements use modality-prefixed format.
7. After all corrections are applied, confirm the written file is compliant.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 7 complete"`.

---

## Phase 8 — Format Verification

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 8 started"`.

1. Invoke `python -B .aib_brain/tools/verify-context.py --workspace .` to run automated format checks against the written `context.md`.
2. If the script exits with code 0 (all checks pass), proceed to completion.
3. If the script exits with code 1 (one or more checks fail), review the reported failures and correct the deviations in `context.md`. Re-run the verification script until all checks pass.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 8 complete"`.

---

## Phase 9 — Update Writable Extensions

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 9 started"`.

After `context.md` is written and verified, process every managed Reference entry in convention-defined order:
1. Preserve valid user-controlled Read and Update values while restoring every convention-owned field to its canonical value.
2. Compare Update case-insensitively. For `yes`, execute the prompt at the registered `Prompt:` path; that prompt owns extension reconciliation and validation. For `no`, skip the entry.
3. For each missing Location, Convention, or Prompt artifact, emit `WARNING: Registered context extension artifact missing: <path>. Continuing without this artifact.` and continue.
4. Log each successfully updated extension via `log-entry.py --workspace . --message "Extension updated: <location>"`.

If no managed entry has Update yes, skip dispatch.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-refresh-context Phase 9 complete"`.

---

## Safety

- Permitted product-content write targets are `.aib_memory/context.md` and extensions written through convention-registered Prompt metadata; normal AIB logs and verification-result flags are also permitted.
- Do NOT edit any existing workspace file.
- Do NOT create files other than `.aib_memory/context.md` or a convention-registered extension created by its registered Prompt.
- Do NOT explore or read `.aib_brain/` contents except `.aib_brain/conventions/context-convention.md`, `.aib_brain/prompts/aib-context-read.md`, convention-registered extension Convention and Prompt paths, and explicitly listed tool scripts.
- Do NOT install packages, create virtual environments, or run tools.
- MAY read `.aib_memory/analysis-<request_id>.md` and `.aib_memory/plan-<request_id>.md` for the active request only (needed for enrichment passes in Phase 5 enrichment verification passes).
- MUST NOT read analysis or plan files for Closed requests.

---

## Done criteria

- `.aib_memory/context.md` exists and is valid Markdown.
- It starts with `# Product Context` and contains the convention-mandated sections and managed References registry.
- It contains the 5 mandatory sections in the order specified by `context-convention.md` (`## Product`, `## Concepts`, `## Requirements`, `## Solution`, `## File Structure`), using the exact headings.
- All sections contain appropriate atomic statements in the format required by context-convention.md.
- `## File Structure` lists all non-excluded workspace files in the required indented-tree format.
- No content is derived from excluded directories.
- No product-content files other than `.aib_memory/context.md` and successfully dispatched managed extensions were modified.
