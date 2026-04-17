# Prompt: create-analysis

Goal:
Generate `.aib_memory/requests/<request-folder>/analysis.md` for the resolved request, and update `request.md` with implementation-relevant sections.

Inputs:
- Active request (`request.md`)
- Optional existing `request.md` optional sections (Assumptions, Plan, Testing, Documentation, Questions & Decisions)
- `.aib_brain/Concepts.md`
- `.aib_memory/references.md`
- All product documentation files that are listed in `.aib_memory/references.md`
- Conventions:
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`

Mandatory preflight (MUST):
1. Read `.aib_memory/requests_register.md` and check for exactly one row with `state = Active`.
   - If exactly one Active row is found: continue to step 2 (standard analysis flow).
   - If zero Active rows are found: switch to the **Auto-Request Creation Branch** (see below).
   - If more than one Active row is found: output the message **"ERROR: Register inconsistency — multiple Active requests found. Execution halted. Fix requests_register.md before running analysis."** Do NOT proceed to any subsequent step. Do NOT write any output files.
2. Resolve active request (use the single Active row identified in step 1).
3. Read the active `request.md`.
4. **Toggle detection (MUST check before any further steps):**
   - Read `## Options` section of `input.md` (`.aib_memory/input.md`).
   - If the **"No changes — provide answer only"** option is checked (`[x]`):
     - This branch produces **exactly two file writes** and MUST NOT produce any other file writes:
       1. Write the timestamped answer to `<request-folder>/answer-<YYYY-MM-DD_HH-MI-SS>.md` using the content of the `## Input` section of `input.md`.
       2. Reset `input.md` to the seed template (`## Active request\nNo active request\n\n## Options\n- [ ] No changes — provide answer only\n- [ ] Skip analysis document generation\n\n## Input\n\n`), then replace `No active request` in the `## Active request` line with the current active request ID and title (resolved from the preflight step), in the format `<request_id> — <title>`.
     - MUST NOT modify `request.md`, `analysis.md`, or any other file.
     - **Stop here. Do NOT proceed to any further steps.**
   - If the **"Skip analysis document generation"** option is checked (`[x]`): proceed normally but skip writing `analysis.md` (Part 1 output). Update `request.md` optional sections only.
5. Read `.aib_memory/references.md`.
6. Build a required-read set containing every `path` from references where `type = product-doc`.
7. Read every file in the required-read set before drafting analysis.
8. Read both conventions listed above.
9. Detect `## Amend Request` section in `request.md`. If present and non-empty:
   a. Apply its free-text instructions to the relevant mandatory sections (Goal, Background, Scope, Out of scope, Constraints, Success criteria) of `request.md`.
   b. Clear the content of the `## Amend Request` from `request.md` after applying.

---

### Auto-Request Creation Branch
**Triggered when:** zero Active rows found in preflight step 1.

**Procedure:**
1. Read `.aib_memory/input.md`.
   - If `## Input` section is empty or contains only whitespace: output **"ERROR: No active request and input.md is empty. Add content to ## Input before running analysis."** Do NOT proceed.
   - Check `## Options` for the **"No changes — provide answer only"** toggle. If checked, output **"ERROR: No active request and 'No changes' toggle is set. Create a request first."** Do NOT proceed.
2. Derive a request title from the `## Input` content (first meaningful sentence or noun phrase, ≤ 60 characters).
3. Invoke `.aib_brain/tools/create-request.py` via python script:
   ```
   python .aib_brain/tools/create-request.py --workspace . --title "<derived-title>"
   ```
4. Read `.aib_memory/requests_register.md` to resolve the newly created request folder.
5. Generate `request.md` in `<request-folder>/` following `.aib_brain/conventions/request-convention.md` and based on the content of `input.md`'s `## Input` section. All 14 mandatory sections MUST be present in this exact order: `## Goal`, `## Background`, `## Scope`, `## Out of scope`, `## Constraints`, `## Success criteria`, `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Questions & Decisions`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`, `## Multi-Perspective Stakeholder Review`. Sections 1–6 (`## Goal` through `## Success criteria`) MUST be non-empty with content derived from `input.md`'s `## Input` section. Sections 7–14 may be empty (they are populated during step 8). Before writing `request.md`, confirm all 14 headings are present and sections 1–6 are non-empty.
6. Archive the current `input.md` content to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`.
   - Use python to create the `inputs/` subfolder and write the archive file.
7. Proceed with the standard analysis flow (steps 4 onward, reading the newly created `request.md`). MUST NOT reset `input.md` during this triggered standard flow — the reset is performed in step 8 below.
8. Reset `input.md` to the seed template (`## Active request\nNo active request\n\n## Options\n- [ ] No changes — provide answer only\n- [ ] Skip analysis document generation\n\n## Input\n\n`). Then read `.aib_memory/requests_register.md`, find the Active request row, and replace `No active request` in the `## Active request` line with `<request_id> — <title>` (the newly created request).

---

