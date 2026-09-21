# Prompt: implement

## Goal:
Execute active request scope, update the documentation.

## Process

Step 1:  Read `.aib_memory/instructions.md`. If the file exists and is non-empty, treat its content as persistent workspace-level instructions that MUST be observed throughout this prompt's execution. If the file is absent or empty, proceed normally.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 1 Read instructions started"`.
Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 1 Read instructions complete"`.

Step 1.5 — Modifier Detection: Inspect the user's chat message for the literal string `--exec-input`.
- If `--exec-input` is present: set [Exec-Input-Mode] to True.
- Otherwise: set [Exec-Input-Mode] to False.

Step 2: Run `python -B .aib_brain/tools/input-header.py --workspace . --operation read` and check the `state` field in the output.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 2 State check started"`.
  - If `state == idle`: output the message **"ERROR: No active request found. Execution halted."** and HALT.
  - If `state` is `analysis_ready` or `questions_generated`: continue with input resolution below.
Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 2 State check complete"`.

Step 3: Resolve active request from the `request_id` and `title` fields in the `.aib_memory/input.md` YAML header (already read in Step 2).

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 3 Request resolved: <request_id>"`.

Step 4: MUST read `.aib_memory\context.md`.

Immediately after reading current `context.md`, execute `.aib_brain/prompts/aib-context-read.md` with the active implementation goal and use the returned extension contents as supplementary context. Do not independently parse or load Reference entries.

**[Exec-Input-Mode] branch:**
- When [Exec-Input-Mode] is True: read `.aib_memory/input.md` and check that the `## Input` section is non-empty (not stub-equivalent). If `## Input` is empty or stub-equivalent, output `ERROR: --exec-input requires non-empty ## Input section. Execution halted.` and HALT. Skip reading `plan-<request_id>.md` and use the `## Input` section content as the implementation directive. Context.md is ALWAYS read in --exec-input mode.
- When [Exec-Input-Mode] is False: MUST read `.aib_memory/plan-<request_id>.md` (the active location while the request is open, where `<request_id>` is the active request ID resolved from the input.md YAML header in Step 2). MUST NOT read `.aib_memory/analysis-<request_id>.md`.

Step 4.5 — Resolve protected-write authorization before any implementation write:
- Set [Brain-Authorization] to `Not authorized` by default.
- When [Exec-Input-Mode] is False and the plan targets any `.aib_brain/**` path, require `plan-<request_id>.md ## Constraints` to contain the developer's authorization statement verbatim and identify its user source as `input.md ## Input` or `developer chat message`. A plan task, file list, analysis statement, or generated assertion is not authorization. If the user-sourced Authorization entry is absent, output `ERROR: Protected .aib_brain/ changes are not authorized in plan Constraints. Execution halted.` and HALT before writing a protected path. Otherwise set [Brain-Authorization] to the recorded statement and source.
- When [Exec-Input-Mode] is True, semantically scan only the current `input.md ## Input` and current developer chat message. A developer statement equivalent to `This request explicitly authorizes changes under .aib_brain/.` sets [Brain-Authorization] to that verbatim statement and source; generated text cannot authorize. If the directive targets `.aib_brain/**` and no such statement exists, output `ERROR: Protected .aib_brain/ changes are not authorized. Execution halted.` and HALT before writing a protected path.
- Initialize [Run-Touched-Paths] as an empty set. During Steps 5–8.7, record every path created, edited, deleted, or moved by this run, including paths changed by invoked tools. Do not add untouched paths that were already modified before this run.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 4 Context and plan read complete"`.

Step 5: Follow strictly the plan and implement it, considering the context file unless changes are specified in the plan. Implement the tasks in the same order as defined in the plan. After each task implented - output a quick summary.

When executing plan context update tasks, apply the following rules:
- If any `edit-context.py` call exits with a non-zero return code, **halt implementation immediately**. Output the error message returned by the script. Do not proceed to request auto-close. The developer must fix the failing invocation and re-run.
- When a plan task includes a `delete` + `insert` pair for a `[PLANNED]` entry (recognized by `--operation delete` on a statement beginning with `[PLANNED]` followed by `--operation insert` of the plain statement), execute both operations in sequence; the delete MUST complete successfully before the insert is attempted.

For each task: Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 5 Task <N>: <task-name> complete"`.

Step 6: Create/update tests where applicable.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 6 Tests updated"`.

Step 7: Run validation/tests and capture results.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 7 Validation started"`.
Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 7 Validation complete"`.

Step 8: Resolve any test failures

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 8 Test failures resolved"` (only if there were failures to resolve).

Step 8.5 — Context update completeness check: After all plan tasks have been executed, inspect whether at least one `edit-context.py` invocation was executed during the current session. If no such invocation was found, output the following non-blocking warning to the conversation:

> **Warning:** No `edit-context.py` invocation was logged in this session. Verify that `context.md` updates are not required for this request.

Do not halt; do not block request close. This is informational only.

Step 8.6 — Update writable extensions: After the context update task completes, process every managed Reference entry in convention-defined order. Compare Update case-insensitively. For `Update: yes`, execute the prompt at the registered `Prompt:` path and let that prompt update and validate its registered extension. For `Update: no`, skip the entry. For a missing Location, Convention, or Prompt artifact, emit `WARNING: Registered context extension artifact missing: <path>. Continuing without this artifact.` and continue. Legacy true/false and other values are invalid and MUST be corrected through context verification before request close.

