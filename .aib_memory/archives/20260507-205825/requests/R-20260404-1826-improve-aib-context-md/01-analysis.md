# Analysis - Iteration 01

## Executive Summary

- **Request ID:** R-20260404-1826

- **Request Title:** improve-aib-context-md

- **Iteration ID:** 01

- **High-level purpose:** Redesign the `aib-context.md` prompt and its output format so that `context.md` becomes a universal, best-in-class, rebuildable product knowledge document — not limited to AIB's current documentation structure — and separate the structural convention from the behavioral prompt.

- The current `aib-context.md` prompt is tightly coupled to the 11-domain product documentation taxonomy in `.aib_memory/docs/`. The generated `context.md` mirrors that taxonomy rather than capturing the deeper product knowledge needed to rebuild a system from scratch.

- The request asks for two new/modified artifacts: (1) a new convention file `.aib_brain/conventions/context-convention.md` defining the format and structure of `context.md`, and (2) a revised `.aib_brain/prompts/aib-context.md` defining only the behavior (how to generate `context.md`), referencing the convention for structure.

- The request supplies ~40 internet sources across software architecture documentation, ADRs, docs-as-code, SDD, contract-first, requirements/assumptions, and formal specifications. These were researched and key learnings extracted.

- No earlier iterations exist; this is the initial analysis for this request.

## Scope Interpretation

- **In scope:**

  - Create `.aib_brain/conventions/context-convention.md` defining the required structure, sections, content guidance, and quality rules for `context.md`.

  - Revise `.aib_brain/prompts/aib-context.md` to contain only behavioral instructions (phases, reads, synthesis logic, safety rules) and reference the new convention for structural requirements.

  - The convention must be product-agnostic — usable for any workspace/repository, not only AIB.

  - The convention must produce a `context.md` that is deep, comprehensive, and sufficient to rebuild the product from scratch.

  - The convention must not lose information for brevity — completeness over conciseness.

  - The convention must be logically structured for both human reading and AI consumption.

  - Incorporate best practices from the supplied internet sources (architecture documentation, ADRs, docs-as-code, SDD, assumptions/constraints, requirements, contract-first design).

  - (implicit rule - AIB framework) Update any affected product documentation if the change touches documented components.

- **Out of scope:**

  - Changing the content of the existing `context.md` itself (that happens when the new prompt is executed).

  - Modifying any other conventions or prompts beyond `aib-context.md`.

  - Changing the structure of `.aib_memory/docs/` or `references.md`.

  - Adding new tool scripts or templates.

  - Changing any lifecycle/request/iteration mechanics.

## Domain Knowledge Essentials

- **Product Context Document (`context.md`):** A single Markdown file under `.aib_memory/` that synthesizes all workspace-specific product knowledge. Currently organized by 11 documentation domains. Intended audience: AI agents and human developers needing full project understanding.

- **AIB Brain/Memory separation:** `.aib_brain/` holds reusable, replaceable framework assets (prompts, conventions, templates, tools). `.aib_memory/` holds project-specific artifacts. Conventions define structure; prompts define behavior.

- **Product Documentation Domains:** The current 11 domains (RQT, ARCH, KNW, CMP, DATA, OBS, SEC, OPR, DEV, DSR, FNL) are AIB-specific taxonomy from `Product_Documentation.md`. The request explicitly asks to decouple `context.md` structure from this taxonomy.

- **Specification-Driven Development (SDD):** An approach treating specifications as the primary contextual artifact — "version control for thinking." Specifications are living documents that evolve alongside code, capturing the "why" behind technical choices. Relevant because `context.md` serves as the specification/context artifact for AI agents.

- **Architecture Decision Records (ADRs):** Lightweight documents capturing architectural decisions, context, alternatives, and consequences. Key insight: decisions and their rationale are among the most valuable content that code alone cannot convey.

- **Docs-as-Code:** Treating documentation as structured, version-controlled, automatable artifacts using plain text formats. Core to AIB's Markdown-based approach.

- **arc42 Template:** A proven 12-section template for software architecture documentation covering goals, constraints, context, building blocks, runtime, deployment, cross-cutting concepts, decisions, quality, risks, and glossary.

