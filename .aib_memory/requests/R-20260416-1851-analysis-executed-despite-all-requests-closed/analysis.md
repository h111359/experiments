## Executive Summary

- **Request ID:** R-20260416-1851

- **Request title:** analysis executed despite all requests closed

- **High-level purpose:** Fix a bug where the `create-analysis` action proceeds despite no Active request existing in the workspace register. The normative contract in `Concepts.md` requires `create-analysis` to HALT when no Active request is found; the `aib-analysis.md` prompt's preflight step 1 does not enforce this with an explicit stop directive.

- **Root cause:** `aib-analysis.md` preflight step 1 states "Resolve active request" but provides no explicit HALT gate when the register contains no Active row. The AI resolves the instruction loosely and may proceed, violating the determinism and safety rules of the invocation contract.

- **Contrast with tool scripts:** `common.py` → `resolve_active_request_or_explicit()` does correctly raise `ValidationError("No active request found; ...")` for Python-backed actions. The gap is prompt-side only.

- **Impact scope:** Single file change — add an explicit, unambiguous preflight halt guard to `aib-analysis.md`.

- **`request.md` updates applied during this analysis run:** Background, Scope, Out of scope, Constraints, and Success criteria populated. Assumptions, Plan, Testing, and Documentation sections appended.

---

## Domain Knowledge Essentials

- **Active request:** A request row in `.aib_memory/requests_register.md` with `state = Active`. At most one may exist at any time.

- **Closed request:** A terminal state for a request. No workflow actions should operate on a Closed request unless an explicit `--request-id` override is provided.

- **Preflight gate:** A mandatory pre-condition check that runs before any substantive output is produced. If the gate condition is not met, execution MUST stop with a human-readable error and MUST NOT leave partial writes.

- **Prompt-driven workflow:** An AIB action executed by an AI model following the instructions in a `.aib_brain/prompts/*.md` file. These are invoked directly in an AI coding interface, bypassing the `menu.py` shell launcher and its state-based visibility filtering.

- **AIB Maintainer:** The human who owns and edits `.aib_brain/` assets. Tool scripts must not modify `.aib_brain/`.

- **Impacted roles/personas:** Developer (runs analysis prompts in AI interface), AI Automation Agent (executes prompt instructions), AIB Maintainer (applies the fix to the prompt file).

- **Impacted business processes:** `create-analysis` workflow; any downstream `implement` runs that depend on a valid, active-scoped analysis.

- **Acceptance impact:** Without the fix, an analysis executed on a Closed request produces artifacts in the wrong request folder or no folder at all, corrupting the workspace state or generating misleading implementation guidance.

---

## Technical Knowledge & Terms

- **`aib-analysis.md`:** The AI prompt file at `.aib_brain/prompts/aib-analysis.md` that drives the `create-analysis` action. It defines mandatory preflight steps, requirements, and output rules for `analysis.md` and `request.md` updates.

- **`requests_register.md`:** A Markdown table at `.aib_memory/requests_register.md` tracking all requests with columns: `request_id`, `title`, `folder`, `state`, `created_at`, `closed_at`.

- **`resolve_active_request_or_explicit()`:** Python function in `.aib_brain/tools/common.py` (lines ~133–161). Enforces the halt guard for tool scripts by raising `ValidationError` when no Active row exists and no explicit `--request-id` is supplied.

- **`filter_visible_actions()`:** Function in `.aib_brain/tools/menu.py` that controls which menu items are visible based on `MenuState.has_active_request`. Prevents the `close-request` action from appearing when no Active request exists — but this is a UI-layer control only, not applicable to prompt-driven actions.

- **Mandatory preflight:** Ordered required checks declared in a prompt file. All steps must pass before any output file is written. Failure at any step must terminate execution.

- **Fail-closed:** The AIB safety posture — if a required condition cannot be confirmed, do not proceed and do not write partial output.

- **HALT directive:** An explicit instruction in a prompt to stop processing, output a specified error message, and return without producing any analysis or update artifacts.

