# Prompt: aib-analyze

## 1. Objective

Generate `.aib_memory/analysis-<request_id>.md` for the resolved active request, and update `.aib_memory/plan-<request_id>.md` with implementation-relevant sections (`## Plan` and `## Decisions`).

`<request_id>` is the active request ID resolved in Preflight (e.g. `R-20260509-2313`).

> **Authoritative invariants for this prompt:**
> - MUST follow the section order and execution sequence defined below without reordering.
> - MUST NOT introduce behaviors not explicitly specified in this prompt.
> - MUST NOT skip or merge any numbered step.

---

## 2. Execution Model Summary

This prompt operates as a deterministic 9-step linear workflow. Each step is strictly ordered and must complete before the next begins.

1. **Preflight + State Resolution** — Read workspace instructions, resolve register state, auto-create request if no Active request exists.
2. **Context check** — Verify `context.md` exists and is non-trivial; trigger `aib-refresh-context.md` if absent or empty.
3. **Read inputs** — Read plan, input.md, attachments, existing analysis, context, additional flagged files, and convention files.
4. **Halt on unanswered questions** — If `## Questions` section is present in `input.md` with unanswered Q-blocks, halt. If all answered, apply answers and continue.
5. **Generate analysis** — Produce `analysis-<request_id>.md` with 5 mandatory sections (full replace on every run).
6. **Archive input and reset** — Invoke `finalize-input.py` to archive and reset `input.md`. Executes only when no Q-blocks are generated in step 8.
7. **Quality check** — Validate analysis against `requirements-analysis-convention.md`.
8. **Q-block generation** — If genuine decision choices tagged `ask` exist, write Q-blocks to `input.md ## Questions` and halt.
9. **Plan generation** — Update `plan-<request_id>.md` with Plan and Decisions sections. Executes only when all prerequisites are met (no Q-blocks generated or all answered on re-run).

---

## 3. Global Rules

### 3.1 Global Constraints

These constraints apply throughout the entire prompt execution. Individual sections reference them by GC identifier rather than restating them.

- **GC-01 — No archive reads:** `inputs/input-archive-*.md` files in request folders MUST NOT be read or referenced during any phase of this prompt.
  
- **GC-02 — Single input reset:** `input.md` MUST be reset exactly once per run. The reset is performed either by the Auto-Request Creation Branch (section 7.1, step 5) or by step 6 (Archive Input and Reset). Never both. **Exception:** When Q-blocks are written to `input.md ## Questions` during this run (step 8), step 6 MUST NOT execute — the reset is deferred so the developer can read and answer the Q-blocks before the next run.
  
- **GC-03 — Q-blocks in first cycle only:** Q-blocks are generated only when this is the first analysis run for the active request (i.e., no answered Q-blocks exist in `input.md`). On re-run after answers, no new Q-blocks are generated.

- **GC-04 — Halt on missing mandatory files:** If any mandatory file listed in section 4.1 (Inputs) cannot be read, execution MUST HALT with an explicit error message identifying the missing file.

- **GC-05 — No partial writes on halt:** When execution halts due to any error condition, MUST NOT write any output files. The workspace state must remain unchanged.
  
- **GC-06 — No closed-request reads:** Files inside `.aib_memory/requests/<folder>/` that belong to a Closed request MUST NOT be read or referenced during any phase of this prompt. This covers all artifact types (request, analysis, implementation, input archives, and any other file). A request folder belongs to a Closed request when its `state` in `requests_register.md` is `Closed`. If in doubt, treat the folder as Closed.
  
- **GC-07 — No implementation writes:** This prompt MUST NOT create, edit, or delete any file outside `.aib_memory/` except for the tool script invocations explicitly authorized in sections 7.1 (step 3 and step 5) and 5.6.2. Source code, test files, CI workflow files, scripts, and all non-AIB-memory artifacts are strictly out of bounds. Discovering that a fix is needed does NOT authorize applying it.

### 3.2 Failure Handling

> **Trigger:** Any of the conditions below MUST cause an immediate execution HALT.
> **Rule:** On halt, output the specified literal error message and MUST NOT write any output files (See GC-05).

