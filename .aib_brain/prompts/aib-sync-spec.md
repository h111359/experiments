# Prompt: aib-sync-spec

## Objective

Synchronise `.aib_memory/context.md` with an external specification file. Auto-creates an AIB request, parses the spec at sentence level, generates one Q-block per detected contradiction, and adds non-contradictory AI-classified future-intent items as `[PLANNED]` entries in `context.md`.

---

## Variables

- `[SpecPath]` — string; path to the external specification file, read from `input.md ## Input`.
- `[ContradictionList]` — list; sentences from the spec that contradict existing `context.md` statements.
- `[NonContradictoryFuture]` — list; sentences classified as future-intent not in contradiction.
- `[NonContradictoryCurrent]` — list; sentences classified as current-state not in contradiction.

---

## Global Rules

- **GC-01 — No archive reads:** `input-archive-*.md` files MUST NOT be read or referenced.
- **GC-02 — Halt on missing mandatory files:** If any mandatory file cannot be read, halt with an explicit error message identifying the file.
- **GC-03 — No partial writes on halt:** When execution halts, MUST NOT write any output files.
- **GC-04 — Convention compliance:** All `context.md` edits MUST comply with `context-convention.md`.
- **GC-05 — edit-context.py error is fatal:** Any `edit-context.py` call that exits non-zero halts execution immediately.

---

## Inputs

| Source | Description |
| --- | --- |
| `.aib_memory/input.md` | `## Input` must contain the path to the external spec file |
| `.aib_memory/context.md` | Workspace product context (mandatory) |
| `.aib_brain/conventions/context-convention.md` | Authoritative format rules for `context.md` |
| `.aib_memory/instructions.md` | Persistent workspace-level directives (optional) |
| External spec file at `[SpecPath]` | The specification to synchronise against |

## Outputs

| Artifact | Location | Description |
| --- | --- | --- |
| `context.md` (updated) | `.aib_memory/context.md` | New `[PLANNED]` entries and plain entries inserted |
| `input.md` (updated) | `.aib_memory/input.md` | Q-blocks added to `## Questions` on first run with contradictions; archived on completion |

---

## Execution Procedure

### Phase 1 — Preflight

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 1 started"`.

1. Read `.aib_memory/instructions.md`. If present and non-empty, observe its content as persistent workspace-level instructions throughout execution.

2. Read `.aib_brain/conventions/context-convention.md`. This is the authoritative source for `context.md` format rules.

3. Read `.aib_memory/context.md`. If absent, halt with:
   `ERROR: context.md not found. Run aib-refresh-context.md first. Execution halted.`

4. Execute `.aib_brain/prompts/aib-context-read.md` with the specification-synchronization goal and treat its returned extension contents as supplementary context. Do not independently parse or load Reference entries.

5. Read `.aib_memory/input.md` YAML header via `python -B .aib_brain/tools/input-header.py --workspace . --operation read`.
   - If `## Input` is empty or contains only whitespace, halt with:
     `ERROR: No spec file path provided in input.md ## Input. Add the path and re-run.`
   - Set `[SpecPath]` to the content of `## Input` (trimmed).
   - If `status == idle`: invoke `.aib_brain/prompts/aib-create-request.md` to auto-create an AIB request. After creation completes, re-read the YAML header to resolve the `request_id`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 1 complete"`.

---

### Phase 2 — Spec Read

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 2 started"`.

1. Read the full content of the file at `[SpecPath]`. If the file does not exist or cannot be read, halt with:
   `ERROR: Spec file not found or unreadable at path: [SpecPath]. Execution halted.`

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 2 complete"`.

---

### Phase 3 — Sentence-Level Extraction

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 3 started"`.

1. Split the spec content into individual sentences (sentence boundary detection).
2. For each sentence, evaluate whether it contains a product-relevant statement that could be mapped to a `context.md` section (Product, Concepts, Requirements, Solution).
3. Discard sentences that are purely structural (headings, metadata, formatting) with no product content.
4. Retain all product-relevant sentences for contradiction detection and classification.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 3 complete"`.

---

### Phase 4 — Contradiction Detection

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 4 started"`.

