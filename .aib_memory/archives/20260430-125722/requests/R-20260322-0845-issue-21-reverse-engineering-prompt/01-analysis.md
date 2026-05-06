# Iteration Analysis

## Executive Summary

- **Request ID:** R-20260322-0845

- **Request title:** Issue 21 — Reverse-engineering prompt for brownfield project documentation

- **Iteration ID:** 01

- **High-level purpose:** Design a prompt-driven approach that enables AIB to systematically scan every file in an arbitrary workspace, cross-reference the findings with `.aib_memory/references.md`, and auto-populate the editable `product-doc` files under `.aib_memory/docs/` with the maximum extractable knowledge — so that a brownfield project can bootstrap its AIB documentation without manual transcription.

- **Scope:** New prompt (and optional supporting tooling) that orchestrates workspace-wide file reading, knowledge extraction, and product-doc population. Must be workspace-agnostic (not coupled to the AI_Builder repo itself).

- **Changes vs previous iteration:** First iteration — no prior analysis exists.

- **Key decisions required:**
  1. Which workspace-traversal strategy to adopt (prompt-only, tool-assisted, or hybrid).
  2. How to handle large workspaces that exceed a single LLM context window.
  3. What level of human review/approval is required before writing to product-doc files.
  4. Whether to introduce a new AIB action or extend an existing one.
  5. How to handle file types the LLM cannot meaningfully interpret (binaries, images, minified bundles).

- **Headline risks:** Context-window overflow for large codebases; hallucinated documentation when source evidence is thin; destructive overwrites of user-curated content in product-doc files.

- **Expected outcome if accepted:** A new reusable `reverse-engineer` (or equivalent) prompt under `.aib_brain/prompts/` that any AIB installation can invoke to bootstrap documentation from an existing codebase.

---

## Scope Interpretation

- **In scope:** Designing the approach / prompt for workspace-wide file scanning and product-doc population.

- **In scope:** Proposing at least 5 materially different approaches (explicit success criterion from request).

- **In scope:** Covering any kind of workspace, not only the current AI_Builder repo.

- **In scope:** Reading all files in the workspace without missing any file.

- **In scope:** Reading all documents defined in `.aib_memory/references.md`.

- **In scope:** Populating only `product-doc` type entries where `edit_allowed = Y` in `.aib_memory/references.md`.

- **In scope (implicit rule — AIB framework):** Documentation updates to product-doc files that will be touched by the new functionality.

- **In scope (implicit rule — AIB framework):** Convention compliance — any new prompt must have a corresponding convention file if it introduces new artifact types.

- **Out of scope:** Implementing the prompt/tool in this iteration (this iteration is brainstorming/analysis only per the iteration summary).

- **Out of scope:** Modifying `.aib_brain/` framework assets (read-only by AIB convention; only humans replace this folder).

- **Out of scope:** Populating files where `edit_allowed = N` in `references.md`.

- **Out of scope:** Runtime testing against a real external brownfield project (no second workspace available in this session).

---

## Domain Knowledge Essentials

- **AI Builder (AIB):** A minimal, model-agnostic framework for specification-driven development that uses prompts, conventions, templates, and tools organized in `.aib_brain/` to drive project work stored in `.aib_memory/`.

- **Brownfield project:** An existing software project with pre-existing code, configuration, and possibly informal or absent documentation that AIB is installed into after-the-fact.

- **Product-doc:** A documentation file under `.aib_memory/docs/` that corresponds to a requirement entry in `Product_Documentation.md` (e.g., ARCH-01, DATA-02). These are the canonical knowledge artifacts AIB uses to reason about the product.

- **references.md:** The registry mapping every documentation file AIB may read or edit, including path, type, and edit permission (`edit_allowed`).

- **Reverse engineering (in this context):** The process of reading existing workspace artifacts (source code, config files, scripts, README, CI definitions, etc.) and extracting structured knowledge to fill AIB documentation templates.

- **Impacted personas:** Developer installing AIB into an existing project; Technical lead reviewing auto-generated documentation; AIB prompt author maintaining the framework.

