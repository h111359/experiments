# Executive Summary

- Request ID: R-20260404-0823

- Request title: Unified requirements and tech specs — create `aib-context.md` prompt

- Iteration ID: 02

- High-level purpose: Design and write a new AIB prompt file `.aib_brain/prompts/aib-context.md` that, when executed by an AI agent, produces or fully replaces `.aib_memory/context.md` — a unified, structured synthesis of all workspace-specific product knowledge organized by the 11 product documentation domains.

- This is iteration 02 (follow-up). Iteration 01 produced a complete analysis (`01-analysis.md`) and questionnaire (`01-questionnaire.md`) with two open user questions: (QID-BF-001) whether `.aib_brain/` exclusion is intentional, and (QID-AT-001) level of detail in `context.md` sections.

- In this iteration, both open questions from iteration 01 are resolved by the AI based on explicit request language and workspace evidence, eliminating the need for user clarification. Per iteration precedence rules, this analysis overrides conflicting guidance from iteration 01.

- No conflicts exist between iteration 01 and iteration 02; this iteration refines and resolves ambiguities identified in the prior analysis.

# Scope Interpretation

- **In scope (explicit):** Creation of exactly one new file: `.aib_brain/prompts/aib-context.md`.

- **In scope (explicit):** The prompt, when executed, must produce or fully replace `.aib_memory/context.md` as a structured synthesis document.

- **In scope (explicit):** The prompt must build a deterministic inventory of all workspace files excluding defined directories (`.aib_brain/`, `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`).

- **In scope (explicit):** The prompt must read all product-doc files from `.aib_memory/docs/` (via `.aib_memory/references.md` where `type=product-doc`) as primary sources.

- **In scope (explicit):** The prompt must read workspace-specific source files outside product-docs: `README.md`, `scripts/`, `tests/`, and any root configuration files.

- **In scope (explicit):** The resulting `context.md` must be organized by the 11 product documentation domains (ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC).

- **In scope (explicit):** Context-window management rules with explicit prioritization and summarization strategy must be built into the prompt.

- **In scope (explicit):** Full content replacement (not append) on each execution; idempotent behavior.

- **In scope (explicit):** Model/vendor/tool-agnostic design.

- **In scope (implicit rule - AIB framework):** The new prompt auto-discovered by the AIB Command Menu as a Prompt Action (TERM-0013) when it follows the `aib-*.md` naming convention in `.aib_brain/prompts/`.

- **Out of scope (explicit):** Modification of any existing file in the workspace (product-docs, scripts, tests, conventions, templates, other prompts).

- **Out of scope (explicit):** Exploration or reading of the `.aib_brain/` folder and its contents (prompts, tools, conventions, templates).

- **Out of scope (explicit):** Exploration of virtual environments (`.venv/`, `venv/`), unmodified package directories (`node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`), and `.git/` version-control internals.

- **Out of scope (explicit):** Addition of a new entry for `context.md` in `.aib_memory/references.md`.

- **Out of scope (explicit):** Modification of any existing prompt, convention, template, or tool file.

# Domain Knowledge Essentials

- **AI Builder (AIB):** Minimal, model-agnostic framework for specification-driven development. Maintains reusable brain assets (`.aib_brain/`) and workspace-specific memory artifacts (`.aib_memory/`) in a repository workspace.

- **Brain Folder (`.aib_brain/`, TERM-0003):** Contains reusable, replaceable AIB framework assets: prompts, conventions, templates, tools. Explicitly excluded from exploration per this request's out-of-scope clause.

- **Memory Folder (`.aib_memory/`, TERM-0004):** Contains workspace-specific artifacts: request files, product documentation (`docs/`), references register, requests register. This is the primary source for `context.md`.

- **Product Doc (TERM-0007):** A convention-governed documentation file listed in `.aib_memory/references.md`. There are 27 product-doc entries in the current workspace spanning 11 domains. Of these, 16 have real content and 11 are stub/templates with only seeded placeholder text.

- **Prompt Action (TERM-0013):** A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file. The new `aib-context.md` will be auto-discovered by the AIB Command Menu.

- **Context File (new concept):** A unified synthesis document at `.aib_memory/context.md` that aggregates all product-relevant information for brainstorming and AI-based comprehension. Not a governed product-doc; a generated artifact analogous to `implementation.md`.

- **Product Documentation Domains:** 11 standard domains defined in `Product_Documentation.md` — ARCH (Architecture), CMP (Compute), DATA (Data), DEV (Development), DSR (Disaster Recovery), FNL (Financial), KNW (Knowledge), RQT (Requirements), OBS (Observability), OPR (Operations), SEC (Security).

