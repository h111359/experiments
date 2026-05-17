# Analysis: R-20260510-1901 — Attachments: scan subdirs recursively and add menu hint

## Executive Summary

- **Request ID:** R-20260510-1901
- **Title:** Attachments: scan subdirs recursively and add menu hint

- **Purpose:** Two tightly related UX improvements to the AIB framework: (1) replace the flat-scan behaviour in `aib-analysis.md` with a recursive walk so that files in subdirectories of `.aib_memory/attachments/` are read and moved correctly; (2) add a short one-line reminder about the attachments folder to the menu guidance messages displayed when the developer is prompted to write into `input.md`.

- **Scope of change:** The change touches two source files (`aib-analysis.md`, `menu.py`), one product-context document (`context.md`), and two test files (`test_analysis_prompt_structure.py`, `test_menu.py`). No Python tool scripts, no workflow scripts, and no test fixtures are structurally changed.

- **Impact classification:** Low risk, isolated textual edits in two narrow locations per file. No new external dependencies. No state or filesystem schema changes.

- **Analysis added to `request-R-20260510-1901.md`:** Sections `## Assumptions`, `## Plan`, and `## Documentation` were appended/replaced during this analysis run.

- **Files read during this analysis run:**
  - `.aib_memory/instructions.md`
  - `.aib_memory/requests_register.md`
  - `.aib_memory/input.md`
  - `.aib_brain/prompts/aib-analysis.md`
  - `.aib_brain/tools/menu.py`
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_memory/context.md`
  - `tests/test_menu.py` (partial)
  - `tests/test_analysis_prompt_structure.py` (partial)

---

## Domain Knowledge Essentials

- **AIB (AI Builder):** A minimal, model-agnostic specification-driven development framework operating entirely within a repository workspace. All state is file-based; there are no databases or cloud services.

- **`.aib_memory/attachments/`:** A staging folder where developers place supplementary files (screenshots, specs, data samples) to accompany their `input.md` request description. These files are read by the AI agent at analysis time and moved to the request archive afterwards.

- **Flat scan:** A directory traversal that lists only the direct children of a directory, ignoring any subdirectories and their contents. This is the current behaviour specified in `aib-analysis.md` for the attachments folder.

- **Recursive walk:** A directory traversal that descends into all subdirectories at any depth and enumerates every file found. In Python this is commonly expressed as `Path.rglob('*')` or `os.walk()`.

- **Developer (persona):** The primary user of AIB who writes request descriptions, reviews analysis outputs, and drives the request lifecycle via `input.md` and the terminal menu.

- **AIB Maintainer (persona):** Owns `.aib_brain/` assets; the changes in this request are to files they own.

- **Menu guidance block:** A state-aware text block rendered before the numbered actions list in the terminal menu. It tells the developer what their next recommended action is based on current workspace state (seven possible states: `idle`, `input_ready`, `request_incomplete`, `questions_pending`, `implementation_ready`, `amendment_pending`, `unknown`).

---

## Technical Knowledge & Terms

- **`pathlib.Path.rglob('*')`:** Python standard-library method (3.4+) that performs a recursive glob, yielding all files and directories at any depth matching the pattern. Using `rglob('*')` and filtering for `f.is_file()` produces all files recursively.

- **`pathlib.Path.iterdir()`:** Python method returning only direct children (non-recursive). This is implied by the current "flat scan" language.

- **`shutil.move(src, dst)`:** Python standard-library function for moving files or directory trees across filesystem boundaries; used in `aib-analysis.md`'s Auto-Request Creation Branch to move attachments.

- **`_GUIDANCE_MESSAGES` dict in `menu.py`:** A module-level dictionary mapping workspace state strings to lists of guidance text lines. Each list element is displayed on a separate line in the `-- Next Step --` block. Adding a new element appends a new line.

- **`aib-analysis.md` preflight step 4:** The mandatory step that reads all text files in `.aib_memory/attachments/` before toggle detection. Currently specifies a flat scan.

- **`aib-analysis.md` Auto-Request Creation Branch step 6:** The step that archives `input.md` and moves all non-`.gitkeep` files from `.aib_memory/attachments/` to `<request-folder>/inputs/`. Currently specifies a flat scan with `shutil.move`.

- **`render_menu()` in `menu.py`:** The function that builds the terminal menu display buffer. It iterates `_GUIDANCE_MESSAGES[guidance_state]` and writes each element prefixed with two spaces. Adding list elements automatically adds new display lines.

- **`test_analysis_prompt_structure.py`:** Existing test file with regex/string assertions on `aib-analysis.md` content. The appropriate location for new prompt-structure tests.

- **`test_menu.py`:** Existing test file with unit tests for `menu.py` logic and rendering.

- **Relative path preservation:** When moving files from `attachments/subdir/file.txt` to `inputs/subdir/file.txt`, the relative path `subdir/file.txt` is preserved rather than flattening to `inputs/file.txt`. This requires `dest.parent.mkdir(parents=True, exist_ok=True)` before each move.

---

## Research Results

**Pattern scan against existing codebase:**

Occurrences of "flat scan" and "ignore subdirectories" in `aib-analysis.md`:

1. **Preflight step 4** (line ~32): `"Perform a flat scan of \`.aib_memory/attachments/\` (ignore subdirectories)."` — this is the primary reading step.
2. **Auto-Request Creation Branch step 6** (line ~80): `"move all files from \`.aib_memory/attachments/\` (flat scan, ignore subdirectories, skip \`.gitkeep\`)"` — this is the move step.

Both occurrences are independent and require separate targeted edits.

Occurrences of "attachments" in `menu.py`:

None in `_GUIDANCE_MESSAGES`. The guidance messages in `idle` and `implementation_ready` states do not mention the attachments folder.

`_GUIDANCE_MESSAGES["idle"]` currently has one element. `_GUIDANCE_MESSAGES["implementation_ready"]` currently has two elements. Both can safely receive an additional element.

Occurrences of "flat staging folder" / "flat scan" in `context.md`:

- Line ~80: "Flat staging folder for developer-supplied supplementary input files."
- Line ~178: "flat scan, skip `.gitkeep`" in the analysis workflow description.
- Line ~250: "flat staging folder for developer-supplied supplementary input files."

These documentation rows must be updated to reflect recursive-walk semantics.

`close-request.py` check (line ~118): uses `attachments_dir.iterdir()` for a flat check that attachments is empty — this is intentionally flat (checking only root level), is NOT part of this request's scope, and must NOT be changed.

**Evidence log:**
- Evidence: `aib-analysis.md` step 4 says "flat scan" → Implication: AI agents currently skip subdirectory attachments silently.
- Evidence: `_GUIDANCE_MESSAGES["idle"]` has no "attachments" text → Implication: developers don't learn about attachments from the menu.
- Evidence: `render_menu()` iterates list elements per line → Implication: adding a list element adds exactly one new display line, no rendering changes needed.

---

## External Benchmarking

**1. Python standard library — `Path.rglob('*')` pattern**
The Python documentation and community best practice uniformly recommend `Path.rglob('*')` (or `os.walk`) for recursive directory traversal. This is idiomatic, cross-platform, and requires no third-party dependencies. Adoption: directly applicable — replaces `Path.iterdir()` in the prompt specification.

**2. Git's staging area and `.gitignore` recursion**
Git itself applies `.gitignore` rules recursively through directory trees. When developers add files to a staging area (like `attachments/`), they naturally expect recursive behavior. A flat staging folder is an uncommon constraint that violates user expectations established by every other tool in the ecosystem. Takeaway: the developer's request aligns with established developer-tool conventions; recursive is the expected default.

**3. Unix `find` command — recursive by default**
The POSIX `find` command, `rsync`, `cp -r`, and similar tools are all recursive by default. The flat-only behavior in AIB attachments is an outlier. Takeaway: changing to recursive is a correctness fix from a UX expectations standpoint, not a feature addition.

---

## Minimal Spikes and Experiments

No spike conducted.

**Justification:** Both changes are low-uncertainty textual edits to well-understood files. The Python `rglob` pattern for recursive file traversal is standard and requires no experimentation. The `render_menu()` function iterates a list directly — adding a list element was verified by code inspection to produce an additional display line with no other side effects. The change to `aib-analysis.md` is a prompt-text edit; no code compilation or runtime behavior is involved. Risk is sufficiently low to proceed without a spike.

---

## AI Copilot Suggestions

**Observation 1 — Move semantics need explicit clarification in the prompt text (Design Quality)**
The current move step says "move it to `<request-folder>/inputs/<filename>`" which implies a flat destination (just the filename, no relative subdirectory). The replacement should explicitly say "move it to `<request-folder>/inputs/<relative-path>` preserving relative subdirectory structure" to leave no ambiguity for the implementing agent. Suggestion: the new wording in `aib-analysis.md` step 6 should explicitly mention both `shutil.move` and relative-path preservation with `dest.parent.mkdir(parents=True, exist_ok=True)`.

**Observation 2 — Menu guidance line length and cognitive load (Maintainability)**
The `"idle"` guidance currently fits in one compact line. Adding a second line for the attachments reminder is appropriate and doesn't clutter the display. However, the `"implementation_ready"` state will grow to three lines. Three lines is still very readable. The concern is that as more guidance lines are added over time, the menu grows vertically. Suggestion: keep the attachments reminder phrased concisely (≤ 80 characters) and review whether any existing guidance lines can be shortened when making this change, to keep the total guidance block compact.

**Observation 3 — `close-request.py` flat check is left unchanged — correct scoping (Scope Creep Risk)**
The `close-request.py` non-empty check uses `iterdir()` (flat) to detect whether attachments remain. This is intentionally flat because it only needs to catch the case where the developer forgot to process attachments before closing — a root-level check is sufficient for this warning. The scope of this request correctly excludes `close-request.py`. Suggestion: add a comment in the Plan's Risk Notes clarifying why `close-request.py` is excluded, so that a future implementing agent does not inadvertently change it.

**Observation 4 — `context.md` has many "flat" references — verify completeness (Testability)**
The `context.md` file has at least three distinct locations describing the attachments folder as "flat". Missing any one of them would leave the documentation inconsistent. Suggestion: the Plan task for `context.md` should run a targeted string search at done-check time to verify zero remaining "flat staging folder" occurrences in attachments-related rows.

**Observation 5 — Scope is appropriately minimal (Scope Clarity)**
The request does exactly what is needed and no more. The attachments folder's purpose, the `.gitkeep` sentinel, the move-to-inputs pattern, and the test suite structure are all retained. The change is a correctness fix (recursive scan) plus a discoverability improvement (menu hint). The scope is neither too large nor too small for the stated goal.

---

## Testing

- **T1 — Flat scan language absent from preflight step 4:** In `tests/test_analysis_prompt_structure.py`, assert that `"flat scan"` does not appear within the content block of preflight step 4 in `.aib_brain/prompts/aib-analysis.md`. Expected outcome: assertion passes; "flat scan" is absent from the reading step.

- **T2 — "ignore subdirectories" absent from attachments sections:** In `tests/test_analysis_prompt_structure.py`, assert that `"ignore subdirectories"` does not appear anywhere in `.aib_brain/prompts/aib-analysis.md`. Expected outcome: assertion passes; the phrase is fully removed from the prompt.

- **T3 — Recursive walk language present in preflight step 4:** In `tests/test_analysis_prompt_structure.py`, assert that a recursive walk keyword (e.g., `"subdirectories"` within the context of reading attachments, or `"recursively"`) appears in `.aib_brain/prompts/aib-analysis.md` near the preflight step 4 block. Expected outcome: assertion passes; recursive-walk language is present.

- **T4 — `"idle"` guidance contains attachments reference:** In `tests/test_menu.py`, assert that `"attachments"` appears in at least one element of `_GUIDANCE_MESSAGES["idle"]`. Expected outcome: assertion passes.

- **T5 — `"implementation_ready"` guidance contains attachments reference:** In `tests/test_menu.py`, assert that `"attachments"` appears in at least one element of `_GUIDANCE_MESSAGES["implementation_ready"]`. Expected outcome: assertion passes.

- **T6 — Full test suite passes:** Run `python -m pytest tests/ -v` from the workspace root. Expected outcome: all pre-existing tests pass; no regressions introduced.

All test cases are automatable assertions. No UAT scenarios file is required.

---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The request is technically sound and scoped conservatively. Both changes (prompt text edit and dict element addition) are isolated and low-risk. The recursive scan using `Path.rglob('*')` is idiomatic Python and has no cross-platform concerns. The relative-path preservation requirement for the move step adds a small implementation detail (`dest.parent.mkdir(parents=True, exist_ok=True)`) that should be made explicit in the prompt wording — an implicit assumption here could cause a flat move on the implementing agent's first pass.

- The two edits to `aib-analysis.md` are in clearly separated and independent locations; no cascading side effects.
- The `_GUIDANCE_MESSAGES` dict is a pure data structure; the `render_menu()` renderer is already written to iterate any number of list elements.
- `context.md` update is documentation-only; no runtime impact.
- No architectural concerns. Straightforward correctness and discoverability fix.

### Product Owner

The request addresses a real usability gap: developers who organize attachments into subfolders were silently losing context with no error or warning. The fix is invisible to developers who use only root-level attachments (backward compatible) while enabling richer input for those with complex supplementary materials.

The menu hint is low-friction discoverability improvement that complements the existing guidance without adding noise.

- Business value is real but moderate: improves the input quality for complex requests without affecting existing simple flows.
- Success criteria are measurable and testable.
- The scope boundary (excluding `close-request.py`) is appropriate and well-justified.

### User (Developer Perspective)

A developer placing files in `attachments/subfolder/` currently gets no warning that those files are being ignored. After this change, those files will be read and moved correctly. The experience is improved silently — no new prompts or configuration required.

The menu hint in the `idle` state is the most valuable: it catches developers at the moment they're about to write into `input.md`, reminding them that supplementary materials are supported. The `implementation_ready` state hint also helps when amending a request.

- The menu changes add one line of text per affected state — acceptable cognitive load.
- Existing developers familiar with the flat attachments behavior will not be disrupted.

### Security Officer

No security concerns. The change involves reading more files from a developer-controlled local directory (`.aib_memory/attachments/`) and updating display strings. Both are already in the trusted developer workspace.

- No new input channels opened. The attachments folder is already trusted by the prompt.
- The recursive walk does not follow symlinks by default with `Path.rglob('*')` — confirm this assumption if symlinks in attachments are a concern in future.
- No authentication, authorization, or data exposure changes.

### Data Governance Officer

No data governance concerns. The attachments folder is classified as internal engineering documentation. Moving files from a subdirectory of `attachments/` to `<request-folder>/inputs/` follows the same data lineage pattern as the current flat move; the destination is the same, only the source traversal changes.

- No new data retention obligations.
- No change in data classification.
- Files remain within the local repository workspace at all times.
