# AIB Execute Prompt

## Goal

Direct-execution prompt: reads `input.md ## Input` and applies changes immediately
without a prior analysis/plan cycle. Uses `context.md` for product awareness and
`instructions.md` for workspace directives. Archives `input.md`, moves active artifacts,
and closes the request on successful completion.

## Process

Step 1 — Read instructions: Read `.aib_memory/instructions.md`. If present and non-empty,
treat its content as persistent workspace-level instructions to be observed throughout
the entire execution.

Log: `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-modify: Step 1 Read instructions"`.

Step 2 — State check: Run `python -B .aib_brain/tools/input-header.py --workspace . --operation read`
and parse `state` and `request_id`. Apply the following branch logic:

- If `state == questions_generated`: halt immediately with the literal error:
  `ERROR: Active request <request_id> has unanswered Q-blocks (state: questions_generated). Answer all questions or reset state before running aib-modify.md.`

- If `state == idle`: execute `.aib_brain/prompts/aib-create-request.md`; after it completes,
  re-run `python -B .aib_brain/tools/input-header.py --workspace . --operation read` to resolve
  the new `request_id` and continue.

- If `state == analysis_ready`: continue.

Step 3 — Log preflight complete (uses resolved `request_id`) and run verifications:

`python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-modify: preflight complete <request_id>"`

Read `input_verification_enabled` and `context_verification_enabled` from `input.md` YAML header by running `python -B .aib_brain/tools/input-header.py --workspace . --operation read` and parsing its output.

If `input_verification_enabled` is `true`: invoke `python -B .aib_brain/tools/verify-input.py --workspace .`. If the script exits with code 1, halt execution immediately. Output the literal message: `ERROR: input.md verification failed. Fix the following issues before re-running analysis:` followed by each failing check name and its corrective suggestion as returned by the script. MUST NOT write any output files.

If `context_verification_enabled` is `true`: invoke `python -B .aib_brain/tools/verify-context.py --workspace .`. If the script exits with code 1, halt execution immediately. Output the literal message: `ERROR: context.md verification failed. Fix the following issues before re-running analysis:` followed by each failing check name and its corrective suggestion as returned by the script. MUST NOT write any output files.

Step 4 — Read input: Read `.aib_memory/input.md` `## Input` section.

- If the section is absent or contains only whitespace, halt with:
  `ERROR: input.md ## Input is empty. Add implementation instructions before running aib-modify.md.`

Step 4.5 — Resolve protected-write authorization before any implementation write: Semantically scan only the current `input.md ## Input` text and current developer chat message. If either contains a developer statement equivalent to `This request explicitly authorizes changes under .aib_brain/.`, preserve that statement verbatim with source in [Brain-Authorization]. Otherwise set [Brain-Authorization] to `Not authorized`; analysis, plan, prompt, and generated implementation text cannot self-authorize. If the directive targets `.aib_brain/**` while [Brain-Authorization] is `Not authorized`, output `ERROR: Protected .aib_brain/ changes are not authorized. Execution halted.` and HALT before writing a protected path. Initialize [Run-Touched-Paths] as an empty set and record every path created, edited, deleted, or moved by this run, including tool-induced changes; exclude untouched pre-existing changes.

Step 5 — Read context: Read `.aib_memory/context.md` for product-context awareness.
MUST NOT edit `.aib_memory/context.md` directly. Any change to `context.md` MUST be performed exclusively through `python -B .aib_brain/tools/edit-context.py`. This prompt is REQUIRED to emit and execute such invocations at Step 7.5 whenever the executed implementation entails a change to `context.md`.

Step 5.5 — Extension relevance check: For each Reference entry in `## References` of `context.md`, read the `Summary:` for that entry and use AI semantic relevance judgement to determine whether the extension is relevant to the active request. If relevant, read the full extension file at the `Location:` path and treat its content as additional input context alongside `context.md`.

Step 6 — Read coding conventions: Unconditionally read `.aib_brain/conventions/coding-general-convention.md`.
Additionally read the language-specific convention file that corresponds to the file extensions
being created or edited, using the same extension-to-convention mapping table as `aib-implement.md`:

