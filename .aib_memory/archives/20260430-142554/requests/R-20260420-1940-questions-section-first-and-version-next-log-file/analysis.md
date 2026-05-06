## Executive Summary

- **Request ID:** R-20260420-1940

- **Request title:** Questions section first and version_next log file

- **High-level purpose:** Two independent UX and workflow improvements: (1) surfacing AI-generated questions earlier in `request.md` by moving `## Questions & Decisions` to position 2 (immediately after `## Goal`), and (2) establishing a permanent VCS-tracked accumulator file (`logs/version_next.md`) that gathers semantic implementation summaries at implementation time, replacing bare PR commit subjects as the primary source for CI-generated per-version release logs.

- **Scope interpretation:** The request touches four asset layers — the request convention, the analysis prompt, the implement prompt, and the release bookkeeping pipeline (Python script + GitHub Actions workflow). All changes are within the existing architecture; no new components or infrastructure are introduced.

- **All three Q-blocks answered:** Q001 (fallback = commit subjects when `version_next.md` absent/empty), Q002 (`initialize.py` excluded; file created only by `aib-implement.md` on first write), Q003 (clear = seed template `# Pending changes for next version\n`). Answers applied to `request.md` Scope, Out of scope, and Assumptions; Q-blocks removed from `## Questions & Decisions`.

- **`request.md` sections updated during this run:** `## Scope` (Q001, Q003 applied), `## Out of scope` (Q002 applied), `## Assumptions` (fully replaced, A1–A4 with confirmed evidence), `## Plan` (Tasks 3, 5, 6 updated), `## Code and Asset Scan for Impacted Components` (initialize.py re-classified), `## Internal Review` (ambiguities resolved).

- **Risk summary:** Low overall. The section reordering is a convention-only change; no tool-script positional parsing confirmed by spike. The `version_next.md` accumulator introduces one new file dependency in the CI pipeline; absent/empty state is handled by fallback to commit subjects.


---

## Domain Knowledge Essentials

**Business terminology:**

- **Request (`request.md`):** The single structured specification file per AIB work item. It contains goal, background, scope, constraints, success criteria, and AI-generated planning sections. It is the authoritative implementation source; `aib-implement.md` reads only this file.

- **`## Questions & Decisions` section:** AI-generated Q-blocks for decision forks that exceed the severity threshold. Currently at position 10 of 12 in the mandatory section ordering. This request moves it to position 2 to improve developer visibility.

- **`logs/version_next.md`:** The new accumulator file proposed by this request. It collects AI-authored implementation summaries (one per request) at implementation time, before CI creates the per-version log.

- **Per-version log (`logs/version_vX.Y.Z_log.md`):** CI-generated changelog artifact written by `release_bookkeeping.py` during the PR workflow. Currently populated from bare git commit subjects; after this change, it uses `version_next.md` content when non-empty.

- **SemVer (Semantic Versioning):** Versioning scheme used by AIB. Patch is bumped on each PR to main.

- **Seed template:** The initial/reset content written to a managed file. For `logs/version_next.md`, the seed is `# Pending changes for next version\n`.

**Impacted roles / personas:**

- **Developer:** Sees Q&D questions at position 2 (immediately after Goal) in future `request.md` files. `logs/version_next.md` is written automatically during implement — no manual action required.

- **AIB Maintainer:** Updates `request-convention.md`, `aib-analysis.md`, `aib-implement.md`, and `release_bookkeeping.py` to implement the changes.

- **Reviewer / Changelog consumer:** Reads the per-version log; after this change, sees richer AI-authored change descriptions when `version_next.md` is non-empty.

**Business processes touched:**

- Execute analysis workflow: generates `request.md` with Q&D section; position of that section changes in the new convention.
- Execute implement workflow: appends entry to `logs/version_next.md` after each completed request.
- Release bookkeeping: CI reads `logs/version_next.md` as the primary changes source; falls back to commit subjects when absent/empty.


---

## Technical Knowledge & Terms

**Technologies and components:**

- **`request-convention.md`:** The normative file defining the 12 mandatory sections and their ordering in `request.md`. Currently places `## Questions & Decisions` at position 10. This file drives all downstream prompt behavior.

- **`aib-analysis.md`:** The analysis prompt. Part 2 generates AI sections in `request.md`, including Q&D. Must be updated to reference the new Q&D position (position 2, after Goal).