- **Impacted personas:** DEVELOPER (primary consumer of `context.md`), AI_AGENT (executes the prompt and uses `context.md` as seed for future tasks), MAINTAINER (owns the new prompt file).

- **Business process touched:** UC-003 (Generate iteration artifacts) — the context prompt is an additional prompt action. Adjacent to UC-004 (reverse-engineer) in workflow.

- **Acceptance impact:** When executed, `context.md` provides a single document for brainstorming instead of navigating 27+ individual files. A developer or AI agent reading only `context.md` can answer: what is this product, what components exist, how are they structured, what are the key workflows, what are the constraints.

# Technical Knowledge & Terms

- **`.aib_brain/prompts/aib-context.md`:** The new AI-executable prompt file to be created. Written in Markdown; contains structured instructions for any AI agent to follow. Produces `.aib_memory/context.md` as its output.

- **`.aib_memory/context.md`:** The runtime output artifact produced when the prompt is executed. A unified Markdown document describing the full product. Written as full content replacement (not append).

- **`aib-reverse-engineer.md`:** Existing prompt that reads the workspace and populates individual product-doc files. Provides the closest structural template for `aib-context.md`: mandatory preflight, file inventory, exclusion rules, context-window management, traceability. The key difference is that the context prompt writes a single aggregated output file rather than multiple product-doc files.

- **Workspace file inventory:** Technique of building a deterministic directory listing of all non-excluded workspace files before deep reading. Used in `aib-reverse-engineer.md`. The context prompt must use the same inventory pattern for the workspace scan phase.

- **Context-window management:** Practical constraint that AI models have limited context windows. With 27 product-doc files plus workspace code, the total volume may exceed capacity. The prompt must define domain prioritization (ARCH, RQT, KNW, CMP first) and summarization fallback.

- **Product Documentation domain registry (`Product_Documentation.md`):** Defines 11 domains and 27 document standard requirements. Used as the section structure for `context.md`.

- **References register (`.aib_memory/references.md`):** Contains 27 product-doc entries + 1 domain entry (Concepts.md). The 27 product-doc paths are the primary read set for the context prompt.

- **Excluded directories:** `.aib_brain/`, `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`.

- **Full content replacement:** The prompt must overwrite `context.md` on every execution, not append. Ensures idempotent behavior.

- **Hybrid read strategy:** Two-phase reading: (1) product-doc files from `.aib_memory/docs/`, (2) targeted workspace scan for non-doc files (`README.md`, `scripts/`, `tests/`, root configs). When product-doc sections are stubs, workspace-derived content supplements.

# Assumptions

- Assumption A1: The `.aib_brain/` folder exclusion is intentional and the success criterion "A developer or AI agent reading only `.aib_memory/context.md` can answer: what is this product, what components exist, how are they structured" refers to understanding the product instance, not recreating the AIB framework itself.
  - Rationale: The request explicitly lists `.aib_brain/` in "Out of scope." The success criteria ask about "the product" — the workspace-specific product described in `.aib_memory/docs/` — not the AIB framework. The framework is a generic, replaceable asset (per Concepts.md). A preamble note in `context.md` pointing to `.aib_brain/` for framework details resolves any ambiguity.
  - Risk if false: `context.md` would not describe AIB framework internals (prompts, conventions, tools). An AI reading only `context.md` could not rebuild `.aib_brain/` from scratch.
  - Falsification method: This assumption is validated by the explicit "Out of scope" clause in request.md. This resolves iteration 01 questionnaire QID-BF-001 with answer A.

- Assumption A2: `context.md` should use an adaptive detail level — concise key-fact summaries for populated product-doc sections (component names, IDs, critical decisions, relationships) and a "not yet documented" notice for stub-only domains.
  - Rationale: The primary use case is "brainstorming sessions and AI-assisted work" where navigating 27 files is inefficient. Concise summaries serve this use case optimally. The success criteria require answering high-level questions (what is this product, what components, key workflows, constraints) — not verbatim reproduction. Full verbatim content would make `context.md` excessively large (50-100KB) and undermine the "faster comprehension path" goal. Adaptive detail preserves signal-to-noise.
  - Risk if false: Summaries may omit details needed for specific deep-dive tasks; users must fall back to individual product-doc files.
  - Falsification method: This assumption is validated by the request's Background ("faster comprehension path") and Success criteria (question-answerable, not verbatim). This resolves iteration 01 questionnaire QID-AT-001 with answer A (concise summaries).

