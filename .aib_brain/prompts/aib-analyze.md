# Prompt: aib-analyze

## 1. Objective

Generate `.aib_memory/analysis-<request_id>.md` for the resolved active request, and update `.aib_memory/plan-<request_id>.md` with implementation-relevant sections (`## Plan` and `## Decisions`).

`<request_id>` is the active request ID resolved in Preflight (e.g. `R-20260509-2313`).

> **Authoritative invariants for this prompt:**
> - MUST follow the section order and execution sequence defined below without reordering.
> - MUST NOT introduce behaviors not explicitly specified in this prompt.
> - MUST NOT skip or merge any numbered step.

---

## 2. Variables definition

The following internal variables are used for process control and are not persisted:

   * [Input-detected] — boolean; True when the user has provided input via the ## Input section in input.md and/or files in attachments. Indicates that change instructions from the user are present. Initially set to False.
  
   * [Questions-detected] - number; How many questions are found defined in  `input.md ## Questions` section. Initially set to 0

   * [Questions-answered] - number; How many questions have answer defined in  `input.md ## Questions` section. Initially set to 0
  
   * [Questions-expected] - number; How many questions need to be added in  `input.md ## Questions` section. Initially set to 0

---

## 3. Global Rules

### 3.1 Global Constraints

These constraints apply throughout the entire prompt execution. Individual sections reference them by GC identifier rather than restating them.

- **GC-01 — No archive reads:** `inputs/input-archive-*.md` files in request folders MUST NOT be read or referenced during any phase of this prompt.
  
- **GC-02 — Halt on missing mandatory files:** If any mandatory file listed in section 4.1 (Inputs) cannot be read, execution MUST HALT with an explicit error message identifying the missing file.

- **GC-03 — No partial writes on halt:** When execution halts due to any error condition, MUST NOT write any output files. The workspace state must remain unchanged.
  
- **GC-04 — No closed-request reads:** Files inside `.aib_memory/requests/<folder>/` that belong to a Closed request MUST NOT be read or referenced during any phase of this prompt. A request folder belongs to a Closed request when its `state` in `requests_register.md` is `Closed`.
  
- **GC-05 — No implementation writes:** This prompt MUST NOT create, edit, or delete any file outside `.aib_memory/` except for the tool script invocations explicitly authorized in **Appendix A — Auto-Request Creation Branch**. Source code, test files, CI workflow files, scripts, and all non-AIB-memory artifacts are strictly out of bounds. Discovering that a fix is needed does NOT authorize applying it.

### 3.2 Failure Handling

> **Trigger:** Any of the conditions below MUST cause an immediate execution HALT.
> **Rule:** On halt, output the specified literal error message and MUST NOT write any output files (See GC-03).

| Condition | Error message |
| --- | --- |
| A mandatory input file (section 4.1) cannot be read | `ERROR: Cannot read mandatory file <path>. Execution halted.` |
| A convention file (`.aib_brain/conventions/*.md`) cannot be read | `ERROR: Cannot read convention file <path>. Execution halted.` |
| A tool script (`.aib_brain/tools/*.py`) exits with a non-zero code | `ERROR: Tool script <script> failed with exit code <N>. Execution halted.` |
| Any write attempted to a file outside .aib_memory not covered by GD-05 exceptions | `ERROR: Unauthorized write to <path> blocked. aib-analyze.md is a reasoning-only prompt. Use aib-implement.md to apply changes.` |
| Answer Application Sub-flow detects one or more unanswered Q-blocks | `Note: <N> of <M> questions in input.md are unanswered. Answer all questions before re-running analysis. Execution halted.` |

---

## 4. Inputs, Outputs & Dependencies

### 4.1 Inputs

| Source | Description |
| --- | --- |
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

### S01. Step 1 — Preflight + State Resolution

S01.1. Read `.aib_memory/instructions.md`. If the file exists and is non-empty, treat its content as persistent workspace-level instructions that MUST be executed and observed throughout this prompt's execution. If the file is absent or empty, proceed normally.