- **C4 Model:** Four-level abstraction for visualizing software architecture (Context, Container, Component, Code). Complementary to arc42.

- **Contract-First Development:** Upfront agreement on interfaces and specifications before implementation. Specifications serve as single sources of truth.

- **Rebuildability:** The ability to reconstruct a system from its documentation alone — the stated quality goal for `context.md`.

## Technical Knowledge & Terms

- **Convention file:** A `.aib_brain/conventions/*.md` file defining normative structural rules for a specific artifact type. Conventions define WHAT the artifact contains and HOW it is formatted, not the process of creating it.

- **Prompt file:** A `.aib_brain/prompts/*.md` file defining behavioral instructions for an AI agent action. Prompts define WHEN to read, WHAT to synthesize, and WHERE to write, referencing conventions for format.

- **Deterministic output:** Given the same input state, the prompt must produce semantically equivalent output on re-execution.

- **Context window:** The maximum amount of text an AI model can process in a single interaction. Context management is critical for large codebases.

- **Full content replacement:** The prompt must overwrite the entire target file atomically on each execution — no appending.

- **Fail-closed:** If a required input is missing or unresolvable, the operation must halt with an error rather than producing partial output.

- **INVEST criteria:** Independent, Negotiable, Valuable, Estimable, Small, Testable — a framework for validating story/specification quality.

- **MoSCoW prioritization:** Must have, Should have, Could have, Won't have — a prioritization framework applicable to specification content.

## Assumptions

- Assumption A1: The new `context-convention.md` will be the single authoritative source for the structure and content requirements of `context.md`, and `aib-context.md` will reference it rather than embed structural definitions.
  - Rationale: This is explicitly stated in the request goal — separate structure from behavior.
  - Risk if false: Duplication of structural rules between convention and prompt leading to drift and inconsistency.
  - Falsification method: Review both files after implementation to confirm no structural rules appear in the prompt.

- Assumption A2: The convention must be product-agnostic, meaning it must not reference AIB-specific domain taxonomy (RQT, ARCH, KNW, etc.) as the primary organizing structure.
  - Rationale: The request explicitly states "the prompt should be able to create a context.md for any product in some other repo."
  - Risk if false: The convention becomes AIB-specific and fails when used in other repositories.
  - Falsification method: Apply the convention mentally or actually to a non-AIB repository and verify no AIB-specific terms are mandatory.

- Assumption A3: The existing 11-domain taxonomy may still appear in a generated `context.md` when those domains are relevant, but the convention's section structure should not be hardcoded to those 11 domains.
  - Rationale: The domains are useful for AIB but may not apply to other products. The convention should define logical sections that any product can populate.
  - Risk if false: Losing traceability to the existing product documentation structure for AIB.
  - Falsification method: Verify that the convention provides a mechanism (e.g., domain-mapping or product-doc integration section) without mandating the specific 11 domains.

- Assumption A4: "Sufficient to rebuild the product from scratch" means the `context.md` should capture: product vision, business knowledge, requirements, architectural decisions, technical design, conventions, constraints, assumptions, operational procedures, and security posture — everything code alone cannot convey.
  - Rationale: The request states "The product should be able to be rebuilt from scratch only based on the information in the context.md file." This implies deep, comprehensive content.
  - Risk if false: The convention produces a shallow summary that omits critical rebuild knowledge.
  - Falsification method: After generating a `context.md`, evaluate whether a competent developer with no prior knowledge could reconstruct the system's architecture and business logic.

- Assumption A5: The prompt file will still handle phases (preflight, read, synthesis, write) and safety rules, while the convention handles headings, content guidance, quality criteria, and formatting.
  - Rationale: Clean separation of concerns as requested.
  - Risk if false: Ambiguity about which artifact governs which aspect.
  - Falsification method: Review whether any behavioral instruction exists in the convention or any structural rule exists in the prompt.

## Impact Assessment

### Affected Components / Areas

