## Executive Summary

- **Request ID**: R-20260430-1430
- **Request title**: Enrich semver bump commit message with changelog content

- **Purpose**: Replace the current terse `"chore: bump ..."` CI commit message in `.github/workflows/aib-semver-patch-bump-and-log.yml` with an enriched multi-line message that includes curated changelog bullets from `logs/next_version_changes.md`, making GitHub commit notification emails self-explanatory for recipients.

- **Key technical finding**: `release_bookkeeping.py` reads and resets `logs/next_version_changes.md` during the "Run release bookkeeping" step — before the "Commit and push" step executes. The curated content must therefore be captured before or during the bookkeeping step, not at commit time.

- **Recommended approach**: Extend `release_bookkeeping.py` to emit the curated bullets as a `changes_body` GitHub Actions output (using heredoc syntax), consistent with the existing `changed` and `new_version` output pattern. The commit step then uses this value to construct a subject + body message, falling back to subject-only when the body is empty.

- **Scope assessment**: Well-scoped. The change is additive and touches two files at most (the workflow YAML and optionally the Python script). No new dependencies, no workflow trigger changes, no structural changes to existing outputs.

- **`request.md` sections updated during this analysis run**: Assumptions (§7), Plan (§8), Documentation (§9), Questions & Decisions (§10), Code and Asset Scan (§11), Internal Review (§12).

## Domain Knowledge Essentials

- **Release bookkeeping**: The AIB CI process of bumping the patch version, creating a per-version log (`logs/version_vX.Y.Z_log.md`), and archiving `.aib_brain/` as a zip under `versions/` — executed automatically on `pull_request` events targeting `main`.

- **Curated change log** (`logs/next_version_changes.md`): An append-only Markdown bullet list maintained by the AI agent during each `aib-implement.md` run (via the `instructions.md` directive). It serves as the preferred `Changes:` source for the version log; CI resets it to empty after successful incorporation.

- **Commit notification email**: GitHub automatically sends email notifications when commits are pushed to a repository. The email body includes both the commit message subject line and body. Recipients currently see only the terse `"chore: bump ..."` subject.

- **Affected roles/personas**:
  - *Repository contributors* who receive commit notification emails and need to understand what changed.
  - *AIB Maintainers* who own the workflow YAML and the release bookkeeping script.
  - *Developers* who author curated bullets during implementation runs.

- **Business process touched**: Release lifecycle — specifically the CI-automated patch bump and commit phase triggered by PR events.

## Technical Knowledge & Terms

- **GitHub Actions Workflow**: YAML-defined automation triggered by repository events. Steps run sequentially within a job. The relevant workflow is `.github/workflows/aib-semver-patch-bump-and-log.yml`.

- **`GITHUB_OUTPUT`**: A file injected into the shell environment by GitHub Actions; writing `key<<DELIMITER…DELIMITER` to this file creates step outputs (including multi-line values) accessible in later steps as `${{ steps.<step_id>.outputs.<key> }}`.

- **Multi-line GitHub Actions output**: Must use the heredoc delimiter format because simple `echo "key=value"` silently truncates on newlines. The delimiter string must be unique enough not to appear in the content (e.g., `AIB_CHANGES_BODY_EOF`).

- **`git commit --file <path>`**: Reads the full commit message from a file; supports multi-line content without shell escaping issues. Safer than concatenating multi-line strings into `-m` arguments.

- **`git commit -m "subject" -m "body"`**: Git treats each `-m` value as a separate paragraph; the result is a standard subject + body message. This approach requires careful quoting when content contains special characters.

- **`set -euo pipefail`**: Bash strict mode active in all workflow steps: `-e` exits on error, `-u` exits on unbound variable reference, `-o pipefail` fails on pipeline errors. All new code must initialize variables before use.

