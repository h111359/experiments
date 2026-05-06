# Proposals — AIB Framework Improvement

Request: R-20260402-1858 | Iteration: 01 | Date: 2026-04-02

Numbered (not sequentially), categorized, self-contained improvement proposals for the AI Builder (AIB) framework.
Each proposal identifies the area, the specific problem, and the concrete change to make.
Proposals marked `[.aib_brain]` require changes inside `.aib_brain/` and must be actioned in a separate request.

---

## Category: Prompt

---

**Proposal 1**
- Category: Prompt
- Area: `.aib_brain/prompts/aib-update-documentation.md`
- Problem: The Mandatory Preflight section contains a duplicate "2." list item. Steps 2a and 2b are both numbered `2.`, causing agents to potentially skip one silently and violating determinism.
- Concrete change `[.aib_brain]`: Renumber all preflight steps sequentially. The compound step that reads references and builds two sets (required-read and target-edit) must be split into discrete numbered lines (1, 2, 3, 4, 5, 6). Each numbered line must represent exactly one atomic action. Acceptance signal: no two preflight steps share the same number.

---

**Proposal 2**
- Category: Prompt
- Area: `.aib_brain/prompts/aib-create-analysis.md`
- Problem: The auto-trigger rule for `create-questionnaire` states "Auto-triggers create-questionnaire when unresolved questions exist." The trigger condition "unresolved questions exist" is subjective and interpreted differently by different models, breaking determinism.
- Concrete change `[.aib_brain]`: Replace the vague trigger condition with an explicit rule: "Auto-triggers `create-questionnaire` if and only if section 13 (Open Questions & Next Actions) of the generated analysis contains at least one item whose owner is `User` or for which no concrete resolution path is provided." Acceptance signal: trigger condition is a single binary test expressed in one sentence.

---

**Change 4**
- Category: Prompt
- Area: `.aib_brain/prompts/aib-implement.md`
- Problem: The logging requirement lists the minimum implementation.md entry fields inline: "Include: iteration ID, implemented changes, tests run/results, outcome, and follow-ups." This duplicates the authoritative field schema in `implementation-convention.md`, and the two may drift over time.
- Concrete change `[.aib_brain]`: Replace the inline field list with a single delegating rule: "Append a new Entry to `implementation.md` following the exact Entry Block Format defined in `.aib_brain/conventions/implementation-convention.md`. Do not reproduce the field schema here." Acceptance signal: no field list in the prompt; a single reference to the convention file.


**Change 8**
- Category: Convention
- Area: `.aib_brain/Concepts.md`
- Problem: Concepts.md describes questionnaire answers as "A, B, C, D + Other" lettered checkboxes, but the `questionnaire-convention.md` defines a richer QID-based block format (QID, Intent, Rationale, Options with labels, Recommended flag). New contributors reading Concepts.md get an outdated mental model that conflicts with the actual convention.
- Concrete change `[.aib_brain]`: In Concepts.md, replace the questionnaire description that mentions "A, B, C, D + Other" with a reference: "Questionnaire structure and answer format are governed by `.aib_brain/conventions/questionnaire-convention.md`, which defines the QID-based canonical Question Block format. Refer to that convention for the authoritative schema." Remove any inline description of A/B/C/D format. Acceptance signal: Concepts.md contains no A/B/C/D questionnaire framing; a single reference to the convention is present.

**Change 10**
- Category: Convention
- Area: `.aib_brain/conventions/analysis-convention.md`, section 4.7 "Research Plan and Findings"
- Problem: Section 4.7 requires "Methodology used," "Evidence summary," "Gaps and unknowns," and "Proposed validation actions," but it does not require listing which files were actually read. Analysis artifacts therefore cannot be audited to confirm the AI read the required-read set.
- Concrete change `[.aib_brain]`: Add a required sub-section "Files Read" to section 4.7 with rule: "Provide a bullet list of every file read during the research phase. Each bullet must state: the file path (workspace-relative) and a one-line note on what was found or confirmed. If a product-doc was skipped due to scope filtering (per context-window management), mark it as `[SKIPPED — context limit]` or `[SKIPPED — domain out of scope]`." Acceptance signal: 4.7 in the convention includes a "Files Read" sub-section with the specified format.

## Category: Tool

**Proposal 16**
- Category: Tool
- Area: `.aib_brain/tools/menu.py`, function `_detect_copilot_cli`
- Problem: `_detect_copilot_cli()` is called during menu initialization and runs a subprocess with a 5-second timeout. On machines where `gh` is not installed, this blocks the menu for up to 5 seconds before anything renders, creating a poor user experience.

## Category: Organization / Concept

---

**Proposal 18**
- Category: Organization
- Area: `.aib_brain/tools/menu.py`, `.aib_brain/tools/menu_config.json`
- Problem: `PROMPT_ACTIONS` list in `menu.py` hardcodes prompt action metadata (id, title, description, prompt_file) at the Python level, while `menu_config.json` defines script-based action metadata. Adding a new prompt action requires editing `menu.py` in Python. This creates a dual-maintenance burden and requires Python knowledge for what should be a configuration change.
- Concrete change `[.aib_brain]`: Eliminate the need of `menu_config.json` and remove this file. The menu is dynamic and will not be defined by a static json file.

