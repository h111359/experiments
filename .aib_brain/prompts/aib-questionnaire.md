# Prompt: create-questionnaire

Goal:
Generate `.aib_memory/requests/<request-folder>/<ITERATION_ID>-questionnaire.md` to clarify unresolved decision points.

Inputs:
- Active request + iteration
- Existing analysis/plan (if present)
- `.aib_brain/Concepts.md`
- `.aib_memory/references.md`
- All product documentation files that are listed in `.aib_memory/references.md`
- Conventions:
  - `.aib_brain/conventions/product-documentation-convention.md`
  - `.aib_brain/conventions/questionnaire-convention.md`

Mandatory preflight (MUST):
1. Resolve active request and active iteration.
2. Read `.aib_memory/references.md`.
3. Build a required-read set containing every `path` from references where:
   - `type = product-doc`
4. Read every file in the required-read set before drafting questions.
5. Read the conventions listed above.

Validation guardrails (MUST):
- Do not write the questionnaire file until all required-read files were successfully read.
- Treat existing analysis/plan as secondary evidence; do not substitute them for reading product docs.
- Only ask questions for information that is still missing after reviewing request artifacts plus all required docs.
- Confirm at the very end of the conversation with the text "--- I am done with the questionnaire ---" that all your activities are finished

Requirements:
- Ask only high-impact questions.
- Maximize answerability with A/B/C/D + Other checkboxes.
- Include rationale under every question.
- Mark one recommended option.
- Keep it concise.

Output:
- Full content replacement of target questionnaire file.
- Include only unresolved high-impact questions after full-doc review.

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