- Assumption A3: The prompt should use the hybrid read strategy (Option C from iteration 01 analysis): product-doc files first, then targeted workspace scan for `README.md`, `scripts/`, `tests/`, and root configs.
  - Rationale: Iteration 01 analysis recommended Option C. Product-doc files are the curated primary sources; workspace scan catches implementation details not in docs. This maximizes coverage while respecting context-window limits.
  - Risk if false: If product docs are mostly stubs, context.md will be sparse for those domains. However, the prompt can fall back to workspace-derived evidence.
  - Falsification method: Execute the prompt and verify non-empty sections for domains with populated docs.

- Assumption A4: `context.md` does not need a `.aib_memory/references.md` entry because it is a generated synthesis artifact, analogous to `implementation.md`.
  - Rationale: The references register tracks files governed by conventions and editable by AIB tools. Generated artifacts are managed by their generating prompts. `implementation.md` is not in references.md either.
  - Risk if false: Future tools that gatekeep on references.md will not recognize `context.md`.
  - Falsification method: The request explicitly states "Addition of a new entry for `context.md` in `.aib_memory/references.md`" is out of scope.

- Assumption A5: The prompt must include a preamble section in `context.md` output that states: (a) the document is auto-generated by `aib-context.md`, (b) framework definition assets live in `.aib_brain/` and are excluded by design, (c) the generation timestamp.
  - Rationale: This addresses the `.aib_brain/` exclusion transparency requirement without violating the out-of-scope constraint.
  - Risk if false: Users may not understand why framework details are absent.
  - Falsification method: Verify the prompt template includes this preamble.

# Impact Assessment

## Affected Components / Areas

- `.aib_brain/prompts/` — New file `aib-context.md` (add)
- `.aib_memory/context.md` — New runtime output artifact, created on first prompt execution (add)
- AIB Command Menu (CMP-ART-0006) — Auto-discovers the new prompt via `aib-*.md` naming convention; no code change required

## Change Type and Dependencies

- **`.aib_brain/prompts/aib-context.md`:**
  - Change type: **add**
  - Dependencies: None (standalone prompt file)
  - Sequencing: Can be created immediately; `context.md` is produced only when the prompt is executed

- **`.aib_memory/context.md`** (execution artifact):
  - Change type: **add** (produced at prompt execution time)
  - Dependencies: Requires an AI agent to execute `aib-context.md`; depends on product-doc files for content
  - Sequencing: Created after the prompt is finalized and executed

- **AIB Command Menu:**
  - Change type: None (autodiscovery)
  - Dependencies: `aib-context.md` must use `aib-` prefix in `.aib_brain/prompts/`

## Domain Impacts

- DOMAIN (ARCH): No direct impact. The new prompt is a brain asset; `context.md` is a derived artifact. No ARCH-01 update required for this request.

- DOMAIN (CMP): No impact. CMP-01 catalogs tool scripts (`*.py`); prompt files are not cataloged in CMP-01.

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): No impact detected.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (KNW): Minor recommended impact.
  - KNW-01 (Domain glossary): New term "Context File" (suggested TERM-0014) should be added to document `.aib_memory/context.md` as a concept. This is a recommended update, not blocking.

- DOMAIN (RQT): No impact detected.

- DOMAIN (OBS): No impact. Per-action execution logging applies automatically when the prompt is run via the menu.

- DOMAIN (OPR): No impact detected.

- DOMAIN (SEC): No impact. The prompt reads workspace files but does not handle secrets or credentials.

## Constraints

- The prompt MUST NOT trigger any edits to existing workspace files.
- The prompt MUST produce `context.md` as full content replacement (not append).
- `.aib_brain/` content is explicitly excluded from exploration.
- The prompt MUST be model/vendor-agnostic.
- Context-window management must be built into the prompt with explicit domain prioritization.

## Required Documentation Updates

- KNW-01 - Domain glossary
  Required update? YES (recommended, not blocking)
  Reason: New concept "Context File" introduced by this request should have a glossary entry (TERM-0014).

- All other product-docs
  Required update? NO

## Decision Points

**DP-1: Should `.aib_brain/` be included in `context.md` exploration?**
- Option A: Exclude as stated — `context.md` captures workspace-specific state only; a preamble note references `.aib_brain/` for framework details.
- Option B: Include `.aib_brain/` — extend exploration to cover prompts, conventions, tools.
- Option C: Partial inclusion — include only `.aib_brain/prompts/` and `.aib_brain/conventions/`.
- DECISION: **Option A.** The request explicitly lists `.aib_brain/` in "Out of scope." The success criteria are about understanding the product, not the framework. A preamble note provides the missing pointer. This resolves QID-BF-001 from iteration 01.

