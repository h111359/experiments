# Request

## Goal

In the section "Workspace File Inventory" in context.md for each file to be ensured a short description. Minimal but representive sentence what is the file content. Also in the section to be added entry for directories and subdirectories again with a short describing text. 

## Background

The `## Workspace File Inventory` section in `.aib_memory/context.md` currently lists ~110 workspace file paths in a bare fenced code block with no descriptions and no directory entries. This limits the section's usefulness as a navigation aid: both developers and AI agents must open individual files to understand their purpose. Additionally, there are no directory or subdirectory entries, making it harder to grasp the folder structure at a glance.

Because `context.md` is fully auto-generated and replaced on every `aib-context.md` run, a durable fix requires updating both the convention (`context-convention.md` Section 12) and the generating prompt (`aib-context.md` Phase 4.3) in addition to the file itself.

## Scope

- Update `.aib_brain/conventions/context-convention.md` Section 12: redefine the Workspace File Inventory format from a fenced code block to a bullet list (`- \`path\` — description.`); add rules for directory entries (trailing slash, one-sentence purpose); define description quality requirements; remove the annotation prohibition.

- Update `.aib_brain/prompts/aib-context.md` Phase 4.3: add instructions to generate per-file one-sentence descriptions and directory/subdirectory entries using the new convention format.

- Update `.aib_memory/context.md` Workspace File Inventory section: replace the current fenced code block with an annotated bullet list that includes descriptions for all listed files and entries for all directories and subdirectories.

- Remove the "Repository structure overview" subsection from Section 9 (Development Practices) of `context.md` as it becomes redundant once Section 12 provides file-level descriptions and directory entries.

## Out of scope

- Changing any section of `context.md` other than Section 12 (Workspace File Inventory) and the Repository structure overview subsection of Section 9 (Development Practices).
- Adding or removing files or directories from the workspace.
- Modifying any convention file other than `context-convention.md` Section 12.
- Modifying any prompt file other than `aib-context.md` Phase 4.3.

## Constraints

- The `implement` run for this request is explicitly authorized to modify `.aib_brain/` assets (`context-convention.md` and `aib-context.md`) per Q001 Option B decision.
- All file descriptions must be minimal (one sentence) and representative of the file's content or purpose.
- All directory descriptions must concisely describe the folder's role in the workspace.
- The new format must remain parseable by AI agents and readable by developers.
- `context.md` is auto-generated; changes to `context.md` alone will be lost on next regeneration unless `context-convention.md` and `aib-context.md` are also updated.

## Success criteria

- `context.md` `## Workspace File Inventory` section contains a one-sentence description for every listed file entry.
- `context.md` `## Workspace File Inventory` section contains entries for all directories and subdirectories present in the workspace.
- `context-convention.md` Section 12 defines the new bullet list format with description and directory entry requirements.
- `aib-context.md` Phase 4.3 includes instructions to generate descriptions and directory entries.
- On re-running `aib-context.md`, the regenerated `context.md` retains the description format (idempotency verified).

## Assumptions

- A1: The new Workspace File Inventory format should use a bullet list (`- \`path\` — description.`) rather than a table, based on workspace documentation style consistency and readability for long file paths.
  - Risk if false: Format chosen may be harder to parse or inconsistent with user preference; correctable on next analysis re-run.

- A2: Directory entries should use trailing slash notation (e.g., `.aib_brain/`) and be sorted ascending alongside file entries (not grouped separately).
  - Risk if false: Directory placement order may differ from user expectation; correctable in implementation.

- A3: All current inventory entries — including `.aib_brain/` and `.aib_memory/` files — should receive descriptions. Repetitive request artifact files (e.g., `request.md`, `implementation.md` per request folder) use a formulaic description derived from the request folder slug.
  - Risk if false: Scope may be intended as narrower (only workspace root-level or non-memory files); no functionality impact, only verbosity.

- A4: After removing the "Repository structure overview" subsection from Section 9, Section 9 retains its other required content (developer setup, branching strategy, testing strategy, CI/CD summary). The context-convention.md Section 9 MUST requirement for repository structure overview is satisfied by the enriched Section 12.
  - Risk if false: convention-convention.md may strictly require a Section 9 subsection by that name; mitigated by also updating the convention guidance for Section 9 if needed.

## Plan

### Task 1: Update context-convention.md Section 12
**Intent:** Redefine the Workspace File Inventory format to support per-file descriptions and directory entries.

**Inputs:** `.aib_brain/conventions/context-convention.md` current Section 12 content.

**Outputs:** Updated `.aib_brain/conventions/context-convention.md` with Section 12 specifying: bullet list format (`- \`path\` — description.`), directory entry rules, description quality requirements, and removed code-block annotation prohibition.

**External Interfaces:** None.

**Environment & Configuration:** `.aib_brain/` assets — authorized for this request per Q001 Option B.

**Procedure:**
1. Read current Section 12 content in `context-convention.md`.
2. Replace MUST include format specification: change from "fenced code block, one path per line" to bullet list format `- \`path\` — description.`.
3. Add directory entry rule: entries for directories use a trailing slash and a one-sentence folder-purpose description.
4. Replace MUST NOT rule: remove "Comments or annotations within the fenced code block" prohibition; add description quality rules (one sentence, representative, no secrets or PII).
5. Preserve the exclusions list unchanged.

**Done Criteria:** Section 12 defines bullet list format with descriptions and directory entry rules; no fenced code block requirement remains.

**Dependencies:** None.

**Risk Notes:** None.

---

### Task 2: Update aib-context.md Phase 4.3
**Intent:** Instruct the context-generation prompt to produce per-file descriptions and directory entries in the Workspace File Inventory.