- **`release_bookkeeping.py`**: Python script that (1) reads `next_version_changes.md` via `_read_curated_entries()`, (2) incorporates bullets into the version log, (3) resets the curated file via `_reset_curated_file()`, and (4) emits `changed` and `new_version` to `GITHUB_OUTPUT`.

- **Evidence → implication log**:
  - `git commit -m "chore: bump to ..."` (single `-m`) → single-line message → email body is uninformative.
  - `_reset_curated_file()` in `release_bookkeeping.py` called before commit step → curated file is empty at commit time → content must be captured earlier.
  - `GITHUB_OUTPUT` heredoc support confirmed by existing workflow usage → safe mechanism for multi-line content propagation between steps.
  - `git commit --file` avoids shell-escaping pitfalls with special characters in curated bullets.

- **Files Read**: `.github/workflows/aib-semver-patch-bump-and-log.yml`, `scripts/release_bookkeeping.py`, `.aib_memory/context.md`, `.aib_brain/Concepts.md`, `.aib_memory/references.md`, `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`.

## Research Results

- **Pattern scan — CI commit message enrichment**: In monorepo and automated release workflows, a common pattern is to read a changelog or changeset file before the release step, store the content in a step output or environment variable, and inject it into the commit/tag message or PR description. This is the same pattern used by `release-please` and similar tools.

- **Pattern scan — GitHub Actions multi-line output**: The `GITHUB_OUTPUT` heredoc pattern (`key<<DELIMITER\n…\nDELIMITER`) is the current GitHub-recommended approach for multi-line output values (replacing the deprecated `::set-output::` command). Confirmed compatible with Ubuntu runners and present in the existing workflow for `changed` and `new_version` outputs.

- **Prior similar solution in workspace**: `release_bookkeeping.py` already writes to `GITHUB_OUTPUT` via `--github-output`. Extending this with a `changes_body` key follows the existing script architecture without introducing new patterns.

## External Benchmarking

- **Semantic Release / release-please (conventional commits ecosystem)**: These tools generate commits that include the full changelog section in the commit body. The subject line is a one-liner (`chore(release): v1.2.9`); the body contains full release notes. Key takeaway: separating subject from body is the universally adopted standard; subject lines should remain concise for tooling that parses them, while the body carries human-readable content.
  - Applicability: Directly applicable. Our subject line (`chore: bump to v1.2.9 (PR #42)`) should remain unchanged; the curated bullets belong in the body.
  - Adoption decision: Adopt the subject + blank line + body structure.

- **GitHub's `actions/github-script` and heredoc patterns (GitHub community)**: The GitHub Actions community extensively documents the `GITHUB_OUTPUT` heredoc pattern for multi-line content (strings with embedded newlines). A commonly recommended unique delimiter is a randomly-generated or context-specific string to prevent collisions with content. For example: `echo "key<<$DELIMITER" >> $GITHUB_OUTPUT`.
  - Applicability: Directly applicable to passing the curated bullet list from the bookkeeping step to the commit step.
  - Adoption decision: Adopt — consistent with existing workflow code and GitHub's current recommendations.

## Minimal Spikes and Experiments

- **Spike: State of `next_version_changes.md` at commit step execution time**
  - Hypothesis: `next_version_changes.md` is already empty when the commit step runs.
  - Approach: Traced execution flow in `release_bookkeeping.py`; located `_reset_curated_file()` call in `main()`; confirmed it is invoked after curated entries are incorporated into the version log and before the script exits.
  - Outcome: Confirmed — the file is cleared by `release_bookkeeping.py` during the "Run release bookkeeping" step, before the "Commit and push" step executes.
  - Conclusion: Curated content must be captured before or during the bookkeeping step; reading the file in the commit step will always yield empty content.