| Condition | Error message |
| --- | --- |
| A mandatory input file (section 4.1) cannot be read | `ERROR: Cannot read mandatory file <path>. Execution halted.` |
| A convention file (`.aib_brain/conventions/*.md`) cannot be read | `ERROR: Cannot read convention file <path>. Execution halted.` |
| A tool script (`.aib_brain/tools/*.py`) exits with a non-zero code | `ERROR: Tool script <script> failed with exit code <N>. Execution halted.` |
| Any write attempted to a file outside .aib_memory not covered by GC-07 exceptions | `ERROR: Unauthorized write to <path> blocked. aib-analyze.md is a reasoning-only prompt. Use aib-implement.md to apply changes.` |
| Answer Application Sub-flow detects one or more unanswered Q-blocks | `Note: <N> of <M> questions in input.md are unanswered. Answer all questions before re-running analysis. Execution halted.` |

---

## 4. Inputs, Outputs & Dependencies

### 4.1 Inputs

| Source | Description |
| --- | --- |
| `.aib_memory/plan-<request_id>.md` | Active plan (authoritative scope source) |
| `.aib_memory/context.md` | Workspace product context (optional; graceful when absent) |
| `.aib_memory/input.md` | Developer input; Q-blocks and options are read here |
| `.aib_memory/attachments/` | Supplementary input files (text read; binary acknowledged by name) |
| `.aib_memory/instructions.md` | Persistent workspace-level directives |
| Additional files listed in `instructions.md` | Developer-flagged context files |

### 4.2 External Dependencies

| Item | Location | Purpose |
| --- | --- | --- |
| `create-request.py` | `.aib_brain/tools/create-request.py` | Creates request folder and register entry (Auto-Request Branch only) |
| `finalize-input.py` | `.aib_brain/tools/finalize-input.py` | Archives `input.md`, moves attachments, resets `input.md` to seed template |
| `analysis-convention.md` | `.aib_brain/conventions/analysis-convention.md` | Mandatory structure for the analysis document |
| `plan-convention.md` | `.aib_brain/conventions/plan-convention.md` | Mandatory structure for `plan.md` |
| `requirements-analysis-convention.md` | `.aib_brain/conventions/requirements-analysis-convention.md` | Requirements gate checklist applied during analysis to verify request completeness before WBS generation |

### 4.3 Outputs

| Artifact | Location | Description |
| --- | --- | --- |
| `analysis-<request_id>.md` | `.aib_memory/` root (active phase) | Full analysis document; set of mandatory sections |
| `plan-<request_id>.md` (updated) | `.aib_memory/` root (active phase) | Updated with Plan and Decisions sections |
| `input.md` (updated) | `.aib_memory/input.md` | Q-blocks written to `## Questions` (when applicable); reset to seed template at end of run **only when no Q-blocks were generated** — reset is deferred when Q-blocks are present so the developer can answer them |

---

## 5. Execution Procedure

> **MUST execute every step in the order shown.** Each step is numbered and must complete before the next begins.

### 5.1 Step 1 — Preflight + State Resolution

1. Read `.aib_memory/instructions.md`. If the file exists and is non-empty, treat its content as persistent workspace-level instructions that MUST be observed throughout this prompt's execution. If the file is absent or empty, proceed normally.

2. Read `.aib_memory/requests_register.md` and count rows with `state = Active`.

3. Branch on the count:
   - **Exactly one Active row** → record the resolved request and continue to step 2.
   - **Zero Active rows** → enter the **Auto-Request Creation Branch** (section 7.1). After the branch completes, continue to step 2.
   - **More than one Active row** → output the literal message **"ERROR: Register inconsistency — multiple Active requests found. Execution halted. Fix requests_register.md before running analysis."** and HALT. MUST NOT proceed to any subsequent step. MUST NOT write any output files.

4. Use the single Active row as the resolved request. The resolved `<request_id>` MUST be used everywhere in this run.

### 5.2 Step 2 — Context Check

