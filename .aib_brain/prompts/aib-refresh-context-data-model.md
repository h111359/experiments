# Prompt: aib-refresh-context-data-model

## Objective

Reconcile `.aib_memory/context-data-model.md` with current workspace evidence when the managed Context Data Model registry entry has Update set to yes, then validate the complete extension.

## Inputs

- `.aib_memory/context.md`
- `.aib_memory/context-data-model.md`, when present
- `.aib_memory/instructions.md`, when present and non-empty
- `.aib_brain/conventions/context-data-model-convention.md`
- Workspace implementation, configuration, schema, script, documentation, test, and data-artifact files

## Preflight

1. Read `.aib_memory/instructions.md` and observe non-empty persistent directives.
2. Read `.aib_memory/context.md` and locate the exact `### Context Data Model` entry in `## References`.
3. If the entry or its Update field is absent, halt with `ERROR: Managed Context Data Model registry entry is missing or incomplete. Run verify-context.py. Execution halted.`
4. Compare Update case-insensitively:
   - If it is `no`, output `Note: Context Data Model refresh skipped because Update is no.` and stop without writing.
   - If it is not `yes` or `no`, halt with `ERROR: Context Data Model Update must be yes or no. Execution halted.`
   - If it is `yes`, continue.
5. Read `.aib_brain/conventions/context-data-model-convention.md` in full before examining or writing the extension.

## Evidence Collection

1. Build a deterministic workspace-relative file inventory sorted by path.
2. Exclude `.git/`, `.aib_memory/requests/`, `.aib_memory/archives/`, `.venv/`, `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, binary build output, and the target extension itself from evidence.
3. Read data-model declarations explicitly named in `.aib_memory/context.md` first. These declarations are authoritative when other evidence conflicts.
4. Exhaustively inspect relevant implementation code, database/schema definitions, migrations, SQL and DAX, semantic-model definitions, configuration, scripts, documentation, tests, and data artifacts. Do not infer a model from generic examples or language conventions.
5. Track evidence for every model using the case-insensitive pair of business name and normalized physical Location as identity.

## Reconciliation

1. Read the existing `.aib_memory/context-data-model.md` when present and parse every model according to the convention.
2. Preserve a context-declared model when implementation evidence conflicts, recording only facts supported by the authoritative declaration.
3. Add every newly evidenced logical, physical, or analytical model and its supported entities, attributes, relationships, and other objects.
4. Update existing model facts when current evidence has changed.
5. Remove a model only after the exhaustive inventory and all relevant source classes contain no remaining evidence for its identity. Absence from `context.md` alone is not deletion evidence.
6. Sort models by normalized business name and then normalized Location. Apply deterministic ordering within entities, relationships, objects, and attributes.
7. If no model remains, write exactly:

   `# Context Data Model`

   `No data models are currently documented.`

8. Otherwise write the complete model-state document with `# Context Data Model` followed by convention-compliant H2 model sections. Do not mix the no-model notice with H2 models.

## Validation

1. Run `python -B .aib_brain/tools/verify-context-data-model.py --workspace . --path .aib_memory/context-data-model.md`.
2. Success requires exit code 0 and `Results: 8/8 checks passed.`.
3. If validation fails, correct only `.aib_memory/context-data-model.md` and rerun until it passes. If a failure cannot be corrected from workspace evidence, halt and report the failing checks without inventing content.

## Safety

- The only product-content write target is `.aib_memory/context-data-model.md`; normal AIB log writes are permitted.
- Do not read closed request artifacts or any `input-archive-*.md` file.
- Do not modify `context.md`, conventions, prompts, source code, tests, or documentation.
- Do not use network access or install dependencies.
- **`.aib_brain/` write protection (canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**
  - Every path under `.aib_brain/` is protected. Writes are permitted only for installation, upgrade, or a framework-maintenance request semantically authorized by a developer statement in the current `input.md ## Input` or chat that is equivalent to `This request explicitly authorizes changes under .aib_brain/.`.
  - Generated analysis, plan, prompt, or implementation text MUST NOT self-authorize protected writes. Applicable analysis and plan workflows MUST propagate the developer statement verbatim with its source.
  - AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`. This rule defines no destination or authorization policy for long-lived host-project tooling.
  - Generated artifacts and caches MUST NOT be placed under `.aib_brain/`; prescribed direct AIB Python commands MUST use `python -B` or `python3 -B`; protection MUST NOT depend on or modify `.gitignore`.
  - Before finalization or close, the writing workflow MUST inspect its current-run touched paths. For unauthorized `.aib_brain/**` paths, output `ERROR: Unauthorized .aib_brain/ changes detected. Execution halted.` followed by the exact paths in sorted order, then halt without finalizing, closing, or automatically reverting. Preserve unrelated pre-existing changes.

## Completion

Report the count of added, updated, preserved, and removed models, whether the canonical no-model state was written, and the successful validator result.