S01.2. Read `.aib_memory/requests_register.md` and count rows with `state = Active`.

S01.3. Branch on the count:
   
   - **Exactly one Active row** → record the resolved request and continue to step 2.
  
   - **Zero Active rows** → execute **Appendix A — Auto-Request Creation Branch**, then resume at Step 2. 
  
   - **More than one Active row** → output the literal message **"ERROR: Register inconsistency — multiple Active requests found. Execution halted. Fix requests_register.md before running analysis."** and HALT. MUST NOT proceed to any subsequent step. MUST NOT write any output files.

S01.4. Use the single Active row as the resolved request. The resolved `<request_id>` MUST be used everywhere in this run.


### S02. Step 2 — Context Check

S02.1. Check whether `.aib_memory/context.md` is absent or empty (contains only whitespace after trimming) or has less than 50 words.

S02.2. If **absent or empty**: execute `.aib_brain/prompts/aib-refresh-context.md` to populate `context.md`. After execution completes, continue to step S03.

S02.3. If **present and non-empty**: continue directly to step S03.

### S03. Step 3 — Read Inputs

S03.1. Read the section `## Input` in `input.md` file. This is what the user has requested. If non-empty - set [Input-detected] to True.

S03.2. Recursively walk all files in `.aib_memory/attachments/` (including files in subdirectories at any depth). Files in `attachments/` are considered part of the input even if not referenced in `input.md`. 
  - If the folder is absent or empty, continue normally. 
  - If instructions for actions found - set [Input-detected] to True. 
  
S03.3. For each file found (excluding `.gitkeep`): 
  - if text-readable, read its full content as additional input context; 
  - if binary, note the filename and acknowledge its presence. 

S03.4. Read the `## Options ` section of `.aib_memory/input.md` and determine the value of the `Minimum questions:` and write the value in [Questions-expected].

### S04. Step 4 — Read Questions

1. Check if `input.md` contains a `## Questions` section with one or more Q-blocks.

2. If **no `## Questions` section exists**: continue directly to the next step.

3. If **`## Questions` section exists**: 
   
   - Count the total number of Q-blocks in `input.md ## Questions` and set the number in [Questions-detected]. 
  
   - Count the number of answered Q-blocks and write in [Questions-answered] the result. A Q-block is answered when any checkbox is [x], Other:is filled, or- Answer: is non-empty. 
  
   - If [Questions-answered] < [Questions-detected]: output `Note: <[Questions-answered]> of <[Questions-detected]> questions in input.md are unanswered. Answer all questions before re-running analysis. Execution halted.` and HALT. MUST NOT write any output files.


### S05. Step 5 — Generate Analysis

> **Rules:**
> - MUST follow required headings and sections structure exactly as defined in `.aib_brain/conventions/analysis-convention.md`.
> - MUST keep statements concrete and traceable to request scope.
> - MAY NOT ask the user for information you can collect yourself from the workspace — review files and search for answers first.
> - MUST seek for information you can find on the Internet or via available tools or MCP — research yourself before raising user-facing questions.
> - MUST explicitly list issues and risks found and write them in the analysis file.
> - If information is insufficient, MUST ask the user wia Q-block question.
> - The analysis document is a reasoning artifact only; it is NOT an implementation driver.
> - Never remove already added user inputs in Input Interpretation section - add the new after the existing.

S05.0. Make a backup of `analysis-<request_id>.md`. The current analysis need to be kept for user audit so make a copy of it in the request folde under `.aib_memory\requests` adding timestamp to its name. Only AFTER the current state is copied, make changes of the `analysis-<request_id>.md` file.

S05.1. If both [Input-detected] is False and [Questions-detected] is 0: output `Note: No new instructions found. Execution halted.` and HALT. MUST NOT write any output files.