- `.aib_brain/prompts/aib-context.md` — Major modification (remove structural definitions, retain behavioral instructions, add convention reference).
- `.aib_brain/conventions/context-convention.md` — New file (define complete structural convention for `context.md`).
- `.aib_memory/context.md` — Indirect impact (will be regenerated with new structure on next prompt execution, but not modified by this request directly).

### Change Type and Dependencies

- `.aib_brain/prompts/aib-context.md`: **modify** — Remove embedded structure (domain sections, scope summaries, domain-to-product-doc mapping), replace with convention reference. Retain Phase 1-5 behavioral logic, safety rules, done criteria.
  - Dependencies: Depends on the new convention existing before the prompt is usable.
  - Sequencing: Convention must be created first; prompt modification second.

- `.aib_brain/conventions/context-convention.md`: **add** — New convention file defining universal context document structure.
  - Dependencies: None (new file).
  - Sequencing: Must be created before prompt modification.

### Domain Impacts

- DOMAIN (ARCH): Low impact. The context.md format change affects how architecture knowledge is captured but not the architecture itself.
  - Relevant requirement IDs: ARCH-01 (component listing may appear differently in new context.md)

- DOMAIN (RQT): No impact detected.

- DOMAIN (KNW): Low impact. Domain glossary terms related to context.md may need updating if the document's role description changes.
  - Relevant requirement IDs: KNW-01

- DOMAIN (CMP): No impact detected.

- DOMAIN (DATA): No impact detected.

- DOMAIN (OBS): No impact detected.

- DOMAIN (SEC): No impact detected.

- DOMAIN (OPR): No impact detected.

- DOMAIN (DEV): No impact detected.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

### Constraints

- The convention must remain product-agnostic while still being useful for AIB.
- The convention must be Markdown-only, no HTML, no external hyperlinks, no images.
- The convention must follow AIB's normative language conventions (MUST, SHOULD, MAY per RFC 2119).
- The resulting `context.md` must still be deterministic (same inputs → same output intent).
- The convention file must live in `.aib_brain/conventions/` per AIB framework rules.
- The prompt file must remain in `.aib_brain/prompts/` per AIB framework rules.

### Required Documentation Updates

- ARCH-01 - High-level Architecture
  Required update? NO
  Reason: No architectural change, only documentation format change.

- KNW-01 - Domain Glossary
  Required update? MAYBE
  Reason: If "Product Context Document" definition changes scope, the glossary entry should be updated when `reverse-engineer` is next run.

### Decision Points

- **DP1: Section structure for universal context.md**
  - Option A: Use a fixed set of universal sections inspired by arc42/C4/SDD (e.g., Product Identity, Business Context, Requirements & Constraints, Architecture & Decisions, Technical Design, Data Architecture, Security & Compliance, Operations, Development Practices, Glossary, Workspace Inventory).
  - Option B: Use a flexible schema where sections are dynamically generated based on what content exists in the workspace (risk: non-deterministic structure).
  - Option C: Hybrid — mandatory skeleton sections plus optional domain-specific expansions.
  - Recommendation: **Option C (Hybrid)** — provides reliable structure for human/AI consumption while accommodating diverse products. A set of mandatory universal sections ensures consistency; optional subsections allow product-specific depth.

- **DP2: How to handle the existing 11-domain mapping**
  - Option A: Remove entirely from the prompt and convention. The prompt discovers domains from workspace content.
  - Option B: Keep as a fallback/example in the convention, but not as the primary organizing structure.
  - Option C: Move to a product-specific configuration file that the prompt reads.
  - Recommendation: **Option B** — The 11 domains are useful for AIB and serve as an example. The convention should define universal sections, and the prompt should map product-doc domains into those sections when product docs exist.

## Research Plan and Findings

### Methodology

1. Internal docs scan: Read `request.md`, `iterations.md`, current `aib-context.md` prompt, existing `context.md`, `Concepts.md`, `analysis-convention.md`, `request-convention.md`, `references.md`, and key product docs (ARCH-01, RQT-01, RQT-02).
2. External research: Fetched and analyzed 7 internet sources covering architecture documentation (arc42, C4), ADRs, docs-as-code, SDD (GitHub Spec Kit, intent-driven.dev), and assumptions/constraints in SRS documents.
3. Pattern synthesis: Cross-referenced findings against AIB's constraints (model-agnostic, Markdown-only, deterministic, fail-closed).