**DP-2: What level of detail should `context.md` sections contain?**
- Option A: Concise key-fact summaries per domain (1–3 paragraphs; key IDs, component names, critical facts).
- Option B: Full verbatim content from source product-doc files.
- Option C: Adaptive — concise for populated, "not yet documented" for stubs.
- DECISION: **Option A/C (combined).** Concise summaries for populated domains; explicit "not yet documented" for stub-only domains. The primary use case is brainstorming (fast comprehension), not verbatim reproduction. This resolves QID-AT-001 from iteration 01.

**DP-3: What read strategy should the prompt use?**
- DECISION: **Hybrid (Option C from iteration 01).** Product-docs first as primary curated sources, then targeted workspace scan for `README.md`, `scripts/`, `tests/`, and root configs. Already resolved in iteration 01.

**DP-4: What structure should `context.md` use?**
- DECISION: **Domain-aligned sections** matching the 11 domains from `Product_Documentation.md`. Provides traceability and consistency with AIB conventions. Already resolved in iteration 01.

# Research Plan and Findings

**Methodology:** Internal-first review of request.md, iteration 01 artifacts (01-analysis.md, 01-questionnaire.md), product-doc files via references.md, existing prompt patterns (aib-reverse-engineer.md), workspace file inventory, and AIB framework documentation (Concepts.md, Product_Documentation.md).

**Evidence summary:**

- Iteration 01 analysis established three decision points (DP-1 through DP-3) and recommended solutions. All are adopted in this iteration.
- Iteration 01 questionnaire raised two user questions (QID-BF-001, QID-AT-001). Both are now resolved by AI based on explicit request language — no user input needed.
- `aib-reverse-engineer.md` provides a proven structural template for the new prompt: mandatory preflight → file inventory → exclusion rules → document population → validation. The context prompt follows the same pattern but writes a single output file.
- Of 27 product-doc files, 16 have real content and 11 are stubs. The prompt must handle both states gracefully.
- 6 existing prompt files exist in `.aib_brain/prompts/`; `aib-context.md` does not exist yet — confirmed net-new.
- `Product_Documentation.md` defines 11 domains with acronyms and scope summaries — these become the section headings for `context.md`.
- No `context.md` exists in `.aib_memory/` — confirmed net-new creation on first execution.
- The AIB Command Menu auto-discovers `aib-*.md` files from `.aib_brain/prompts/`; no configuration changes needed.

**Gaps and unknowns:**

- None remaining. All open questions from iteration 01 are resolved.

**Proposed validation actions:**

- After creating the prompt, execute it once to verify `context.md` is produced with non-empty sections for populated domains and "not yet documented" notices for stub domains.
- Verify `context.md` structure matches the 11 domain sections.
- Verify no existing workspace files are modified.

**Files Read:**

- `.aib_brain/prompts/aib-create-analysis.md` — prompt instructions for this analysis
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/request.md` — primary request input
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/iterations.md` — confirmed iteration 02 is active
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/01-analysis.md` — iteration 01 analysis with decisions, assumptions, solution options
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/01-questionnaire.md` — iteration 01 questionnaire with two unresolved user questions
- `.aib_memory/requests/R-20260404-0823-unified-requirements-and-tech-specs/implementation.md` — empty log (no implementation yet)
- `.aib_memory/references.md` — 27 product-doc entries + 1 domain entry
- `.aib_brain/Concepts.md` — framework concepts, lifecycle rules, action contract
- `.aib_brain/Product_Documentation.md` — 11 domains, 27 document standards
- `.aib_brain/conventions/analysis-convention.md` — analysis document structure and authoring rules
- `.aib_brain/conventions/request-convention.md` — request file format for rewrite proposal
- `.aib_brain/prompts/aib-reverse-engineer.md` — reference pattern for prompt structure
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — populated high-level architecture
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — stub (topology)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — stub (capacity model)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — populated ADRs
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — populated runtime interaction sequences
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — populated resource catalog
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — populated script catalog
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — populated algorithm specs
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — populated source data catalog
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — populated data models
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — stub (data lineage)
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — stub (data storage strategy)
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — populated data consumption patterns
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — stub (metrics catalog)
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — stub (data quality rules)
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — populated archiving/deletion policy
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — populated dashboard inventory (empty by design)
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — populated domain glossary
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — populated business process catalog
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — populated use cases & personas
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — populated logging specification
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — stub (product charter)
- `.aib_memory/docs/03 Requirements/RQT-02.md` — populated requirements document
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — stub (access management)
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — stub (data protection)
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — stub (secrets management)
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — stub (network security)
- `README.md` — project overview, installation instructions, CI workflow description