- **`aib-implement.md`:** The implementation prompt. Currently invokes `close-request.py` as its final step. Must be updated to append a summary entry to `logs/version_next.md` before that final step.

- **`release_bookkeeping.py`:** Python 3.10+ standard-library-only script. Currently reads commit subjects via `_read_commit_subjects()` and passes them to `_write_version_log()`. Two new helpers are needed: `_read_version_next(log_dir)` returns non-header, non-empty lines from `logs/version_next.md` or `[]` if absent/empty; `_clear_version_next(log_dir)` resets the file to the seed template.

- **`aib-semver-patch-bump-and-log.yml`:** GitHub Actions workflow. The "Commit and push" step uses `git add .aib_brain logs versions`, which already stages the full `logs/` directory. Confirmed by spike: no structural workflow change is needed.

- **`common.py`:** Shared utilities for tool scripts. Does not parse `request.md` by section position; uses heading-name-based lookups. Confirmed safe for the section reorder.

**Data models / assets:**

- `logs/version_next.md`: Plain Markdown file. Seed: `# Pending changes for next version\n`. Entries format: `- <request_id>: <one-line summary>` (one per implemented request). CI reads non-header, non-empty lines as the changes list.

- `request.md`: 12-section Markdown file. Sections identified by level-2 headings (`##`). No positional parsing exists in tool scripts — confirmed by code scan.

**Non-functional attributes:**

- **Idempotency:** `release_bookkeeping.py` must remain idempotent on CI reruns. `_clear_version_next` sets deterministic seed state; the idempotency guard (`log_path.exists() and head_marker == target_marker`) is unaffected (confirmed by spike).

- **Python standard library only:** No new libraries in `release_bookkeeping.py` or any tool script.

- **VCS tracking:** `logs/version_next.md` must not be gitignored. `logs/` is staged by the CI workflow's `git add` command (confirmed).

**Key terms:**

- **Q-block:** A structured question block in `## Questions & Decisions` with checkbox options and an `> Answer:` field.
- **Severity threshold:** The level at which a decision fork is raised as a Q-block vs. resolved autonomously. Default is 3 (Moderate).
- **Fallback:** When `version_next.md` is absent or empty, `release_bookkeeping.py` uses PR commit subjects (current behavior preserved).

**Files read during this analysis:**

- `.aib_memory/requests/R-20260420-1940-questions-section-first-and-version-next-log-file/request.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/input.md`
- `.aib_memory/references.md`
- `.aib_memory/context.md`
- `.aib_brain/Concepts.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/prompts/aib-implement.md`
- `scripts/release_bookkeeping.py`
- `.github/workflows/aib-semver-patch-bump-and-log.yml`


---

## Research Results

**Pattern scan — section position references in tool scripts:**

Searched all `.aib_brain/tools/*.py` files for positional section parsing patterns (`position`, numeric-section patterns, `Questions`). Result: zero matches for section-index-based parsing. All tool scripts use `parse_markdown_table` (for register files) and heading-based text extraction. Conclusion: reordering Q&D from position 10 to position 2 carries no runtime risk to tool scripts. A1 confirmed.

**Pattern scan — `request-convention.md` Validation Rules:**

The Validation Rules section states the non-empty requirement using the phrase "the six mandatory sections (Goal, Background, Scope, Out of scope, Constraints, Success criteria)." It also states AI-generated sections are "sections 7–14." After implementation, Q&D moves to position 2; the Validation Rules must be updated to enumerate non-empty sections by name (not positional range) and to clarify that Q&D at position 2 is AI-generated and may be empty. This update is captured in Task 1 of the Plan.

**Pattern scan — `aib-analysis.md` Part 2 Q&D instructions:**

The current `aib-analysis.md` instructs writing/updating Q&D as one of the optional sections after `## Success criteria`. After implementation, the prompt must instruct writing Q&D after `## Goal` (position 2). The Q-block format, severity scale, and re-run merging rules are heading-name-based and require no structural update.

**Pattern scan — `release_bookkeeping.py` structure:**

- `_read_commit_subjects(path)` reads a flat text file (one subject per line) and returns a normalized list.
- `_write_version_log(...)` accepts `commit_subjects: list[str]` and renders them as a bullet list under `Changes:`.
- The `main()` function passes commit subjects directly to `_write_version_log`.
- No reading of `logs/version_next.md` currently exists.
- Idempotency guard: `if log_path.exists() and head_marker == target_marker: return 0` — checks the log path and marker, not `version_next.md`. Adding `_clear_version_next` after log write does not affect this guard. Spike confirmed.