1. Check whether `.aib_memory/context.md` is absent or empty (contains only whitespace after trimming) or has less than 50 words.

2. If **absent or empty**: execute `.aib_brain/prompts/aib-refresh-context.md` to populate `context.md`. After execution completes, continue to step 3.

3. If **present and non-empty**: continue directly to step 3.

**Non-recursion guarantee:** `aib-refresh-context.md` does NOT invoke `aib-analyze.md`. No recursive execution loop can occur.

### 5.3 Step 3 — Read Inputs

1. Read the active `plan-<request_id>.md` from `.aib_memory/plan-<request_id>.md`. If the file is absent, check `.aib_memory/input.md` for the presence of a `## Questions` section. If a `## Questions` section exists, set a **deferred-creation** flag and continue without reading `plan.md` (it will be created by the Answer Application Sub-flow, section 7.2). If `plan.md` is absent and no `## Questions` section exists in `input.md`, halt with the GC-04 error message.

2. Recursively walk all files in `.aib_memory/attachments/` (including files in subdirectories at any depth). For each file found (excluding `.gitkeep`): if text-readable, read its full content as additional input context; if binary, note the filename and acknowledge its presence. Files in `attachments/` are considered part of the input even if not referenced in `input.md`. If the folder is absent or empty, continue normally.

3. Read the `## Options` section of `input.md` (`.aib_memory/input.md`).

4. Read `.aib_memory/context.md`. If the file is absent or empty, continue normally with no error; otherwise treat its content as the unified workspace product context for this analysis run.

5. If `.aib_memory/instructions.md` lists additional file paths the developer has flagged for AIB to read, read each of those files. Otherwise skip.

6. Read all three convention files: `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/plan-convention.md`, and `.aib_brain/conventions/requirements-analysis-convention.md`.

7. Read existing `analysis-<request_id>.md` if present (for re-run Input Interpretation source).

### 5.4 Step 4 — Halt on Unanswered Questions

1. Check if `input.md` contains a `## Questions` section with one or more Q-blocks.

2. If **no `## Questions` section exists**: continue directly to step 5.

3. If **`## Questions` section exists**: enter the **Answer Application Sub-flow** (section 7.2).
   - If any Q-block is unanswered → HALT (per section 7.2 step 0).
   - If all Q-blocks are answered → apply answers, remove `## Questions` section, and continue to step 5.

### 5.5 Step 5 — Generate Analysis

> **Invariants:**
> - MUST follow required headings exactly as defined in `analysis-convention.md`.
> - MUST keep statements concrete and traceable to request scope.
> - MUST NOT ask the user for information you can collect yourself from the workspace — review files and search for answers first.
> - MUST NOT ask the user for information you can find on the Internet or via available tools or MCP — research yourself before raising user-facing questions.
> - MUST explicitly list risks in the analysis.
> - If information is insufficient, MUST make a research-based assumption and record it in the relevant Plan task's Risk Notes in `plan.md`.
> - The analysis document is a reasoning artifact only; it is NOT an implementation driver.

Generate `analysis-<request_id>.md` as a full content replacement (overwrite) at `.aib_memory/analysis-<request_id>.md`. Must follow the section structure defined in `analysis-convention.md`. Refer to section 6 for output behavioral rules.

Detect `## Amend Request` section in `plan.md`. If present and non-empty: apply its free-text instructions to the relevant mandatory sections (`## Goal`, `## Constraints`, `## Success criteria`) of `plan.md`, then clear the content of `## Amend Request`.

### 5.6 Step 6 — Archive Input and Reset

> **Trigger guard:** This step executes ONLY when no Q-blocks are generated in step 8. If Q-blocks are generated in step 8, this step is skipped — the reset is deferred so the developer can answer the questions. The Auto-Request Creation Branch (section 7.1) also suppresses this step (its own step 5 already handled archive + move + reset). This step MUST NOT execute when `aib-analyze.md` is triggered from `aib-implement.md`.

#### 5.6.1 Eligibility Check