# Rewrite Proposal of the Request

## Goal

Create the file `.aib_brain/prompts/aib-context.md` — an AI-executable prompt that, when run by any AI agent (GitHub Copilot, Claude, or any other LLM-based agent), produces or fully replaces the file `.aib_memory/context.md`. The resulting document must be a unified, structured synthesis of all workspace-specific product knowledge. It must be organized by the 11 product documentation domains defined in `.aib_brain/Product_Documentation.md` (ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC). It must use concise key-fact summaries for populated domains and explicit "not yet documented" notices for stub-only domains. The document must enable a developer or AI agent to answer, from `context.md` alone: what is this product, what components exist, how are they structured, what are the key workflows, and what are the constraints and requirements.

## Background

The AIB workspace stores product knowledge across 27 individual documentation files under `.aib_memory/docs/` spanning 11 product-documentation domains. For brainstorming sessions and AI-assisted work, navigating 27 separate files is inefficient and exceeds practical context-window limits. A single unified context document — `.aib_memory/context.md` — provides a faster comprehension path and a reliable seed for AI-driven tasks. The `aib-context.md` prompt is the mechanism for generating and refreshing this document. It is analogous to `.aib_brain/prompts/aib-reverse-engineer.md` (which populates individual product-doc files) but writes to a single aggregated output instead.

### Actors and systems involved

- **AI Agent** (any supported model): Executes the prompt; reads workspace files; writes `context.md`.
- **Developer** (DEVELOPER persona, KNW-03): Primary consumer of `context.md` for brainstorming and product comprehension.
- **Maintainer** (MAINTAINER persona, KNW-03): Owns and maintains the `aib-context.md` prompt file.
- **AIB Command Menu** (CMP-ART-0006): Auto-discovers and surfaces the prompt as a Prompt Action (TERM-0013).
- **`.aib_memory/references.md`**: Source registry for determining which files are product-docs (`type=product-doc`).
- **`.aib_brain/Product_Documentation.md`**: Defines the 11 domain section headings and their scope summaries.

## Scope

- Creation of exactly one new file: `.aib_brain/prompts/aib-context.md`
- The prompt, when executed by an AI agent, must perform these steps in order:
  1. **Preflight:** Read `.aib_memory/references.md` and build the set of all product-doc file paths (`type=product-doc`)
  2. **Primary read phase:** Read all product-doc files from `.aib_memory/docs/` as curated primary sources
  3. **Supplementary read phase:** Build a deterministic file inventory of the workspace root (excluding `.aib_brain/`, `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`, `.aib_memory/`); read `README.md`, `scripts/`, `tests/`, and root configuration files (e.g., `.gitignore`)
  4. **Synthesis:** Merge findings into `.aib_memory/context.md` using domain-aligned sections (one `##` section per domain); include a preamble stating the document is auto-generated by `aib-context.md`, that `.aib_brain/` framework assets are excluded by design, and the generation timestamp
  5. **Stub handling:** For domains where all associated product-doc files are stubs (seeded placeholder text only), output a "Not yet documented" notice with the domain scope summary from `Product_Documentation.md`
  6. **Context-window management:** If aggregate read volume exceeds 80% of available context, prioritize domains in this order: RQT, ARCH, KNW, CMP, DATA, OBS, SEC, OPR, DEV, DSR, FNL; summarize deprioritized files and note which files were summarized
- The prompt MUST be model/vendor/tool-agnostic — no tool-specific extensions or APIs
- The prompt MUST produce full content replacement of `context.md` on each execution (not append); re-execution with unchanged sources produces semantically equivalent output

## Out of scope

