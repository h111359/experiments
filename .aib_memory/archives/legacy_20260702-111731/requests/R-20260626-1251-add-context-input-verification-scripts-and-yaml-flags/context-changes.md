# Context Changes — R-20260626-1251

## Requirements

- [I] MUST: verify-context.py MUST be updated whenever context-convention.md quality gates are changed.
- [I] MUST: verify-input.py MUST be updated whenever input-convention.md validation rules are changed.

## Solution

- [D] verify-context.py validates context.md format compliance against context-convention.md with the 6-section check set.
- [I] verify-context.py validates context.md format compliance against context-convention.md with a 10-check validation set.
- [D] input.md YAML frontmatter header fields: request_id (~ when idle), title (~ when idle), state (idle|analysis_ready|questions_generated), options.minimum_questions (integer, default 0).
- [I] input.md YAML frontmatter header fields: request_id (~ when idle), title (~ when idle), state (idle|analysis_ready|questions_generated), options.minimum_questions (integer, default 0), input_verification_enabled (bool, default true), input_verification_result (null/valid/invalid, default null), context_verification_enabled (bool, default true), context_verification_result (null/valid/invalid, default null).
- [I] verify-input.py validates input.md YAML header, mandatory body sections, and Q-block format against input-convention.md and q-block-convention.md, exiting with code 0 on all checks passing and code 1 on any failure.
- [I] aib-analyze.md invokes verify-input.py and verify-context.py within S01 preflight (after reading instructions.md) when their respective enabled flags are true; on failure halts with per-check fix suggestions.
- [I] menu.py verify_input and verify_context commands run the respective verification scripts, update YAML result flags in input.md, and are hidden from the menu when their enabled flag is false.

## File Structure

- [U] .aib_brain/tools/ line: add verify-input.py to the Python scripts list (after verify-context.py).
- [U] .aib_brain/conventions/ line: note input-convention.md alongside existing convention files.

