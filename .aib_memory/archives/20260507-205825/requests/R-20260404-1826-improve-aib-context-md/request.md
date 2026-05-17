# Request

## Goal

Separate the structural definition of `.aib_memory/context.md` from the behavioral prompt `.aib_brain/prompts/aib-context.md` by creating a new convention file `.aib_brain/conventions/context-convention.md`. The convention defines a universal, product-agnostic section structure and content standard for `context.md` that enables any product to be rebuilt from scratch using only that document. The prompt retains only behavioral logic (phases, reads, synthesis, safety, write) and references the convention for format.

The redesigned `context.md` structure must incorporate best practices from software architecture documentation (arc42, C4 model), architectural decision records, specification-driven development, docs-as-code, contract-first design, and requirements engineering - as synthesized from the internet sources listed in the Background section.

Actors:
- DEVELOPER: Executes the prompt via AIB to generate `context.md` for their workspace.
- MAINTAINER: Owns `.aib_brain/` assets including the new convention and revised prompt.
- AI_AGENT: Reads the prompt and convention to produce `context.md`; also consumes `context.md` as shared context for subsequent operations.

Triggers:
- The DEVELOPER or AI_AGENT executes the `aib-context.md` prompt action.

Inputs:
- `.aib_brain/conventions/context-convention.md` (new, defines target structure)
- `.aib_memory/references.md` (read set for product docs)
- All product-doc files where `type = product-doc` in `references.md`
- Workspace source files (README, scripts, tests, configs)

Outputs:
- `.aib_memory/context.md` - fully replaced with content conforming to the new convention.

## Background

The current `aib-context.md` prompt embeds both behavioral instructions (5-phase execution: preflight, primary read, supplementary read, synthesis, write) and structural definitions (11 fixed domain sections, domain-to-product-doc mapping table, scope summary table). This coupling causes three problems:

1. The structure of `context.md` is locked to AIB's 11-domain taxonomy (RQT, ARCH, KNW, CMP, DATA, OBS, SEC, OPR, DEV, DSR, FNL), making it unusable for non-AIB repositories.
2. Structural changes require modifying the prompt, mixing concerns.
3. The generated `context.md` mirrors the product-doc folder hierarchy rather than capturing the deeper knowledge needed for product rebuild (decisions, rationale, constraints, business context, conventions, security posture).

Research across 40+ internet sources on architecture documentation (arc42, C4), ADRs, SDD (GitHub Spec Kit, intent-driven.dev), docs-as-code, and requirements engineering confirms that a rebuildable context document must capture: product identity/vision, business domain knowledge, requirements and acceptance criteria, architectural decisions with rationale, technical design details, data architecture, security and compliance posture, operational procedures, development practices, constraints, assumptions, and glossary.

Key internet sources consulted (grouped by category):

Architecture documentation: workingsoftware.dev (arc42 guide), softwaresystemdesign.com, freecodecamp.org, dellenny.com.
ADRs: calmops.com, AWS architecture blog, Microsoft Learn, Google Cloud.
Docs-as-code: docsascode.org, writethedocs.org, gitscrum docs, hyperlint.
Requirements/constraints: qat.com, parallelhq.com, atlassian.com, moldstud.com.
SDD/contract-first: intent-driven.dev, developer.microsoft.com (Spec Kit), scalablepath.com, zencoder docs, augmentcode.com, openpracticelibrary.com, thearchitectguild.com, kpavlov.me, moesif.com, devguide.dev.
API-first: swagger.io, requestly.com, easecloud, postman.com.
Formal specs/RFCs: TLA+ (Wikipedia, learntla.com, Lamport), osoco, pragmaticengineer.com, leaddev.com, IETF, GitHub gist RFC template.

## Scope

1. **Create** `.aib_brain/conventions/context-convention.md`:
   - Define mandatory and optional sections for `context.md` using a universal, product-agnostic structure.
   - Sections MUST cover: product identity, business context, requirements summary, architecture and key decisions, technical design, data architecture, security and compliance, operations, development practices, constraints and assumptions, glossary, and workspace inventory.
   - Define content guidance for each section (what to include, what to omit, quality expectations).
   - Define formatting rules (Markdown only, heading levels, traceability references, no HTML, no external links).
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
- Changing any other convention files beyond the new `context-convention.md`.
- Changing any other prompt files beyond `aib-context.md`.
- Adding new tool scripts or templates.
- Modifying `.aib_memory/references.md` or `.aib_memory/docs/` structure.
- Changing request/iteration lifecycle mechanics.
- Adding product-doc convention files for new domains.

## Constraints

- The convention MUST be product-agnostic - no AIB-specific domain acronyms (RQT, ARCH, etc.) as mandatory section headings.
- The convention MUST produce Markdown-only output (no HTML, no images, no external hyperlinks).
- The convention MUST follow AIB's normative language interpretations (RFC 2119 / RFC 8174).
- The prompt MUST remain model-agnostic and vendor-agnostic (per NFR-001).
- The prompt MUST produce deterministic output (same memory state -> same output intent, per NFR-002).
- The prompt MUST NOT modify any file other than `.aib_memory/context.md`.
- The prompt MUST NOT read `.aib_brain/` contents except the referenced convention file.
- Both files MUST be placed in their canonical AIB locations (`.aib_brain/conventions/` and `.aib_brain/prompts/`).
- The convention MUST NOT describe process/behavior (how to generate context.md); that belongs in the prompt.
- The prompt MUST NOT describe structure/format (what sections context.md contains); that belongs in the convention.

## Success criteria

1. `.aib_brain/conventions/context-convention.md` exists and defines a complete, product-agnostic section structure for `context.md` with at least 10 mandatory sections covering the knowledge areas identified in the research.
2. `.aib_brain/prompts/aib-context.md` contains zero structural definitions (no hardcoded section names, no domain mapping tables, no scope summary tables) - only behavioral instructions and a reference to the convention.
3. `.aib_brain/prompts/aib-context.md` explicitly references `.aib_brain/conventions/context-convention.md` for format.
4. Executing the revised prompt on the AIB workspace produces a `context.md` with all mandatory convention sections populated.
5. The generated `context.md` captures sufficient knowledge that a competent developer could understand the product's purpose, architecture, decisions, and constraints without reading source code.
6. The convention can be applied to a non-AIB repository without modification to its mandatory sections.
7. No other files in the workspace are modified by this change.