- Modification of any existing file in the workspace (product-docs, scripts, tests, conventions, templates, other prompts)
- Exploration or reading of the `.aib_brain/` folder and its contents (prompts, tools, conventions, templates) — the prompt itself lives in `.aib_brain/prompts/` but does not read other `.aib_brain/` files at execution time
- Exploration of virtual environments: `.venv/`, `venv/`
- Exploration of unmodified package directories: `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- Exploration of `.git/` version-control internals
- Addition of a new entry for `context.md` in `.aib_memory/references.md` (it is a generated artifact, not a governed product-doc)
- Modification of any existing prompt, convention, template, or tool file
- KNW-01 glossary update for "Context File" term (recommended but deferred to a separate request)

## Constraints

- The prompt MUST NOT edit any existing workspace file; the only permitted write target is `.aib_memory/context.md`
- Re-executing the prompt MUST produce semantically equivalent output given unchanged source files (full replacement, not append)
- The prompt MUST follow the `aib-*.md` naming convention (already satisfied by `aib-context.md`)
- The prompt MUST include an explicit context-window management section with domain prioritization order: RQT > ARCH > KNW > CMP > DATA > OBS > SEC > OPR > DEV > DSR > FNL
- The prompt MUST NOT require or embed tool-specific extensions; it must work in any AI agent environment
- The prompt must use concise key-fact summaries (not full verbatim reproduction) for domain sections; each section should be 1–5 paragraphs covering: component/entity names, IDs, key relationships, critical decisions, and constraints

## Success criteria

- SC-1: File `.aib_brain/prompts/aib-context.md` exists and is valid Markdown
- SC-2: When executed by any supported AI agent, the prompt produces `.aib_memory/context.md` without modifying any other file
- SC-3: `.aib_memory/context.md` contains a clearly labeled `##` section for each of the 11 product documentation domains (ARCH, CMP, DATA, DEV, DSR, FNL, KNW, RQT, OBS, OPR, SEC)
- SC-4: Sections for domains with populated product-doc files contain concise, non-empty key-fact summaries (component names, IDs, relationships, critical decisions)
- SC-5: Sections for domains with only stub product-doc files contain a "Not yet documented" notice with the domain scope summary
- SC-6: Workspace code artifacts (`scripts/`, `tests/`) are summarized under applicable domain sections (CMP for scripts, DEV for tests)
- SC-7: No content is derived from excluded directories (`.aib_brain/`, `.venv/`, `.git/`, etc.)
- SC-8: `context.md` includes a preamble noting it is auto-generated, that `.aib_brain/` assets are excluded, and a generation timestamp
- SC-9: Re-executing the prompt produces output with equivalent structure and semantically consistent content (idempotent behavior)
- SC-10: A developer or AI agent reading only `.aib_memory/context.md` can answer: what is this product, what components exist, how are they structured, what are the key workflows, and what are the constraints and requirements

# Solution Options

## Option A: Minimal prompt — product-doc read only

**Overview:** The prompt reads all 27 product-doc files from `.aib_memory/docs/` (via references.md) and synthesizes them into domain-aligned `context.md` sections. No workspace code scan.

**Benefits:**
- Simplest prompt; fewest instructions
- Leverages curated, convention-governed docs exclusively
- Fast execution; fewer files to read

**Trade-offs:**
- Misses code-level detail from `scripts/`, `tests/`, `README.md`
- 11 of 27 product-doc files are stubs; those domain sections will be near-empty
- Does not capture implementation reality beyond what is documented

**Constraints:** Depends on product docs being sufficiently populated.

**Risks:** Sparse output for stub-heavy domains. Does not meet SC-6 (workspace code summary).

**Expected effort:** Low — straightforward prompt creation.

**Acceptance test:** Execute prompt; verify `context.md` has sections; check SC-6 fails.

---

## Option B: Hybrid approach — product-docs + targeted workspace scan (recommended)

**Overview:** Two-phase read strategy:
1. Primary: Read all product-doc files from `.aib_memory/docs/` via references.md
2. Supplementary: Deterministic workspace file inventory (excluding defined directories); read `README.md`, `scripts/`, `tests/`, root configs

Synthesize both into a domain-aligned `context.md`. Populated product-doc content forms the primary section body. Workspace code artifacts supplement the relevant domain sections (scripts → CMP, tests → DEV). Stub-only domains receive "Not yet documented" notices enriched with any workspace-derived evidence.

**Benefits:**
- Maximum coverage: curated docs + direct code evidence
- Stub domains supplemented by workspace scan findings
- Consistent with `aib-reverse-engineer.md` proven pattern
- Meets all success criteria (SC-1 through SC-10)

**Trade-offs:**
- Slightly longer prompt with two phases
- Higher total read volume; requires context-window management
- More complex execution path

**Constraints:** Must include explicit context-window management with domain prioritization order.

**Risks:** If both docs and workspace are sparse, output remains sparse — but this accurately reflects workspace state.

**Expected effort:** Medium — two-phase prompt with context-window handling.

**Acceptance test:** Execute prompt; verify all 11 domain sections present; verify SC-6 (code artifacts summarized); verify no excluded-directory content.

---

**Recommendation:** **Option B (Hybrid).** It satisfies all success criteria, provides the best coverage, and follows the established `aib-reverse-engineer.md` pattern. The additional complexity is minimal and justified by the comprehensiveness requirement.

# Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Recommended: new term "Context File" (TERM-0014) for `.aib_memory/context.md`; deferred to separate request |

# Operational & Documentation Implications