- **Business process touched:** AIB initialization and onboarding workflow — specifically the gap between `initialize` (which seeds empty doc stubs) and productive use (which requires populated docs).

- **Acceptance impact:** If successful, the time-to-value for AIB in brownfield scenarios drops dramatically because the manual documentation bootstrapping step is automated.

---

## Technical Knowledge & Terms

- **LLM context window:** The maximum token count an AI model can process in a single interaction. Relevant because large workspaces may exceed this limit.

- **`.aib_brain/`:** Immutable (to AIB) framework folder containing prompts, conventions, templates, and tools. Replaced only by humans during upgrades.

- **`.aib_memory/`:** Mutable project-specific folder containing requests, iteration artifacts, references, and documentation files.

- **Convention file:** A markdown document under `.aib_brain/conventions/` that defines the normative structure and rules for a specific product-doc (e.g., `arch-01-convention.md` governs `ARCH-01.md`).

- **Prompt file:** An instruction document under `.aib_brain/prompts/` that an AI agent executes to produce an artifact.

- **Tool script:** A Python script under `.aib_brain/tools/` invoked by script-backed AIB actions (e.g., `create-request.py`).

- **File glob / recursive directory traversal:** Programmatic enumeration of all files in a workspace tree, typically via `os.walk()` (Python) or glob patterns.

- **Token budget:** The practical allocation of context-window tokens across system prompt, workspace content, and generation output.

- **Chunking:** Splitting large content into smaller pieces that individually fit within the token budget, processed sequentially or in batches.

- **Binary file:** A file whose content is not human-readable text (e.g., images, compiled binaries, archives). These cannot be meaningfully interpreted by an LLM for documentation extraction.

---

## Assumptions

- Assumption A1: The workspace will already have AIB initialized (`.aib_memory/` exists with seeded product-doc stubs) before the reverse-engineering prompt is invoked.
  - Rationale: The prompt targets population of existing product-doc files, not creation of the memory structure.
  - Risk if false: The prompt would fail to find target files and produce no output.
  - Falsification method: Check for existence of `.aib_memory/docs/` and `references.md` as a preflight step.

- Assumption A2: The LLM executing the prompt has filesystem read access to all workspace files via the tool environment (VS Code Copilot, Claude Code, Cursor, etc.).
  - Rationale: AIB is designed to be model/vendor agnostic, and all supported environments provide file-read capabilities.
  - Risk if false: The prompt cannot scan the workspace and must fall back to user-pasted content.
  - Falsification method: Attempt a directory listing in the target environment.

- Assumption A3: Workspace sizes vary widely; some brownfield projects may contain thousands of files and millions of lines of code that exceed any single LLM context window.
  - Rationale: Enterprise projects routinely have 10k+ files.
  - Risk if false: A naive "read everything at once" approach would silently truncate or fail.
  - Falsification method: Measure token count of a representative large project.

- Assumption A4: Not all product-doc files will have meaningful content extractable from the workspace (e.g., capacity model, SLAs, business process catalog may not be inferrable from code alone).
  - Rationale: Code encodes technical decisions but rarely encodes business context or operational targets.
  - Risk if false: The prompt over-generates speculative content and misleads the user.
  - Falsification method: Run against a sample project and compare extraction yield per document category.

- Assumption A5: The `edit_allowed` flag in `references.md` will be set to `Y` for product-doc entries the user wants populated. Currently all defaults are seeded with `Y`.
  - Rationale: The request specifies populating only editable product-doc files.
  - Risk if false: No files would be written if all flags are `N`.
  - Falsification method: Read `references.md` and verify flags before writing.

- Assumption A6: The reverse-engineering prompt should NOT modify `references.md` itself — only consume it as read-only input.
  - Rationale: `references.md` is a registry; adding/removing entries is a separate concern.
  - Risk if false: Accidental corruption of the reference registry.
  - Falsification method: Review prompt output targets; ensure only product-doc files are written.

---

## Impact Assessment

### Affected Components / Areas

