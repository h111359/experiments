

## Goal

- Update the documentation governance so that for every `product-doc` entry listed in `.aib_memory/references.md`, there is an explicitly documented association to a per-document convention file under `.aib_brain/conventions/`.

- Changing the schema of `.aib_memory/references.md` is approved

- Define a deterministic mapping method (or an explicit authoritative list) for resolving `product-doc` requirement IDs (e.g., `ARCH-01`) to convention files (e.g., `.aib_brain/conventions/arch-01-convention.md`).
  
- Update `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md` so that when a product documentation file is eligible to be edited (`edit_allowed=Y`) and is being edited, the corresponding convention file is read first and its rules are enforced.
  
- Acceptance criteria:
  - For any edit of a `product-doc` file, the prompt explicitly requires reading the corresponding convention file and following its required structure.
  - The mapping is explicit and reviewable without inference.
  - Failure behavior on missing convention is defined (error vs warning) and is deterministic.
- 
- Out of scope:
  - Filling out the seeded product docs with project-specific content.

