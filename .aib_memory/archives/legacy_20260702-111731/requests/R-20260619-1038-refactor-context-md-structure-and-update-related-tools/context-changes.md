# Context Changes for R-20260619-1038

Changes to be made to `.aib_memory/context.md` during implementation of request R-20260619-1038 (Refactor context.md structure and update related tools).

Note: This request performs a full migration of context.md to a new 6-section format. All 22-area content is remapped; the changes below highlight the specific statements that are deleted or inserted as distinct tracking changes. The full migration of all other statements is described in plan Task 7.

## Statements to Delete (old format — remove during migration)

[D] Area: `Data structures` — `- N: Atomic statements in context.md follow format: - TYPE: text with 22 valid area names and 9 type letters.`

[D] Area: `Technical Design` — `- D: context.md uses atomic statement format with type-letter-indexed entries; tools use text-based line matching for CRUD ops.`

[D] Area: `Technical Design` — `- I: verify-context.py validates context.md format compliance against context-convention.md with 10 automated checks.`

[D] Area: `Documentation` — `- I: context convention defines atomic statement format with 22 valid area names and 9 statement types.`

## Statements to Insert (new format — add via edit-context.py in plan Task 11)

[I] Section: `Solution` — `- context.md uses a 6-section structure (Product, Concepts, Requirements, Solution, File Structure, References) replacing the prior 22-area classified-statement model.`

[I] Section: `Requirements` — `- MUST: Requirements section statements use [MUST|MUST NOT|OPTIONAL] modality prefix.`

[I] Section: `Solution` — `- verify-context.py validates context.md format compliance against context-convention.md with the 6-section check set.`

[I] Section: `Solution` — `- edit-context.py supports CRUD operations on Product, Concepts, Requirements, and Solution sections with format enforcement per section type.`

## Statements to Update

[U] Area: `Best Practices` — `- U: context.md is fully replaced on each aib-refresh-context.md execution with no append semantics.`
    → Maps to new Section: `Requirements` — `- MUST: context.md is fully replaced on each aib-refresh-context.md execution with no append semantics.`
