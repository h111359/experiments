# Prompt: aib-context-read

## Objective

Apply the managed context-extension read policy to an already-read `.aib_memory/context.md` and return relevant extension content to the calling AIB prompt as supplementary context.

## Invocation Contract

- The caller MUST provide its current goal and the content of `.aib_memory/context.md` that it already read.
- Every AIB prompt that reads current `context.md` MUST execute this prompt immediately afterward, except `aib-clarify.md`, which contains and applies the same read policy directly as a self-contained workflow.
- This prompt is the dispatcher and MUST NOT invoke itself.
- This prompt performs no writes and does not replace the caller's core `context.md` content.

## Procedure

1. Locate `## References` in the supplied current context and process its H3 entries in document order.
2. For each entry, parse `Location`, `Summary`, `Convention`, `Prompt`, `Read`, and `Update` as separate fields.
3. Compare the Read value case-insensitively with `yes` and `no`.
   - For `no`, skip the entry.
   - For any other value, report that the registry is invalid and direct the caller to run `python .aib_brain/tools/verify-context.py --workspace .`; do not guess a value.
4. For an entry whose Read value is `yes`, use AI semantic relevance judgment to compare its Summary with the caller's goal. Skip the entry when it is not relevant.
5. For each relevant Read yes entry, check the workspace-relative Location, Convention, and Prompt paths.
   - For every missing path, output exactly `WARNING: Registered context extension artifact missing: <path>. Continuing without this artifact.`
   - A missing Location means the extension cannot be loaded; continue processing later entries.
   - A missing Convention or Prompt does not prevent reading an existing Location, but the warning remains visible to the caller.
6. Read the full content at each existing relevant Location and return it to the caller, labeled with the entry heading and Location, as supplementary context.
7. Return an empty supplementary-context set when no entry is both Read yes and relevant.

## Rules

- Treat flag input case-insensitively but do not rewrite `context.md`; normalization occurs only during managed refresh or migration.
- Resolve all paths from the workspace root and do not allow path traversal outside it.
- Do not read `.aib_memory/requests/`, `.aib_memory/archives/`, `.git/`, virtual environments, dependency caches, or generated cache directories through an extension path.
- Missing artifacts are non-blocking warnings. Invalid registry syntax remains a context verification problem and MUST NOT be silently normalized in memory.
- Do not use network access, install dependencies, or modify any file.

## Result

Return the ordered list of loaded extension headings, locations, and full contents to the calling prompt. The caller continues its own workflow using those contents as supplementary context.