1. **`.aib_brain/prompts/`** — New prompt file to be added (e.g., `aib-reverse-engineer.md`).
2. **`.aib_brain/conventions/`** — Potentially a new convention file if the reverse-engineering output has unique structural rules.
3. **`.aib_brain/Concepts.md`** — May need an update to document the new action in the invocation contract and holistic workflow.
4. **`.aib_memory/docs/` (all 27 product-doc files)** — Target files for population.
5. **`.aib_memory/references.md`** — Read-only input; consumed but not modified.
6. **`.aib_brain/tools/`** — Optional: new Python tool script if a tool-assisted approach is chosen.

### Change Type and Dependencies

| Area | Change type | Dependencies |
|------|------------|--------------|
| `.aib_brain/prompts/` | Add | Depends on conventions for product-doc files |
| `.aib_brain/conventions/` | Add (optional) | None |
| `.aib_brain/Concepts.md` | Modify | Depends on chosen approach |
| `.aib_memory/docs/*` | Modify (content population) | Depends on workspace content + conventions |
| `.aib_brain/tools/` | Add (optional) | Depends on chosen approach |

Sequencing: Prompt design must precede tool implementation; conventions for each product-doc already exist and will govern output format.

### Domain Impacts

- **ARCH:** High impact — ARCH-01 through ARCH-07 are primary targets for extraction from code structure, config, and infrastructure-as-code files.
  - Relevant: ARCH-01, ARCH-02, ARCH-03, ARCH-04, ARCH-06, ARCH-07

- **CMP:** Medium impact — CMP-01 (scripts/notebooks) and CMP-02 (algorithms) are directly extractable from file system enumeration and code analysis.
  - Relevant: CMP-01, CMP-02

- **DATA:** Medium impact — Data models (DATA-02), lineage (DATA-03), storage patterns (DATA-04) may be partially inferrable from schema files, ORM definitions, and data pipeline code.
  - Relevant: DATA-01 through DATA-09

- **KNW:** Low-to-medium impact — Domain glossary (KNW-01) and business processes (KNW-02) may be partially extractable from README files, comments, and naming conventions, but are largely business-knowledge dependent.
  - Relevant: KNW-01, KNW-02, KNW-03

- **RQT:** Low impact — Product charter (RQT-01) and requirements (RQT-02) are typically not encoded in source code. May extract from existing documentation files if present.
  - Relevant: RQT-01, RQT-02

- **OBS:** Medium impact — Logging patterns (OBS-01) extractable from code (logging frameworks, config).
  - Relevant: OBS-01

- **SEC:** Medium impact — Access management (SEC-01), data protection (SEC-02), secrets management (SEC-03), network security (SEC-04) partially inferrable from config files, IAM definitions, and security-related code.
  - Relevant: SEC-01 through SEC-04

- **DEV:** No impact detected (no DEV-prefixed documents in current references).

- **DSR:** No impact detected.

- **FNL:** No impact detected.

- **OPR:** No impact detected (no OPR-prefixed documents in current references).

### Constraints

- **Technical:** LLM context window limits how much workspace content can be processed at once.
- **Technical:** Binary/non-text files cannot be interpreted by the LLM.
- **Framework:** `.aib_brain/` must not be modified by AIB scripts or prompts (human-only replacement).
- **Framework:** Product-doc files must conform to their respective convention files when populated.
- **Operational:** The approach must be model-agnostic and work across VS Code Copilot, Claude Code, Cursor, and CLI environments.
- **Business:** Must not require proprietary APIs, external services, or paid tooling beyond the already-present LLM environment.