1. Evaluate whether `.aib_memory/input.md` is in a non-stub state.
   - **Definition of "non-stub":** the file content is not exactly equivalent to the seed template state after normalization of line endings and trailing whitespace. The seed template state is:
     ```
     ## Active request
     No active request

     ## Options
     - Minimum questions: 0

     ## Input

     ```
     (literal seed: `## Active request\nNo active request\n\n## Options\n- Minimum questions: 0\n\n## Input\n\n`)

#### 5.6.2 Finalize Script Invocation

2. Invoke `finalize-input.py` to handle the archive + move + reset sequence atomically. The script will:
   - If non-stub: archive the pre-reset `input.md` content to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md` before resetting.
   - If stub-equivalent: skip archive creation for this standard-flow reset.
   - Move any remaining non-`.gitkeep` files from `.aib_memory/attachments/` to `<request-folder>/inputs/`.
   - Reset `input.md` to the seed template with the active request ID injected.
   ```
   python .aib_brain/tools/finalize-input.py --workspace . --request-id <request_id>
   ```
   where `<request_id>` is the active request ID.

#### 5.6.3 Post-conditions

- The reset inherently clears any `## Questions` section that was present in `input.md`.
- No further file writes are permitted after this step completes.

### 5.7 Step 7 — Quality Check

After generating the analysis (step 5), evaluate every mandatory checklist item from `requirements-analysis-convention.md` against the active request (`plan-<request_id>.md`) and `input.md`. Surface the gate evaluation — item-by-item status, any unmet mandatory items, and any identified gaps — in the `## Research Results` section of the analysis document under a **Requirements Gate Evaluation** sub-heading. If any mandatory item cannot be satisfied by a reasonable documented assumption, tag the gap `ask` in the Decision Points section and generate a corresponding Q-block in step 8.

### 5.8 Step 8 — Q-block Generation

1. Enumerate ALL implementation decision forks identified in the request scope. Record the complete enumeration in the **`### Decision Points`** section within `## Decision Register` of the analysis document.

2. Tag each fork as `ask` or `resolve-autonomously` using the classification rules in section 6.3.

3. For every fork tagged `ask`, generate one Q-block. Write Q-blocks to a `## Questions` section appended to `input.md`.

4. If Q-blocks are generated: `## Plan` in `plan.md` MUST be set to the deferral stub (see section 6.2), step 6 is skipped, and execution halts after step 8.

5. If no Q-blocks are generated (no genuine multi-choice forks): do NOT write a `## Questions` section. Continue to step 6, then step 9.

### 5.9 Step 9 — Plan Generation

> **Precondition:** This step executes only when no Q-blocks were generated in step 8, OR on re-run after the Answer Application Sub-flow (step 4) has processed all answers.

Update `.aib_memory/plan-<request_id>.md` with Plan and Decisions sections per the rules in section 6.2. The full WBS MUST be generated. All 4 mandatory plan sections MUST be present.

---

## 6. Output Specifications

### 6.1 Analysis Document

