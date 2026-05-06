## Executive Summary

- **Request ID:** R-20260416-2124

- **Title:** file description in context

- **High-level purpose:** Enhance `context.md` in two ways: (1) replace the bare-path `## Workspace File Inventory` fenced code block with an annotated bullet list giving every file and directory a short, representative one-sentence description; (2) remove the "Repository structure overview" subsection from Section 9 (Development Practices) because it is made redundant by the improved Workspace File Inventory.

- **Trigger:** The current Section 12 lists ~110 workspace file paths with no descriptions and no directory entries. The Section 9 "Repository structure overview" partially fills that gap at a folder-only level but creates duplication once Section 12 is enriched.

- **Affected components:** Four artifacts require change: (1) `context-convention.md` — Section 12 format redefined to allow descriptions and directory entries; (2) `aib-context.md` — Phase 4.3 updated to generate descriptions and directory entries; (3) `context.md` — Section 12 replaced with annotated bullet list; (4) `context.md` — Section 9 "Repository structure overview" subsection removed.

- **Q001 resolved:** The user selected Option B — the `implement` run for this request is explicitly authorized to modify `.aib_brain/` assets (`context-convention.md` and `aib-context.md`).

- **Durability:** Changes to `context.md` alone would be reverted on next `aib-context.md` regeneration. All four artifacts must be updated together. With Q001 resolved, all changes can be applied in a single `implement` run.

- **`request.md` sections added/updated in this run:** Scope (Amends applied — Section 9 Repository structure removal added); Out of scope (narrowed); Constraints (Q001 answer applied — authorization added); Assumptions A1–A3 (refreshed); Plan Tasks 1–4 (Task 4 added for Section 9); Testing T1–T6 (T6 added); Documentation (updated); Questions & Decisions (Q001 removed — answered).

---

## Domain Knowledge Essentials

- **Workspace File Inventory:** Section 12 of `context.md`. Its stated purpose per the convention is "to provide a quick structural reference of all non-excluded workspace files so that agents and developers can navigate the codebase without prior knowledge." Currently fulfils this purpose only partially — paths are listed, but without descriptions a reader cannot determine file purpose without opening each file.

- **context.md:** Auto-generated unified product knowledge artifact. Fully replaced on every `aib-context.md` execution. Listed in `references.md` as REF-0001 with `edit_allowed = Y`. Any format change to its Workspace File Inventory section must be reflected in both the convention and the generating prompt to survive regeneration; a direct edit alone is not durable.

- **context-convention.md:** Normative convention file in `.aib_brain/conventions/`. Defines the required structure, formatting rules, and quality gates for `context.md`. It is the authoritative specification that `aib-context.md` and the `implement` prompt read before editing `context.md`. Changing Section 12 here makes the format change durable.

- **aib-context.md:** Prompt action in `.aib_brain/prompts/`. Synthesizes and fully replaces `context.md`. Phase 4.3 references `context-convention.md` Section 12 directly. Must be updated with explicit instructions to produce descriptions and directory entries; otherwise regeneration will revert to the current bare-path format.

- **AIB Maintainer:** Role responsible for `.aib_brain/` framework assets. The user of this workspace is effectively the AIB Maintainer. Modifications to `.aib_brain/` are reserved for this role and are explicitly blocked by the `implement` prompt safety rules.

- **Developer / AI agent consumer:** Reads `context.md` Workspace File Inventory to understand codebase layout without opening individual files. Descriptions reduce cognitive load during exploration and improve navigation for AI agents resolving ambiguous file purposes.

---

## Technical Knowledge & Terms

- **Fenced code block (Markdown):** A block delimited by triple backticks. The current format for the Workspace File Inventory. `context-convention.md` Section 12 explicitly states "MUST NOT include: Comments or annotations within the fenced code block." This means descriptions cannot be added under the current convention without first changing it.

- **Markdown bullet list:** A list of items prefixed with `- `. Allows inline annotations using an em-dash separator, e.g., `- \`path\` — description.` This format is already used in other sections of `context.md` (Glossary, Module Breakdown) and is consistent with workspace documentation style.

- **Markdown table:** Two-column GH-flavored table. Already used in `context.md`'s `## Repository Structure` section for high-level folder purposes. Suitable for structured tabular data; less readable for lists containing long, variable-length file paths.

- **Directory entry:** A path in the inventory representing a folder rather than a file. Identified by a trailing `/` in the path. Provides hierarchical context so readers can understand the scope of a subtree without reading every file entry.

- **Auto-generation and durability:** `context.md` is fully replaced on every `aib-context.md` run. A change applied only to `context.md` survives until the next regeneration. To make the change permanent, the convention and the prompt must also be updated.

- **edit_allowed flag:** A field in `references.md` controlling whether AI automation may edit a file. `context.md` carries `edit_allowed = Y` (REF-0001). `context-convention.md` and `aib-context.md` are not in `references.md`; their modification is governed by the `.aib_brain/` maintainer restriction.