S05.2. If [Input-detected] is True:

   S05.2.1. If `analysis-<request_id>.md` does not exists - generate it as per  `.aib_memory/input.md`, the files in `.aib_memory/attachments` and `.aib_memory/context.md` following `.aib_brain\conventions\analysis-convention.md ` 

   S05.2.2. If `analysis-<request_id>.md` exists - this means the user has added additional input instructions to be modified already existing analysis. Detect what should be changed in the analysis and change only the affected lines. You should follow `.aib_brain\conventions\analysis-convention.md ` and the structure of the analysis file should not be corrupted. Do not change lines where no need of change and the current content does not contradict to the new input.  

S05.3. If [Questions-detected] is more than 0:

   S05.3.1. If `analysis-<request_id>.md` does not exists - this probably means it was manually deleted. Output a note `[S05.3.1] questions detected but no analyis exists.This is unexpected state. Halting.`  and HALT. MUST NOT write any output files.  

   S05.3.2. If `analysis-<request_id>.md` exists - this means the user has answered to the questions and now the answers should be applied in the analysis. Detect the decision points in which the answers should be reflected in the analysis. Detect if in the other part of the analysis a change should be made accordingly the answers of the questions. Change only the affected lines. You should follow `.aib_brain\conventions\analysis-convention.md ` and the structure of the analysis file should not be corrupted. Do not change lines where no need of change and the current content does not contradict to the answers. 

S05.4. Ensure the **Decision Register** sub-heading is present in the analysis document. The solution described in the plan file will consist of tasks, each containing procedural steps. Each step may have multiple valid execution approaches depending on the provided input. When the differences between valid approaches would produce a significantly different implementation outcome, this is called a **Decision Point**. Identify all Decision Points during this step and record them in the `### Decision Points` section within `## Decision Register` of the analysis document, following `.aib_brain\conventions\analysis-convention.md`. If Decision Points are already registered in the document, check whether additional ones are needed and add them. Do not add Decision Points whose answer can be concluded from the input, attachments, context, or other workspace content.

S05.5. Ensure the **Requirements Gate Evaluation** sub-heading is present in the analysis document. Evaluate the analysis just produced against every item in requirements-analysis-convention.md and write the Requirements Gate Evaluation as the final sub-section of ## Research Results. If any mandatory item cannot be satisfied by a reasonable documented assumption, ad a new decision point in the analysis and tag it with `ask` in the Decision Points section.

### S06. Step 6 — Context Review

S06.1. Using the context.md content already loaded in S02, identify gaps relevant to the active request scope (based on the analysis just generated in S05).

S06.2. For each gap found:
   - Output a note `[S06] gap: <short-description-of-the-gap>`
   - First attempt to resolve it by scanning workspace files for the missing information.
   - If the gap can be resolved - output a note `[S06] gap: <short-description-of-the-gap> - can be resolved from workspace`
   - If the gap cannot be resolved from workspace sources, add a new Decision Point in the analysis document tagged `ask`, describing what information is missing from `context.md` and why it matters to the request. 

S06.3. If no gaps are found or all gaps were resolved from workspace sources - continue to the next step without adding Decision Points.

### S07. Step 7 — Archive Input and Reset

S07.1. Invoke `finalize-input.py` to handle the archive + move + reset sequence atomically. The script will:
   - Archive the pre-reset `input.md` content to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md` before resetting.
   - Move any remaining non-`.gitkeep` files from `.aib_memory/attachments/` to `<request-folder>/inputs/`.
   - Reset `input.md` to the seed template with the active request ID injected.
   ```
   python .aib_brain/tools/finalize-input.py --workspace . --request-id <request_id>
   ```
   where `<request_id>` is the active request ID.

### S08. Step 8 — Q-block Generation

> **Rules:**
> - Multiple-choice is preferred when bounded options exist.
> - Use free-text only when the answer space is unbounded (e.g., naming, external URLs, configuration values).

S08.1. If [Questions-expected] is more than the decision points marked as `ask` - change the tag of the most critical decision points marked as `resolve-autonomously` to `ask`. 

S08.2. For every Decision Point tagged `ask`, generate one Q-block following the instructions in `.aib_brain/conventions/q-block-convention.md`. Q-blocks MUST reference the alternative by name from the Decision Register section when applicable. Write Q-blocks to a `## Questions` section appended to `input.md`.