1. For each retained sentence, compare against existing `context.md` statements.
2. A **contradiction** exists when the extracted sentence directly conflicts with an existing statement (not merely when it is new or supplementary).
3. Collect all detected contradictions into `[ContradictionList]`. For each contradiction record: the spec sentence, the conflicting `context.md` statement, and the section where the conflict occurs.
4. Separate non-contradictory sentences and classify each as:
   - **Future-intent:** AI judges the sentence describes a feature not yet present in the workspace → add to `[NonContradictoryFuture]`.
   - **Current-state fact:** AI judges the sentence describes a currently implemented fact → add to `[NonContradictoryCurrent]`.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 4 complete"`.

---

### Phase 5 — Q-block Generation (first run with contradictions)

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 5 started"`.

If `[ContradictionList]` is non-empty AND `input.md` YAML header `status != questions_generated`:

1. For each contradiction in `[ContradictionList]`, generate one Q-block in `input.md ## Questions` with:
   - The contradiction description (spec sentence and conflicting `context.md` statement).
   - Reference: the spec file path and the sentence location (sentence index or excerpt).
   - Options (mutually exclusive checkboxes):
     - `[ ] Keep existing context statement` *(recommended)*
     - `[ ] Adopt spec version`
     - `[ ] Merge both (describe merge intent in Answer: field)`
     - `[ ] Skip (do not update context.md for this item)`

2. Run `python -B .aib_brain/tools/input-header.py --workspace . --operation write --state questions_generated`.

3. Halt with:
   `Note: [N] contradiction(s) detected between spec and context.md. Q-blocks written to input.md ## Questions. Answer all questions and re-run aib-sync-spec.md to apply non-contradictory items and resolve contradictions.`

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 5 Q-blocks generated"`.

If `[ContradictionList]` is empty OR `status == questions_generated` (answers provided), proceed to Phase 6.

---

### Phase 6 — Apply Non-Contradictory Items and Contradiction Resolutions

> **Precondition:** All Q-blocks in `input.md ## Questions` must be answered before this phase executes. If any Q-block is unanswered, halt with:
> `ERROR: Unanswered Q-blocks in input.md ## Questions. Answer all questions and re-run.`

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 6 started"`.

1. **Apply non-contradictory future-intent items:** For each sentence in `[NonContradictoryFuture]`, determine the best-fit `context.md` section (Product, Concepts, Requirements, Solution) and run:
   `python -B .aib_brain/tools/edit-context.py --operation insert --area <section> --planned --text "<statement>" --workspace .`
   If the call exits non-zero, halt immediately.

2. **Apply non-contradictory current-state items:** For each sentence in `[NonContradictoryCurrent]`, determine the best-fit `context.md` section and run:
   `python -B .aib_brain/tools/edit-context.py --operation insert --area <section> --text "<statement>" --workspace .`
   If the call exits non-zero, halt immediately. (Duplicate statements are silently skipped by `edit-context.py`.)

3. **Apply contradiction resolutions:** For each answered contradiction Q-block:
   - If `Keep existing`: no action.
   - If `Adopt spec version`: delete the existing statement and insert the spec version.
     - `python -B .aib_brain/tools/edit-context.py --operation delete --area <section> --text "<existing statement>" --workspace .`
     - `python -B .aib_brain/tools/edit-context.py --operation insert --area <section> --text "<spec statement>" --workspace .`
   - If `Merge both`: insert a merged statement (preserving both intents) and optionally delete the old one.
   - If `Skip`: no action.

4. After all edits, run `python -B .aib_brain/tools/verify-context.py --workspace .`. If it exits with code 1, correct deviations before proceeding.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 6 complete"`.

---

### Phase 7 — Completion

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 7 started"`.

1. Run `python -B .aib_brain/tools/finalize-input.py --workspace .` to archive `input.md` and reset to seed template.
2. Output a completion summary: number of `[PLANNED]` entries added, number of plain entries added, number of contradiction resolutions applied.

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-sync-spec Phase 7 complete"`.

---

## Safety

- The only permitted write targets are `.aib_memory/context.md` and `.aib_memory/input.md`.
- MUST NOT create files outside `.aib_memory/`.
- All `edit-context.py` invocations that exit non-zero cause an immediate halt.
- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.
