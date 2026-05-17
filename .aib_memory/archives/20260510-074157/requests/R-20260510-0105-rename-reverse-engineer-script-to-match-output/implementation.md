Implementation record for request R-20260510-0105.

.aib_memory files taken into consideration:
- .aib_memory/instructions.md
- .aib_memory/requests_register.md
- .aib_memory/request-R-20260510-0105.md
- .aib_memory/context.md

## Implementation Log

### Entry 2026-05-10 02:00
#### Scope
Renamed the workspace inventory helper from reverse-engineer naming to file-inventory naming and aligned active prompt, test, and context references while preserving behavior and CLI semantics.

#### Changes
- Renamed `.aib_brain/tools/reverse-engineer.py` to `.aib_brain/tools/file-inventory.py`.
- Updated helper metadata strings in `.aib_brain/tools/file-inventory.py` to use file-inventory naming while keeping arguments and output unchanged.
- Updated optional helper path reference in `.aib_brain/prompts/aib-context.md`.
- Updated filename literals in `tests/test_reverse_engineer.py` to load and execute `.aib_brain/tools/file-inventory.py`.
- Updated active context references in `.aib_memory/context.md` from `reverse-engineer.py` to `file-inventory.py`.
- Updated the stale filename literal in `.aib_brain/tools/test_common.py` from `reverse-engineer.py` to `file-inventory.py`.

#### Tests
- unit: `tests/test_reverse_engineer.py` via `pytest` - pass.
- unit: `tests/test_analysis_prompt_structure.py` via `pytest` - pass.
- unit: `tests/test_instructions_md.py` via `pytest` - pass.
- integration: smoke run of `.aib_brain/tools/file-inventory.py --workspace . --max-files 3 --output .aib_memory/logs/inventory-smoke.jsonl` - pass.
- integration: scoped active-reference scan for `reverse-engineer.py` in `.aib_brain`, `tests`, and `.aib_memory/context.md` - pass (no active matches).

#### Outcome
Implementation completed successfully. The helper filename now matches behavior, active references are aligned, and targeted validation passed with no unresolved test failures or blockers.

#### Evidence
- `.aib_brain/tools/file-inventory.py`
- `.aib_brain/prompts/aib-context.md`
- `tests/test_reverse_engineer.py`
- `.aib_memory/context.md`
- `.aib_memory/logs/inventory-smoke.jsonl`
- `pytest` output: 33 passed in 0.19s across `tests/test_reverse_engineer.py`, `tests/test_analysis_prompt_structure.py`, and `tests/test_instructions_md.py`.

#### Notes (Optional)
- Historical archives under `.aib_memory/archives/` retain old-name references by design and were not modified.
