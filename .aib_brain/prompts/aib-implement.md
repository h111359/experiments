# Prompt: implement

Goal:
Execute active request scope, update the documentation and update request-scoped `implementation.md`.

Input resolution:
- Resolve active request from `.aib_memory/requests_register.md` unless explicit ID is provided.
- Resolve active iteration from request `iterations.md`.
- Use newest iteration artifacts as truth when conflicts exist.
- Read `.aib_brain/Concepts.md` for normative lifecycle and safety rules.

Execution requirements:
- Apply code/documentation changes required by request scope.
- Create/update tests where applicable.
- Run validation/tests and capture results.
- Resolve any test failures
- Continue until done criteria are met or blockers are explicitly recorded.
- Execute `.aib_brain\prompts\aib-documentation.md`
- Confirm at the very end of the conversation with the text "--- I am done with the implementation ---" that all your activities are finished

Documentation reading requirements:
- Read `.aib_memory/references.md`.
- Build a required-read set containing every `path` from references where:
   - `type = product-doc`
- Read every file in the required-read set before implementation.
- Read `.aib_brain/conventions/product-documentation-convention.md` (authoritative mapping) before editing any `product-doc`.
- Convention enforcement preflight (fail-closed for product-doc edits):
   - For every `product-doc` in the required-read set:
      - Derive requirement ID from the document filename (e.g., `ARCH-01.md` -> `ARCH-01`).
      - Resolve the per-document convention file path deterministically as:
         `.aib_brain/conventions/<requirement-id-lower>-convention.md`.
      - Verify the mapping row exists in `.aib_brain/conventions/product-documentation-convention.md` for the doc title and resolved convention path.
      - Read the resolved convention file.
   - If any mapping row is missing or any convention file cannot be read, DO NOT edit any product-docs; record the blocker and required remediation in `implementation.md`.
- You MAY edit only files listed in `.aib_memory/references.md` with `edit_allowed=Y`.
- Do not edit files listed with `edit_allowed=N` unless explicitly instructed otherwise.

Logging requirements:
- Append a new Entry to `implementation.md` following the exact Entry Block Format defined in `.aib_brain/conventions/implementation-convention.md`. Do not reproduce the field schema here.

Safety:
- Do not modify `.aib_brain/` assets during implementation work.
- Do not add files under `.aib_brain/`
- If nothing else specified, add tests in the folder of the request
- Do not create Python virtual environment unless explicitely specified in the request or in plan or in the documentation
- Do not install any additional libraries or third party software  unless explicitely specified in the request or in plan or in the documentation

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