**Pattern scan — CI workflow `git add` step:**

Line `git add .aib_brain logs versions` stages the entire `logs/` directory. `logs/version_next.md` is covered. A2 confirmed. No structural change to the YAML is needed.


---

## External Benchmarking

**Keep a Changelog pattern (keepachangelog.com):**

The "Keep a Changelog" convention defines an `[Unreleased]` section at the top of `CHANGELOG.md` where changes accumulate between releases. On each release the unreleased block is promoted to a versioned section and reset. `logs/version_next.md` directly mirrors this pattern scoped to AIB: the accumulator collects entries at implementation time and is promoted + cleared by CI at release time.
- Key takeaway: Capturing change intent at the point of implementation (not at release time) produces the most accurate and semantically rich changelog entries.
- Applicability: High. Adopt with adaptation — AIB uses per-version log files (not a single CHANGELOG.md) and CI-driven clearing eliminates the manual promotion step.
- Adopted.

**Conventional Commits (conventionalcommits.org):**

A specification for structuring commit messages (`feat:`, `fix:`, `chore:`) to enable automated changelog generation from commit history. AIB's current approach (raw commit subjects) is weaker than Conventional Commits. The `version_next.md` mechanism sidesteps the commit-format requirement by writing semantically rich descriptions during implementation.
- Key takeaway: Commit-subject-based changelog generation produces machine-parseable but often low-context entries.
- Applicability: Medium. The accumulate-at-implementation pattern is superior for AIB's use case.
- Adapted: keep commit subjects as a fallback (Q001 answer); use `version_next.md` as primary source when non-empty.

**GitHub Releases "Generate Release Notes" feature:**

GitHub auto-generates release notes from PR titles and labels — terse metadata similar to AIB's current commit-subject approach. Lacks implementation-level context.
- Applicability: Low for AIB. External API dependency; not vendor-agnostic; out of scope.
- Rejected: reinforces the case for human+AI authored summaries at implementation time.

**Conclusion:** The proposed `logs/version_next.md` accumulator pattern is well-aligned with industry best practices. It improves on bare commit subjects and is achievable within AIB's standard-library-only, file-first constraints.


---

## Minimal Spikes and Experiments

**Spike: CI `git add logs` coverage of `logs/version_next.md`**

- Hypothesis: The existing `git add .aib_brain logs versions` command in the CI workflow already stages `logs/version_next.md` when it is cleared after CI use, eliminating the need for a workflow structural change.
- Approach: Read `.github/workflows/aib-semver-patch-bump-and-log.yml`, locate the "Commit and push" step, and inspect the `git add` command.
- Outcome: Line `git add .aib_brain logs versions` stages the entire `logs/` directory tree unconditionally. No path-specific filtering exists.
- Conclusion: A2 confirmed. No workflow structural change is needed. The scope item "Update `.github/workflows/...` as needed" resolves to read-only review.

**Spike: Tool script position-based section parsing**

- Hypothesis: No tool script in `.aib_brain/tools/` uses numeric position to identify sections of `request.md`, making the Q&D reorder safe.
- Approach: Searched all `.py` files in `.aib_brain/tools/` for patterns: `position`, `Questions`, numeric-section references, and index-based list access on `request.md` content.
- Outcome: Zero matches for positional section parsing. `parse_markdown_table` is used for register files only. No script reads `request.md` sections by index.
- Conclusion: A1 confirmed. Reordering Q&D from position 10 to position 2 is safe for all existing tool scripts.

**Spike: `release_bookkeeping.py` idempotency guard interaction with `_clear_version_next`**

- Hypothesis: Adding `_clear_version_next` (called after `_write_version_log`) does not break the idempotency guard, because the guard checks `log_path.exists()` and `head_marker == target_marker`, not the content of `version_next.md`.
- Approach: Read `main()` in `release_bookkeeping.py`; trace the idempotency guard logic.
- Outcome: Guard `if log_path.exists() and head_marker == target_marker: return 0` fires before any call to `_write_version_log` or `_clear_version_next`. On rerun where log exists and marker is already bumped, execution returns 0 without calling clear. On first run, log is written then file is cleared. No conflict.
- Conclusion: Idempotency is preserved. The guard does not need modification.


---

