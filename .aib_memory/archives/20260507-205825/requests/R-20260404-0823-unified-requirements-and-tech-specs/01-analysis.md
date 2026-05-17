# Executive Summary

- Request ID: R-20260404-0823

- Request title: Unified requirements and tech specs — create `aib-context.md` prompt

- Iteration ID: 01

- High-level purpose: Design and write a new AIB prompt file `.aib_brain/prompts/aib-context.md` that, when executed by an AI agent, produces or replaces the file `.aib_memory/context.md`. This unified file must consolidate all workspace-specific product knowledge so that an AI agent can fully understand and recreate the product from that single document.

- Background context: The AIB workspace currently stores product knowledge across 27 individual documentation files in `.aib_memory/docs/`. For brainstorming and AI-driven comprehension, navigating 27 files is cumbersome. A single unified context document provides a faster comprehension path and a reliable seed for AI tasks.

- No existing `aib-context.md` prompt exists; this is a net-new addition to `.aib_brain/prompts/`.

- No existing `context.md` exists in `.aib_memory/`; it will be created by executing the new prompt.

- This is iteration 01; no prior iterations exist for this request. No conflicts to resolve.

# Scope Interpretation

- **In scope (explicit):** Creation of a new prompt file at exactly `.aib_brain/prompts/aib-context.md`.

- **In scope (explicit):** The prompt, when executed, creates or updates `.aib_memory/context.md` as a full content replacement.

- **In scope (explicit):** The prompt must explore the workspace excluding `.aib_brain/`, virtual environment folders, and unmodified external libraries.

- **In scope (explicit):** The resulting `context.md` must be complete enough for an AI agent to recreate the product from it alone.

- **In scope (implicit rule - AIB framework):** The new prompt must follow the `aib-*.md` naming convention and be discoverable by the AIB Command Menu as a Prompt Action (TERM-0013).

- **In scope (implicit rule - AIB framework):** The prompt must be model/vendor/tool-agnostic and handle context-window limitations.

- **Out of scope (explicit):** The prompt must NOT explore the `.aib_brain/` folder.

- **Out of scope (explicit):** The prompt must NOT modify any existing documentation file.

- **Out of scope (explicit):** Virtual environments (`.venv/`, `venv/`), unmodified external libraries, package caches (`node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`), and the `.git/` directory are excluded from exploration.

- **Out of scope (implicit):** Creating a `references.md` entry for `context.md` — this is a generated artifact, not a governed product-doc.

# Domain Knowledge Essentials

- **AIB (AI Builder):** Minimal, model-agnostic framework for specification-driven development. Maintains brain assets (`.aib_brain/`) and memory artifacts (`.aib_memory/`) in a repository workspace.

- **Brain Folder (`.aib_brain/`, TERM-0003):** Contains reusable, replaceable AIB framework assets: prompts, conventions, templates, tools. Explicitly excluded from exploration per this request.

- **Memory Folder (`.aib_memory/`, TERM-0004):** Contains workspace-specific artifacts: request files, product documentation (`docs/`), references register, requests register.

- **Product Doc (TERM-0007):** A convention-governed documentation file listed in `.aib_memory/references.md`. There are 27 product-doc entries in the current workspace spanning 11 domains.

- **Prompt Action (TERM-0013):** A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file. Executable when copilot CLI is present; displayed as informational when absent. The new `aib-context.md` will be auto-discovered by the AIB Command Menu.

- **Context File (new concept, not yet in KNW-01):** A unified synthesis document at `.aib_memory/context.md` that aggregates all product-relevant information for brainstorming and AI-based comprehension. Not a governed product-doc; generated artifact.

- **Product Documentation domains (from `Product_Documentation.md`):** ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC — 11 domains, 27 standard documents.

- **Impacted personas:** DEVELOPER (primary consumer of `context.md` for brainstorming), AI_AGENT (executes the prompt; uses `context.md` as input for future AI tasks), MAINTAINER (owns the new prompt file).

