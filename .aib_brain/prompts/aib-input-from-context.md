# Prompt: aib-input-from-context

## Objective

Read all `[PLANNED]` entries and Issues from `context.md` and append structured goal bullets to `input.md ## Input`. Fails with an error if an active request already exists.

---

## Variables

- `[PlannedEntries]` — list; statements prefixed with `[PLANNED]` found in Product, Concepts, Solution, and Requirements sections of `context.md`.
- `[IssueEntries]` — list; plain bullet entries found in the `## Issues` section of `context.md`.
- `[GoalBullets]` — list; formatted goal bullets to append to `input.md ## Input`.

---

## Global Rules

- **GC-01 — Active request guard:** If an active request exists (`status != idle`), halt immediately with an error. This prompt is intentionally designed for use only when no active request is open.
- **GC-02 — No write on halt:** When execution halts due to any error condition, MUST NOT write any output files.
- **GC-03 — Append only:** MUST append to `## Input`; must not overwrite or truncate any existing content in that section.

---

## Inputs

| Source | Description |
| --- | --- |
| `.aib_memory/input.md` | Active-request state check; target for appended goal bullets |
| `.aib_memory/context.md` | Source of `[PLANNED]` entries and `## Issues` bullets |
| `.aib_memory/instructions.md` | Persistent workspace-level directives (optional) |

## Outputs

| Artifact | Location | Description |
| --- | --- | --- |
| `input.md` (updated) | `.aib_memory/input.md` | Goal bullets appended to `## Input` section |

---

## Execution Procedure

### Step 1 — Preflight

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 1 started"`.

1. Read `.aib_memory/instructions.md`. If present and non-empty, observe its content as persistent workspace-level instructions throughout execution.

2. Run `python -B .aib_brain/tools/input-header.py --workspace . --operation read`. Parse `status` and `request_id` from the output.

3. If `status != idle`, halt with:
   `ERROR: Active request <request_id> already exists (status: <status>). Close the current request before running aib-input-from-context.md.`

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 1 complete"`.

---

### Step 2 — Read Context and Extensions

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 2 started"`.

1. Read `.aib_memory/context.md`. If absent, halt with:
   `ERROR: context.md not found. Run aib-refresh-context.md first. Execution halted.`

2. Execute `.aib_brain/prompts/aib-context-read.md` with the goal-collection task and treat its returned extension contents as supplementary context. Do not independently parse or load Reference entries.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 2 complete"`.

---

### Step 3 — Collect [PLANNED] Entries

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 3 started"`.

1. Scan the four sections that permit the tag (Product, Concepts, Requirements, and Solution) for statements beginning with `- [PLANNED]`.
2. For each matching statement, strip the `[PLANNED] ` prefix and record the remaining text in `[PlannedEntries]`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 3 complete"`.

---

### Step 4 — Collect Issues Entries

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 4 started"`.

1. Scan the `## Issues` section of `context.md` for all plain bullet entries.
2. For each entry, record the description text (after stripping the `- ` prefix) in `[IssueEntries]`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 4 complete"`.

---

### Step 5 — Generate Goal Bullets

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 5 started"`.

1. For each entry in `[PlannedEntries]`, format as:
   `- Implement: <statement text>`

2. For each entry in `[IssueEntries]`, format as:
   `- Resolve issue: <description>`

3. Collect all formatted lines into `[GoalBullets]`.

4. If `[GoalBullets]` is empty, output:
   `Note: No [PLANNED] entries or Issues found in context.md. Nothing to append.`
   Exit without modifying `input.md`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 5 complete"`.

---

### Step 6 — Append to Input

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 6 started"`.

1. Read the current content of `.aib_memory/input.md`.
2. Locate the `## Input` section.
3. Append all lines from `[GoalBullets]` after any existing content in `## Input`. Preserve existing content.
4. Write the updated content back to `.aib_memory/input.md`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 6 complete"`.

---

### Step 7 — Confirmation

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-input-from-context Step 7 complete"`.

Output a confirmation message:
`Appended <N> goal bullets to input.md ## Input (<P> [PLANNED] entries, <I> Issues entries).`

Where `<N>` is the total count, `<P>` is the count from `[PlannedEntries]`, and `<I>` is the count from `[IssueEntries]`.

---

## Safety

- The only permitted write target is `.aib_memory/input.md`.
- MUST NOT modify `context.md`.
- MUST NOT create files outside `.aib_memory/`.
- MUST append to existing `## Input` content; never overwrite.
- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.