- **Evidence log:**

  | Evidence | Implication |
  | --- | --- |
  | `Concepts.md` § "Common input resolution rules": "If no `Active` request exists and no explicit `request_id` is provided, execution MUST fail with a validation error and MUST NOT create output files." | The normative contract is already defined; the prompt is out of compliance. |
  | `Concepts.md` § "Workflow guardrails": "`create-analysis` and `implement` MUST fail when no request is `Active`..." | Confirms both `aib-analysis.md` and `aib-implement.md` should have explicit halt gates. |
  | `aib-analysis.md` preflight step 1: "Resolve active request." | No STOP/HALT instruction present when resolution fails. |
  | `common.py` `resolve_active_request_or_explicit()`: raises `ValidationError("No active request found...")` | Tool scripts comply; prompt does not. |
  | `menu.py` `filter_visible_actions()`: hides lifecycle scripts based on `has_active_request` | UI layer guard only; prompt invocations bypass the menu. |

- **Files read during this analysis:**
  - `.aib_memory/references.md`
  - `.aib_memory/context.md` (REF-0001)
  - `.aib_brain/Concepts.md` (REF-0002)
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/prompts/aib-analysis.md`
  - `.aib_brain/prompts/aib-implement.md`
  - `.aib_brain/tools/common.py`
  - `.aib_brain/tools/menu.py`
  - `.aib_memory/requests_register.md`
  - `.aib_memory/requests/R-20260416-1851-analysis-executed-despite-all-requests-closed/request.md`

---

## Research Results

### 1. Internal review of `request.md` and relevant docs

The user-reported scenario: the active request was accidentally closed; subsequently, `aib-analysis.md` was executed and the analysis ran anyway. This implies the AI found no Active request but did not halt — it likely resolved the most recently modified Closed request folder or proceeded without a valid request context.

`Concepts.md` (domain doc, `edit_allowed=N`) states explicitly:
- "If no `Active` request exists and no explicit `request_id` is provided, execution MUST fail with a validation error and MUST NOT create output files."
- "`create-analysis` and `implement` MUST fail when no request is `Active` unless `request_id` is explicitly provided and valid."

`aib-analysis.md` mandatory preflight step 1 reads only: "Resolve active request." There is no subsequent instruction: "If resolution fails (no Active row), STOP with error — do not proceed." This omission is the direct cause of the bug.

### 2. Code and asset scan for impacted components

- `.aib_brain/tools/common.py`: `resolve_active_request_or_explicit()` correctly raises `ValidationError` on no Active request. Tool scripts are compliant.
- `.aib_brain/tools/menu.py`: `resolve_menu_state()` and `filter_visible_actions()` control menu visibility. `SCRIPT_CLOSE_REQUEST` only appears when `has_active_request` is True. This does not protect prompt-driven invocations.
- `.aib_brain/prompts/aib-analysis.md`: Missing explicit HALT directive. **This is the defect location.**
- `.aib_brain/prompts/aib-implement.md`: Also says "Resolve active request from `.aib_memory/requests_register.md`..." without an explicit HALT gate. A secondary finding — out of scope for this request but analogous risk.
- `.aib_brain/prompts/aib-context.md`: No active-request dependency; not affected.

### 3. Pattern scan against organizational standards and prior solutions

AIB conventions apply a fail-closed posture throughout. The `analysis-convention.md` section 7 ("Determinism Rules") states: "If request ambiguity exists that cannot be resolved internally, create a `Q<nnn>` question block in `request.md`." The `Concepts.md` invocation contract mandates validation failure on no-Active-request. The fix pattern is established and just needs to be wired into the prompt preflight.

### 4. External benchmarking

Not applicable. This is an internal prompt engineering / framework consistency issue.

### 5. Minimal spike

The fix requires inserting a single conditional HALT block into the preflight section of `aib-analysis.md`. The block must appear as the first check (before any file reads or output writes) and must:
1. Read `requests_register.md`.
2. Check whether any row has `state = Active`.
3. If none: output a clear error, do NOT proceed, do NOT write any files.
4. If exactly one: continue as normal.
5. If more than one: fail with a different error (register inconsistency).