- **Spike: Multi-line content via `GITHUB_OUTPUT` heredoc in existing workflow**
  - Hypothesis: The workflow already uses `GITHUB_OUTPUT` successfully; extending it with a multi-line value is safe.
  - Approach: Reviewed the `release_bookkeeping.py` `--github-output` argument handling and confirmed the script writes `changed=true/false` and `new_version=vX.Y.Z` to the output file. GitHub Actions runtime handles these correctly.
  - Outcome: No runtime spike needed; the mechanism is confirmed by existing successful usage and GitHub documentation.
  - Conclusion: Adding `changes_body` as a multi-line output from `release_bookkeeping.py` using `<<EOF` heredoc is safe and consistent with the existing pattern.

## AI Copilot Suggestions

- **Observation 1 — The implementation fork in Task 1 has different maintenance footprints**: Option A (read file in a new workflow step) keeps all changes in the YAML and avoids modifying the Python script, but it introduces a bash file-read step with its own quoting/escaping surface. Option B (extend `release_bookkeeping.py` output) keeps the YAML clean, reuses the existing `GITHUB_OUTPUT` pattern, and lets the Python layer handle file-not-found and empty-content gracefully. Option B is the better long-term choice because the Python layer already has the logic to determine what constitutes usable curated content. However, Option B does add a new output key to the script's interface contract, which future callers must be aware of.
  - Suggestion: Choose Option B and document the new `changes_body` output in `context.md` alongside `changed` and `new_version`.

- **Observation 2 — Shell escaping of multi-line content is a well-known GitHub Actions failure mode**: If the commit step uses inline `${{ steps.bookkeeping.outputs.changes_body }}` expansion directly in a `git commit -m` argument, content with backticks, `$` signs, or double quotes will break the shell command under `set -euo pipefail`. Writing the commit message to a temp file and using `git commit --file` entirely avoids this class of bug.
  - Suggestion: In the commit step, always write the commit message to a `RUNNER_TEMP` temp file and use `git commit --file "$msg_file"` regardless of body emptiness; clean up the temp file in the "Cleanup transient artifacts" step.

- **Observation 3 — The scope is minimally sufficient; no over-engineering risk detected**: The request is precisely scoped to the commit message change. Resist the temptation to also enrich the PR description or add a separate "Notify" step — those are separate concerns. The commit message is the right level of enrichment for the stated goal (email notifications).
  - Suggestion: Keep the implementation focused on the commit message only; if PR description enrichment is later desired, treat it as a separate request.

## Testing

- T1 — Curated changes captured as step output: Run a PR where `logs/next_version_changes.md` has non-empty curated bullets before the bookkeeping step. Expected outcome: the `changes_body` output of the bookkeeping step (or capture step) is non-empty and contains the bullet lines that were in the file.

- T2 — Commit message body contains changelog bullets: After the workflow commits to the PR branch on a PR with non-empty curated changes, inspect the latest commit. Expected outcome: `git log --format=%B -n 1` shows the subject line `chore: bump to <version> (PR #<number>)` followed by a blank line and the curated bullet list.

- T3 — Empty curated log produces subject-only commit: Run a PR where `logs/next_version_changes.md` is empty before the bookkeeping step. Expected outcome: `git log --format=%B -n 1` shows only the subject line; no trailing blank lines or empty body.

- T4 — Strict mode compliance: The modified workflow steps must not produce unbound variable or pipeline errors. Expected outcome: each modified step exits with code 0; workflow run completes successfully.

- T5 — Idempotency on PR synchronize: Push a second commit to an already-processed PR. Expected outcome: the workflow runs again, produces a second enriched commit (or subject-only fallback if no new curated content), and exits cleanly without conflicts.

- T6 — Changed gate preserved: When `release_bookkeeping.py` emits `changed=false` (no file changes), the "Commit and push" step is skipped. Expected outcome: no commit is made to the PR branch; workflow exits with code 0.

- T7 — Existing test suite passes: Run `pytest tests/` after modifying `release_bookkeeping.py`. Expected outcome: all existing tests pass with no new failures.

