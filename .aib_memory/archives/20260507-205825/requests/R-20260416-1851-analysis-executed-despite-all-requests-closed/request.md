# Request

## Goal

User reported: I accidently closed the active request, but after running analysis, it still performed it.
The intended behavior should be: No active requests, no work is conducted.

Fix the bug.

## Background

The `create-analysis` action is driven by the AI prompt file `.aib_brain/prompts/aib-analysis.md`. `Concepts.md` normatively requires this action to fail when no Active request exists: "If no `Active` request exists and no explicit `request_id` is provided, execution MUST fail with a validation error and MUST NOT create output files."

The prompt's mandatory preflight step 1 ("Resolve active request") implies finding an Active request but provides no explicit HALT directive when none is found. As a result, the AI model may proceed, producing analysis artifacts for a Closed request or in an indeterminate state.

Tool scripts in `.aib_brain/tools/` correctly enforce this rule via `resolve_active_request_or_explicit()` in `common.py`. The gap is exclusively in the prompt file.

## Scope

- `.aib_brain/prompts/aib-analysis.md` — add an explicit preflight halt gate: if no Active request is found in `requests_register.md`, STOP immediately and report an error; do not produce any output files.

- `.aib_brain/prompts/aib-implement.md` — add an identical preflight halt gate: if no Active request is found in `requests_register.md`, STOP immediately and report an error; do not produce any output files.

## Out of scope

- `.aib_brain/tools/` — tool scripts already enforce the halt via `resolve_active_request_or_explicit()`; no changes needed.

- `.aib_brain/tools/menu.py` — UI-layer visibility filtering already guards menu actions; no changes needed.

## Constraints

- `.aib_brain/` assets must not be modified by tool scripts. The fix is applied directly by the AIB Maintainer (human) to the prompt file.

- The fix must not alter the existing preflight structure beyond inserting the halt gate as the first preflight check.

- The fix must preserve normal analysis flow when exactly one Active request exists.

## Success criteria

- `aib-analysis.md` preflight step 1 contains an explicit, unambiguous halt gate: if `requests_register.md` has no row with `state = Active`, execution stops immediately with a clear human-readable error and no output files are written.

- `aib-implement.md` input resolution block contains an identical halt gate: if `requests_register.md` has no row with `state = Active`, execution stops immediately with a clear human-readable error and no output files are written.

- Running either prompt with no Active request produces the error message and no output file changes.

- Running either prompt with one Active request proceeds normally (regression check).

## Assumptions

- A1: The bug manifests exclusively in the two prompt files (`aib-analysis.md`, `aib-implement.md`); no tool script changes are needed.
  - Risk if false: If a tool script also bypasses the check, additional files must be patched.

- A2: The intended halt gate applies globally — not only when all requests are Closed, but also when the user attempts to run a prompt without any Active request (e.g., immediately after initialization before creating a request).
  - Risk if false: A narrower condition (Closed-only) would require a different gate expression; however, the normative contract supports the broader condition.

- A3: The same halt gate pattern (zero Active → error; >1 Active → inconsistency error) is appropriate for both `aib-analysis.md` and `aib-implement.md` since both prompts have the same normative requirement.
  - Risk if false: If one prompt requires different error messaging, the wording would need minor adjustment — but the structure and behaviour remain identical.

## Plan

### Task 1: Add explicit preflight halt gate to `aib-analysis.md`
**Intent:** Insert an unambiguous STOP directive at the start of the mandatory preflight in `aib-analysis.md` so the AI halts when no Active request exists.

**Inputs:** `.aib_brain/prompts/aib-analysis.md` (current content), `Concepts.md` (normative contract), `common.py` `resolve_active_request_or_explicit()` (reference implementation logic)

**Outputs:** Updated `.aib_brain/prompts/aib-analysis.md` with halt gate inserted as the first preflight step.

**External Interfaces:** None — file-only change.

**Environment & Configuration:** No environment variables or secrets involved.