- **Business process touched:** UC-003 (Generate iteration artifacts) — the context prompt is an additional prompt action. Also supplements the reverse-engineer workflow (UC-004 adjacent).

- **Acceptance impact from product/business perspective:** When executed, `.aib_memory/context.md` provides a single document for brainstorming instead of navigating 27+ individual files.

# Technical Knowledge & Terms

- **`.aib_brain/prompts/aib-context.md`:** The new AI-executable prompt file to be created. Written in Markdown; contains instructions for an AI agent.

- **`.aib_memory/context.md`:** The runtime output artifact produced when the prompt is executed. A unified Markdown document describing the full product. Written as full content replacement (not append).

- **`aib-reverse-engineer.md`:** Existing prompt that reads the workspace and populates individual product-doc files. Provides the closest structural template for `aib-context.md`. Key patterns to reuse: mandatory preflight, file inventory, context-window management, exclusion rules.

- **Workspace file inventory:** Technique of building a directory listing of all non-excluded workspace files before deep reading. Used in `reverse-engineer.py` and `aib-reverse-engineer.md`. The `context.md` prompt must use the same inventory pattern.

- **Context window management:** The practical constraint that AI models have a maximum context window. With 27 product-doc files plus workspace code, the total read volume may exceed 80% of available context. The prompt must define a prioritization and summarization fallback strategy.

- **Product Documentation domain registry (`Product_Documentation.md`):** Defines 11 domains and 27 document standard requirements. The `context.md` file should use these domains as section headings for consistency.

- **References register (`.aib_memory/references.md`):** Contains 27 product-doc entries + 1 domain entry (Concepts.md). All 27 product-doc paths are candidates for reading during context generation.

- **Excluded directories (normative for this prompt):** `.aib_brain/`, `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`.

- **Workspace-specific source files (in scope for direct read):** `README.md`, `scripts/release_bookkeeping.py`, `tests/` folder, root configuration files (`.gitignore`, `requirements.txt` if present). These are not covered by product-doc conventions.

- **Full content replacement:** The prompt must overwrite `context.md` on every execution, not append. This ensures idempotent behavior (same sources → equivalent output).

- **Non-functional attributes:** Model/vendor-agnostic; idempotent; context-window-aware; fail-safe (no edits to existing files on error).

# Assumptions

- Assumption A1: The `.aib_brain/` folder exclusion is intentional even though it contains the AIB framework definition (prompts, tools, conventions that define "how AIB works").
  - Rationale: The request explicitly states this exclusion. The stated purpose is capturing product-instance knowledge, not framework documentation.
  - Risk if false: `context.md` will be incomplete for full framework recreation; an AI using only `context.md` cannot rebuild the AIB framework itself.
  - Falsification method: Confirm with the user whether the exclusion is intentional given the "recreatable" success criterion.

- Assumption A2: `context.md` should use a structured domain-aligned format (mirroring the 11 domains from `Product_Documentation.md`) rather than a flat narrative or free-form structure.
  - Rationale: Domain alignment makes sections traceable to source product-doc files and easier to maintain. Consistent with AIB's convention-driven approach.
  - Risk if false: User may prefer a different structure (e.g., narrative or task-oriented).
  - Falsification method: Review final prompt structure with user feedback after first execution.

- Assumption A3: The prompt should use a hybrid read strategy: read product-doc files from `.aib_memory/docs/` first (primary sources), then supplement with direct workspace scans for code/test artifacts not covered by product docs.
  - Rationale: Product docs are curated and convention-governed; direct scans catch implementation details in `scripts/` and `tests/` not represented in docs.
  - Risk if false: If product docs are empty stubs, the hybrid approach produces a sparse context.md; a direct-scan-only approach would be more resilient.
  - Falsification method: Check at execution time whether product docs have meaningful content before relying on them.