### Evidence Summary

| Evidence | Implication |
| --- | --- |
| arc42 template uses 12 fixed sections covering goals through glossary | Universal context.md should have a fixed section skeleton covering product identity through glossary |
| ADRs capture decision + context + alternatives + consequences | context.md must include a dedicated "Key Decisions" section summarizing ADR-style content |
| SDD treats specs as "version control for thinking" | context.md is the specification artifact; must capture intent, not just implementation |
| GitHub Spec Kit uses constitution.md for non-negotiable principles | context.md should capture conventions, constraints, and non-negotiable principles |
| Docs-as-code emphasizes version-controlled, testable, automatable docs | context.md must remain plain Markdown, deterministic, and machine-parseable |
| Assumptions/constraints best practices: distinguish clearly, be specific, include rationale | context.md needs explicit assumptions and constraints sections with rationale |
| SDD anti-pattern: "specification bloat" from AI-generated content | Convention must set quality gates against verbosity; prefer information density over volume |
| arc42 pitfall: "Don't document everything upfront" | context.md should document what exists and is known, not speculate about future state |
| Contract-first: specs are single sources of truth | context.md should be the authoritative product knowledge reference |
| C4 model: layered abstraction (Context → Container → Component → Code) | context.md architecture section should follow layered abstraction, not dump raw component lists |

### Gaps and Unknowns

- No gap identified that blocks analysis completion. All required information is available from workspace content and researched sources.

### Proposed Validation Actions

- After implementation, execute the revised prompt on the AIB workspace and verify: (a) all convention sections are populated, (b) content is sufficient for rebuild assessment, (c) no AIB-specific taxonomy is hardcoded in the convention.

### Files Read

- `.aib_memory/requests/R-20260404-1826-improve-aib-context-md/request.md` — Full request with ~40 internet source URLs across 5 categories.
- `.aib_memory/requests/R-20260404-1826-improve-aib-context-md/iterations.md` — Single active iteration 01.
- `.aib_memory/references.md` — 28 product-doc references plus 1 domain reference.
- `.aib_brain/Concepts.md` — AIB framework concepts, lifecycle, preferences, folder structure.
- `.aib_brain/conventions/analysis-convention.md` — Analysis document convention (full).
- `.aib_brain/conventions/request-convention.md` — Request document convention (full).
- `.aib_brain/prompts/aib-context.md` — Current context generation prompt (full, 200 lines).
- `.aib_brain/prompts/aib-create-analysis.md` — Analysis creation prompt.
- `.aib_memory/context.md` — Current generated context document (full).
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — Stub.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Populated (architecture summary, components, data flows).
- `.aib_memory/docs/03 Requirements/RQT-02.md` — Populated (functional/non-functional requirements).
- Web: workingsoftware.dev (arc42 guide) — Confirmed arc42 12-section structure, C4 compatibility, docs-as-code approach.
- Web: calmops.com (ADR guide) — Confirmed ADR structure, lifecycle, categorization, maintenance practices.
- Web: docsascode.org — Confirmed docs-as-code principles: versioning, automation, testing, suitable format.
- Web: writethedocs.org — Confirmed docs-as-code community practices and tooling.
- Web: developer.microsoft.com (GitHub Spec Kit) — Confirmed SDD approach: specs as shared context, constitution.md, cross-agent compatibility.
- Web: intent-driven.dev (SDD best practices) — Confirmed: human reviewability, minimal specs, meaningful decomposition, context management, anti-patterns.
- Web: qat.com (SRS assumptions/constraints) — Confirmed: types of assumptions/constraints, best practices for documentation, validation importance.

## Rewrite Proposal of the Request

## Goal