- **implement safety rules:** The `aib-implement.md` prompt contains an explicit Safety clause: "Do not modify `.aib_brain/` assets during implementation work." This applies unconditionally to `context-convention.md` and `aib-context.md`.

- **Evidence log:**
  - "Workspace File Inventory is a fenced code block with bare paths, no descriptions" → implication: descriptions cannot be added within the current format without a convention change.
  - "context-convention.md Section 12 MUST NOT include comments or annotations in code block" → implication: the convention must change before descriptions can be added.
  - "aib-context.md Phase 4.3: 'follow format defined in context-convention.md Section 12'" → implication: updating the convention and adding explicit Phase 4.3 instructions is sufficient to make new runs produce descriptions.
  - "Section 9 MUST include 'Repository structure overview': key folders and their purpose" per context-convention.md" → implication: the convention must be checked; but the convention only says MUST include such content, not that it must be a standalone subsection. Removing the subsection while retaining equivalent coverage in Section 12 satisfies the requirement.
  - "implement safety: 'Do not modify .aib_brain/ assets' — overridden for this request by Q001 Option B" → implication: `.aib_brain/` changes are authorized for this implement run.
  - "Repository Structure section already has high-level folder descriptions" → implication: file-level descriptions in the inventory complement, not duplicate, existing section content.
  - **Files read:** `.aib_memory/context.md`, `.aib_brain/conventions/context-convention.md`, `.aib_brain/prompts/aib-context.md`, `.aib_brain/prompts/aib-implement.md`, `.aib_brain/Concepts.md`, `.aib_memory/references.md`, `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`.

---

## Research Results

1. **Internal review of `request.md` and product docs:**
   - Goal is clear and actionable: add one-sentence descriptions per file and add directory/subdirectory entries to the Workspace File Inventory.
   - All mandatory `request.md` sections were empty; completed from request goal and workspace context.
   - `context.md` current state: Workspace File Inventory is a fenced code block with approximately 110 path entries, no descriptions, no directory entries.
   - `context-convention.md` Section 12 current format: fenced code block; explicitly prohibits annotations; must be updated.
   - `aib-context.md` Phase 4.3 current instruction: "Write the final mandatory section (`## Workspace File Inventory`) listing all non-excluded files discovered in Phase 3. Follow the format defined in `context-convention.md` Section 12." — inherits format from convention; needs an explicit instruction to generate descriptions and directory entries.

2. **Code and asset scan for impacted components:**
   - `.aib_brain/conventions/context-convention.md` — Section 12 format definition must be rewritten.
   - `.aib_brain/prompts/aib-context.md` — Phase 4.3 must be updated with description and directory-entry generation instructions.
   - `.aib_memory/context.md` — Workspace File Inventory section must be replaced with annotated bullet list.
   - No tests are affected. No scripts are affected. No other convention files are affected.
   - The `## Repository Structure` section in `context.md` covers high-level folder purposes; it is complementary and does not overlap with file-level descriptions.

3. **Pattern scan against organizational standards:**
   - Workspace documentation already uses bullet lists with em-dash annotations in multiple places: Glossary (`**Term**: definition`), Module Breakdown (`- \`script.py\` — description.`).
   - A bullet list `- \`path\` — description.` is consistent with the workspace's established documentation style and more readable than a table for long file paths.
   - The existing `## Repository Structure` table in `context.md` validates that tabular format is already used for folder-level descriptions; adding a table in Section 12 would partly duplicate that content at a different granularity. Bullet list format avoids this overlap.

4. **External benchmarking:**
   - Standard practice in developer documentation: file inventories pair each path with a brief purpose statement. A bullet list with an em-dash separator is the dominant pattern in README files and developer guides for repositories with many files. Tables are used when columnar alignment adds value (e.g., comparing attributes); for single-attribute description lists, bullet format is preferred.
   - Removing duplicate navigation aids (a folder-only subsection when a file-level inventory exists) is a widely applied doc hygiene practice; it reduces maintenance burden and avoids version skew between two redundant views.

5. **Spike / uncertainty assessment:**
   - No spike needed. Descriptions for all current inventory entries can be derived directly from content already present in `context.md` (Repository Structure, Module Breakdown, Technical Design, and Glossary sections name and describe all key files and folders). No unknown file content requires discovery.
   - The Section 9 "Repository structure overview" subsection provides a folder-level table. Once Section 12 includes directory entries with descriptions, this table is redundant. The context-convention.md Section 9 guidance says MUST include "Repository structure overview: key folders and their purpose" — this is a content requirement, not a subsection-name requirement. The enriched Section 12 satisfies that intent, so removing the Section 9 subsection is convention-compliant provided Section 9 retains other required content (developer setup, branching strategy, testing strategy, CI/CD summary).
   - Q001 is resolved: Option B (explicit authorization for `.aib_brain/` edits in this request). No open unknowns remain.
