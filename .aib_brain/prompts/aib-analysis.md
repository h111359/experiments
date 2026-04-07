# Prompt: create-analysis

Goal:
Generate `.aib_memory/requests/<request-folder>/<ITERATION_ID>-analysis.md` for the resolved request and iteration and create a questionnaire if questions need to be asked by executing `.aib_brain\prompts\aib-questionnaire.md`.

Inputs:
- Active request (`request.md`)
- Active iteration (`iterations.md`)
- Optional existing questionnaire/plan/history files
- `.aib_brain/Concepts.md`
- `.aib_memory/references.md`
- All product documentation files that are listed in `.aib_memory/references.md`
- Conventions:
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`

Mandatory preflight (MUST):
1. Resolve active request and active iteration.
2. Read `.aib_memory/references.md`.
3. Build a required-read set containing every `path` from references where:
   - `type = product-doc`
4. Read every file in the required-read set before drafting analysis.

Requirements:
- Follow required headings exactly.
- Keep statements concrete and traceable to request scope.
- Do not ask user for information you can collect yourself from the workspace - review the files in the workspace and search for answers of your open questions first
- Do not ask the user for information you can find in Internet or via available tools or MCP - make research yourself before to address the open questions to the user
- Explicitly list assumptions and risks.
- If information is insufficient, list unknowns as assumptions and risks.
- Explain explicitely all not-common terms in domain and technical essentials section
- Confirm at the very end of the conversation with the text "--- I am done with the analysis ---" that all your activities are finished

Output:
- Full content replacement of the target analysis file.
- Based on the analysis findings, provide a more specific, detailed, and unambiguous rewrite of the request.md file of the current active request so to be ready for implementation. Follow the instructions in `.aib_brain\conventions\request-convention.md` for proper format of the proposal.Must include:
    *   Named actors, systems, inputs, triggers, and data
    *   Measurable acceptance criteria with observable thresholds
    *   Explicit out-of-scope statements
    *   Functional and non-functional expectations
    *   Traceability to affected artifacts/IDs where available

- Auto-triggers `create-questionnaire` if and only if section 13 (Open Questions & Next Actions) of the generated analysis contains at least one item whose owner is `User` or for which no concrete resolution path is provided. Execute `.aib_brain\prompts\aib-questionnaire.md` only when this condition is true.

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

