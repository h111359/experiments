# Analysis: R-20260422-1308 — Add AIB directive to maintain next version log file

## Executive Summary

- Request ID: R-20260422-1308.

- Request title: Add AIB directive to maintain next version log file.

- High-level purpose: improve release log quality by adding a persistent directive in `.aib_memory/instructions.md` and extending `scripts/release_bookkeeping.py` to prefer curated entries from `logs/next_version_changes.md` with safe fallback to git commit subjects.

- Scope correction applied from current input: do not add `logs/next_version_changes.md` to `.aib_memory/references.md`.

- Lifecycle decision already resolved from existing answered questions in `request.md`: after incorporation, CI clears `logs/next_version_changes.md` to empty and commits the reset.

- `request.md` was updated in this run by replacing `## Assumptions`, `## Plan`, and `## Documentation`, removing answered entries from `## Questions & Decisions`, and updating conflicting request content to align with the input prohibition.

## Domain Knowledge Essentials

- AIB (AI Builder): a specification-driven framework that stores project state in `.aib_memory/` and reusable framework assets in `.aib_brain/`.

- Persistent directive: `.aib_memory/instructions.md` is a workspace-level instruction file read by all AIB prompts before main execution.

- Release bookkeeping: `scripts/release_bookkeeping.py` is the CI script that bumps the patch marker and writes `logs/version_vX.Y.Z_log.md`.

- Curated delta log: `logs/next_version_changes.md` is intended to hold human-readable, intent-level change bullets gathered during implementation.

- Personas affected:
  - Developer: expects readable version logs and predictable fallback behavior.
  - Maintainer: preserves deterministic CI and idempotency constraints.

- Business acceptance impact:
  - Better changelog readability without introducing external dependencies.
  - No disruption to current CI workflow when curated file is missing or empty.

## Technical Knowledge & Terms

- SemVer marker file: a single empty filename in `.aib_brain/` in form `vMAJOR.MINOR.PATCH` used as authoritative version source.

- Idempotency: repeated runs with unchanged state should not produce extra writes or divergent outcomes.

- Fallback chain: script uses curated entries first when present and non-empty; otherwise uses commit subjects; if both absent, sentinel text is emitted.

- Standard-library constraint: changes must stay within Python 3.10+ standard library only.

