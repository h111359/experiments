Implementation record for request R-20260421-1705: Add instructions.md for persistent AIB directives.

Files from `.aib_memory/` taken into consideration:
- `.aib_memory/requests_register.md`
- `.aib_memory/references.md`
- `.aib_memory/context.md`

## Implementation Log

### Entry 2026-04-22 09:30
#### Scope
Create `.aib_memory/instructions.md` as an empty workspace-level persistent instructions file, update all three AIB prompts to include a mandatory pre-read step for it, update `initialize.py` to seed the file on initialization, document the feature in `.aib_brain/README.md`, and update the Component Map in `.aib_memory/context.md`.

#### Changes
- Created `.aib_memory/instructions.md` as an empty file (zero bytes).
- Updated `.aib_brain/prompts/aib-implement.md`: inserted a "Workspace instructions pre-read (MUST)" section immediately after the Goal, directing the prompt to read `.aib_memory/instructions.md` and apply its content if non-empty.
- Updated `.aib_brain/prompts/aib-analysis.md`: inserted a "Workspace instructions pre-read (MUST)" section immediately after the Goal, directing the prompt to read `.aib_memory/instructions.md` and apply its content if non-empty.
- Updated `.aib_brain/prompts/aib-context.md`: inserted a "Workspace instructions pre-read (MUST)" section immediately after the Goal, directing the prompt to read `.aib_memory/instructions.md` and apply its content if non-empty.
- Updated `.aib_brain/tools/initialize.py`: added an idempotent block that seeds an empty `instructions.md` if the file does not already exist.
- Updated `.aib_brain/README.md`: added a `## Workspace Instructions` section documenting the file's location, purpose, usage guidance, examples of directive categories, graceful-absence behavior, and a security note.
- Updated `.aib_memory/context.md`: added a `Workspace Instructions` row to the Component Map table and updated the `AIB Memory Artifacts` row to include `instructions.md`.

#### Tests
- unit: `test_initialize_seeds_instructions_md` — verified `initialize.py` creates an empty `instructions.md` when absent — pass
- unit: `test_initialize_does_not_overwrite_instructions_md` — verified re-running `initialize.py` does not overwrite an existing file — pass
- unit: `test_instructions_md_exists_and_is_empty` — verified `.aib_memory/instructions.md` exists and has no content — pass
- unit: `test_prompts_contain_instructions_md_reference` — verified all three prompt files contain the string `instructions.md` — pass
- unit: `test_readme_documents_instructions_md` — verified `.aib_brain/README.md` contains the `Workspace Instructions` section — pass
- integration: `pytest tests/` — full test suite — pass

#### Outcome
Successful. All success criteria met. No unresolved failures or blockers. The `instructions.md` mechanism is graceful-by-default: any absent or empty file is a no-op for all prompts.

#### Evidence
- Path: `.aib_memory/instructions.md`
- Path: `.aib_brain/prompts/aib-implement.md`
- Path: `.aib_brain/prompts/aib-analysis.md`
- Path: `.aib_brain/prompts/aib-context.md`
- Path: `.aib_brain/tools/initialize.py`
- Path: `.aib_brain/README.md`
- Path: `.aib_memory/context.md`
