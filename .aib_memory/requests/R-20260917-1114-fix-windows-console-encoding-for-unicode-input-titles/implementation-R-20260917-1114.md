# Implementation R-20260917-1114

## Result

Fixed Unicode title output during Windows analysis preflight. The standard command `python -B .aib_brain/tools/input-header.py --workspace . --operation read` now emits UTF-8 without requiring a user environment-variable change. Valid titles and the eight-line key=value protocol are preserved.

## Root cause and reproduction

The screenshot diagnosis was confirmed on Windows with Python 3.13. The input file is read as UTF-8 and parsed correctly, but the original CLI prints the title using stdout's inherited encoding. With CP1252 stdout, the arrow in POS→NSR raises UnicodeEncodeError after the request_id line, returning exit code 1 and triggering the analysis prompt's tool-failure halt. The -B flag only prevents bytecode writes; it does not configure output encoding.

Before the fix, the focused CP1252 pipe reproduction produced 3 failures (arrow, Cyrillic/Japanese, emoji) and 1 passing ASCII case. The request file was not the cause.

## Changes

- Add common.configure_utf8_output and call it at CLI entry in input-header.py, verify-input.py, and verify-context.py before argument parsing or diagnostic output.
- Apply the same encoding to stdout and stderr, preserving text-only capture streams and leaving stdin untouched.
- Cover the later verify-context.py header echo and Unicode validation diagnostics so preflight does not immediately encounter another encoding failure.
- Keep parsing, validation, file serialization, title contents, and non-zero failure handling unchanged.
- Specify UTF-8 decoding for captured stdout/stderr in aib-analyze.md and the verifier test callers.
- Update the README, user guide, release note, context (exclusively through edit-context.py), and requirements history.

## Verification

- Before fix: 3 failed, 1 passed in the CP1252 pipe reproduction.
- After fix: 256 passed and 4 subtests passed across the selected tool, prompt, protection, bytecode, and guide suites.
- 68 focused regression cases cover ASCII, POS→NSR, Cyrillic/Japanese, emoji, accented text, CP1252/UTF-8/default environments, raw pipes, redirected files, explicit UTF-8 capture decoding, malformed/missing input, Unicode validation errors, Unicode stderr paths, and embedded capture streams.
- The S01.1a/S01.2 tool sequence (header read, input verification, context verification, header read) passes with Unicode titles and both enabled verification flags. This confirms progression beyond header reading; no separate AI-generated analysis/plan run was performed.
- Header reads preserve input.md byte-for-byte; verification preserves the title and Input body while updating only its existing verification-result fields.
- Updated workspace context passes all 12 verification checks.
- No additional dependencies or virtual environment were created.

Validation command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m pytest tests/test_input_header_encoding.py tests/test_verify_input.py tests/test_verify_context.py tests/test_verify_context_planned.py tests/test_tools_common.py tests/test_analysis_prompt_structure.py tests/test_bytecode_prevention.py tests/test_aib_brain_write_protection.py tests/test_authorization_propagation.py tests/test_user_guide_product_accuracy.py tests/test_questions_in_input_md.py -q --tb=short
```

## Authorization

Source: `.aib_memory/input.md ## Input`. The explicit request to fix the named framework tool and invocation authorizes the scoped framework-maintenance changes:

> Inspect `.aib_brain/tools/input-header.py` and its invocation in `.aib_brain/prompts/aib-analyze.md`, including `python -B .aib_brain/tools/input-header.py --workspace . --operation read`. Reproduce the failure with a Unicode title and CP1252 standard output, then implement a durable fix so the normal workflow handles Unicode without requiring users to set an environment variable manually. Preserve the original title and the existing machine-readable output format, and ensure any subprocess output is decoded consistently. Keep valid request data intact and retain error handling for actual parsing or validation failures.

## Scope audit

The protected paths touched by this run are:

- .aib_brain/README.md
- .aib_brain/prompts/aib-analyze.md
- .aib_brain/tools/common.py
- .aib_brain/tools/input-header.py
- .aib_brain/tools/verify-context.py
- .aib_brain/tools/verify-input.py
- .aib_brain/user_guide.html

The pre-existing aib-setup.yaml edit is preserved outside the implementation commit. Existing framework bytecode files dated August 19, 2026 are untouched. The supplied screenshot and input are archived with this request by the normal finalization workflow.
