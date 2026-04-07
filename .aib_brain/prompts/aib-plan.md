# Prompt: create-plan

Goal:
Generate `.aib_memory/requests/<request-folder>/<ITERATION_ID>-plan.md` for execution of active iteration.

Inputs:
- Active request
- Active iteration
- Questionnaire answers (if available)
- Existing analysis
- `.aib_brain/Concepts.md`
- `.aib_memory/references.md`
- All product documentation files that are listed in `.aib_memory/references.md`
- Conventions:
  - `.aib_brain/conventions/product-documentation-convention.md`
  - `.aib_brain/conventions/plan-convention.md`

Note:
- The plan MUST be authored directly from `.aib_brain/conventions/plan-convention.md`.

Mandatory preflight (MUST):
1. Resolve active request and active iteration.
2. Read `.aib_memory/references.md`.
3. Build a required-read set containing every `path` from references where:
   - `type = product-doc`
4. Read every file in the required-read set before drafting the plan.
5. Read the conventions listed above.

Requirements:
- Respect latest iteration as source of truth.
- Provide deterministic, ordered tasks.
- Every task must include inputs, outputs, and done criteria.
- Keep task descriptions actionable and testable.
- Keep “Decision Gates” concise (prefer compact answers with references to analysis/questionnaire sections for rationale/evidence).
- Confirm at the very end of the conversation with the text "--- I am done with the plan ---" that all your activities are finished

Output:
- Full content replacement of target plan file.

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