- **AIB Command Menu:** The new `aib-context.md` prompt will be auto-discovered and surfaced as a Prompt Action (TERM-0013). No code changes to `menu.py` required. When copilot CLI is absent, the menu displays it as informational only.

- **Per-action execution logging (OBS-01):** When executed via the AIB Command Menu, a per-action log is generated automatically. No changes to the logging specification required.

- **Product documentation:** KNW-01 glossary should add "Context File" (TERM-0014). This is a recommended update deferred to a future request.

- **Runbooks:** No runbook changes required; the prompt is standalone.

- **`.aib_memory/context.md` lifecycle:** Generated artifact managed exclusively by re-executing `aib-context.md`. Should be committed to version control. Not tracked in references.md.

# Risks

- Risk R1: Sparse context.md for stub-heavy domains
  - Probability: Medium (11 of 27 product-docs are stubs)
  - Impact: Low (stub domains get explicit "Not yet documented" notices; populated domains produce useful content; hybrid strategy supplements with workspace evidence where available)
  - Mitigation: Prompt uses hybrid strategy with workspace-derived fallback for stub domains
  - Owner (role): AI_AGENT

- Risk R2: Context window overflow during prompt execution
  - Probability: Medium (27 product-docs + workspace files may exceed 80% of context)
  - Impact: High (AI agent may skip critical docs or produce incomplete sections)
  - Mitigation: Prompt includes explicit context-window management with domain prioritization order (RQT > ARCH > KNW > CMP > DATA > OBS > SEC > OPR > DEV > DSR > FNL); deprioritized files summarized; skipped files noted
  - Owner (role): AI_AGENT
  - Contingency: If context overflow persists, split execution into two passes (read + write) with intermediate state

- Risk R3: Non-idempotent output across executions
  - Probability: Low (deterministic structure + same sources = equivalent output)
  - Impact: Low (minor content wording drift acceptable; structural consistency enforced by prompt)
  - Mitigation: Prompt enforces domain-aligned section structure and full content replacement
  - Owner (role): AI_AGENT

- Risk R4: Stale context.md after product-doc updates
  - Probability: Medium (product-docs may be updated without re-executing the context prompt)
  - Impact: Medium (context.md drifts from current product state)
  - Mitigation: Users/maintainers re-execute `aib-context.md` after significant documentation changes; preamble includes generation timestamp for staleness awareness
  - Owner (role): DEVELOPER / MAINTAINER

# Disambiguation Questionnaire

- Q1: What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded?
  - **Chosen Answer / Value:** MSI is the single file `.aib_brain/prompts/aib-context.md` that, when executed, produces `.aib_memory/context.md`. Excluded: all file modifications except `context.md`, references.md entry, KNW-01 glossary update.
  - **Rationale:** Request scope is narrowly defined as one new prompt file. Glossary update is deferred.
  - **Evidence / Reference:** request.md Scope and Out of Scope sections
  - **Impact if changed:** Adding references.md entry or glossary update expands scope; requires updating implementation target list.

- Q2: Which user-visible changes (if any) MUST be demonstrable at iteration end?
  - **Chosen Answer / Value:** `.aib_brain/prompts/aib-context.md` is present and discoverable in the AIB Command Menu. Executing it produces a valid `context.md` with 11 domain sections.
  - **Rationale:** The menu auto-discovers prompt files. The execution output is the primary deliverable.
  - **Evidence / Reference:** ARCH-01 component inventory (AIB Command Menu); TERM-0013 (Prompt Action)
  - **Impact if changed:** If menu discovery fails, a menu config change would be needed (unlikely per current architecture).

- Q3: What are the non-functional targets applicable to this iteration?
  - **Chosen Answer / Value:** Model/vendor-agnostic; idempotent full-replacement writes; context-window-aware with documented prioritization.
  - **Rationale:** Request Constraints section specifies these explicitly.
  - **Evidence / Reference:** request.md Constraints section
  - **Impact if changed:** Adding latency/throughput targets would require benchmarking prompt execution time.

- Q4, Q5, Q6: Data sources, serialization, error handling
  - **Chosen Answer / Value:** N/A — The prompt reads Markdown files from the local filesystem; no data ingestion pipeline, serialization format changes, or retry policies apply.
  - **Rationale:** This is a prompt-authoring task, not a data pipeline.
  - **Evidence / Reference:** request.md Scope (Markdown files only)
  - **Impact if changed:** If external data sources were introduced, the prompt would need ingestion rules.