**Procedure:**
1. Read `.aib_brain/prompts/aib-analysis.md` in full.
2. Locate the `Mandatory preflight (MUST):` block.
3. Rewrite step 1 to explicitly read `requests_register.md` and halt with a specified error message if no Active row is found.
4. Ensure the halt gate also covers the case of multiple Active rows (register inconsistency).
5. Renumber remaining preflight steps.
6. Write the updated file.

**Done Criteria:**
- `aib-analysis.md` preflight step 1 contains an explicit HALT block for the no-active-request condition.
- HALT block specifies the exact error message to output.
- HALT block explicitly states: "Do NOT proceed to any subsequent step. Do NOT write any output files."
- Existing preflight steps are renumbered but unchanged in intent.

**Dependencies:** None.

**Risk Notes:** None — single-file prompt change with no side effects.

### Task 2: Add explicit preflight halt gate to `aib-implement.md`
**Intent:** Insert an identical STOP directive at the start of the `Input resolution` block in `aib-implement.md` so the AI halts when no Active request exists.

**Inputs:** `.aib_brain/prompts/aib-implement.md` (current content), `Concepts.md` (normative contract)

**Outputs:** Updated `.aib_brain/prompts/aib-implement.md` with halt gate inserted as the first item in the Input resolution block.

**External Interfaces:** None — file-only change.

**Environment & Configuration:** No environment variables or secrets involved.

**Procedure:**
1. Read `.aib_brain/prompts/aib-implement.md` in full.
2. Locate the `Input resolution:` block.
3. Insert a new bullet before the existing first bullet that reads `requests_register.md` and halts with the specified error message if no Active row or multiple Active rows are found.
4. Write the updated file.

**Done Criteria:**
- `aib-implement.md` `Input resolution` block contains an explicit HALT bullet for the no-active-request condition.
- HALT block specifies the exact error message to output.
- HALT block explicitly states: "Do NOT proceed to any subsequent step. Do NOT write any output files."
- Remaining input resolution items are unchanged in intent.

**Dependencies:** None.

**Risk Notes:** None — single-file prompt change with no side effects.

## Testing

- T1 — analysis halt gate present: Verify `.aib_brain/prompts/aib-analysis.md` preflight step 1 contains an explicit HALT/STOP directive. Expected outcome: Step 1 includes zero-Active and multiple-Active error conditions with explicit "Do NOT proceed" language.

- T2 — implement halt gate present: Verify `.aib_brain/prompts/aib-implement.md` `Input resolution` block contains an identical explicit HALT directive as its first item. Expected outcome: The block includes zero-Active and multiple-Active error conditions with explicit "Do NOT proceed" language.

- T3 — analysis halts on zero Active: With no Active request in register, invoke `aib-analysis.md`. Expected outcome: AI outputs "No active request found. Execution halted." and produces no `analysis.md` or `request.md` changes.

- T4 — implement halts on zero Active: With no Active request in register, invoke `aib-implement.md`. Expected outcome: AI outputs "No active request found. Execution halted." and produces no `implementation.md` or other output file changes.

- T5 — analysis halts on multiple Active: Edit `requests_register.md` to temporarily have two Active rows and run `aib-analysis.md`. Expected outcome: AI outputs the register inconsistency error and produces no output.

- T6 — implement halts on multiple Active: Same two-Active-row state; run `aib-implement.md`. Expected outcome: AI outputs the register inconsistency error and produces no output.

- T7 — analysis normal flow regression: With exactly one Active request, run `aib-analysis.md`. Expected outcome: Analysis proceeds normally; `analysis.md` is created and `request.md` is updated.

- T8 — implement normal flow regression: With exactly one Active request, run `aib-implement.md`. Expected outcome: Implementation proceeds normally; `implementation.md` is updated.

## Documentation

- .aib_memory/context.md (ref_id: REF-0001) — update to reflect the preflight halt gate addition to both `aib-analysis.md` and `aib-implement.md` under Requirements Summary (FR-004, FR-005) and Prompt actions technical design section.
