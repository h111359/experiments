# Request

## Goal

Design and specify a new AIB prompt (and optional supporting tool script) called `reverse-engineer` that enables the AI copilot to:

1. Enumerate every file in the current workspace directory tree (recursively, without missing any file).
2. Read all documents referenced in `.aib_memory/references.md`.
3. For each `product-doc` entry in `.aib_memory/references.md` where `edit_allowed = Y`, extract relevant knowledge from the workspace files and populate the corresponding documentation file under `.aib_memory/docs/` in compliance with the document's convention file (resolved via `.aib_brain/conventions/<requirement-id-lower>-convention.md`).

The approach must be workspace-agnostic (applicable to any project, not only AI_Builder) and model/vendor-agnostic (executable in VS Code Copilot, Claude Code, Cursor, CLI, etc.).

## Background

When AIB is installed into a brownfield (pre-existing) project, the `initialize` action seeds 27 empty product-doc stubs. Manual population of these files is labor-intensive and error-prone. An automated reverse-engineering capability would dramatically reduce time-to-value by extracting maximum useful information from the existing codebase.

## Scope

- New prompt file: `.aib_brain/prompts/aib-reverse-engineer.md`
- Optional new tool script: `.aib_brain/tools/reverse-engineer.py`
- Updates to `Concepts.md` to register the new action (if chosen approach warrants it)
- Population of all 27 editable product-doc files with extracted content
- Handling of workspaces with thousands of files and varied file types

## Out of scope

- Modifying the `.aib_brain/` folder structure beyond adding the new prompt/tool
- Changing `references.md` schema or entries
- Supporting file types that are not human-readable text
- Providing 100% accuracy — the output is a best-effort draft requiring human review

## Constraints

- Must not exceed LLM context-window limits; must handle workspaces of any practical size
- Must conform to each product-doc's convention file when writing content
- Must respect `edit_allowed` flag — never write to files marked `N`
- Must be model-agnostic and vendor-agnostic
- `.aib_brain/` is read-only to AIB automation, still the current request can modify its content when needed. The generated prompt should not modify `.aib_brain/`

## Success criteria

- The prompt can be invoked on any workspace where AIB has been initialized
- All workspace files are enumerated and considered (none missed)
- Product-doc files are populated with structured, convention-compliant content derived from workspace evidence
- At least 5 materially different approaches are proposed in the analysis
- Each populated document includes traceability to source files from which knowledge was extracted
- Human reviewer can verify and refine the auto-generated content with reasonable effort