## AI Copilot Suggestions

**Observation 1 — Convention non-empty requirement wording requires careful update (design quality)**

Moving `## Questions & Decisions` to position 2 breaks the positional logic in `request-convention.md` Validation Rules, which currently states the non-empty requirement applies to "sections 1–6." After the reorder, Q&D (AI-generated, may be empty) occupies position 2, making positional enumeration unreliable. The validation rule must be restated by section name rather than positional range to remain both accurate and convention-safe.
- Suggestion: Update `request-convention.md` to enumerate non-empty sections by name (Goal, Background, Scope, Out of scope, Constraints, Success criteria) and add an explicit note that Q&D is AI-generated and MAY be empty.

**Observation 2 — First-write edge case in `aib-implement.md` (implementation risk)**

If `logs/version_next.md` is deleted or the repository is re-initialized on a fresh clone after the first release cycle, `aib-implement.md` will attempt to append to a non-existent file. The plan describes "create the file with seed template if absent," but the Done Criteria in Task 4 do not explicitly include a test for this defensive creation path.
- Suggestion: Add a test case (T-defensive-create) that verifies `aib-implement.md` creates `logs/version_next.md` with the seed template and appends the entry when the file does not exist. Explicitly state in `aib-implement.md` that the file must be created if absent.

**Observation 3 — SC-4 success criterion wording remains ambiguous despite Q001 resolution (testability)**

SC-4 states "incorporates the content from `logs/version_next.md` rather than (or in addition to) bare commit subjects." The Q001 answer and the Scope now clearly define the behavior (replace when non-empty; fall back when empty), but SC-4 still uses "rather than (or in addition to)" which is not a pass/fail test condition. A reviewer checking only SC-4 cannot determine the expected behavior.
- Suggestion: During implementation, revise SC-4 to: "The changes section of the version log uses `version_next.md` entries when the file is non-empty, and falls back to PR commit subjects when the file is absent or empty (seed-template-only content is treated as empty)."

**Observation 4 — Multi-entry format underspecification for the `version_next.md` accumulator (maintainability)**

The accumulator may receive multiple entries between releases (one per implemented request). The format `- <request_id>: <summary>` is stated in Assumptions but not enforced in the prompt instructions. If a future implementer writes multi-line entries or uses a different bullet character, the `_read_version_next` helper may misparse the content.
- Suggestion: Explicitly document the single-line entry format constraint in `aib-implement.md` and in the seed template comment. Constrain summary to one line; no continuation lines permitted.

**Scope note:** The scope is appropriately sized. Both changes are localized prompt/convention/script edits. The two features are independent; Task 3 (create file) and Task 1 (convention reorder) have no shared files, allowing parallel implementation if needed.


---

## Testing

- T1 — SC-1 (Q&D position in new request.md): Generate a new `request.md` via `aib-analysis.md` from a test input. Parse the level-2 headings in order. Expected outcome: the second `##` heading is `## Questions & Decisions`, immediately following `## Goal`.

- T2 — SC-1 (convention file): Read `request-convention.md`. Verify the Document Structure section lists `## Questions & Decisions` as section 2 (immediately after `## Goal`). Expected outcome: "2. `## Questions & Decisions`" appears in the section list at the correct position.

- T3 — SC-2 (file existence): Assert `Path('logs/version_next.md').exists()` returns `True`. Expected outcome: file present in `logs/`.

- T4 — SC-2 (VCS tracking): Run `git ls-files logs/version_next.md`. Expected outcome: command outputs `logs/version_next.md`, confirming the file is tracked.

- T5 — `_read_version_next` non-empty: Write a test `version_next.md` with two bullet lines; call `_read_version_next`. Expected outcome: returns a list of two strings matching the bullet lines.

- T6 — `_read_version_next` absent: Call `_read_version_next` when the file does not exist. Expected outcome: returns `[]` without raising an exception.

- T7 — `_read_version_next` seed-only: Call `_read_version_next` on a file containing only the seed comment line. Expected outcome: returns `[]` (comment line is not treated as a change entry).

- T8 — SC-4 fallback behavior: Unit test `main()` with absent/empty `version_next.md` and two commit subjects. Expected outcome: version log changes section contains the two commit subjects.

- T9 — SC-4 override behavior: Unit test `main()` with `version_next.md` containing one entry and two commit subjects. Expected outcome: version log changes section contains only the `version_next.md` entry; commit subjects are absent.