Requirements:
- Follow required headings exactly as defined in `analysis-convention.md`.
- Keep statements concrete and traceable to request scope.
- Do not ask user for information you can collect yourself from the workspace — review files and search for answers first.
- Do not ask the user for information you can find in the Internet or via available tools or MCP — research yourself before raising user-facing questions.
- Explicitly list risks in the analysis.
- If information is insufficient, make a research-based assumption and record it in `## Assumptions` in `request.md`.
- Explain explicitly all non-common terms in Domain Knowledge Essentials and Technical Knowledge & Terms sections.
- The analysis document is a reasoning artifact only; it is NOT an implementation driver.
- `inputs/input-archive-*.md` files in request folders MUST NOT be read or referenced by this prompt beyond archiving.

Output — Part 1: Analysis file
- Full content replacement of `.aib_memory/requests/<request-folder>/analysis.md`.
- Must follow the section structure defined in `analysis-convention.md`.
- Skipped if the "Skip analysis document generation" toggle is checked.

Output — Part 2: Update `request.md` with implementation-relevant sections

After generating the analysis, update `request.md` by appending or replacing the following optional sections. Add a section only when it has content; never add an empty shell section.

### Section: `## Assumptions`
- List all implementation-affecting assumptions derived during analysis.
- Format: `- A<n>: <text>` followed by `  - Risk if false: <short impact statement>`.
- Fully replace this section on every re-run (AI-generated; no user data).

### Section: `## Plan`
- Generate a Work Breakdown Structure with numbered tasks for this iteration.
- Each task MUST use this schema:
  ```
  ### Task <N>: <Task Name>
  **Intent:** <single-sentence goal>
  **Inputs:** <files, configs, parameters, data preconditions>
  **Outputs:** <artifacts produced or changed; file paths or product components>
  **External Interfaces:** <systems, data sources, modules consumed or produced>
  **Environment & Configuration:** <environments, config keys, secrets handling notes>
  **Procedure:** <ordered, concise steps>
  **Done Criteria:** <objective pass/fail checks>
  **Dependencies:** <Task IDs or external>
  **Risk Notes:** <if any>
  ```
- Keep tasks vertically sliceable; each must produce at least one verifiable output.
- Target ≤ 12 tasks per iteration; keep each procedure to ≤ 6 steps unless strictly necessary.
- Fully replace this section on every re-run (AI-generated; no user data).

### Section: `## Testing`
- Define intent-level test cases: what to test and what the expected observable outcome is.
- Format: `- T<n> — <name>: <description>. Expected outcome: <observable pass/fail result>.`
- Cover: file existence checks, content checks, tool/script execution, test suite runs, and re-run idempotency.
- Fully replace this section on every re-run (AI-generated; no user data).

### Section: `## Documentation`
- List all documentation files that must be revised because of this request.
- Format: `- <relative path> (ref_id: <REF-ID>) — <reason for update>.`
- If ref_id is not in `references.md`, use `(ref_id: N/A)`.
- Fully replace this section on every re-run (AI-generated; no user data).

### Section: `## Questions & Decisions`
- Add only when the analysis identifies unknowns or decision forks that cannot be resolved through research.
- Each question block:
  ```
  **Q<nnn>**: <question text>
  - [ ] Option A: <text>
  - [ ] Option B: <text>
  - [ ] Other: ___
  > Answer: 
  ```
- Use stable QIDs starting from Q001 (or the next available number on re-run).
- Re-run merging rules (MUST enforce):
  - Read the existing `## Questions & Decisions` section before writing.
  - A question is "answered" if at least one checkbox is `[x]` OR the `> Answer:` line has non-empty text after the colon.
  - Answered questions MUST be applied as embedded instructions to the relevant sections of `request.md` (Goal, Scope, Constraints, etc.) based on what the answer addresses, then removed from `## Questions & Decisions`.
  - Mapping hint: inspect the question text and answer to determine which mandatory section it addresses; if ambiguous, apply to `## Scope`.
  - New unanswered questions are appended after any remaining unanswered questions with sequentially higher QIDs.
  - If an answered question's prior answer appears to conflict with the updated analysis context, append `> [!NOTE] DECISION REVIEW NEEDED: <reason>` immediately after the existing answer block. Do not alter the answer.


Re-run behaviour summary:
- `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`: always fully replaced.
- `## Questions & Decisions`: answered questions are applied to relevant `request.md` sections and removed; unanswered questions are preserved.
- Sections with no content: do not add (never create an empty shell section).

Standard flow final step (MUST execute when invoked directly, MUST NOT execute when triggered from `aib-implement.md`):
- After all Part 1 and Part 2 outputs are fully written and confirmed, reset `input.md` to the seed template (`## Active request\nNo active request\n\n## Options\n- [ ] No changes — provide answer only\n- [ ] Skip analysis document generation\n\n## Input\n\n`). Then replace `No active request` in the `## Active request` line with the current active request ID and title (format: `<request_id> — <title>`). This reset MUST be the last action of the run. MUST NOT perform this reset if the current analysis run was triggered from `aib-implement.md`.

Context-window management:
- If the aggregate size of required-read files exceeds 80% of available context, prioritize files by relevance to request scope, summarize the rest, and note which files were summarized in the output artifact.

Confirm at the very end of the conversation with the text "--- I am done with the analysis ---" that all your activities are finished.