### Required Documentation Updates

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Target for population |
| REF-0002 | ARCH-02 - Topology/network description | .aib_memory/docs/04 Technology/Architecture/ARCH-02.md | Target for population |
| REF-0003 | ARCH-03 - Capacity model | .aib_memory/docs/04 Technology/Architecture/ARCH-03.md | Target for population |
| REF-0004 | ARCH-04 - ADRs repository | .aib_memory/docs/04 Technology/Architecture/ARCH-04.md | Target for population |
| REF-0005 | ARCH-06 - Runtime interaction sequences | .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | Target for population |
| REF-0006 | ARCH-07 - Resource catalog | .aib_memory/docs/04 Technology/Inventory/ARCH-07.md | Target for population |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | Target for population |
| REF-0008 | CMP-02 - Algorithm specification register | .aib_memory/docs/04 Technology/Compute/CMP-02.md | Target for population |
| REF-0009 | DATA-01 - Source data catalog and data ingestion | .aib_memory/docs/04 Technology/Data Sources/DATA-01.md | Target for population |
| REF-0010 | DATA-02 - Data models (logical & physical) | .aib_memory/docs/04 Technology/Data Models/DATA-02.md | Target for population |
| REF-0011 | DATA-03 - Data lineage | .aib_memory/docs/04 Technology/Data Workspace/DATA-03.md | Target for population |
| REF-0012 | DATA-04 - Data storage strategy & patterns | .aib_memory/docs/04 Technology/Data Workspace/DATA-04.md | Target for population |
| REF-0013 | DATA-05 - Data consumption & access patterns | .aib_memory/docs/04 Technology/Data Workspace/DATA-05.md | Target for population |
| REF-0014 | DATA-06 - Metrics catalog | .aib_memory/docs/04 Technology/Analytics/DATA-06.md | Target for population |
| REF-0015 | DATA-07 - Data quality rules, monitoring & reporting | .aib_memory/docs/04 Technology/Data Workspace/DATA-07.md | Target for population |
| REF-0016 | DATA-08 - Data archiving & deletion policy | .aib_memory/docs/04 Technology/Data Workspace/DATA-08.md | Target for population |
| REF-0017 | DATA-09 - Dashboard inventory | .aib_memory/docs/04 Technology/Analytics/DATA-09.md | Target for population |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Target for population |
| REF-0019 | KNW-02 - Business process catalog | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md | Target for population |
| REF-0020 | KNW-03 - Use cases & personas | .aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md | Target for population |
| REF-0021 | OBS-01 - Logging | .aib_memory/docs/04 Technology/Observability/OBS-01.md | Target for population |
| REF-0022 | RQT-01 - Product charter | .aib_memory/docs/01 Product Management/Product Charter/RQT-01.md | Target for population |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | Target for population |
| REF-0024 | SEC-01 - Access management | .aib_memory/docs/04 Technology/Access and Security/SEC-01.md | Target for population |
| REF-0025 | SEC-02 - Infrastructure data protection | .aib_memory/docs/04 Technology/Access and Security/SEC-02.md | Target for population |
| REF-0026 | SEC-03 - Secrets management & rotation policy | .aib_memory/docs/04 Technology/Access and Security/SEC-03.md | Target for population |
| REF-0027 | SEC-04 - Infrastructure network security | .aib_memory/docs/04 Technology/Access and Security/SEC-04.md | Target for population |

### Decision Points

**DP-1: Should the reverse-engineering capability be a new AIB action or a standalone prompt?**
- Option A: New formal action (`reverse-engineer`) added to the action contract matrix in `Concepts.md`, with optional tool script.
  - Implication: Full lifecycle integration; can be invoked via `run.bat`/`run.sh`; requires Concepts.md update.
- Option B: Standalone prompt only, invoked manually by the user.
  - Implication: Simpler; no framework changes needed; but less discoverable and not part of the canonical workflow.
- Recommended: Option A — aligns with the action-contract model and makes the feature a first-class citizen.

**DP-2: What granularity of human review is required?**
- Option A: Fully automated — prompt writes all product-doc files in one shot.
  - Implication: Fast but risky; may overwrite user content or produce low-quality entries.
- Option B: Two-phase — first pass generates a review document; human approves; second pass writes files.
  - Implication: Safe but slower; adds a review artifact.
- Option C: Per-document approval via questionnaire.
  - Implication: Very safe but impractically slow for 27 documents.
- Recommended: Option B — balances safety and speed.

