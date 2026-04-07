# Prompt: update-documentation

Goal:
Update documentation references and documentation files enabled for editing in `.aib_memory/references.md`.

Rules:
- Update only rows with `edit_allowed=Y` unless explicitly instructed otherwise.
- Preserve file naming and path conventions.
- Keep changes aligned to active request scope.
- Summarize changes within active request `implementation.md` entry.
- Confirm at the very end of the conversation with the text "--- I am done with the documentation update ---" that all your activities are finished

Mandatory preflight (MUST):
1. Read `.aib_brain/Concepts.md` for normative lifecycle and safety rules.
2. Read `.aib_memory/references.md`.
3. In a single pass through references, build a required-read set containing every `path` where `type = product-doc`.
4. In the same pass, build a target-edit set containing every `path` where `type = product-doc` and `edit_allowed = Y`.
5. Read every file in the required-read set before updating documentation.
6. Read `.aib_brain/conventions/product-documentation-convention.md` (authoritative mapping).
7. Convention enforcement preflight (fail-closed):
   - For every `product-doc` in the required-read set:
     - Derive requirement ID from the document filename (e.g., `ARCH-01.md` -> `ARCH-01`).
     - Resolve the per-document convention file path deterministically as:
       `.aib_brain/conventions/<requirement-id-lower>-convention.md`.
     - Verify the mapping row exists in `.aib_brain/conventions/product-documentation-convention.md` for the doc title and resolved convention path.
     - Read the resolved convention file.
   - If any mapping row is missing or any convention file cannot be read, STOP and report an error (do not edit any product-docs).
8. Only modify files in the target-edit set unless explicitly instructed otherwise.

When editing any product-doc in the target-edit set:
- Follow the required structure and rules from its per-document convention file.

Post-update step:
- After completing all documentation edits, execute `.aib_brain\prompts\aib-context.md` to regenerate `.aib_memory/context.md`.

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

