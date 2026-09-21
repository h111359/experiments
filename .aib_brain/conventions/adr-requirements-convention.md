# ADR / Requirements Convention

**Scope:** Normative
**Applies to:** `.aib_memory/adr.md` — append-only architecture-decision
history — and `.aib_memory/requirements.md` — append-only user-requirements
history.
**Enforced by:** `.aib_brain/prompts/aib-update-adr-requirements.md` (the
sole writer) and by the three caller prompts `aib-implement.md`,
`aib-modify.md`, and `aib-execute.md` that invoke it.

Normative keywords **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, and **MAY**
are interpreted per BCP 14 (RFC 2119 / RFC 8174).

---

## 1. Purpose

`.aib_memory/requirements.md` and `.aib_memory/adr.md` are append-only
Markdown files that together form the durable, per-workspace record of:

- **`requirements.md`** — the user requirements observed across the request
  lifecycle. One row per requirement.
- **`adr.md`** — the architecture / design decisions made by AIB prompts on
  top of the user requirements while implementing requests. One row per
  decision.

These files are maintained by the shared subroutine prompt
`.aib_brain/prompts/aib-update-adr-requirements.md`, which is invoked as
the last documentation step of every implementation-oriented prompt run
(`aib-implement.md`, `aib-modify.md`, `aib-execute.md`).

---

## 2. Row Schema (verbatim)

Every row in both files MUST match the following schema, on a single line,
in UTF-8 Markdown:

```
- [YYYYMMDD-HHMMSS-<request_id>] [<TAG>] <text>
```

Field definitions:

- `YYYYMMDD-HHMMSS` — timestamp in **UTC**, 24-hour, no separators, exactly
  15 characters (8 date + 1 dash + 6 time).
- `<request_id>` — the currently active AIB request identifier resolved
  from the `input.md` YAML header at the moment the row is appended.
- `<TAG>` — a single provenance tag from the registry in Section 3,
  enclosed in square brackets.
- `<text>` — a single-line description of the requirement or decision.
  MUST NOT contain embedded newlines. SHOULD be a complete, self-contained
  statement.

Rows are appended one per line. Each file ends with a trailing newline.

---

## 3. Provenance Tag Registry

The `<TAG>` field encodes which caller prompt appended the row. The
registry is:

| Tag  | Caller prompt         | Meaning                                                 |
| ---- | --------------------- | ------------------------------------------------------- |
| `A`  | *(legacy)*            | Pre-registry rows appended before this convention. Immutable. |
| `I`  | `aib-implement.md`    | Row appended during a plan-driven implementation run.   |
| `M`  | `aib-modify.md`       | Row appended during a direct-execution modify run.      |
| `E`  | `aib-execute.md`      | Row appended during a direct-execution + context-updating run. |

Rules:

- Legacy `[A]`-tagged rows MUST remain untouched. They are historically
  valid and MUST NOT be modified, retagged, or removed.
- Adding a new tag to the registry requires an update to this convention
  and to `.aib_brain/prompts/aib-update-adr-requirements.md`.
- Rows with a tag not listed in this registry are PROHIBITED.

---

## 4. Timestamp

The `YYYYMMDD-HHMMSS` timestamp MUST be captured in Coordinated Universal
Time (UTC) at the moment the row is written. Local-time or unspecified-zone
timestamps are PROHIBITED.

---

## 5. Deduplication Rule

Before appending any candidate row, the writer MUST extract the row's
`<text>` portion (the substring after the second `] ` delimiter) and
compare it against the `<text>` portion of every existing row in the
target file, using the following normalization:

- Trim leading and trailing whitespace.
- Collapse any run of consecutive whitespace (spaces, tabs, newlines) to a
  single space.
- Compare case-insensitively.

If a normalized match already exists anywhere in the target file — including
matches against legacy `[A]`-tagged rows — the candidate row MUST be skipped.
Otherwise the candidate row MUST be appended.

Dedup is scoped to the target file only. `requirements.md` and `adr.md` are
compared independently; a match in one file does NOT prevent an append to the
other.

---

## 6. Failure Semantics

On any I/O or write failure while appending, the writer MUST:

1. Retry the append ONCE immediately, without delay.
2. If the retry also fails, HALT the calling prompt with a clear error
   identifying the failing file and the underlying I/O error, and MUST NOT
   proceed to finalize / move / close the request.

---

## 7. Append-Only Invariant

`.aib_memory/adr.md` and `.aib_memory/requirements.md` are append-only.

- Rewriting, editing, reformatting, reordering, or deleting historical rows
  is PROHIBITED, regardless of tag.
- The writer MUST always append to the end of the file; it MUST NOT insert
  rows in the middle or at the top.
- Automated tooling and manual edits both MUST respect this invariant.

---

## 8. References

- Sole writer prompt: `.aib_brain/prompts/aib-update-adr-requirements.md`.
- Caller prompts: `.aib_brain/prompts/aib-implement.md`,
  `.aib_brain/prompts/aib-modify.md`,
  `.aib_brain/prompts/aib-execute.md`.