Separate the structural definition of `.aib_memory/context.md` from the behavioral prompt `.aib_brain/prompts/aib-context.md` by creating a new convention file `.aib_brain/conventions/context-convention.md`. The convention defines a universal, product-agnostic section structure and content standard for `context.md` that enables any product to be rebuilt from scratch using only that document. The prompt retains only behavioral logic (phases, reads, synthesis, safety, write) and references the convention for format.

The redesigned `context.md` structure must incorporate best practices from software architecture documentation (arc42, C4 model), architectural decision records, specification-driven development, docs-as-code, contract-first design, and requirements engineering — as synthesized from the internet sources listed in the original request.

## Background

The current `aib-context.md` prompt embeds both behavioral instructions (5-phase execution: preflight, primary read, supplementary read, synthesis, write) and structural definitions (11 fixed domain sections, domain-to-product-doc mapping table, scope summary table). This coupling means:

1. The structure of `context.md` is locked to AIB's 11-domain taxonomy, making it unusable for non-AIB repositories.
2. Structural changes require modifying the prompt, mixing concerns.
3. The generated `context.md` mirrors the product-doc folder hierarchy rather than capturing the deeper knowledge needed for product rebuild (decisions, rationale, constraints, business context, conventions, security posture).

Research across 40+ internet sources on architecture documentation, ADRs, SDD, docs-as-code, and requirements engineering confirms that a rebuildable context document must capture: product identity/vision, business domain knowledge, requirements and acceptance criteria, architectural decisions with rationale, technical design details, data architecture, security and compliance posture, operational procedures, development practices, constraints, assumptions, and glossary.

## Scope

1. **Create** `.aib_brain/conventions/context-convention.md`:
   - Define mandatory and optional sections for `context.md` using a universal, product-agnostic structure.
   - Sections must cover: product identity, business context, requirements summary, architecture and key decisions, technical design, data architecture, security and compliance, operations, development practices, constraints and assumptions, glossary, and workspace inventory.
   - Define content guidance for each section (what to include, what to omit, quality expectations).
   - Define formatting rules (Markdown, heading levels, traceability references, no HTML, no external links).
   - Define quality gates (completeness, specificity, rebuildability, determinism).
   - Include normative language per RFC 2119.

2. **Modify** `.aib_brain/prompts/aib-context.md`:
   - Remove all structural definitions: domain section list, domain-to-product-doc mapping table, scope summary table, Case A/Case B formatting rules.
   - Retain Phase 1-5 behavioral logic (preflight, primary read, supplementary read, synthesis, write).
   - Add a reference to `.aib_brain/conventions/context-convention.md` as the authoritative structural source.
   - Adjust synthesis phase to populate sections defined by the convention rather than hardcoded domain sections.
   - Retain safety rules, context-window management, and done criteria.
   - Retain determinism and idempotency requirements.

## Out of scope

- Modifying the content of `.aib_memory/context.md` directly (it will be regenerated when the revised prompt is next executed).
- Changing any other convention files.
- Changing any other prompt files.
- Adding new tool scripts or templates.
- Modifying `.aib_memory/references.md` or `.aib_memory/docs/` structure.
- Changing request/iteration lifecycle mechanics.
- Adding product-doc convention files for new domains.

## Constraints

- The convention MUST be product-agnostic — no AIB-specific domain acronyms as mandatory section headings.
- The convention MUST produce Markdown-only output.
- The convention MUST follow AIB's normative language interpretations (RFC 2119 / RFC 8174).
- The prompt MUST remain model-agnostic and vendor-agnostic.
- The prompt MUST produce deterministic output (same memory state → same output intent).
- The prompt MUST NOT modify any file other than `.aib_memory/context.md`.
- The prompt MUST NOT read `.aib_brain/` contents except as explicitly needed (convention reference).
- Both files MUST be placed in their canonical AIB locations (`.aib_brain/conventions/` and `.aib_brain/prompts/`).

## Success criteria