**DP-3: How to handle context-window limits for large workspaces?**
- Option A: Tool-assisted file inventory + selective reading (Python script enumerates files, prompt reads selectively).
- Option B: Pure prompt chunking (prompt reads files in batches, accumulates findings).
- Option C: Hybrid with a manifest file (tool generates a summary manifest, prompt uses it to prioritize reads).
- Recommended: Option C — most robust across different environments and workspace sizes.

---

## Research Plan and Findings

### Methodology

1. Internal-first review of `request.md`, `iterations.md`, `Concepts.md`, all product-doc files, and all convention files.
2. Workspace structure scan of the AI_Builder repository to understand the existing file layout, tooling, and patterns.
3. Pattern scan of existing AIB prompts (`aib-create-analysis.md`, `aib-create-questionnaire.md`, `aib-create-plan.md`, `aib-implement.md`, `aib-update-documentation.md`) to understand the prompt authoring pattern.
4. Analysis of AIB tool scripts (`initialize.py`, `create-request.py`, etc.) to understand the tool invocation model.

### Evidence Summary

| Evidence | Implication |
|----------|-------------|
| All 27 product-doc files contain only seed placeholders | Confirms the brownfield bootstrapping problem is real and pressing |
| `references.md` has `edit_allowed=Y` for all product-doc entries | All files are eligible targets for auto-population |
| Existing prompts follow a consistent pattern: preflight → read references → read conventions → generate artifact | The new prompt should follow the same pattern for consistency |
| `aib-update-documentation.md` prompt already exists | There may be overlap or reuse opportunity with the reverse-engineering prompt |
| Tool scripts use Python 3.10+ and operate on `.aib_memory/` | A companion tool script could enumerate files and produce a manifest |
| Concepts.md defines model/vendor agnosticism as a hard requirement | The solution must not depend on tool-specific APIs |
| AIB convention files exist for every product-doc (27 convention files) | Each populated document must conform to its specific convention |

### Gaps and Unknowns

- The `aib-update-documentation.md` prompt was not fully read — it may already contain partial reverse-engineering logic.
- Real-world workspace sizes and file-type distributions are unknown for typical brownfield targets.
- Token limits vary significantly across models (GPT-5.3 Codex vs Claude Opus 4.6 vs Gemini 3.1).

### Proposed Validation Actions

- Read `aib-update-documentation.md` to check for overlap.
- Define a reference workspace profile (file count, total size, binary ratio) to test chunking strategies.

---

## Rewrite Proposal of the Request

## Goal

Design and specify a new AIB prompt (and optional supporting tool script) called `reverse-engineer` that enables the AI copilot to:

1. Enumerate every file in the current workspace directory tree (recursively, without missing any file).
2. Read all documents referenced in `.aib_memory/references.md`.
3. For each `product-doc` entry in `.aib_memory/references.md` where `edit_allowed = Y`, extract relevant knowledge from the workspace files and populate the corresponding documentation file under `.aib_memory/docs/` in compliance with the document's convention file (resolved via `.aib_brain/conventions/<requirement-id-lower>-convention.md`).

The approach must be workspace-agnostic (applicable to any project, not only AI_Builder) and model/vendor-agnostic (executable in VS Code Copilot, Claude Code, Cursor, CLI, etc.).

## Background

When AIB is installed into a brownfield (pre-existing) project, the `initialize` action seeds 27 empty product-doc stubs. Manual population of these files is labor-intensive and error-prone. An automated reverse-engineering capability would dramatically reduce time-to-value by extracting maximum useful information from the existing codebase.

## Scope

- New prompt file: `.aib_brain/prompts/aib-reverse-engineer.md`
- Optional new tool script: `.aib_brain/tools/reverse-engineer.py`
- Updates to `Concepts.md` to register the new action (if chosen approach warrants it)
- Population of all 27 editable product-doc files with extracted content
- Handling of workspaces with thousands of files and varied file types

## Out of scope

- Modifying the `.aib_brain/` folder structure beyond adding the new prompt/tool
- Changing `references.md` schema or entries
- Supporting file types that are not human-readable text
- Providing 100% accuracy — the output is a best-effort draft requiring human review

## Constraints