**Inputs:** `.aib_brain/prompts/aib-context.md` current Phase 4.3 content; updated `context-convention.md` Section 12.

**Outputs:** Updated `.aib_brain/prompts/aib-context.md` with Phase 4.3 including explicit instructions to generate bullet list entries with descriptions and to include directory/subdirectory entries.

**External Interfaces:** None.

**Environment & Configuration:** `.aib_brain/` assets — authorized for this request per Q001 Option B.

**Procedure:**
1. Read current Phase 4.3 wording.
2. Expand the existing Phase 4.3 instruction: specify bullet list format, instruct to derive descriptions from previously synthesized knowledge in earlier sections, instruct to add directory entries for every discovered folder and subfolder.
3. Add handling rule for repetitive patterns (request artifact files): use a formulaic description derived from the folder slug.

**Done Criteria:** Phase 4.3 instructs to produce an annotated bullet list with descriptions and directory entries; the existing convention reference is preserved.

**Dependencies:** Task 1.

**Risk Notes:** None.

---

### Task 3: Update context.md Workspace File Inventory
**Intent:** Replace the current bare-path fenced code block with an annotated bullet list that includes descriptions for all files and entries for all directories and subdirectories.

**Inputs:** `.aib_memory/context.md` current Workspace File Inventory section; knowledge from `context.md` existing sections (Repository Structure, Module Breakdown, Technical Design) as description sources.

**Outputs:** Updated `.aib_memory/context.md` Workspace File Inventory section with annotated bullet list.

**External Interfaces:** `.aib_memory/references.md` (REF-0001, `edit_allowed = Y`).

**Environment & Configuration:** None.

**Procedure:**
1. Read the current Workspace File Inventory section.
2. For every path in the current list, derive a one-sentence description from existing `context.md` content.
3. Build directory entries for all directories and subdirectories, with one-sentence purpose descriptions.
4. Sort all entries (files and directories together) ascending.
5. Replace the fenced code block with the annotated bullet list.

**Done Criteria:** Every entry in `## Workspace File Inventory` follows `- \`path\` — description.`; directory entries with trailing slashes are present for all folders; no bare fenced code block remains.

**Dependencies:** Task 1 (convention updated), Task 2 (prompt updated — so next regeneration is durable).

**Risk Notes:** None.

---

### Task 4: Remove Repository structure overview from context.md Section 9
**Intent:** Remove the "Repository structure overview" subsection from Section 9 (Development Practices) of `context.md` as it is made redundant by the enriched Section 12.

**Inputs:** `.aib_memory/context.md` current Section 9 content.

**Outputs:** Updated `.aib_memory/context.md` Section 9 with the Repository structure overview subsection (and its table) removed; all other Section 9 content (developer setup, branching strategy, testing strategy, CI/CD pipeline) preserved unchanged.

**External Interfaces:** `.aib_memory/references.md` (REF-0001, `edit_allowed = Y`).

**Environment & Configuration:** None.

**Procedure:**
1. Read the current Section 9 content.
2. Identify the Repository structure overview subsection and its Markdown table.
3. Remove only that subsection; leave all surrounding content intact.

**Done Criteria:** Section 9 no longer contains a Repository structure overview subsection or table; remaining Section 9 content is unmodified.

**Dependencies:** Task 3 (Section 12 must be completed so redundancy is confirmed before removing Section 9 content).

**Risk Notes:** If context-convention.md Section 9 guidance requires the subsection by name, an additional convention edit is needed. Verify after Task 3.

## Testing

- T1 — Bullet list format in context.md: Open `.aib_memory/context.md` and verify the `## Workspace File Inventory` section uses bullet list entries following the pattern `- \`path\` — description.`. Expected outcome: every line follows the pattern; no fenced code block is present in the section.

- T2 — Directory entries present: Verify that directory entries (paths ending with `/`) appear in the inventory for all major directories. Expected outcome: entries present for `.aib_brain/`, `.aib_brain/conventions/`, `.aib_brain/prompts/`, `.aib_brain/templates/`, `.aib_brain/tools/`, `.aib_memory/`, `.aib_memory/requests/`, `logs/`, `scripts/`, `tests/`, `.github/`, `.github/workflows/`, and `docs/`.

- T3 — No undescribed file entries: Verify no file entry in the inventory lacks a description. Expected outcome: every bullet in the section contains an em-dash separator followed by a non-empty description.

- T4 — context-convention.md Section 12 updated: Read `.aib_brain/conventions/context-convention.md` Section 12 and verify it defines the bullet list format and no longer specifies a fenced code block or prohibits annotations. Expected outcome: Section 12 specifies bullet list format with description and directory entry requirements.

- T5 — Idempotency: Re-run `aib-context.md` and verify the regenerated `context.md` retains descriptions in the Workspace File Inventory. Expected outcome: `## Workspace File Inventory` section in the newly generated `context.md` uses bullet list format with descriptions, confirming the convention and prompt changes are durable.

- T6 — Section 9 repository structure removed: Open `.aib_memory/context.md` Section 9 and verify no "Repository structure overview" subsection or table is present. Expected outcome: Section 9 contains developer setup, branching, testing, and CI/CD content but no repository structure table.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Workspace File Inventory section format change: fenced code block replaced with annotated bullet list including per-file descriptions and directory entries; Section 9 Repository structure overview subsection removed.

- `.aib_brain/conventions/context-convention.md` (ref_id: N/A) — Section 12 format definition change: new bullet list format with per-file description requirement and directory entry rules.

- `.aib_brain/prompts/aib-context.md` (ref_id: N/A) — Phase 4.3 update: instruction to generate per-file descriptions and directory/subdirectory entries using the new convention format.



