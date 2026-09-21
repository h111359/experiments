# Prompt: aib-update-adr-requirements

## Goal

Subroutine prompt that appends new user-requirement rows to
`.aib_memory/requirements.md` and new architecture-decision rows to
`.aib_memory/adr.md`. Invoked as the final documentation step by the three
caller prompts: `aib-implement.md`, `aib-modify.md`, and `aib-execute.md`.

The authoritative schema for the appended rows is
`.aib_brain/conventions/adr-requirements-convention.md`. That convention
governs the row format, the provenance-tag registry, the timestamp format,
the deduplication rule, and the append-only invariant.

## Inputs (from the calling prompt)

- **Caller identifier**: exactly one of `aib-implement.md`, `aib-modify.md`,
  or `aib-execute.md`. Determines the provenance tag written into every row
  appended in the current invocation:
  - tag `[A]`: means the entry is active
  - tag `[D]`: means the entry is deprecated
- **Current `## Input` text**: the full body of the `## Input` section from
  `.aib_memory/input.md` at the moment the caller invokes this subroutine.
- **Implementation notes**: any decisions the caller made while implementing
  the request that are NOT already visible from other workspace files.

## Process

Step 1 — Log start:

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-update-adr-requirements: start caller=<caller-id>"`.

Step 2 — Resolve active request:

Run `python -B .aib_brain/tools/input-header.py --workspace . --operation read`
and parse `state` and `request_id`.

- If `state == idle` OR `request_id` is `~`: halt immediately with the
  literal error:
  `ERROR: aib-update-adr-requirements requires an active request. State is idle; no request_id available.`
  Do NOT proceed to close on the calling prompt.

Step 3 — Ensure target files exist:

Ensure both `.aib_memory/requirements.md` and `.aib_memory/adr.md` exist. If
either is absent, create the missing file as an empty UTF-8 Markdown file
(no header, no seed content).

Step 4 — Extract new user requirements:

From the caller-supplied `## Input` text, identify each new user requirement
statement — a MUST / MUST NOT / OPTIONAL directive, a Scope In / Scope Out
item, an assumption, or an acceptance criterion — that expresses **user
intent** and is NOT already recorded in `requirements.md`.

Do NOT include architecture or design decisions here. Those belong to the
ADR extraction step below.

Step 5 — Extract new architecture / design decisions:

From the caller-supplied implementation notes, identify each new architecture
or design decision the caller made **on top of** the user requirements while
implementing this request, that is NOT already visible from other workspace
files (source code, plan, analysis, context.md, or previous ADR rows).

Do NOT include user requirements here. Those belong to `requirements.md`.

Step 6 — Apply the row schema:

For every extracted item (from Step 4 or Step 5), format a single-line row
according to `.aib_brain/conventions/adr-requirements-convention.md`:

```
- [YYYYMMDD-HHMMSS-<request_id>] [<TAG>] <text>
```

Where:
- `YYYYMMDD-HHMMSS` is the current time in UTC.
- `<request_id>` is the active request ID resolved in Step 2.
- `<TAG>` is the provenance tag mapped from the caller identifier in
  Step 0 (Inputs): `[A]`, or `[D]`.
- `<text>` is a single-line statement (no embedded newlines) describing the
  requirement or the decision.

Step 7 — Deduplicate against existing rows:

For every candidate row, extract its `<text>` portion, normalize it by
collapsing consecutive whitespace and lower-casing, and compare against the
normalized `<text>` portion of every existing row in the target file (any
tag, including legacy `[A]`). If a normalized match already exists in the
target file, SKIP the candidate row. Otherwise, retain it for append.

Step 8 — Append with retry-once-then-halt semantics:

Append the retained rows to their target files (`requirements.md` for the
Step 4 items, `adr.md` for the Step 5 items). Preserve trailing newlines.

On any I/O or write failure:
- Retry the append ONCE immediately, without delay.
- If the retry also fails, HALT the calling prompt with a clear error
  identifying the failing file and the underlying I/O error. Do NOT proceed
  to close on the calling prompt.

Step 9 — Log completion:

Run `python -B .aib_brain/tools/log-entry.py --workspace . --message "aib-update-adr-requirements: complete caller=<caller-id> requirements+=<n_req> adr+=<n_adr>"`.

## Rules

- MUST NOT modify or delete any existing row in `requirements.md` or
  `adr.md`. Legacy `[A]`-tagged rows are preserved byte-identically.
- MUST NOT append rows to any file other than the two target files.
- MUST use UTC for the timestamp.
- MUST apply the caller-mapped provenance tag exactly. Rows with an
  unmapped tag are PROHIBITED.
- MUST reference `.aib_brain/conventions/adr-requirements-convention.md`
  as the authoritative schema; if the two documents diverge, the convention
  wins.
- MUST NOT emit `edit-context.py` invocations. Product-context updates are
  the responsibility of the calling prompt.
- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.

## Modifier flags

- This prompt has no modifier flags; it operates in a single execution mode.
