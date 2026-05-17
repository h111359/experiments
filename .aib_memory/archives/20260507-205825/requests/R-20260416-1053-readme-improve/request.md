# Request

## Goal

Review `.aib_brain\README.md`. Check for obsolete information. Try to make it easyer for reading and explaining all the finctionality of AIB in short and memorable way.

## Background

`.aib_brain/README.md` is the primary user guide for working with the AIB framework. As AIB has evolved — deprecating iterations, introducing the `create-analysis` step, and stabilising the canonical 5-step workflow — the guide may contain gaps or structural noise that reduce its usefulness as a first-read reference. The goal is to align the README with the current state of the framework and improve its clarity.

## Scope

- Review `.aib_brain/README.md` for obsolete, inaccurate, or missing content.

- Update the Typical Daily Flow to reflect the canonical 5-step workflow (initialize → create-request → create-analysis → implement → close-request).

- Consolidate or remove redundant content (duplicate Quick Start text blocks; overlapping Scenarios 3 and 4).

- Improve overall structure and phrasing so a new user can understand the core AIB workflow after a single read.

## Out of scope

- Changes to tool scripts, prompt files, or any file other than `.aib_brain/README.md`.

- Changes to the root `README.md`.

- Adding new AIB functionality or new prompt/tool scripts.

- Changes to `.aib_memory/` artifacts.

## Constraints

- The revised README must be accurate with respect to current tool scripts and prompt files on disk.

- Content must remain in Markdown format.

- The document should be concise; avoid expanding it beyond what is needed to convey the workflow clearly.

## Success criteria

- No obsolete or inaccurate content remains in `.aib_brain/README.md`.

- The Typical Daily Flow matches the canonical 5-step workflow described in `Concepts.md` and `context.md`.

- Redundant content (duplicate Quick Start blocks, overlapping scenarios) is consolidated.

- A developer unfamiliar with AIB can understand the complete workflow from a single read of the document.

## Assumptions

- A1: The current README Typical Daily Flow was written before the `create-analysis` step was formalised and has not been updated since.
  - Risk if false: The flow section is intentionally minimal and the analysis step should remain omitted from it.

- A2: The two Quick Start code blocks showing menu output text are redundant and one can be removed without loss of information.
  - Risk if false: Both blocks serve distinct pedagogical purposes and must both be retained.

- A3: Scenarios 3 and 4 can be merged into a single scenario since both describe running `aib-context.md` as a standalone action, with only a minor difference in framing.
  - Risk if false: The "after implementation" framing and the "standalone, fresh summary" framing have distinct audiences and should remain as separate scenarios.

## Plan

### Task 1: Audit `.aib_brain/README.md` for obsolete and missing content
**Intent:** Identify every inaccuracy, omission, and redundancy in the current README against the canonical AIB workflow.
**Inputs:** `.aib_brain/README.md`, `.aib_memory/context.md`, `.aib_brain/Concepts.md`, `.aib_brain/prompts/` file listing, `.aib_brain/tools/` file listing
**Outputs:** Inline annotations / mental model of changes needed (no file output; feeds Task 2)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read the current README.
2. Compare the Typical Daily Flow against the canonical 5-step flow in context.md.
3. Verify all listed prompt file paths against `.aib_brain/prompts/` directory.
4. Verify all listed tool file paths against `.aib_brain/tools/` directory.
5. Identify structural redundancies (duplicate blocks, overlapping scenarios).
6. Note any missing actions (e.g., `create-analysis` absent from flow).
**Done Criteria:** A complete, traceable list of changes to make is established.
**Dependencies:** None
**Risk Notes:** None — read-only audit.

### Task 2: Rewrite `.aib_brain/README.md`
**Intent:** Produce a revised README that is accurate, non-redundant, and readable for a new AIB user.
**Inputs:** Findings from Task 1; current `.aib_brain/README.md`; canonical workflow from `context.md`
**Outputs:** Updated `.aib_brain/README.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Update the Typical Daily Flow to include `create-analysis` (optional) and `implement` steps.
2. Remove one of the two redundant Quick Start menu output text blocks.
3. Merge Scenarios 3 and 4 into a single "Regenerate / update workspace context" scenario.
4. Add a short framing note to major sections to improve first-read memorability.
5. Verify all tool and prompt file paths are still accurate after edits.
6. Confirm the overall document length is reduced or comparable; no new bloat introduced.
**Done Criteria:** `.aib_brain/README.md` accurately reflects the canonical 5-step workflow; redundant blocks removed; all paths verified accurate.
**Dependencies:** Task 1
**Risk Notes:** Rewrite must not remove genuinely useful content (Troubleshooting, copy-paste invocations).

## Testing

- T1 — File exists: `.aib_brain/README.md` is present after editing. Expected outcome: file is readable and non-empty.

- T2 — Flow completeness: The Typical Daily Flow section contains all five canonical steps (initialize, create-request, create-analysis, implement, close-request). Expected outcome: all five steps appear, with `create-analysis` marked optional.

- T3 — Prompt path accuracy: Each prompt file path listed in the README (`aib-analysis.md`, `aib-context.md`, `aib-implement.md`) exists under `.aib_brain/prompts/`. Expected outcome: no 404 / file-not-found for any listed path.

- T4 — Tool path accuracy: Each tool listed under Common Commands (`initialize.py`, `create-request.py`, `close-request.py`) exists under `.aib_brain/tools/`. Expected outcome: all three files present on disk.

- T5 — No deprecated tool references: No mention of `create-iteration.py` or `close-iteration.py` appears in the updated README. Expected outcome: grep finds zero matches.

- T6 — Redundancy removed: Only one Quick Start menu output text block remains. Expected outcome: the README does not contain two `AI Builder terminal command menu` code blocks.

- T7 — Scenario consolidation: Scenarios formerly numbered 3 and 4 (both about `aib-context.md`) are consolidated into a single scenario. Expected outcome: the word "Regenerate" appears as a scenario heading at most once.

- T8 — Re-run idempotency: Re-running this analysis with the same request state produces the same analysis intent. Expected outcome: same findings, same plan structure.

## Documentation

- `.aib_brain/README.md` (ref_id: N/A) — Primary target of this request; requires content review and restructuring to reflect current AIB workflow.