- Files read:
  - `.aib_memory/requests_register.md`
  - `.aib_memory/input.md`
  - `.aib_memory/references.md`
  - `.aib_memory/context.md`
  - `.aib_memory/requests/R-20260422-1308-add-aib-directive-to-maintain-next-version-log-file/request.md`
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/Concepts.md`
  - `scripts/release_bookkeeping.py`
  - `.github/workflows/aib-semver-patch-bump-and-log.yml`

- Evidence to implication:
  - Evidence: `.aib_memory/input.md` explicitly says not to add `logs/next_version_changes.md` to references.
  - Implication: any plan or criterion requiring a references row is out of scope and must be removed.
  - Evidence: answered Q001 and Q002 in request.
  - Implication: no new question needed on lifecycle or source-priority decisions.

## Research Results

- Pattern scan result: the current script architecture supports additive input-source logic cleanly because content already flows through normalized list processing before log writing.

- Repository state result: `.aib_memory/instructions.md` is empty, so the requested directive is net-new and does not require merge conflict resolution.

- Workflow result: CI already passes a commit-subjects file and commits `.aib_brain`, `logs`, and `versions`; adding curated-source support remains compatible with current commit behavior.

- Governance result: because references register currently lists only `.aib_memory/context.md` as editable product-doc, choosing not to add `logs/next_version_changes.md` there is consistent with the user’s explicit input and must be treated as an intentional exception.

## External Benchmarking

- Benchmark: Keep a Changelog style release narratives.
  - Takeaway: curated, user-facing bullets improve comprehension versus raw SCM subjects.
  - Applicability: directly applicable for content quality; adapted to per-PR staging in `logs/next_version_changes.md`.
  - Decision: adopt quality principle, not full changelog taxonomy.

- Benchmark: semantic-release and similar commit-driven generators.
  - Takeaway: full automation works best only when commit discipline is strict across all contributors.
  - Applicability: partially applicable; this repository’s current commit subjects are intentionally fallback, not primary source.
  - Decision: reject full commit-only model and keep dual-source fallback logic.

## Minimal Spikes and Experiments

- Spike: feasibility of dual-source input in release bookkeeping.
  - Hypothesis: one helper for `next_version_changes.md` plus existing normalization path is sufficient.
  - Approach: inspect current script data flow from argument parsing to `_write_version_log`.
  - Outcome: data flow is linear and supports source substitution without structural rewrite.
  - Conclusion: low implementation complexity, medium behavior risk only around lifecycle timing.

- Spike: workflow compatibility with file reset behavior.
  - Hypothesis: clearing `logs/next_version_changes.md` in CI remains compatible with current staged paths.
  - Approach: inspect workflow commit step paths.
  - Outcome: `git add .aib_brain logs versions` already includes the target file path.
  - Conclusion: lifecycle reset via CI commit is operationally compatible.

## AI Copilot Suggestions

- Observation: the current request became cleaner after removing the references-row requirement.
  - Suggestion: keep this scope boundary explicit in constraints to prevent future re-introduction by reruns.

- Observation: behavioral reliability depends on directive clarity more than script complexity.
  - Suggestion: use precise directive wording in `.aib_memory/instructions.md` covering format, append behavior, and no-overwrite rule.

- Observation: idempotency can regress if file-clearing is placed before early-exit guards.
  - Suggestion: implement lifecycle reset at a deterministic point only after content is incorporated and change intent is confirmed.

- Scope note: current scope is slightly smaller than earlier draft and is now better sized to the stated goal.

## Testing

- T1 — Directive file update: verify `.aib_memory/instructions.md` contains a concrete instruction referencing `logs/next_version_changes.md`. Expected outcome: non-empty directive present with append semantics.

- T2 — Curated source preferred: run `scripts/release_bookkeeping.py` with non-empty `logs/next_version_changes.md` and commit-subjects file. Expected outcome: generated version log uses curated entries as `Changes:` bullets.

- T3 — Fallback when curated file missing: run script without `logs/next_version_changes.md`. Expected outcome: no error; commit subjects populate `Changes:`.

- T4 — Fallback when curated file empty: run script with empty curated file. Expected outcome: no error; fallback to commit subjects.

- T5 — Lifecycle clear behavior: verify CI execution path clears `logs/next_version_changes.md` after incorporation and stages the reset in commit paths. Expected outcome: file remains tracked but empty post-run.

- T6 — Idempotency re-run: run same inputs twice. Expected outcome: second run reports no further changes or converges without duplicate side effects.

- T7 — Test suite regression: run `pytest tests/`. Expected outcome: all tests pass.

- T8 — Manual behavior validation: see `UAT_scenarios.md` UAT-01 and UAT-02. Expected outcome: implementation appends curated entries and CI-generated version log reflects them.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The revised scope is technically coherent and avoids unnecessary register expansion. The key architectural risk is preserving idempotency while adding a second content source and lifecycle clear behavior.

- Existing script shape supports additive logic with low refactor risk.
- Lifecycle reset timing must not conflict with idempotent early-exit branches.
- Keeping references untouched reduces cross-artifact coupling.

### Product Owner

The request has clear business value because release logs become readable for stakeholders. Removing the references update keeps delivery focused and faster.

- Success criteria are measurable and acceptance-oriented.
- User instruction from input is reflected as an explicit scope boundary.
- Fallback behavior ensures no pipeline interruption.

### User

The expected behavior is simple: implementation writes curated bullets, CI converts them into release log content. Developer workflow impact is minimal.

- No new manual step is required for normal flow.
- Resulting release notes should better match user-visible changes.
- Predictable fallback avoids friction when curated file is absent.

### Security Officer

No material expansion of attack surface is introduced. The flow stays file-based and local to repository + GitHub Actions.

- No new secrets or external integrations are introduced.
- Markdown content is treated as plain text data.
- Existing PR review and CI boundaries remain unchanged.

### Data Governance Officer

Data lineage remains internal and auditable through VCS. Clearing the curated file after use limits accumulation while preserving release evidence in version logs.

- Classification remains Internal engineering documentation.
- Retention of final release logs is preserved.
- Reset policy reduces stale carry-over across releases.
