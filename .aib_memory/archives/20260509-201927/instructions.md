# Workspace Instructions (AIB Persistent Directives)

These directives are read by every AIB prompt before execution and MUST be observed throughout the prompt run.

## Directive: Maintain `logs/next_version_changes.md` during implementation

During every `aib-implement.md` run, the AI agent MUST curate a human-readable summary of the changes it is about to commit and append it to `logs/next_version_changes.md`. This file is the curated source of `Changes:` bullets used by `scripts/release_bookkeeping.py` when CI generates the next per-version log under `logs/`.

Apply the following rules:

1. File location and creation
   - The file path is `logs/next_version_changes.md` (workspace-relative).
   - If the file does not exist, create it. The file MUST remain VCS-tracked so CI can read it.
   - If the file exists, append to it; never overwrite or truncate existing entries from prior implementation runs that have not yet been incorporated by CI.

2. Entry format
   - Each entry MUST be a single Markdown bullet line starting with `- ` (dash + space).
   - Each bullet MUST be a short, present-tense, user-visible description of one logical change (for example, `- Add curated change source to release bookkeeping script.`).
   - Do NOT include headings, code fences, tables, or HTML; bullet lines only.
   - Do NOT prefix bullets with commit SHAs, ticket numbers, file paths, or author names.
   - One bullet per logical change. Multiple bullets per implementation run are expected when the run touches multiple logical concerns.

3. Append behavior
   - New bullets MUST be appended at the end of the existing file content.
   - Do NOT modify, reorder, or delete bullets that were appended by previous implementation runs.
   - Preserve a trailing newline at end-of-file.

4. CI lifecycle (informational)
   - When CI runs `scripts/release_bookkeeping.py` for a PR targeting `main`, the script reads `logs/next_version_changes.md` and uses its bullets as the `Changes:` source of the generated `logs/version_vX.Y.Z_log.md`. After successful incorporation, CI clears `logs/next_version_changes.md` to empty and commits the reset back to the PR branch.
   - The agent MUST NOT clear or reset this file during implementation; lifecycle reset is exclusively a CI responsibility.

5. Fallback compatibility
   - If `logs/next_version_changes.md` is absent or empty at CI time, `scripts/release_bookkeeping.py` falls back to git commit subjects without error. The directive above ensures curated content is the primary source whenever an implementation run produced user-visible changes.
