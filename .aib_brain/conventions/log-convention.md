# Log Convention

**Scope:** Normative
**Applies to:** `.aib_memory/log.md` (shared active runtime log) and
`<request-folder>/log_<request_id>.md` (per-request close-time archive).
The shared archival lifecycle also applies to clarification history as specified
in section 9; runtime entry formatting applies only to the runtime log.
**Enforced by:** `.aib_brain/tools/log-entry.py` and
`.aib_brain/tools/move-request-artifacts.py`.

---

## 1. Purpose

Single append-only audit trail for AIB prompt-execution events. `log-entry.py`
is a state-independent appender: it writes to one shared active log at
`.aib_memory/log.md` regardless of whether a request is active. At request
closure the complete stream is archived into
`<request-folder>/log_<request_id>.md` so the full chronological history —
including pre-request activity — is preserved under the closing request's
identifier.

---

## 2. Files

- Active log: `.aib_memory/log.md`. Created lazily on the first
  `log-entry.py` invocation when absent. Left empty (present, zero-length)
  after each successful close-time archival.
- Per-request archive: `<request-folder>/log_<request_id>.md`. Created by
  `move-request-artifacts.py` during request closure.
- Staging snapshot: `.aib_memory/log-staging-<request_id>.md`. Transient file
  used during rename-to-staging archival; retained after a failed transaction
  until a later invocation recovers it.

Both the active log and the per-request archive MUST be regular non-symlink
files. Directories, symlinks, and other special file types at either path
block the archival transaction without modifying any file.

---

## 3. Entry Format

Each log entry MUST follow the format:

```
YYYYMMDD-HHmmss: <message>
```

- The timestamp MUST be UTC in 24-hour format.
- The timestamp format is `YYYYMMDD-HHmmss` (no separators within the date or
  time components).
- The message follows the timestamp separated by `: ` (colon and space).
- Each entry occupies exactly one line terminated by a newline character.

Example:

```
20260630-143022: S01 Preflight started
```

---

## 4. Append Semantics

- Each `log-entry.py` invocation appends exactly one line to
  `.aib_memory/log.md`.
- The active log is never truncated, overwritten, or cleared by
  `log-entry.py` or any prompt.
- If `.aib_memory/log.md` does not exist it is created on first invocation.
- `log-entry.py` also echoes the written entry to stdout.

---

## 5. Invocation

Every AIB prompt uses the same shared-stream invocation:

```
python -B .aib_brain/tools/log-entry.py --workspace . --message "<message>"
```

`log-entry.py` accepts only `--workspace` and `--message`. Any other option —
including the flag that historically routed writes to a separate general log —
is unrecognized and MUST be rejected by standard `argparse` handling with a
non-zero exit code and an "unrecognized arguments" message on stderr. No
compatibility shim or deprecation warning is emitted.

---

## 6. Close-Time Rotation

At request closure, `move-request-artifacts.py` archives the shared active
log into `<request-folder>/log_<request_id>.md` using the following
transaction:

1. Verify each existing managed path (`.aib_memory/log.md`, the staging
   snapshot, and the archive) is a regular non-symlink file. Fail closed on
   any other path type.
2. Drain any leftover `.aib_memory/log-staging-<request_id>.md` snapshot from
   an aborted prior run into the archive first, preserving chronological
   order.
3. When `.aib_memory/log.md` exists, `os.replace` it to the staging path so
   the active log becomes empty immediately for subsequent writes; then
   re-create an empty `.aib_memory/log.md`.
4. Open the archive in binary append mode. When the archive is non-empty, the
   staging snapshot is non-empty, and the archive's last byte is not `\n`,
   write exactly one `b"\n"` separator before the snapshot.
5. Stream the staging snapshot into the archive in binary mode using a
   bounded chunk buffer.
6. Call `os.fsync` on the archive file descriptor before closing it. Remove
   the staging snapshot only after `fsync` succeeds.