- Q7, Q8, Q9: Algorithm/specification variant, accuracy thresholds, hardware constraints
  - **Chosen Answer / Value:** N/A — No algorithm selection, accuracy measurement, or hardware constraints apply. The prompt is a set of natural-language instructions for an AI agent.
  - **Rationale:** The output is Markdown text synthesis, not a computational algorithm.
  - **Evidence / Reference:** request.md Scope
  - **Impact if changed:** If quality scoring were introduced for context.md, measurement criteria would be needed.

- Q10, Q11: API endpoints, compatibility
  - **Chosen Answer / Value:** N/A — No APIs, message topics, or versioned interfaces. The prompt produces a local Markdown file.
  - **Rationale:** File-based output only.
  - **Evidence / Reference:** request.md Scope
  - **Impact if changed:** If context.md were served via API, versioning and SLA would be needed.

- Q12: What identities/roles may access the new/changed assets?
  - **Chosen Answer / Value:** Any user with repository read access can read the prompt and context.md. Execution requires AI agent access. No additional RBAC needed.
  - **Rationale:** AIB is a file-first framework; access is governed by repository permissions.
  - **Evidence / Reference:** SEC-01 (stub; no RBAC model defined yet); repository-level access control
  - **Impact if changed:** If sensitive data were included in context.md, classification rules would apply.

- Q13, Q14: Data classifications, secrets
  - **Chosen Answer / Value:** N/A — No sensitive data, PII, or secrets are involved. The prompt reads and synthesizes existing documentation.
  - **Rationale:** Product-doc files contain technical documentation only.
  - **Evidence / Reference:** SEC-01 through SEC-04 (stubs; no sensitive data policies defined)
  - **Impact if changed:** If product-docs contained classified data, masking rules would govern context.md output.

- Q15, Q16, Q17: Observability, alerts, runbooks
  - **Chosen Answer / Value:** Existing per-action execution logging (OBS-01) applies automatically when the prompt is run via the menu. No new metrics, alerts, or runbook updates required.
  - **Rationale:** OBS-01 already covers menu-executed prompt actions.
  - **Evidence / Reference:** OBS-01 logging specification; ARCH-01 (AIB Command Menu component)
  - **Impact if changed:** If execution health monitoring were required, custom metrics would need definition.

- Q18: Which product docs must be created or updated?
  - **Chosen Answer / Value:** KNW-01 (recommended, deferred). No blocking documentation updates required.
  - **Rationale:** The new "Context File" concept warrants a glossary term but is not blocking for implementation.
  - **Evidence / Reference:** KNW-01 current term list (13 terms; no "Context File")
  - **Impact if changed:** If the glossary update were mandatory, scope expands to include KNW-01 editing.

- Q19: What acceptance evidence will be recorded and where?
  - **Chosen Answer / Value:** Successful execution producing `context.md` with 11 domain sections; recorded in `implementation.md` of this request.
  - **Rationale:** Standard AIB implementation log practice.
  - **Evidence / Reference:** Concepts.md action contract; implementation.md convention
  - **Impact if changed:** If formal test cases were required, a test plan would need creation.

- Q20: What is the rollback strategy if acceptance fails?
  - **Chosen Answer / Value:** Delete `aib-context.md` from `.aib_brain/prompts/` and delete `context.md` from `.aib_memory/` (if generated). No other files are modified, so no further rollback needed.
  - **Rationale:** The change is additive (new file only); rollback is deletion.
  - **Evidence / Reference:** request.md (only permitted write is `context.md`)
  - **Impact if changed:** If existing files were modified, rollback would require git revert.

# Open Questions & Next Actions

1. **[AI — resolved]** `.aib_brain/` exclusion is intentional per explicit request Out of Scope clause. `context.md` will include a preamble noting that framework assets live in `.aib_brain/` and are excluded by design.
   - Owner: AI
   - Due: Resolved in this analysis (DP-1)
   - Resolution path: Adopted Option A. Resolves QID-BF-001 from iteration 01.

2. **[AI — resolved]** Level of detail: concise key-fact summaries per domain with "Not yet documented" notices for stub-only domains.
   - Owner: AI
   - Due: Resolved in this analysis (DP-2)
   - Resolution path: Adopted Option A/C combined. Resolves QID-AT-001 from iteration 01.

3. **[AI — resolved]** Read strategy: hybrid (product-docs first, then targeted workspace scan). Adopted from iteration 01 recommendation.
   - Owner: AI
   - Due: Resolved in this analysis (DP-3)
   - Resolution path: Adopted Option C from iteration 01. No user input needed.

4. **[AI — resolved]** `context.md` structure: domain-aligned sections matching `Product_Documentation.md` 11 domains.
   - Owner: AI
   - Due: Resolved in this analysis (DP-4)
   - Resolution path: Adopted from iteration 01 recommendation. No user input needed.