- Must not exceed LLM context-window limits; must handle workspaces of any practical size
- Must conform to each product-doc's convention file when writing content
- Must respect `edit_allowed` flag — never write to files marked `N`
- Must be model-agnostic and vendor-agnostic
- `.aib_brain/` is read-only to AIB automation

## Success criteria

- The prompt can be invoked on any workspace where AIB has been initialized
- All workspace files are enumerated and considered (none missed)
- Product-doc files are populated with structured, convention-compliant content derived from workspace evidence
- At least 5 materially different approaches are proposed in the analysis
- Each populated document includes traceability to source files from which knowledge was extracted
- Human reviewer can verify and refine the auto-generated content with reasonable effort

---

## Solution Options

### Option A: Single-Pass Monolithic Prompt

**Overview:** A single prompt file that instructs the AI to recursively list all workspace files, read each one, and then write all 27 product-doc files in one interaction.

**Benefits:**
- Simplest to implement — one prompt, no tooling.
- No new dependencies or scripts.
- Easy to understand and maintain.

**Trade-offs:**
- Will fail on any workspace that exceeds the context window.
- No intermediate checkpointing — if the session crashes mid-way, all work is lost.
- Quality degrades as context fills up with file content.

**Constraints:**
- Only viable for very small workspaces (~50 files, ~100KB total text).

**Risks:**
- Context overflow causing silent truncation or hallucination.
- No human review checkpoint before writing.

**Expected effort:** Low (1–2 hours for prompt authoring).

**Acceptance-test idea:** Run on a toy project with <20 files; verify all docs populated.

---

### Option B: Tool-Assisted Manifest + Prompt Pipeline

**Overview:** A Python tool script (`reverse-engineer.py`) first traverses the entire workspace, generates a **manifest file** (`.aib_memory/workspace-manifest.md`) containing file paths, sizes, types, and summary metadata. The prompt then reads the manifest, prioritizes files by relevance to each product-doc, reads the top-priority files, and populates documentation.

**Benefits:**
- Decouples file enumeration (deterministic, fast, no token cost) from content analysis (LLM-driven).
- Manifest can be reviewed by the human before the LLM processes content.
- Works for large workspaces because the manifest is compact.
- Follows existing AIB tool pattern (`initialize.py`, etc.).

**Trade-offs:**
- Requires a new Python script in `.aib_brain/tools/`.
- Two-step invocation (run script, then run prompt).
- Manifest generation logic must handle edge cases (symlinks, very long paths, encoding issues).

**Constraints:**
- Python 3.10+ required (already the AIB standard).

**Risks:**
- Manifest may still be large for huge monorepos (mitigated by summarization and filtering heuristics in the script).

**Expected effort:** Medium (4–6 hours: script + prompt + manifest format design).

**Acceptance-test idea:** Run script on a 1000+ file project; verify manifest is complete and under 50KB; run prompt and verify populated docs.

---

### Option C: Iterative Document-by-Document Prompt Chain

**Overview:** One master prompt orchestrates a loop: for each product-doc file, it reads the relevant convention, identifies which workspace files are likely relevant (using directory listing and filename/path heuristics), reads those files, and writes that single product-doc. Repeats for all 27 documents.

**Benefits:**
- Each document gets a focused, fresh context window — avoids overflow.
- Convention compliance is enforced per document.
- Failures are isolated — one document failing doesn't block others.
- Most natural fit for the existing "read convention → read sources → write doc" pattern in AIB prompts.

**Trade-offs:**
- 27 sequential prompt invocations — slower.
- Some workspace files will be re-read across multiple document passes (redundant I/O).
- Requires a dispatch mechanism (the master prompt or a tool script must track progress).

**Constraints:**
- Model must support multi-turn or the user must trigger each iteration.

**Risks:**
- Inconsistencies between documents if different workspace snapshots are used per pass (mitigated if workspace is stable during the process).

**Expected effort:** Medium-high (6–8 hours: master prompt + per-doc logic + progress tracking).

**Acceptance-test idea:** Run on a medium project; verify each of the 27 docs is populated, passes convention validation, and references specific source files.