1. `.aib_brain/conventions/context-convention.md` exists and defines a complete, product-agnostic section structure for `context.md` with at least 10 mandatory sections covering the knowledge areas identified in the research.
2. `.aib_brain/prompts/aib-context.md` contains no structural definitions (no hardcoded section names, no domain mapping tables, no scope summary tables) — only behavioral instructions.
3. `.aib_brain/prompts/aib-context.md` explicitly references `.aib_brain/conventions/context-convention.md`.
4. Executing the revised prompt on the AIB workspace produces a `context.md` with all mandatory sections populated.
5. The generated `context.md` captures sufficient knowledge that a competent developer could understand the product's purpose, architecture, decisions, and constraints without reading source code.
6. The convention can be applied to a non-AIB repository without modification to its mandatory sections.
7. No other files in the workspace are modified by this change.

## Solution Options

### Option A: Minimal Separation — Extract structure verbatim

- **Overview:** Move the current structural definitions (11 domain sections, mapping table, scope summaries) from `aib-context.md` into `context-convention.md` with minimal changes. The convention retains the AIB-specific domain taxonomy as-is.
- **Benefits:** Lowest effort; no risk of regression; proven structure.
- **Trade-offs:** Does not achieve the request's goal of product-agnostic universal structure. The convention remains AIB-specific.
- **Constraints:** Fails the product-agnostic requirement.
- **Risks:** Does not address the core request.
- **Expected effort:** Small.
- **Acceptance-test ideas:** Verify structural rules moved; verify prompt references convention.

### Option B: Universal Redesign — Product-agnostic convention with deep sections

- **Overview:** Design a new convention from scratch using insights from arc42, C4, SDD, ADR, and docs-as-code research. Define ~12 mandatory universal sections (Product Identity, Business Context, Requirements, Architecture & Decisions, Technical Design, Data Architecture, Security & Compliance, Operations, Development Practices, Constraints & Assumptions, Glossary, Workspace Inventory). The prompt dynamically maps workspace content into these sections. AIB's 11-domain product docs become source material mapped into universal sections, not the section structure itself.
- **Benefits:** Fully product-agnostic; comprehensive; rebuildable-quality; incorporates industry best practices. Achieves all stated goals.
- **Trade-offs:** Higher effort; requires careful design to avoid over-specification. Need to ensure the prompt can still map AIB's product docs into universal sections.
- **Constraints:** Must remain Markdown-only; must be deterministic.
- **Risks:** Risk R1: New structure may miss AIB-specific nuances currently captured. Mitigation: Include an "Additional Domain Sections" mechanism for product-specific extensions.
- **Expected effort:** Medium.
- **Acceptance-test ideas:** Generate context.md for AIB; verify all knowledge is captured; apply convention mentally to a different repo type (e.g., a web API project).

### Option C: Hybrid — Universal core with optional domain mapping

