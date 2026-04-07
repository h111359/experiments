# Introduction

This glossary defines canonical terms used by AI Builder (AIB) and its workspace layout. It reduces ambiguity in request/iteration workflows and documentation updates.

# How to Use This Glossary

- Search for an existing term before adding a new one.
- Prefer the Approved meaning when interpreting requirements.
- Add new terms as Proposed and request maintainer review.
- Keep definitions precise and product-specific.

# Term Entries

| term_id | term | definition | examples | owner | synonyms | tags | status | version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-0001 | AI Builder | Minimal, model-agnostic framework for specification-driven development in a repository workspace. | initialize workspace, create request | AIB Maintainers | AIB | framework, workflow | Proposed | 1 |
| TERM-0002 | Workspace | Repository root containing AIB brain and memory folders plus any product code. | repo root, project folder | Product Team | project root | workspace, repo | Proposed | 1 |
| TERM-0003 | Brain Folder | Folder with reusable AIB assets: prompts, conventions, templates, tools. | .aib_brain | AIB Maintainers | brain | aib, assets | Proposed | 1 |
| TERM-0004 | Memory Folder | Folder with workspace-specific artifacts: requests, references, product docs. | .aib_memory | Product Team | memory | aib, artifacts | Proposed | 1 |
| TERM-0005 | Request | Tracked unit of work with stable request id and lifecycle state. | R-20260322-0845 | Product Team | work item | request, lifecycle | Proposed | 1 |
| TERM-0006 | Iteration | Numbered step within a request; one active at a time. | iteration 01 | Product Team | step | iteration, lifecycle | Proposed | 1 |
| TERM-0007 | Product Doc | Convention-governed documentation file listed in references register. | ARCH-01, DATA-06 | Product Team | documentation file | product-doc, docs | Proposed | 1 |
| TERM-0008 | References Register | Table listing referenced files and whether automation may edit them. | references.md | Product Team | references | governance, docs | Proposed | 1 |
| TERM-0009 | Convention File | File defining required structure and validation rules for a product doc. | arch-01-convention | AIB Maintainers | spec | convention, schema | Proposed | 1 |
| TERM-0010 | SemVer Marker File | Single empty file in brain folder whose filename encodes vMAJOR.MINOR.PATCH. | v1.0.8 | AIB Maintainers | version marker | semver, versioning | Proposed | 1 |
| TERM-0011 | Tool Script | Python script implementing deterministic AIB actions. | initialize.py | AIB Maintainers | cli tool | python, tooling | Proposed | 1 |
| TERM-0012 | Implementation Log | Request-scoped append-only record of changes, tests, outcomes. | implementation.md | Product Team | impl log | audit, traceability | Proposed | 1 |
| TERM-0013 | Prompt Action | A `.aib_brain/prompts/aib-*.md` file that defines the instructions an AI agent executes to produce a specific AIB artifact. Invoked directly in the AI chat or coding interface; not gated on any CLI availability. | aib-analysis.md, aib-implement.md | AIB Maintainers | — | menu, tooling | Proposed | 2 |

# Conventions & Style Rules

- Keep definitions to one concise paragraph.
- No links or code formatting inside the table.
- Use stable TERM ids and Title Case terms.

# Validation Rules

- Exactly one Term Entries table with required headers.
- term_id values are unique and match TERM-0001 pattern.

# Operations (Edit, Review, Publish)

- Add new terms as Proposed.
- Review and promote to Approved when stable.
- Increment version on definition change.

# Change Log

| date (YYYY-MM-DD) | actor | term_id | field | old_value → new_value | rationale |
| --- | --- | --- | --- | --- | --- |
| 2026-03-22 | AI Agent | TERM-0001..TERM-0012 | created | — → initial set | Seeded glossary for AIB workspace terms. |
| 2026-04-03 | AI Agent | TERM-0013 | created | — → Prompt Action | Added Prompt Action term for R-20260403-0939 / Iteration 04. |
| 2026-04-05 | AI Agent | TERM-0013 | definition, examples, version | old → updated | Removed copilot CLI dependency; updated examples to new prompt file names — R-20260404-2326 / Iteration 01. |