- T10 — `_clear_version_next`: Call `_clear_version_next`. Expected outcome: `logs/version_next.md` content equals `# Pending changes for next version\n`.

- T11 — SC-5 dry-run does not clear: Call `main(--dry-run)` with non-empty `version_next.md`. Expected outcome: `version_next.md` content is unchanged after the call.

- T12 — Idempotency on rerun: Run `main()` twice. Expected outcome: second run exits 0 with "No changes needed"; `version_next.md` is in cleared (seed) state from first run; second run does not clear again.

- T13 — Test suite regression: Run `pytest tests/` after all changes. Expected outcome: all existing tests pass (zero failures).

- T14 — SC-3 (implement appends entry): See `UAT_scenarios.md` — UAT-01.

- T15 — SC-4/SC-5 (CI uses and clears version_next.md): See `UAT_scenarios.md` — UAT-02 and UAT-03.


---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

Both changes are localized and low-coupling. The Q&D section reorder is a pure convention and prompt update with no runtime code changes, no data migration, and no backward compatibility risk for closed requests (explicitly out of scope). The `version_next.md` accumulator introduces a new file dependency between `aib-implement.md` and `release_bookkeeping.py`, mediated by a plain Markdown file in a VCS-tracked directory. The CI fallback behavior preserves backward compatibility for PRs created before `aib-implement.md` is updated.

- Architectural risk is low; both changes are additive (new helper functions, new file, convention update).
- Idempotency of `release_bookkeeping.py` is preserved per the spike analysis.
- The `request-convention.md` Validation Rules non-empty requirement must be restated by section name, not positional range, to remain valid after Q&D moves to position 2.
- The two-feature bundling is a minor maintainability concern: a bug in either change requires reviewing the combined diff.

### Product Owner

The business value is clear and measurable. The Q&D reorder addresses real usability friction: reviewers currently must scroll past six sections to discover pending questions. The `version_next.md` accumulator directly improves changelog quality for release communication and audit trail. Both features have explicit acceptance criteria (SC-1 through SC-5); SC-1 through SC-4 are automatable; SC-3, SC-4, and SC-5 require a CI run (UAT planned).

- SC-4 wording is ambiguous in the success criterion even though the behavior is clear from Q001 + Scope; should be corrected during implementation.
- No new user-facing workflows are introduced; both changes are transparent to the developer in daily use.
- Acceptance criteria coverage is complete for both functional areas.

### User

The Q&D section reorder is an immediate usability improvement: the most action-requiring content (open questions needing answers) appears near the top of `request.md`, reducing the cognitive load for developers reviewing active requests. The `version_next.md` mechanism is invisible to the daily developer workflow — it is written automatically by `aib-implement.md` — but produces a visible benefit at release time through richer changelog entries.

- Zero learning curve for the Q&D reorder: content and format of Q-blocks are unchanged.
- If `version_next.md` accumulates many entries between releases, version log changes sections could become verbose; a one-line summary constraint mitigates this.
- Developers reviewing `logs/version_next.md` mid-cycle will see accumulated entries — this is expected behavior and not a problem.

### Security Officer

Neither change introduces new attack surface, credential handling, external network calls, or privilege escalation paths. `logs/version_next.md` contains implementation change summaries authored by the AI agent; these are Internal engineering documentation committed to the repository. The CI workflow already writes to the PR branch; no new permissions are required. The clearing mechanism is equivalent in security risk to the existing log-write operation.

- No authentication or authorization changes.
- No new external endpoints or APIs.
- Process reminder: `aib-implement.md` prompt should explicitly state that summaries must not include secrets, credentials, or sensitive configuration values.

### Data Governance Officer

All artifacts are classified as Internal engineering documentation, consistent with all other AIB files. `logs/version_next.md` is VCS-tracked; its content (implementation summaries) is derived from `request.md` (already Internal). No personal data, regulated data, or customer data is expected. Per-version logs produced from `version_next.md` are permanent VCS-tracked records.

- No new data classification risk.
- Data lineage: `request.md` → `aib-implement.md` → `logs/version_next.md` → `release_bookkeeping.py` → `logs/version_vX.Y.Z_log.md`. Lineage is clear and traceable.
- Clearing `version_next.md` via a CI commit does not destroy data — git history preserves all prior content.
- No cross-border data transfer; all operations are local filesystem and GitHub-managed storage.