- Assumption A4: The new prompt will be auto-discovered by the AIB Command Menu (CMP-ART-0006) when it follows the `aib-*.md` naming convention in `.aib_brain/prompts/`.
  - Rationale: ARCH-01 and CMP-01 confirm the menu dynamically discovers all `aib-*.md` files; TERM-0013 defines this behavior.
  - Risk if false: A `menu_config.json` entry may be required; additional configuration needed.
  - Falsification method: Inspect `menu.py` `EXCLUDE_SCRIPTS` list and menu loading logic to confirm autodiscovery behavior.

- Assumption A5: The `context.md` output file does not need a `.aib_memory/references.md` entry because it is a generated synthesis artifact (analogous to `implementation.md`), not a governed product-doc.
  - Rationale: The references register tracks files that AIB tools may read and edit according to conventions. Generated artifacts are managed by their generating prompts.
  - Risk if false: Without a references entry, future AIB tools that gatekeep on references.md will not recognize `context.md` as an editable target.
  - Falsification method: Check whether `implementation.md` or similar generated files appear in references.md (they do not).

# Impact Assessment

## Affected Components / Areas

- `.aib_brain/prompts/` — New file `aib-context.md` (add)
- `.aib_memory/context.md` — New runtime output artifact, created on first execution (add)
- AIB Command Menu (CMP-ART-0006) — Auto-discovers the new prompt; no code change required
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — New glossary term "Context File" (optional documentation update)

## Change Type and Dependencies

- **`.aib_brain/prompts/aib-context.md`:**
  - Change type: **add**
  - Dependencies: None (standalone prompt file; requires no code changes)
  - Sequencing: Can be created immediately; the runtime output `context.md` is produced only when the prompt is executed

- **`.aib_memory/context.md`** (execution artifact):
  - Change type: **add** (produced at prompt execution time)
  - Dependencies: Requires an AI agent to execute `aib-context.md`
  - Sequencing: Created after the prompt is finalized and executed

- **AIB Command Menu (CMP-ART-0006):**
  - Change type: None (autodiscovery handles the new entry)
  - Dependencies: `aib-context.md` must use `aib-` prefix in `.aib_brain/prompts/`

## Domain Impacts

- DOMAIN (ARCH): No direct impact. ARCH-01 could optionally note the new prompt and `context.md` artifact; not required for this request.

- DOMAIN (CMP): No impact. CMP-01 catalogs tool scripts (`*.py`); prompt files are not cataloged in CMP-01.

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): No impact detected.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (KNW): Minor recommended impact.
  - KNW-01 (Domain glossary): New term "Context File" should be added (TERM-0014) to document `.aib_memory/context.md` as a concept.

- DOMAIN (RQT): No impact detected.

- DOMAIN (OBS): No impact. The AIB Command Menu will produce a per-action log when the prompt is run via menu (OBS-01 behavior; no changes needed).

- DOMAIN (OPR): No impact detected.

- DOMAIN (SEC): No impact. The prompt reads workspace files but does not handle secrets or credentials.

## Constraints

- The prompt MUST NOT trigger any edits to existing workspace files.
- The prompt MUST produce `context.md` as full content replacement (not append).
- `.aib_brain/` content is explicitly excluded from exploration.
- The prompt MUST be model/vendor-agnostic and runnable without tool-specific extensions.
- Context-window management must be built into the prompt for workspaces with many populated docs.

## Required Documentation Updates

- KNW-01 - Domain glossary
  Required update? YES (recommended)
  Reason: New concept "Context File" introduced by this request needs a glossary entry.

- ARCH-01 - High-level architecture
  Required update? NO (optional)
  Reason: The new prompt is a framework asset under `.aib_brain/` (excluded domain); `context.md` is a derived artifact. Noting it in ARCH-01 is optional and can be deferred.

- All other product-docs
  Required update? NO
  Reason: No structural changes to existing components.

## Decision Points