S08.3. Edit `.aib_memory/input.md` to replace the line `State: analysis_ready` with `State: questions_generated`. HALT.

S08.4. If no Decision Point tagged `ask` are found, do NOT write a `## Questions` section. Continue with the next step.

### S09. Step 9 — Plan Generation

S09.1. Generate or recreate `.aib_memory/plan-<request_id>.md` based solely on `.aib_memory/analysis-<request_id>.md` and the developer's input archived in the request folder. The plan MUST be self-sufficient: a human engineer or a fresh AI session MUST be able to execute it without consulting `.aib_memory/context.md` or any other file not referenced within the plan itself. Follow strictly the format and structure defined in `.aib_brain/conventions/plan-convention.md`.

S09.2. Self-sufficiency requirements — the generated plan MUST:
   - Include in `## Goal` the full background context explaining why the change is needed and which components are affected, so no external file needs to be read to understand the task.
   - Reference the exact file path in every procedure step that operates on a file. Steps that run terminal commands MUST name the command and its expected output.
   - Include a mandatory context update task (typically as the final or near-final task in the WBS) that specifies the exact `edit-context.py` invocations with literal `--operation`, `--area`, `--type`, and `--text` arguments for every atomic statement to be inserted or deleted. The implement agent MUST be able to run these commands verbatim without reading `context.md` first. The exact current text of any statement to be deleted MUST be embedded in the plan task procedure steps. During this step, read `.aib_memory/context.md` to identify the exact text of statements that need to change, then embed those exact texts into the plan task procedure steps.

### S10. Step 10 - Completion Confirmation

S10.1. Confirm at the very end of the conversation (this should be the very last message to the user after all other generated response) with the text "--- I am done with the analysis of `<request_id>` ---".

S10.2. Do not add additional text after "--- I am done with the analysis of `<request_id>` ---" line. MUST: If needed to be written somenting in the output chat - do it before this line.

---

## Appendix A — Auto-Request Creation Branch

> **Trigger:** Entered from Step 1 (§5.1) when zero Active rows are found in `requests_register.md` and `input.md ## Input` is non-empty.

**A.1.** Read `.aib_memory/input.md`.
   - If `## Input` section is empty or contains only whitespace: output the literal message **"ERROR: No active request and input.md is empty. Add content to ## Input before running analysis."** and HALT. Do NOT proceed.

**A.2.** Derive a request title from the `## Input` content (first meaningful sentence or noun phrase, ≤ 60 characters).

**A.3.** Invoke `.aib_brain/tools/create-request.py`:
   ```
   python .aib_brain/tools/create-request.py --workspace . --title "<derived-title>"
   ```

**A.4.** Read `.aib_memory/requests_register.md` to resolve the newly created request folder and `<request_id>`.

## Appendix B —  Decision Point Classification

**B.1.** A decision point MUST be tagged `resolve-autonomously` ONLY when ALL of the following hold:

1. The developer's own `input.md ## Input` text OR a named, specific section of a workspace convention file explicitly and unambiguously resolves it.
2. The cited source uses clear, explicit language — not inference, implication, or "spirit of" interpretation.
3. The rationale in the Decision Points section quotes or cites the exact source text and file path.

**B.2.** A decision point MUST be tagged `ask` in every other case, including:

- When the answer seems "obvious" or follows "industry best practice" without a named workspace source explicitly stating so.
- When external literature, benchmarking findings, or AI judgment provide the only justification.
- When the answer is "strongly implied" but not explicitly stated.
- When in doubt.