---

### Option D: Two-Phase Extract-Then-Populate

**Overview:**
- **Phase 1 (Extract):** The prompt (or tool) scans the workspace and produces an intermediate **knowledge extraction document** (`.aib_memory/requests/<folder>/workspace-extract.md`) organized by AIB documentation domains (ARCH, DATA, SEC, etc.). Each entry cites the source file and extracted fact.
- **Phase 2 (Populate):** A second prompt reads the extraction document plus the conventions and writes each product-doc file from the curated extractions.

**Benefits:**
- Clean separation of concerns: extraction is source-evidence-focused; population is convention-focused.
- The extraction document serves as an auditable evidence trail.
- Human can review/edit the extraction before population — maximum safety.
- Phase 2 is essentially the existing `aib-update-documentation.md` flow with better input.

**Trade-offs:**
- Two distinct prompts/phases; more complex orchestration.
- The extraction document can be large.
- Requires defining a new intermediate artifact format.

**Constraints:**
- Extraction document must be structured enough for Phase 2 to consume deterministically.

**Risks:**
- Information loss between extraction and population if the intermediate schema is too lossy.

**Expected effort:** High (8–12 hours: extraction prompt + schema + population prompt + integration).

**Acceptance-test idea:** Run Phase 1; human reviews extraction; run Phase 2; verify docs populated; compare coverage with a human-authored baseline.

---

### Option E: Hybrid Manifest + Chunked Extraction with Progress State

**Overview:** Combines the best of Options B, C, and D:
1. A Python tool generates a workspace manifest with file metadata and approximate token counts.
2. The manifest is analyzed by a prompt to produce a **reading plan** — which files to read for which product-docs, in what order, chunked to fit context windows.
3. The prompt executes the reading plan in chunks, accumulating extracted knowledge in a **state file** (`.aib_memory/requests/<folder>/re-state.json` or `.md`).
4. After all chunks are processed, a final prompt reads the accumulated state + conventions and writes all product-doc files.
5. Progress is checkpointed in the state file so the process can resume after interruption.

**Benefits:**
- Handles workspaces of any size via deterministic chunking.
- Checkpointing enables resume-after-failure.
- Auditable state file for human review.
- Model-agnostic — the manifest tool is Python; the prompts work on any LLM.
- Most robust and production-ready approach.

**Trade-offs:**
- Most complex to implement.
- Requires defining a state file schema.
- Multiple invocations (tool + N prompt rounds + final write).

**Constraints:**
- Requires the environment to support multi-step prompt execution or user-triggered steps.

**Risks:**
- Over-engineering for small projects where Option A would suffice.
- State file corruption if process is interrupted during write.

**Expected effort:** High (12–16 hours: tool + reading plan prompt + chunked extraction prompt + final write prompt + state schema).

**Acceptance-test idea:** Run on a large open-source project (e.g., 5000+ files); verify all chunks processed; verify state file completeness; verify populated docs; test resume by interrupting mid-way.

---

### Option F: Convention-Driven Targeted Scan (Lightweight Approach)

**Overview:** Instead of reading all files, the prompt reads each product-doc convention file first and extracts **search patterns** (file types, naming patterns, keywords) that would contain relevant information for that document. Then it uses targeted file searches (e.g., `*.tf` for infrastructure, `*.yaml` for CI/CD, `requirements.txt` for dependencies) to find and read only the relevant files for each document.

**Benefits:**
- Minimal file reads — only reads what matters per document.
- Fits within context windows even for large workspaces.
- Leverages existing convention files as heuristic guides.
- Fast and token-efficient.