- Full content replacement (overwrite) of `.aib_memory/analysis-<request_id>.md` (NOT inside the request subfolder — the active analysis lives at `.aib_memory/` root while the request is active, using the ID-suffixed filename). On every run — first pass or re-run — the file is written from scratch and ALL prior content is discarded. MUST NOT append to, prepend to, or partially edit the existing file. The fact that the prior analysis file was read during this run (e.g., to source ## Input Interpretation for the Answer Application Sub-flow) does NOT authorize retaining any of its content in the output.
- Must follow the section structure defined in `analysis-convention.md`: `## Overview`, `## Files Read During This Analysis Run`, `## Input Interpretation`, `## Research Results`, `## Decision Register`.
- Always generated unless triggered from `aib-implement.md` (see step 6 trigger guard in section 5.6).
- Refer to `analysis-convention.md` section 4 for the complete structural definition of each mandatory section.

After reading `requirements-analysis-convention.md` (step 3.6), evaluate every mandatory checklist item against the active request (`plan-<request_id>.md`) and `input.md`. Surface the gate evaluation — item-by-item status, any unmet mandatory items, and any identified gaps — in the `## Research Results` section of the analysis document under a **Requirements Gate Evaluation** sub-heading. If any mandatory item cannot be satisfied by a reasonable documented assumption, tag the gap `ask` in the Decision Points section and generate a corresponding Q-block.

---

### 6.2 plan.md Updates

After generating the analysis, update `.aib_memory/plan-<request_id>.md` by appending or replacing the following optional sections.

> **Invariant:** Add a section only when it has content; never add an empty shell section.

#### Section: `## Plan`

> **Plan deferral rule (Option A):** If Q-blocks are written to `input.md ## Questions` during this run, `## Plan` MUST be set to the following stub and MUST NOT contain a WBS:
> ```
> *Plan deferred — pending Q&A. Re-run analysis after answering questions in `input.md`.*
> ```
> The full WBS is generated only on the re-run when the Answer Application Sub-flow (section 7.2) has processed all answers — i.e., when no `## Questions` section is present in `input.md` at step 4. The 4-section plan structure (Goal, Constraints, Success criteria, Plan) MUST always be fully present when the file is written.

- Generate a Work Breakdown Structure with numbered tasks for this iteration.
- Each task MUST use this schema:
  ```
  ### Task <N>: <Task Name>

  #### Intent
  <single-sentence goal>

  #### Outputs
  <artifacts produced or changed; file paths or product components>

  #### Procedure
  <step 1>

  <step 2>

  <...each step on its own paragraph, separated by one blank line; each step MUST cite the exact file path it operates on>

  #### Done criteria
  <objective pass/fail checks>

  #### Dependencies
  <Task IDs or external>

  #### Risk notes
  <if any>
  ```

**Plan-level invariants:**

- Keep tasks vertically sliceable; each must produce at least one verifiable output.
- Target ≤ 12 tasks per iteration; keep each procedure to ≤ 6 steps unless strictly necessary.
- Every Procedure step MUST reference the exact file path it operates on. Steps that do not operate on a specific file (e.g., running a terminal command) MUST name the command and its expected output location.
- Every plan MUST include:
  - (a) a task defining automated test steps for the request scope (covering all testable Success Criteria defined in `plan.md`);
  - (b) a task to update `.aib_memory/context.md` and any other documentation files affected by the request, reflecting changes made and any discovered discrepancies. The documentation task MUST be planned using the same Procedure explicitness standard as code tasks: each documentation step MUST specify (1) the target file path, (2) what to change, and (3) an acceptance test.
- Pre-flight findings (cross-reference issues, missing information, factual inconsistencies, impacted files) MUST be redistributed into the relevant Plan task's `Risk Notes` field or raised as Q-blocks in `## Decisions` when user input is needed. Do NOT create separate top-level sections for these findings.
- Fully replace this section on every re-run (AI-generated; no user data).

#### Section: `## Decisions`

> **Note:** Q-blocks are NOT written to `plan.md ## Decisions`. They are written to `input.md ## Questions` instead (see Q-block Generation Rules in section 6.3).

- `## Decisions` records resolved Q&A entries — one entry per question that was asked to the developer and answered.
- Each entry uses the format: `**Q<nnn>:** <question text> → **Chosen:** <chosen option text>`.
- Entries are appended by `aib-analyze.md` when applying answered Q-blocks (Answer Application Sub-flow, section 7.2); they are never removed after being written.
- **Re-run rule:** append-only; never modify or remove existing entries.

---

### 6.3 Q-block Rules

#### 6.3.1 Decision Identification

**Step 1 — Decision Fork Enumeration (MUST execute before any Q-block generation):**
Enumerate ALL implementation decision forks identified in the request scope. Record the complete enumeration in the **`### Decision Points`** section within `## Decision Register` of the analysis document. Tag each fork as `ask` or `resolve-autonomously` using the rules in section 6.3.2. Q-blocks are then generated only for `ask`-tagged forks.

#### 6.3.2 Decision Classification (strictly enforced)

**Step 2 — Classification rules:**

A fork MUST be tagged `resolve-autonomously` ONLY when ALL of the following hold:

1. The developer's own `input.md ## Input` text OR a named, specific section of a workspace convention file explicitly and unambiguously resolves it.
2. The cited source uses clear, explicit language — not inference, implication, or "spirit of" interpretation.
3. The rationale in the Decision Points section quotes or cites the exact source text and file path.

A fork MUST be tagged `ask` in every other case, including:

- When the answer seems "obvious" or follows "industry best practice" without a named workspace source explicitly stating so.
- When external literature, benchmarking findings, or AI judgment provide the only justification.
- When the answer is "strongly implied" but not explicitly stated.
- When in doubt.

The AI MUST NOT express a preference or steer the developer toward any option when tagging a fork `ask`.

#### 6.3.3 Q-block Generation

**Step 3 — Q-block generation for `ask`-tagged forks:**
For every fork tagged `ask` in the Decision Points section, generate one Q-block. Q-blocks MUST reference the alternative by name from the Decision Register section when applicable.

For `resolve-autonomously` forks: document the chosen resolution inline in the relevant `plan.md` section and record the rationale in the Decision Points section.

Do NOT raise Q-blocks for decisions with no meaningful implementation impact.

**Minimum-questions handling:** If the developer has set a `Minimum questions:` value greater than 0 in `input.md ## Options`, generate at least that many Q-blocks. If fewer genuine decision points exist than the minimum, document the shortfall in the analysis but do NOT generate low-value filler questions.

**Q-block generation target — `input.md ## Questions`:**

- Q-blocks are written to a `## Questions` section appended to `input.md` (`.aib_memory/input.md`).
- If no Q-blocks are generated (no genuine multi-choice forks), do NOT write a `## Questions` section to `input.md`.
- One cycle of Q&A is assumed: after all questions in `input.md` are answered, the Answer Application Sub-flow (step 4 / section 7.2) resolves them and no new Q-blocks are generated on re-run.

**Q-block format (multiple-choice):**

- Each question block:
  ```
  **Q<nnn>**: <question text>
  > **Why this matters:** <one-sentence explanation of impact on implementation>
  - [ ] Option A: <text> *(recommended)*
  - [ ] Option B: <text>
  - [ ] Option C: <text>
  - [ ] Other: ___
  ```
- Use stable QIDs starting from Q001 (or the next available number if questions already exist).
- MUST include the `> **Why this matters:**` line immediately after the question text.
- MUST mark exactly one option per Q-block as `*(recommended)*`. The recommended option MUST be placed first in the list. All other options MUST NOT carry the marker.
- Multiple-choice is preferred when bounded options exist.

**Q-block format (free-text):**

- Use when information cannot be inferred by the AI agent and no bounded options exist:
  ```
  **Q<nnn>**: <question text>
  > **Why this matters:** <one-sentence explanation of impact on implementation>
  - Answer: ___
  ```
- Free-text questions must explain what information is needed, why, and the impact.
- Use free-text only when the answer space is unbounded (e.g., naming, external URLs, configuration values).

---

## 7. Sub-flows

### 7.1 Auto-Request Creation Branch

**Triggered when:** zero Active rows found in Preflight step 1.

> **Constraint:** This branch is the only place where `create-request.py` is invoked from `aib-analyze.md`. After completing the branch, control returns to section 5.6 of the standard flow (NOT step 1).

**Procedure:**

1. Read `.aib_memory/input.md`.
   - If `## Input` section is empty or contains only whitespace: output the literal message **"ERROR: No active request and input.md is empty. Add content to ## Input before running analysis."** and HALT. Do NOT proceed.
2. Derive a request title from the `## Input` content (first meaningful sentence or noun phrase, ≤ 60 characters).
3. Invoke `.aib_brain/tools/create-request.py`:
   ```
   python .aib_brain/tools/create-request.py --workspace . --title "<derived-title>"
   ```
4. Read `.aib_memory/requests_register.md` to resolve the newly created request folder and `<request_id>`.
5. Archive the current `input.md` content and move attachments by invoking `finalize-input.py`:
   ```
   python .aib_brain/tools/finalize-input.py --workspace . --request-id <request_id>
   ```
   where `<request_id>` is the newly created request ID resolved in step 4. The script:
   - archives `input.md`,
   - moves all non-`.gitkeep` attachment files from `.aib_memory/attachments/` to `<request-folder>/inputs/`,
   - resets `input.md` to the seed template with the request ID injected.

   After the script completes, `.aib_memory/attachments/` MUST contain only `.gitkeep`.
6. Resume the standard analysis flow at step 2 (Context Check).
   - After resuming, if the analysis generates Q-blocks, `plan-<request_id>.md` MUST NOT be written in this pass — it remains absent. If the analysis generates no Q-blocks, `plan-<request_id>.md` is written as part of step 9 during this same pass. All 4 mandatory sections MUST be present when the file is first written, whether in the no-Q-blocks first pass or in the Answer Application Sub-flow re-run.
   - **MUST NOT** reset `input.md` again during this triggered standard flow — the reset was already performed by `finalize-input.py` in step 5.
   - **MUST NOT** execute step 6 (Archive Input and Reset) for this triggered run.

### 7.2 Answer Application Sub-flow

**Triggered when:** `## Questions` section is present in `input.md` (detected in step 4).

**Procedure:**

0. **All-answered pre-check:** Count the total number of Q-blocks in `input.md ## Questions` (M). Count the number of answered Q-blocks (N) — a Q-block is answered when at least one checkbox is marked `[x]` OR the `- Answer:` line has non-empty text after the colon. If N < M: output `Note: <N> of <M> questions in input.md are unanswered. Answer all questions before re-running analysis. Execution halted.` and HALT. MUST NOT modify `input.md`, `plan.md`, or any other file. MUST NOT continue to any subsequent step of this sub-flow or to the standard analysis flow.

1. Before applying Q-block answers to `plan.md` sections, check whether `.aib_memory/plan-<request_id>.md` exists. If the file is absent (deferred-creation state), create it from scratch using the following sources: (1) the `## Input Interpretation` section from the existing `.aib_memory/analysis-<request_id>.md`; (2) the Q&A answers from the `## Questions` section of `input.md`; (3) the request title from `requests_register.md`. All 4 mandatory sections MUST be present in the newly created file. Sections 3–4 (`## Success criteria`, `## Plan`) MAY be empty here — they are populated during the standard analysis output generation (Chapter 6 output generation) that follows the Answer Application Sub-flow.

2. For each Q-block in `## Questions`: apply the chosen option (the checked `[x]` option or the non-empty `- Answer:` text) to the relevant `plan.md` section (`## Goal`, `## Constraints`, etc.) based on what the answer addresses. If the target section is ambiguous, apply to `## Goal`. Append a resolved entry to `plan.md` `## Decisions` in the format `**Q<nnn>:** <question text> → **Chosen:** <chosen option text>`.
3. After all Q-blocks are processed, remove the entire `## Questions` section from `input.md`.
4. Continue with the normal analysis flow (step 5 onward). The Plan deferral rule (section 6.2) does NOT apply on this re-run — Q-blocks have been resolved and the full plan MUST be generated. No new Q-blocks are generated when re-running after answers — all ambiguities were resolved in the prior run.

### 7.3 Re-run Behaviour Summary (Navigational Reference)

> **Note:** This section is a navigational summary derived from sections 5–6. The authoritative rules live in those sections; this summary MUST NOT be read as authoritative if it conflicts with the body of the prompt.

- `## Plan` (in `plan.md`): stubbed when Q-blocks are generated on first run; fully generated on re-run after Q&A answers are applied (see section 6.2).
- `## Decisions` (in `plan.md`): append-only; entries are added by the Answer Application Sub-flow and never removed (see section 6.2).
- `## Questions` (in `input.md`): answered/unanswered Q-blocks are processed and the section is cleared by the Answer Application Sub-flow (step 4 / section 7.2) on re-run.
- Sections with no content: do not add (never create an empty shell section).

---

## 8. Completion Confirmation

Confirm at the very end of the conversation (this should be the very last message to the user after all other generated response) with the text "--- I am done with the analysis ---" that all your activities are finished.