---

**Proposal 19**
- Category: Organization
- Area: `docs/Development_and_Deployment_Specification.md`, § 7 Deployment Procedure
- Problem: The `logs/` directory at workspace root contains version history that is of ongoing value, but `docs/Development_and_Deployment_Specification.md` does not explicitly list it among files preserved across `.aib_brain/` upgrades. Since the spec says `.aib_brain/` is replaceable wholesale, a careless upgrade could delete or neglect the logs folder.
- Concrete change: Add a bullet to `docs/Development_and_Deployment_Specification.md` § 7 (Deployment Procedure): "The `logs/` directory at workspace root MUST be preserved across `.aib_brain/` upgrades and MUST NOT be deleted or modified during the upgrade procedure." Add a corresponding item to the § 10 Compliance Checklist: `[ ] logs/ directory preserved and not modified by the upgrade.` Acceptance signal: both the procedure text and the checklist contain explicit preservation rules for `logs/`.

---

**Proposal 21**
- Category: Organization
- Area: `.aib_brain/tools/common.py`, `.aib_brain/tools/create-request.py` and other scripts that consume `request.md`
- Problem: `request-convention.md` defines six required sections in `request.md` and states that `create-analysis`, `create-questionnaire`, and `create-plan` MUST fail if validation fails. However, no `validate_request_md` function exists in `common.py`, and none of the scripts perform this validation. Malformed requests silently proceed through the lifecycle. Exclude behavior insructions from `request-convention.md` - it should define the structure, not requirement for validation or failure

---

**Proposal 24**
- Category: Organization
- Area: `.aib_brain/README.md`
- Problem: Users don't have clear guidance on when to create a new iteration (within the same request) versus closing the current request and opening a new one. This leads to either over-long request chains with scope drift, or fragmented requests covering related work.
- Concrete change `[.aib_brain]`: Add a "When to Create a New Iteration vs a New Request" section to the README with the following decision criteria: create a new iteration when the goal stays the same but new information (answers, blockers, discoveries) requires a revised plan; create a new request when the goal changes, the scope of the original request has been completed, or a follow-up action is independent enough to stand on its own. Include three illustrative scenarios labeled: "Same goal, new info → new iteration," "Goal completed, related follow-up → new request," "Unrelated change discovered mid-request → new request." Acceptance signal: README section exists with decision criteria and three labeled scenarios.

---

## Category: Best Practice

---

## Category: Pitfall

---

**Proposal 28**
- Category: Pitfall
- Area: `.aib_brain/tools/initialize.py`
- Problem: `initialize.py` is idempotent for `requests_register.md` (skips if exists) but always overwrites `references.md` on every invocation. If a user has added custom rows to `references.md` (user-added source code or domain document references), re-running `initialize.py` silently destroys those customizations.
- Concrete change `[.aib_brain]`: Apply the same skip-if-exists guard to `references.md` that already exists for `requests_register.md`: if `.aib_memory/references.md` already exists, skip overwrite and print `"references.md already exists — skipping overwrite."` Add a `--force` flag to `parse_args()` that, when provided, allows overwriting both files. Update the README "Common Commands" section to document `--force`. Acceptance signal: re-running `initialize.py` on a workspace with an existing `references.md` skips it; `--force` overwrites; unit test covers both paths.

---

**Proposal 29**
- Category: Pitfall
- Area: `.aib_brain/tools/common.py` function `slugify`, `.aib_brain/tools/create-request.py`
- Problem: `slugify` falls back to `"request"` when no alphanumeric characters remain after transformation (e.g., title `"!!! ???"` slugifies to `"request"`). This creates a folder named `R-<id>-request` silently, w2222hich is ambiguous and may collide with other degenerate-title requests. The user is not informed of the substitution.
- Concrete change `[.aib_brain]`: In `create-request.py`, after computing the slug, add a validation step: if the original title contains no ASCII letter (`[a-zA-Z]`), raise `ValidationError("Title must contain at least one letter to generate a meaningful slug.")`. Do not change `slugify` itself (it is a pure function used elsewhere). Add a unit test: `create-request` with title `"123 !!!"` raises ValidationError; `create-request` with `"Fix bug"` succeeds. Acceptance signal: ValidationError raised for letter-free titles; unit test passes.

**Proposal 30**
Area: .aib_brain/tools/common.py, function slugify
Problem: slugify has no maximum length guard. A long request title produces a folder name that, combined with the full workspace path, can exceed the Windows MAX_PATH limit of 260 characters, causing silent file creation failures on Windows.
Concrete change [.aib_brain]: Add a max_length: int = 64 parameter to slugify. After generating the slug, truncate to max_length characters and strip trailing hyphens: result = lowered[:max_length].rstrip("-"). Update the caller in create-request.py to pass max_length=64. Add a unit test: assert len(slugify("a" * 200)) <= 65. Acceptance signal: slugify("a" * 200) returns a string ≤ 64 characters; unit test passes.