**Trade-offs:**
- May miss unexpected sources of knowledge (e.g., critical information in a README that isn't targeted by any pattern).
- Convention files must contain enough hints to derive meaningful search patterns (currently they may not).
- Some manual tuning of search heuristics per convention may be needed.

**Constraints:**
- Requires that conventions or a separate mapping define which file patterns are relevant to each product-doc.

**Risks:**
- Incomplete coverage — the "no file missed" requirement is partially relaxed (files are enumerated but not all read).

**Expected effort:** Medium (4–6 hours: pattern extraction logic + targeted reading prompt).

**Acceptance-test idea:** Run on a medium project; measure coverage (% of product-docs populated with substantive content) vs. Option C or D.

---

### Recommendation

**Option E (Hybrid Manifest + Chunked Extraction with Progress State)** is recommended for a production-quality solution due to its robustness across workspace sizes, checkpointing, and auditability.

However, **Option B (Tool-Assisted Manifest + Prompt Pipeline)** offers the best effort-to-value trade-off for an initial implementation and can be evolved toward Option E incrementally.

For a practical phased approach: implement Option B first, validate on real projects, then extend to Option E as needed.

---

## Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | New tool script would be cataloged here |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Architecture section may need update to document the reverse-engineering flow |

All 27 product-doc files are indirect targets (they will be populated by the new capability), but the above two are directly affected by the implementation of the capability itself.

---

## Operational & Documentation Implications

- **Runbooks:** A new operational runbook entry will be needed to describe how to invoke the reverse-engineering prompt on a brownfield project.
- **SLAs/SLOs:** Not applicable.
- **Monitoring/observability:** No runtime monitoring needed; the prompt is invoked on-demand.
- **Data quality rules:** The populated product-doc files should be treated as draft quality until human-reviewed; a mechanism to mark documents as "draft" vs "reviewed" may be desirable.
- **Product documentation:** `Concepts.md` needs an update to register the new action (if approach A is chosen in DP-1). The `README.md` at the workspace root should mention the reverse-engineering capability.

---

## Risks

- Risk R1: Context-window overflow for large workspaces
  - Probability: High
  - Impact: High
  - Mitigation: Use manifest-based approach (Options B/E) to keep per-invocation context bounded; implement chunking.
  - Owner (role): Prompt author

- Risk R2: Hallucinated documentation content when source evidence is insufficient
  - Probability: Medium
  - Impact: High
  - Mitigation: Require source-file citations in every populated section; flag low-confidence entries; mandate human review phase.
  - Owner (role): Prompt author + Human reviewer

- Risk R3: Overwriting user-curated content in product-doc files that were manually edited
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Check if product-doc content is non-placeholder before writing; prompt user for confirmation; or write to a separate draft file first.
  - Owner (role): Prompt author

- Risk R4: Model/vendor incompatibility — prompt features that work in one environment may not work in another
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Use only standard markdown prompt patterns; avoid environment-specific tool calls in the prompt itself; isolate vendor-specific logic in tool scripts.
  - Owner (role): Prompt author

- Risk R5: Inconsistent output quality across the 27 documents — some will have rich extractable content, others almost none
  - Probability: High
  - Impact: Low
  - Mitigation: Accept that some documents will remain sparse; clearly indicate confidence level and extraction coverage in each populated document.
  - Owner (role): Prompt author

---

## Open Questions & Next Actions

1. **What is the content of `aib-update-documentation.md`?** There may be significant overlap with the proposed reverse-engineering prompt.
   - Owner: AI agent
   - Trigger: Before plan creation
   - Resolution path: Read the file and assess overlap; decide whether to extend it or create a new prompt.

2. **Should the reverse-engineering prompt become a formal AIB action (with entry in the action contract matrix) or remain a standalone prompt?**
   - Owner: Human (product owner)
   - Due: Before iteration 01 plan
   - Resolution path: Answer via questionnaire DP-1.

3. **What level of human review is acceptable before writing to product-doc files?**
   - Owner: Human (product owner)
   - Due: Before iteration 01 plan
   - Resolution path: Answer via questionnaire DP-2.

4. **Are there known target brownfield projects to validate the approach against?**
   - Owner: Human (product owner)
   - Due: Before implementation
   - Resolution path: Identify 1–2 candidate projects for pilot testing.

5. **Should populated product-doc files include a "draft" watermark or confidence indicator?**
   - Owner: Human (product owner)
   - Due: Before implementation
   - Resolution path: Answer via questionnaire.
