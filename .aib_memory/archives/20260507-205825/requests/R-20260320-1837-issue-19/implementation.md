# Implementation Log

Append-only entries. Add a new section for every execution update.

## Entry Template

### [YYYY-MM-DD HH:mi] Iteration [ID]

#### Implemented changes

#### Technical notes

#### Verification steps

#### Evidences for done

#### End result summary

#### Guidance for human how to verify

### 2026-03-20 21:01 Iteration 03

#### Implemented changes
- Updated authoritative product-doc -> convention mapping documentation and normalized mapping paths to `/`.
- Added deterministic convention resolution rule (requirement-id from filename -> `.aib_brain/conventions/<id-lower>-convention.md`) and documented fail-closed behavior.
- Updated prompts so that, before any product-doc edits, the workflow reads the mapping + all per-doc conventions and fails deterministically if any mapping/convention is missing.

#### Technical notes
- Mapping source of truth remains `.aib_brain/conventions/product-documentation-convention.md` (explicit and reviewable).
- Prompts enforce: mapping-row presence AND convention-file readability as a hard preflight gate.
- Exception documented: this iteration modifies specific `.aib_brain/` prompt/convention files because the active request scope explicitly required it.

#### Verification steps
- Ran `python .aib_memory/requests/R-20260320-1837-issue-19/validate_product_doc_conventions.py`.

#### Evidences for done
- Validator output: `OK: validated 27 product-doc entries`.
- Prompts now explicitly require reading/enforcing per-document conventions with deterministic fail-closed behavior.

#### End result summary
Product documentation governance now has an explicit, auditable mapping to per-document conventions and prompt-level enforcement to read/apply those conventions before editing.

#### Guidance for human how to verify
- Open `.aib_brain/prompts/aib-update-documentation.md` and `.aib_brain/prompts/aib-implement.md` and confirm they require reading `.aib_brain/conventions/product-documentation-convention.md` plus all per-doc convention files before any product-doc edits.
- Re-run the validator script above; it should continue to pass unless a mapping/convention file is removed or renamed.