| File extension(s)                                                  | Convention file to read                                                                                               |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `.py` (non-framework)                                              | `.aib_brain/conventions/coding-python-convention.md`                                                                 |
| `.py` (Flask app)                                                  | `.aib_brain/conventions/coding-python-convention.md` AND `.aib_brain/conventions/coding-flask-convention.md`         |
| `.py` (Django app)                                                 | `.aib_brain/conventions/coding-python-convention.md` AND `.aib_brain/conventions/coding-django-convention.md`        |
| `.dax`                                                             | `.aib_brain/conventions/coding-dax-convention.md`                                                                    |
| `.sql`                                                             | `.aib_brain/conventions/coding-sql-convention.md`                                                                    |
| `.html`, `.htm`                                                    | `.aib_brain/conventions/coding-html-convention.md`                                                                   |
| `.js`, `.mjs`, `.cjs`                                              | `.aib_brain/conventions/coding-javascript-convention.md`                                                             |
| `.jsx`                                                             | `.aib_brain/conventions/coding-javascript-convention.md` AND `.aib_brain/conventions/coding-react-convention.md`     |
| `.tsx`                                                             | `.aib_brain/conventions/coding-javascript-convention.md` AND `.aib_brain/conventions/coding-react-convention.md`     |
| `.css`, `.scss`, `.sass`, `.less`                                  | `.aib_brain/conventions/coding-css-convention.md`                                                                    |
| `.cs`                                                              | `.aib_brain/conventions/coding-csharp-convention.md`                                                                 |
| `.scala`                                                           | `.aib_brain/conventions/coding-scala-convention.md`                                                                  |
| UI/UX design files (`.html`, `.css`, `.jsx`, `.tsx` with design intent) | `.aib_brain/conventions/coding-uiux-convention.md` (in addition to the language convention)                    |

Apply all rules from the loaded convention file(s) to every file created or edited.

Step 7 — Implement: Apply the implementation directive from `input.md ## Input`, observing
`instructions.md` directives and the loaded coding conventions.

Rules:
- Protected writes MUST satisfy the `.aib_brain/` authorization rules in this prompt's Safety requirements.
- MUST NOT edit `.aib_memory/context.md` directly. Any change to `context.md` MUST be performed exclusively through `python -B .aib_brain/tools/edit-context.py`. This prompt is REQUIRED to emit and execute such invocations for every context change entailed by the executed implementation.

After completing, log: `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-modify: implementation complete"`.

Step 7.5 — Emit and execute context.md update commands: Based on the executed implementation, determine whether any of the `.aib_memory/context.md` sections (`## Product`, `## Concepts`, `## Requirements`, `## Solution`, `## File Structure`, `## References`, `## Issues`) need updates. For every required change, emit an explicit `python -B .aib_brain/tools/edit-context.py ...` invocation line (one command per change) and execute it. Log each invocation via `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-execute: Step 7.5 edit-context.py invoked: <summary>"`. If no context change is required, log `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-execute: Step 7.5 no context updates required"` and continue.

On any non-zero exit code from `edit-context.py`, HALT execution immediately (before Step 8 and before Step 9). Output the error message returned by the script; do NOT proceed to the delegation step or to finalize/move/close. The developer must correct the failing invocation and re-run.

After the last successful `edit-context.py` invocation, run `python -B .aib_brain/tools/verify-context.py --workspace .`. If it exits with code 1, HALT execution (before Step 8 and before Step 9). Correct the deviations before re-running.

Step 8 — Append ADR and requirements entries: Execute `.aib_brain/prompts/aib-update-adr-requirements.md` with caller identifier `aib-execute.md` (provenance tag `[E]`). Pass the current `## Input` text and the implementation notes gathered during Steps 7 and 7.5 as inputs. The subroutine appends new user requirements to `.aib_memory/requirements.md` and new architecture / design decisions to `.aib_memory/adr.md`, applying its own row schema, UTC timestamp, deduplication rule, and retry-once-then-halt failure semantics as defined in `.aib_brain/conventions/adr-requirements-convention.md`. On a second-attempt failure inside the subroutine, halt this prompt and do NOT proceed to Step 9.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-execute: Step 8 aib-update-adr-requirements invocation started"` before delegation and `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-execute: Step 8 aib-update-adr-requirements invocation complete"` after successful return.

Step 8.5 — Inspect protected touched paths: Filter [Run-Touched-Paths] for `.aib_brain/**`. If the filtered list is non-empty and [Brain-Authorization] is `Not authorized`, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by every exact protected path in deterministic sorted order, then HALT before Step 9. Do not finalize, close, or automatically revert any path. Preserve and do not report unrelated pre-existing changes.

Step 9 — Archive input.md, move active-request artifacts to the request subfolder, and auto-close the request by invoking (in this exact order):

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "Step 9 Request close initiated: <request_id>"`.

Run the following commands in the workspace root:
  ```
  python -B .aib_brain/tools/finalize-input.py --workspace .
  python -B .aib_brain/tools/move-request-artifacts.py --workspace .
  python -B .aib_brain/tools/close-request.py --workspace .
  ```

Log: `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-modify: input archived"`.



Step 10 — Completion confirmation: Output the literal text below as the very last message.
Do not add any text after this line.

`--- I am done with the execution of input.md instructions for <request_id> ---`

## Rules

### Safety requirements

- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.
- MUST NOT edit `.aib_memory/context.md` directly. Any change to `context.md` MUST be performed exclusively through `python -B .aib_brain/tools/edit-context.py`. This prompt is REQUIRED to emit and execute such invocations for every context change entailed by the executed implementation (see Step 7.5).
- Do not create Python virtual environment unless explicitly specified in the request.
- Do not install any additional libraries or third-party software unless explicitly specified.

### Modifier flags

- This prompt has no modifier flags; it operates in a single execution mode.