See UAT_scenarios.md — UAT-01 (manual verification of commit notification email content).

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The change is architecturally minimal: it modifies one CI workflow step and optionally extends one Python script output. The critical architectural insight — that `next_version_changes.md` is consumed and reset by `release_bookkeeping.py` before the commit step — is correctly identified and addressed. Routing the curated content through the existing `GITHUB_OUTPUT` mechanism (Option B) keeps the data flow clean and avoids introducing a second file-read path in bash.

- The recommended `git commit --file` approach is more robust than multi-argument `-m` concatenation and is safe under `set -euo pipefail`.
- The unique heredoc delimiter mitigates the delimiter-collision risk; content containing the delimiter string would cause silent output truncation — choosing a sufficiently unique string is important.
- No changes to workflow triggers, concurrency gates, or step ordering are required; the architectural footprint is minimal.
- Finding: The design is consistent with ADR-0004, ADR-0008, and FR-011; no architectural conflicts detected.

### Product Owner

The request has direct and high business value: GitHub commit notification emails are the primary asynchronous communication channel for repository activity, and the current message is acknowledged as uninformative. The change directly addresses this without introducing new infrastructure, dependencies, or workflow complexity.

- Success criteria SC-1 through SC-5 are measurable and testable.
- The fallback to subject-only message (when curated log is empty) ensures backward compatibility with PRs that do not go through the standard `aib-implement.md` workflow.
- Scope is appropriately narrow; the request does not attempt to change version log content, PR descriptions, or notification delivery mechanisms.
- Gap: The exact formatted output of the commit body is not specified in the request (indented bullets vs. raw lines). Based on analysis, keeping the raw `- bullet` format is the natural choice and is resolved autonomously (see Q-block section in `request.md`).

### User

Recipients of GitHub commit notification emails will immediately notice that the automated release commit now carries meaningful content. The change is transparent to developers: no new steps in the PR or development workflow; the menu, `input.md`, and request lifecycle are unaffected.

- The enriched commit message appears in both the GitHub web UI commit history and in notification emails.
- If `next_version_changes.md` was not populated during the implementation run (e.g., a manual or non-AIB commit), the email remains as before — no regression.
- The subject line remains unchanged, which is important for developers who scan commit histories by subject.

### Security Officer

The change introduces handling of user-authored content (curated bullets from `logs/next_version_changes.md`) inside a GitHub Actions workflow step. The risk surface is limited.

- Curated bullets are written by the AI agent during `aib-implement.md` runs and stored in a VCS-tracked file; they are not externally supplied at runtime and are not influenced by PR authors.
- Injecting file content into a commit message via `GITHUB_OUTPUT` does not execute the content; git and GitHub treat commit messages as plain text.
- No secrets, credentials, or sensitive data are expected in curated bullets; the `instructions.md` directive constrains content to present-tense, user-visible change descriptions.
- Risk: a bullet containing a Git-special string like a line starting with `From ` could theoretically confuse `git am` or mbox-format email parsers — extremely low probability given the controlled authorship and content constraints.
- Finding: no new attack surface is introduced; the file-content-to-commit-message flow is a read-only, append-only data path with no code execution.

### Data Governance Officer

Commit messages are persisted in Git history permanently and are visible to all repository collaborators with read access. The enriched message will contain the same content that already appears in `logs/version_vX.Y.Z_log.md`, which is also VCS-tracked.

- Data classification: Internal engineering documentation — same as existing version logs and commit history.
- Retention: Commit messages are retained indefinitely in Git history; this is consistent with existing repository practice.
- No PII, credentials, or sensitive business data are expected in curated change bullets based on the `instructions.md` directive (present-tense, user-visible change descriptions only).
- The data flow (curated bullets → commit message → Git history → email notification) is a subset of the existing data flow (curated bullets → version log → Git history); no new data exposure beyond what is already committed.
- Finding: no data lineage, retention, classification, or compliance concerns identified.