- **Overview:** Similar to Option B, but the convention explicitly includes an optional mechanism for mapping product-specific documentation domains (like AIB's 11 domains) into the universal sections. The prompt reads a domain mapping if available, otherwise uses workspace discovery.
- **Benefits:** Best of both worlds — universality with backward compatibility.
- **Trade-offs:** Slightly more complex convention; the domain mapping mechanism adds a concept.
- **Constraints:** Domain mapping must be optional, not required.
- **Risks:** Complexity of the mapping mechanism may confuse AI agents.
- **Expected effort:** Medium-High.
- **Acceptance-test ideas:** Same as Option B, plus verify the domain mapping works for AIB and is optional for non-AIB repos.

**Recommendation:** **Option B (Universal Redesign)** — It most directly fulfills the request's goals. The concern about missing AIB-specific content is mitigated by the universal sections being comprehensive enough (Architecture & Decisions, Technical Design, Data Architecture all cover what the current 11 domains cover). The prompt's synthesis phase can reference `references.md` product docs as source material without the convention mandating them as structural sections.

## Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| No affected documents identified at this stage. | | | |

No product documentation files are directly modified by this request. The new convention and modified prompt are `.aib_brain/` assets, not product docs. Downstream `context.md` regeneration may affect product documentation summaries, but that is an indirect effect of executing the prompt, not of this change itself.

## Operational & Documentation Implications

- **Runbooks:** No change.
- **SLAs/SLOs:** No change.
- **Monitoring/observability/logging/alerts/dashboards:** No change.
- **Data quality rules:** No change.
- **Product documentation artifacts:** The generated `context.md` will have a new section structure after the prompt is next executed. Downstream consumers of `context.md` (humans, AI agents reading context as part of other prompts) will see a different format. This is expected and desired.

## Risks

- Risk R1: The new universal section structure may not capture all AIB-specific detail currently present in the domain-organized context.md.
  - Probability: Low
  - Impact: Medium
  - Mitigation: Design universal sections broad enough to subsume all current domain content. Verify by comparing generated output before/after.
  - Owner (role): DEVELOPER

- Risk R2: The separation of convention from prompt may introduce ambiguity about which file governs which aspect, leading to inconsistent implementations.
  - Probability: Low
  - Impact: Medium
  - Mitigation: Each file includes a scope statement. Convention explicitly states "structure only, not process." Prompt explicitly states "behavior only, references convention for structure."
  - Owner (role): MAINTAINER

- Risk R3: AI agents with smaller context windows may struggle with a deeply comprehensive context.md.
  - Probability: Medium
  - Impact: Low
  - Mitigation: The convention and prompt retain context-window management rules (chunking, prioritization). The convention can define a "summary preamble" at the top of context.md for quick orientation.
  - Owner (role): DEVELOPER

- Risk R4: The convention may become overly prescriptive, making it difficult to adapt to diverse product types.
  - Probability: Low
  - Impact: Medium
  - Mitigation: Use "MUST" for core sections and "MAY" for optional extensions. Allow sections to contain "Not yet documented" notices.
  - Owner (role): MAINTAINER

## Disambiguation Questionnaire

- **Q1: Should the convention mandate specific section headings, or should it define content areas with flexible naming?**
  - Chosen Answer: Mandate specific headings.
  - Rationale: Deterministic, machine-parseable structure requires fixed headings. Flexible naming introduces non-determinism.
  - Evidence: analysis-convention.md and other AIB conventions use fixed mandatory headings. SDD best practices emphasize structured, predictable artifacts.
  - Impact if changed: AI agents would need fuzzy matching to find sections; reduces reliability.

- **Q2: Should the convention retain the 11-domain taxonomy as an optional mapping?**
  - Chosen Answer: No. The prompt handles domain-to-section mapping internally. The convention defines only universal sections.
  - Rationale: Including AIB-specific taxonomy in the convention contradicts the product-agnostic goal.
  - Evidence: Request explicitly states the convention should work for "any product in some other repo."
  - Impact if changed: Convention loses product-agnostic property.

- **Q3: Should `context.md` include a verbatim copy of workspace file inventory?**
  - Chosen Answer: Yes, as the final section.
  - Rationale: Provides quick structural reference of the workspace. Currently included and useful for orientation.
  - Evidence: Current context.md includes it; it aids AI agents in understanding repository layout.
  - Impact if changed: AI agents would lose workspace structure awareness.

- **Q4: What is the appropriate depth for the Architecture & Decisions section?**
  - Chosen Answer: Summarize ADR content (decision, rationale, consequences) rather than full ADR documents. Reference ADR IDs for traceability.
  - Rationale: context.md is a synthesis document, not a duplication target. ADRs have their own files.
  - Evidence: arc42 approach: "put something on a shelf as you work on it." ADR guide: capture WHAT, WHY, ALTERNATIVES, CONSEQUENCES.
  - Impact if changed: Over-detailed decisions section would bloat context.md and duplicate ADR files.

- **Q5: Should the prompt still read `.aib_brain/` conventions during context generation?**
  - Chosen Answer: The prompt MUST read the context convention to know the target structure. It SHOULD NOT read other convention files (analysis, plan, etc.) — those are framework internals not relevant to product context.
  - Rationale: The prompt needs to know the target format but should not explore brain internals for product knowledge.
  - Evidence: Current prompt explicitly excludes `.aib_brain/` exploration. The exception is reading the referenced convention for format guidance.
  - Impact if changed: Reading all conventions would increase context window usage without adding product knowledge.

## Open Questions & Next Actions

1. No unresolved questions remain. All structural decisions have been made based on the research and request analysis. Implementation can proceed.