**DP-1: Should `context.md` be added to `.aib_memory/references.md`?**
- Option A: Add as `type=other`, `edit_allowed=Y`. Enables AIB reference gating.
- Option B: Do not add. Treat as a generated artifact managed by the prompt (same as `implementation.md`).
- Recommended: **Option B.** `context.md` is a generated synthesis; it is managed by re-executing `aib-context.md`. No references.md entry needed.

**DP-2: What read strategy should the prompt use?**
- Option A: Product-docs only (from `.aib_memory/docs/`).
- Option B: Direct workspace scan only.
- Option C: Hybrid — product-docs first, then targeted workspace scan for code/test files.
- Recommended: **Option C (hybrid).** Maximizes coverage; built-in fallback when docs are stubs.

**DP-3: What structure should `context.md` use?**
- Option A: Domain-aligned sections (ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC) matching `Product_Documentation.md`.
- Option B: Narrative structure (Overview → Architecture → Domain → Operations → Security).
- Option C: Free-form synthesis.
- Recommended: **Option A.** Domain-aligned structure makes sections traceable to source files and consistent with AIB conventions.

# Research Plan and Findings

**Methodology:** Internal document scan, repository file inventory, pattern scan against existing prompts.

**Evidence summary:**
- The `.aib_brain/prompts/` directory contains exactly 6 existing prompt files; none is `aib-context.md`. Confirmed new file needed.
- `aib-reverse-engineer.md` provides the closest structural template: mandatory preflight, file inventory, exclusion list, context-window management, validation section.
- 27 product-doc files exist in `.aib_memory/docs/`; several are populated (ARCH-01, CMP-01, KNW-01, KNW-03, OBS-01, RQT-02) while many remain as stubs ("seeded by AIB initialize").
- `scripts/release_bookkeeping.py` and `tests/*.py` exist as workspace-specific code not covered by product-doc conventions; they must be read during workspace scan.
- `README.md` exists at repo root and is a key entry-point document.
- No `context.md` exists in `.aib_memory/`; confirmed net-new creation.
- The AIB Command Menu (`menu.py`) uses autodiscovery for `aib-*.md` files; no menu configuration changes needed.

**Gaps and unknowns:**
- The exact level of detail expected in `context.md` (summary vs. full content) is not specified in the request.
- Whether the `aib_brain/` exclusion is intentional given the "full recreation" success criterion is ambiguous (see Assumption A1).

**Proposed validation actions:**
- After creating the prompt, execute it once to verify `context.md` is produced with non-empty sections.
- Verify `context.md` passes a manual review: can an AI agent understand the product structure from it alone?

**Files Read:**

- `.aib_brain/prompts/aib-create-analysis.md` — confirmed prompt structure and output target for this analysis
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/request.md` — primary request input
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/iterations.md` — confirmed iteration 01 is active
- `.aib_memory/references.md` — confirmed 27 product-doc entries + 1 domain entry
- `.aib_brain/Concepts.md` — framework concepts, lifecycle rules, folder structure
- `.aib_brain/conventions/analysis-convention.md` — required analysis document structure and authoring rules
- `.aib_brain/conventions/request-convention.md` — request file format for rewrite proposal
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — product charter (stub only)
- `.aib_memory/docs/03 Requirements/RQT-02.md` — requirements document (populated; confirmed functional/non-functional requirements)
- `.aib_memory/docs/03 Requirements/RQT-04.md` — assumptions & constraints register (stub)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — high-level architecture (populated; confirmed component inventory)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — topology/network (stub)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-05.md` — identifier naming (stub)
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — script catalog (populated; confirmed tool script inventory)
- `.aib_memory/docs/04 Technology/Development/DEV-01.md` — developer setup guide (stub)
- `.aib_memory/docs/04 Technology/Development/DEV-03.md` — code version control (stub)
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — logging specification (populated; confirmed log schema)
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — use cases & personas (populated; confirmed personas and use cases)
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — domain glossary (populated; confirmed 13 terms; "Context File" not yet defined)
- `.aib_brain/prompts/aib-reverse-engineer.md` — reference pattern for prompt structure (preflight, inventory, exclusions, context management)
- `.aib_brain/Product_Documentation.md` — confirmed 11 domains, 27 document types
- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/01-analysis.md` — reference for analysis format and style
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — [SKIPPED — domain out of scope for this request]
- `.aib_memory/docs/04 Technology/Backup and Disaster Recovery/DSR-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Operations/OPR-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Operations/OPR-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Operations/OPR-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Operations/OPR-05.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Inventory/FNL-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/01 Product Management/Budget and Cost/FNL-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/01 Product Management/User Training and Support/KNW-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-05.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Observability/OBS-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Development/DEV-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Development/DEV-05.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Deployment/DEV-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Deployment/DEV-08.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Compute/DEV-06.md` — [SKIPPED — domain out of scope]