The transaction is idempotent across the explicit pre-close invocation from
`aib-implement.md` and the safety-net invocation from `close-request.py`:

- A missing `.aib_memory/log.md` plus an existing archive preserves its content
  and creates an empty active log.
- A missing `.aib_memory/log.md` with no prior archive creates an empty
  archive and an empty active log and does not error.
- A leftover staging snapshot from an aborted run is drained on the next
  call before returning success.

Delivery semantics are at-least-once: duplicated entries in the archive after
an ambiguous crash between `fsync` and staging-file removal are acceptable.

The workflow is single-writer: AIB prompt execution and request closure are
serialized by the caller. No cross-process lock is introduced.

---

## 7. Failure Semantics

- `move-request-artifacts.py` returns a distinguished non-zero exit code and
  prints a human-readable error on stderr when the log archival transaction
  fails, including path validation and I/O failures during rotation, append,
  flush, fsync, or staging cleanup.
- `close-request.py` fails closed on any log-archive error: it propagates a
  non-zero exit code, does not reset `input.md` state to idle, and does not
  archive the plan or analysis. The active request remains open so the audit
  trail remains attributable.
- Other artifact-move failures (plan, analysis) retain their existing
  warn-and-continue behaviour and MUST NOT block request closure.
- Pre-request logging failures are ordinary tool failures. Prompts MUST NOT
  suppress `log-entry.py` errors "because the active request has not yet
  been resolved"; the shared-log contract removes any such precondition.

---

## 8. Exclusions

The following files are out of scope for this convention and MUST NOT be
created, moved, deleted, or otherwise modified by `log-entry.py`,
`move-request-artifacts.py`, or `close-request.py`:

- Legacy `.aib_memory/log_general.md`.
- Pre-existing root-level `.aib_memory/log_<request_id>.md` files.
- CI-generated per-version release logs at `logs/version_v*.md`.

These files may remain in a workspace from earlier framework versions and
are preserved verbatim across the archival transaction.

---

## 9. Clarification History Lifecycle

- Active history: `.aib_memory/clarification_questions.md`, created directly by
  `aib-clarify.md` when it first records a question, even in idle state.
- Archive: `<request-folder>/clarification_questions_<request_id>.md`.
- Staging snapshot:
  `.aib_memory/clarification_questions-staging-<request_id>.md`.
- Question formatting, identifiers, responses, and revisions follow
  `q-block-convention.md`. This is a Markdown conversation history, not a
  UTC-prefixed runtime log. `log-entry.py` does not write to it, and other
  prompts do not begin logging questions here.
- Request creation, analysis, input archival, and input reset MUST preserve
  the complete active history. Only the existing request-artifact archival
  workflow rotates it; no previously recorded answers are migrated.
- `move-request-artifacts.py` archives the runtime log first and clarification
  history second, before moving plan or analysis files. Both streams use the
  same regular-file checks, rename-to-staging rotation, conditional-newline
  binary append, bounded streaming, fsync-before-cleanup, and single-writer
  contract from section 6. Existing archive bytes are preserved.
- After successful archival the active history MUST be present and empty.
  Missing or empty history succeeds and leaves empty active/archive files.
  Repeated successful pre-close and close safety-net calls append no duplicate
  content; entries added since the previous archival are appended in order.
- On history archival failure, both archival and closure return a non-zero
  exit code identifying `clarification-history-archive`. The request remains
  active and plan/analysis files remain in place. The runtime log may already
  have been archived successfully; its bytes remain recoverable there.
- Preserve recoverable root, staging, and archive content on failure. Correct
  the underlying failure and rerun the archival/closure command; the next call
  drains leftover staging before newer active entries. Do not automatically
  delete staging or roll back a successfully archived stream.
- Recovery has the runtime log's at-least-once semantics: an interrupted append
  or failure between fsync and staging removal can cause replayed bytes on
  retry. Exactly-once crash recovery is not guaranteed.

