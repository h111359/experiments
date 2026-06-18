# Context Changes for R-20260618-1607

Changes to `.aib_memory/context.md` required by this request.
Format: [I] insert, [D] delete, [U] update.

## Technical Design

[D] `- D: context.md uses atomic statement format with type-letter-indexed entries; tools use text-based line matching for CRUD ops.`

[I] `- context.md uses type-less atomic statement format; area sections are sole organizational mechanism; tools use text-based line matching for CRUD ops.`

## Data structures

[D] `- N: Atomic statements in context.md follow format: - TYPE: text with 22 valid area names and 9 type letters.`

[I] `- Atomic statements in context.md follow format: - text (plain bullet) with 22 valid area names; no type prefix.`

## Documentation

[D] `- I: context convention defines atomic statement format with 22 valid area names and 9 statement types.`

[I] `- context convention defines type-less atomic statement format with 22 valid area names.`