# Rewrite Proposal of the Request

## Goal

Create the file `.aib_brain/prompts/aib-context.md` — an AI-executable prompt that, when run by an AI agent (GitHub Copilot, Claude, or any other supported model), produces or fully replaces `.aib_memory/context.md`. The resulting file must be a unified, structured synthesis of all workspace-specific product knowledge organized by the 11 product documentation domains (ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC), enabling an AI agent to fully understand the product and its structure from that single document.

## Background

The AIB workspace stores product knowledge across 27 individual documentation files under `.aib_memory/docs/`. For brainstorming sessions and AI-assisted work, navigating 27 separate files is inefficient. A single unified context document — `.aib_memory/context.md` — provides a faster comprehension path and a reliable seed for AI-driven tasks. The `aib-context.md` prompt is the mechanism for generating and refreshing this document. It is analogous to `aib-reverse-engineer.md` but writes to a single aggregated output instead of individual product-doc files.

## Scope

- Creation of exactly one new file: `.aib_brain/prompts/aib-context.md`
- The prompt, when executed by an AI agent, must:
  - Build a deterministic inventory of all workspace files excluding defined directories
  - Read all product-doc files from `.aib_memory/docs/` (via `.aib_memory/references.md` where `type=product-doc`) as primary sources
  - Read workspace-specific source files outside product-docs: `README.md`, `scripts/`, `tests/`, and any root configuration files (e.g., `.gitignore`)
  - Synthesize all findings into `.aib_memory/context.md` using domain-aligned sections
  - Handle context-window limitations with explicit prioritization and summarization rules
  - Produce full content replacement of `context.md` (not append)
- The prompt must be model/vendor/tool-agnostic

## Out of scope