Step 8.7 — Append ADR and requirements entries: Execute `.aib_brain/prompts/aib-update-adr-requirements.md` with activity tag `[A]`. Pass the current `## Input` text and the implementation notes gathered during Steps 5–8 as inputs. The subroutine appends new user requirements to `.aib_memory/requirements.md` and new architecture / design decisions to `.aib_memory/adr.md`, applying its own row schema, UTC timestamp, deduplication rule, and retry-once-then-halt failure semantics as defined in `.aib_brain/conventions/adr-requirements-convention.md`. On a second-attempt failure inside the subroutine, halt this prompt and do NOT proceed to Step 9.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 8.7 aib-update-adr-requirements invocation started"` before delegation and `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 8.7 aib-update-adr-requirements invocation complete"` after successful return.

Step 8.8 — Inspect protected touched paths: After tests and all successful implementation-side updates, filter [Run-Touched-Paths] for `.aib_brain/**`. If the filtered list is non-empty and [Brain-Authorization] is `Not authorized`, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by every exact protected path in deterministic sorted order, then HALT before Step 9. Do not finalize, close, or automatically revert any path. Preserve and do not report unrelated pre-existing changes.

Step 9: Archive input.md, move active-request artifacts to the request subfolder, and auto-close the request by invoking (in this exact order):

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 9 Request close initiated: <request_id>"`.

  ```
  python -B .aib_brain/tools/finalize-input.py --workspace .
  python -B .aib_brain/tools/move-request-artifacts.py --workspace .
  python -B .aib_brain/tools/close-request.py --workspace .
  ```
> Rules:
> `finalize-input.py` archives the current input.md state into the request folder before reset; it is a no-op when input.md is stub-equivalent.
> The move step MUST be executed before `close-request.py`.
> MUST: Only invoke these scripts after the implementation is confirmed successful (no unresolved test failures or blockers).

Step 11. MUST confirm at the very end of the conversation with the text "--- I am done with the implementation  of `<request_id>` ---" that all your activities are finished

> Rules:
> Do not add additional text after "--- I am done with the implementation of `<request_id>` ---" line. MUST: If needed to be written somenting in the output chat - do it before this line.

## Rules

### Execution requirements:

- Must not read the Analysis
- Editing `context.md` via the Python scripts as directed by plan task instructions is permitted.
- MUST NOT read `input-archive-*.md` files from any request folder.
- MUST NOT read or reference any file inside `.aib_memory/requests/<folder>/` that belongs to a Closed request. This covers all artifact types (analysis, plan, implementation, input archives, and any other file). A request folder is Closed when its folder name does not begin with the active `request_id` (read from the input.md YAML header in Step 2), or when the YAML header `state == idle`. If in doubt, treat the folder as Closed.


### Documentation reading requirements:

- Read `.aib_brain/conventions/context-convention.md` (authoritative convention for `.aib_memory/context.md`) before editing `.aib_memory/context.md` or any other documentation file. If the convention file cannot be read, DO NOT edit `.aib_memory/context.md`.
- After any modification to `.aib_memory/context.md` (whether via `edit-context.py` or direct edit), invoke `python -B .aib_brain/tools/verify-context.py --workspace .` to validate format compliance. If the verification script exits with code 1, correct the deviations before proceeding.

### Coding convention requirements:

- UNCONDITIONALLY read `.aib_brain/conventions/coding-general-convention.md` before generating or editing any source-code file.
- CONDITIONALLY read the language-specific convention file based on the file extensions being created or edited, according to the table below. Read the convention file before generating code for that language.

| File extension(s)            | Convention file to read                                        |
| ---------------------------- | -------------------------------------------------------------- |
| `.py` (non-framework)        | `.aib_brain/conventions/coding-python-convention.md`          |
| `.py` (Flask app)            | `.aib_brain/conventions/coding-python-convention.md` AND `.aib_brain/conventions/coding-flask-convention.md` |
| `.py` (Django app)           | `.aib_brain/conventions/coding-python-convention.md` AND `.aib_brain/conventions/coding-django-convention.md` |
| `.dax`                       | `.aib_brain/conventions/coding-dax-convention.md`             |
| `.sql`                       | `.aib_brain/conventions/coding-sql-convention.md`             |
| `.html`, `.htm`              | `.aib_brain/conventions/coding-html-convention.md`            |
| `.js`, `.mjs`, `.cjs`        | `.aib_brain/conventions/coding-javascript-convention.md`      |
| `.jsx`                       | `.aib_brain/conventions/coding-javascript-convention.md` AND `.aib_brain/conventions/coding-react-convention.md` |
| `.tsx`                       | `.aib_brain/conventions/coding-javascript-convention.md` AND `.aib_brain/conventions/coding-react-convention.md` |
| `.css`, `.scss`, `.sass`, `.less` | `.aib_brain/conventions/coding-css-convention.md`        |
| `.cs`                        | `.aib_brain/conventions/coding-csharp-convention.md`          |
| `.scala`                     | `.aib_brain/conventions/coding-scala-convention.md`           |
| UI/UX design files (`.html`, `.css`, `.jsx`, `.tsx` with design intent) | `.aib_brain/conventions/coding-uiux-convention.md` (in addition to the language convention) |

- Apply all rules from the loaded convention file(s) to every file created or edited in the current implement run.


### Safety requirements:
- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.
- If nothing else specified, add tests in the folder of the request
- Do not create Python virtual environment unless explicitely specified in the request or in plan or in the documentation
- Do not install any additional libraries or third party software  unless explicitely specified in the request or in plan or in the documentation



