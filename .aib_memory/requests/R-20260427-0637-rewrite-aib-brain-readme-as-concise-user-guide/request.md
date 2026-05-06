## Goal
Rewrite `.aib_brain/README.md` to be a concise, user-friendly guide that helps a newcomer to AIB quickly understand how to work with the framework from a user standpoint. The current README is long; the new version must be shorter while still fully covering AIB functionality.

## Background
The `.aib_brain/README.md` serves as the primary user-facing guide for anyone working with the AIB framework in a workspace. As the framework has grown, the README has accumulated substantial detail that makes it hard to scan and consume quickly. Newcomers need a faster on-ramp.

## Scope

- Rewrite `.aib_brain/README.md` to be concise (target: ≤ 80 lines where possible) and readable.

- Preserve all user-facing functionality descriptions: prerequisites, quick start, daily flow, prompt invocations, use case scenarios, workspace instructions, question threshold, and request folder artifacts.

- Remove or condense repetitive prose while keeping all actionable steps.

- Keep all existing section headings or replace with equivalents that aid scannability.

## Out of scope
- No changes to any `.aib_brain/` assets other than `README.md`.
- No changes to prompts, conventions, tools, or templates.
- No functional changes to AIB behavior.

## Constraints
- The README must remain fully accurate with respect to the current AIB workflow.
- All prompt invocation strings must remain correct and copy-pasteable.

## Success criteria
- `.aib_brain/README.md` is shorter than the current version and easier to scan.
- All sections (Quick Start, Daily Flow, Prompts, Use Case Scenarios, Workspace Instructions, Question Threshold, Request Folder Artifacts) are represented.
- All automated tests in `tests/` pass.

## Assumptions
- A1: The new README will be a full replacement of the existing file.
  - Risk if false: partial edits could leave inconsistent content.
- A2: No tests reference the exact content of `.aib_brain/README.md` in a way that would break.
  - Risk if false: test failures on content-level checks.

## Plan

### Task 1: Rewrite .aib_brain/README.md
**Intent:** Replace the current README with a concise, well-structured user guide.
**Inputs:** Current `.aib_brain/README.md`, input.md request description.
**Outputs:** Updated `.aib_brain/README.md`.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Read the full current README.
2. Identify all sections to retain and condense.
3. Write new concise content that preserves all user-facing information.
4. Replace the file.
**Done Criteria:** File exists, is shorter than before, retains all functional sections.
**Dependencies:** None.
**Risk Notes:** None.

### Task 2: Update context.md
**Intent:** Reflect README changes in `.aib_memory/context.md`.
**Inputs:** Updated README, existing context.md.
**Outputs:** Updated `.aib_memory/context.md`.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Execute `aib-context.md` prompt to regenerate context.md.
**Done Criteria:** context.md updated and reflects new README structure.
**Dependencies:** Task 1.
**Risk Notes:** None.

### Task 3: Run tests
**Intent:** Verify no regression from the README change.
**Inputs:** Test suite in `tests/`.
**Outputs:** Test run results.
**External Interfaces:** None.
**Environment & Configuration:** Python venv active.
**Procedure:**
1. Run `pytest tests/`.
2. Confirm all tests pass.
**Done Criteria:** All tests pass.
**Dependencies:** Task 1.
**Risk Notes:** None.

## Documentation
- `.aib_memory/context.md` (ref_id: REF-0001) — update to reflect revised README structure.

## Questions & Decisions

## Code and Asset Scan for Impacted Components
- `.aib_brain/README.md` — primary target for rewrite.

## Internal Review of Request and Product Docs
The request is straightforward: rewrite one documentation file to be more concise while retaining all information. No cross-component risk.