- Modification of any existing file in the workspace (product-docs, scripts, tests, conventions, templates, other prompts)
- Exploration or reading of the `.aib_brain/` folder and its contents (prompts, tools, conventions, templates)
- Exploration of virtual environments: `.venv/`, `venv/`
- Exploration of unmodified package directories: `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- Exploration of `.git/` version-control internals
- Addition of a new entry for `context.md` in `.aib_memory/references.md`
- Modification of any existing prompt, convention, template, or tool file

## Constraints

- The prompt MUST NOT edit any existing workspace file; the only permitted write is `.aib_memory/context.md`
- Re-executing the prompt must produce semantically equivalent output (full replacement, not append)
- The prompt MUST follow the `aib-*.md` naming convention (already satisfied by the target filename)
- The prompt MUST include an explicit context-window management rule specifying which domains to prioritize when context is constrained
- The prompt MUST NOT require or embed tool-specific extensions; it must work in any AI agent environment

## Success criteria

- File `.aib_brain/prompts/aib-context.md` exists and is valid Markdown
- When executed by any supported AI agent, the prompt produces `.aib_memory/context.md` without modifying any other file
- `.aib_memory/context.md` contains:
  - A clearly labeled section for each of the 11 product documentation domains
  - Non-empty content for every domain that has populated product-doc files; "not yet documented" notice for stub-only domains
  - Summary of workspace code artifacts (`scripts/`, `tests/`) under the applicable domain sections
  - No content derived from excluded directories
- Re-executing the prompt produces output with equivalent structure and semantically consistent content (idempotent behavior)
- A developer or AI agent reading only `.aib_memory/context.md` can answer: what is this product, what components exist, how are they structured, what are the key workflows, what are the constraints and requirements

# Solution Options

## Option A: Synthesis-only from product-doc files

**Overview:** The prompt reads all 27 product-doc files from `.aib_memory/docs/` via references.md and synthesizes them into `context.md`. No direct workspace code scan.

**Benefits:**
- Simple implementation; fewest instructions in the prompt
- Leverages curated, convention-governed product docs
- Fast execution; fewer files to read
- Consistent with the existing AIB documentation-centric approach

**Trade-offs:**
- Relies entirely on product docs being populated; empty stubs produce empty or near-empty sections
- Misses code-level evidence in `scripts/`, `tests/` not represented in product docs
- Product docs may lag behind actual code

**Constraints:** At least the key product docs (ARCH-01, CMP-01, KNW-01) must be populated for useful output.

**Risks:** If docs are mostly stubs, `context.md` will be sparse and insufficient for reconstruction.

**Expected effort:** ~2 hours to write the prompt.

**High-level acceptance test:** Execute prompt; verify `context.md` has non-empty sections for ARCH, CMP, KNW, OBS, RQT domains (confirmed populated).

---

## Option B: Direct workspace scan (no reliance on product docs)

**Overview:** The prompt scans the entire workspace file tree directly (excluding exclusion list), reads source files, scripts, tests, README, and builds `context.md` from raw evidence without reading product-doc files.

**Benefits:**
- Always reflects actual state of the workspace
- No dependency on product docs being populated
- Captures implementation details directly from code and scripts

**Trade-offs:**
- More complex prompt logic (file discovery + selective reading)
- Potentially large context window consumption
- Produces less structured output (no convention alignment)
- Redundantly re-derives what may already be in product docs
- Harder to maintain as the workspace grows

**Constraints:** Must implement aggressive context-window management.

**Risks:** Context window overflow; inconsistent structure across executions.

**Expected effort:** ~4-5 hours to write and validate the prompt.

**High-level acceptance test:** Execute prompt; verify `context.md` references actual script names, function descriptions, and code artifacts.

---

## Option C: Hybrid approach (recommended)

**Overview:** The prompt performs two read phases:
1. Primary: Read all product-doc files from `.aib_memory/docs/` via references.md as curated knowledge sources
2. Supplementary: Perform a targeted workspace scan for key non-doc files (`README.md`, `scripts/`, `tests/`, root configs)
Synthesize both into a structured, domain-aligned `context.md`. When a product-doc section is empty/stub, fall back to workspace-derived content.

**Benefits:**
- Maximum coverage: curated docs + direct code evidence
- Context-aware fallback: stub docs are supplemented by workspace facts
- Produces structured, domain-aligned output consistent with AIB conventions
- Model/vendor-agnostic; works in any AI agent environment
- Closely mirrors the established `aib-reverse-engineer.md` pattern

**Trade-offs:**
- Slightly more complex prompt (two phases)
- Higher total read volume; requires explicit context-window management
- Execution time is longer than Option A

**Constraints:** Must include an explicit context-window management section specifying prioritization order.

**Risks:** If both product docs and workspace code are sparse, output remains sparse — but this accurately reflects the actual state of the workspace.

**Expected effort:** ~3-4 hours to write and validate.

**Recommendation:** **Option C.** It provides the best coverage for the stated success criterion ("product can be recreated by AI just from this file") with built-in fallback. The existing `aib-reverse-engineer.md` prompt provides a proven structural template. The additional complexity is justified by the comprehensiveness requirement.

# Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | New term "Context File" (TERM-0014) should be added to document `.aib_memory/context.md` as a concept |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Optional: note `aib-context.md` prompt and `context.md` artifact; not required for this iteration |

# Operational & Documentation Implications

- **AIB Command Menu:** The new `aib-context.md` prompt will be auto-discovered and surfaced as a Prompt Action (TERM-0013) in the AIB Command Menu when copilot CLI is available. No code changes to `menu.py` are required. The menu will display it as an informational entry when CLI is absent.

- **Per-action execution logging (OBS-01):** When executed via the AIB Command Menu, a per-action log will be generated at `logs/aib-action-<timestamp>-<action-id>.log`. No changes to the logging specification are required.

- **Product documentation:** KNW-01 glossary should add a new term "Context File" (TERM-0014) to document `.aib_memory/context.md` as a first-class concept. This update is recommended but can be deferred to a future iteration.

- **Runbooks:** No runbook changes required; the prompt is standalone and does not alter system lifecycle state.

- **`.aib_memory/context.md` lifecycle:** The file is a generated artifact managed exclusively by re-executing `aib-context.md`. It should be committed to version control to persist across sessions. It is not tracked in references.md (per DP-1).

# Risks

- Risk R1: Sparse context.md due to empty product-doc stubs
  - Probability: Medium (many docs remain as "seeded by AIB initialize" stubs per workspace scan)
  - Impact: Medium (context.md will have empty or minimal sections; partially useful for brainstorming)
  - Mitigation: Prompt uses hybrid strategy (Option C); falls back to direct workspace code scan when product docs are empty
  - Owner (role): AI_AGENT

- Risk R2: Context window overflow when reading 27 product-docs plus workspace files
  - Probability: Medium (total read volume may exceed 80% of available context)
  - Impact: High (AI agent may skip critical docs or hallucinate content for missing sections)
  - Mitigation: Prompt must include explicit context-window management rules: prioritize populated docs and critical domains (ARCH, RQT, KNW, CMP first); summarize verbose docs; note which files were skipped
  - Owner (role): AI_AGENT

- Risk R3: `aib_brain/` exclusion creates an incomplete recreation document
  - Probability: High (exclusion is explicit and deterministic)
  - Impact: Low-Medium (context.md captures the product instance; framework behavior requires separate `.aib_brain/` assets)
  - Mitigation: Add a note in `context.md` preamble that framework assets are in `.aib_brain/` and excluded by design; this is an accepted trade-off per the request
  - Owner (role): DEVELOPER (accept the trade-off)

- Risk R4: Non-idempotent execution — re-running produces structurally different `context.md`
  - Probability: Low (same source files and prompt → deterministic structure; model-level variation is minor)
  - Impact: Low (minor content drift acceptable for brainstorming use case; structure remains consistent)
  - Mitigation: Prompt explicitly states full content replacement and domain-aligned structure; structure is enforced by prompt instructions
  - Owner (role): AI_AGENT

# Open Questions & Next Actions

1. **[User — clarification needed]** Is the exclusion of `.aib_brain/` intentional given that `.aib_brain/` contains the framework prompts, tools, and conventions that define how AIB works? The current success criterion states "the product can be recreated by AI just from this file" — but without `.aib_brain/` content, an AI could not recreate the AIB framework itself from `context.md`.
   - Owner: User
   - Due: Before implementation
   - Resolution path: If yes (exclusion is intentional), add a note in `context.md` preamble that framework recreation requires `.aib_brain/`. If no (include `.aib_brain/`), update the Out of Scope section accordingly.

2. **[AI — resolved]** Read strategy: Option C (hybrid) is the recommended approach. No user input needed.
   - Owner: AI
   - Due: Resolved in analysis
   - Resolution path: Adopt Option C per analysis recommendation.

3. **[AI — resolved]** `context.md` structure: domain-aligned sections (Option A from DP-3) are the recommended structure. No user input needed.
   - Owner: AI
   - Due: Resolved in analysis
   - Resolution path: Adopt domain-aligned structure per analysis recommendation.
