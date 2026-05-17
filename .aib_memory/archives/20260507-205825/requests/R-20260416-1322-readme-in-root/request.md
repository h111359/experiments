# Request

## Goal

Remove the technical information, keep it simple how to install and where to read for further info (the .aib_brain/README.md). All the rest info should be included in .aib_memory/context.md and in .aib_brain/Concepts.md

## Background

The root `README.md` is the repository landing page displayed by GitHub. It currently contains both an onboarding orientation (Overview, Installation) and a detailed technical section documenting the GitHub Actions CI release-bookkeeping workflow. The technical section is not useful to a developer onboarding via the root README; it belongs in the product knowledge base (`context.md`) and the domain reference (`Concepts.md`), both of which already capture or synthesize the relevant content.

## Scope

- Root `README.md` — remove the "Automated version bump & release log" section.

- Root `README.md` — retain the Overview section (brief product description + pointer to `Concepts.md`).

- Root `README.md` — retain the Installation section (copy `.aib_brain/`, run commands, pointer to `.aib_brain/README.md`).

- Verify that `.aib_memory/context.md` already captures CI workflow details so no information is lost.

## Out of scope

- Editing `.aib_brain/Concepts.md` (`edit_allowed = N` in `references.md`).

- Editing `.aib_memory/context.md` directly (auto-generated; manual edits would be overwritten on next context regeneration run).

- Editing `.aib_brain/README.md` (no changes requested or required).

- Changes to the GitHub Actions workflow or `release_bookkeeping.py`.

## Constraints

- `Concepts.md` is `edit_allowed = N` in `references.md`; the implement workflow MUST NOT write to it.

- `context.md` is fully replaced on each `aib-context.md` execution; manually inserted content would be lost.

- Root `README.md` is not listed in `references.md`; editing it is authorised by this explicit user request.

## Success criteria

- Root `README.md` contains only: a brief Overview, an Installation section, and a pointer to `.aib_brain/README.md` for further reading.

- The "Automated version bump & release log" section (and all its subsections) no longer exists in root `README.md`.

- No content that was in the removed section is lost — `context.md` retains CI workflow details through its regular synthesis.

## Assumptions

- A2: Root `README.md` is implicitly editable for this request despite not being registered in `references.md`, because the user explicitly requested the edit.
  - Risk if false: References register would need a new entry for `README.md` before the implement workflow can write to it.

## Plan

### Task 1: Simplify root README.md
**Intent:** Remove the "Automated version bump & release log" section from root `README.md`, keeping only Overview and Installation.
**Inputs:** `README.md` (current content)
**Outputs:** `README.md` (simplified, CI workflow section removed)
**External Interfaces:** None
**Environment & Configuration:** No environment dependencies; file edit only.
**Procedure:**
1. Open `README.md`.
2. Identify the `## Automated version bump & release log (Issue #17)` heading and all content beneath it to end of file.
3. Remove that section entirely.
4. Confirm the Installation section already references `.aib_brain/README.md` as the next-read destination; add the pointer if missing.
5. Verify Overview and Installation sections are present and complete.
**Done Criteria:** `README.md` contains only `## Overview` and `## Installation`; no heading or content from the CI workflow section remains.
**Dependencies:** None
**Risk Notes:** A2 — README.md not in `references.md`; implement workflow proceeds on the basis of explicit user authorisation.

## Testing

- T1 — README.md simplified: Open `README.md` and confirm the `## Automated version bump & release log` section and all its subsections are absent. Expected outcome: no heading or bullet from the CI workflow section exists in the file.

- T2 — Overview retained: Confirm `## Overview` section with brief product description and `Concepts.md` pointer is present. Expected outcome: section present and unchanged.

- T3 — Installation retained: Confirm `## Installation` section with copy instructions and run commands is present. Expected outcome: section present; `.aib_brain/README.md` referenced as next-read destination.

- T4 — context.md CI coverage: Open `.aib_memory/context.md` and verify that Release Bookkeeping and GitHub Actions Workflow entries are present. Expected outcome: `context.md` contains ADR-0004, ALG-0001, SEQ-003, and Deployment notes — confirmed in analysis.

- T5 — Re-run idempotency: Re-run `aib-analysis.md` on the same request with no changes; confirm output converges to same intent. Expected outcome: `analysis.md` and `request.md` optional sections regenerate without errors.

## Documentation

- `README.md` (ref_id: N/A) — primary artifact being edited; CI/release-bookkeeping technical section removed.

- `.aib_memory/context.md` (ref_id: REF-0001) — no edit required; CI workflow details already present from regular `aib-context.md` synthesis. Verified in this analysis run.
