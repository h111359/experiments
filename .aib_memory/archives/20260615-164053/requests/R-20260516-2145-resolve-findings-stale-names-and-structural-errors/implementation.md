Implementation updates for request R-20260516-2145.

Files from .aib_memory taken into consideration:
- .aib_memory/instructions.md
- .aib_memory/requests_register.md
- .aib_memory/plan-R-20260516-2145.md
- .aib_memory/context.md
- .aib_memory/input.md

## Implementation Log

### Entry 2026-05-17 09:46
#### Scope
Apply all planned fixes for stale prompt/file-name references and structural inconsistencies, remove obsolete UAT artifact movement behavior, validate with full tests, refresh context, and close the active request.

#### Changes
- Updated .aib_brain/prompts/aib-analyze.md to state 6 mandatory analysis sections and require at least three industry findings.
- Reordered and renumbered section 4 in .aib_brain/conventions/analysis-convention.md to 4.1 through 4.6 in mandatory order, and aligned stale references to current naming.
- Updated .aib_brain/prompts/aib-refresh-context.md by replacing remaining dangling Phase 3 references with Phase 2.
- Replaced all stale aib-context.md references in .aib_brain/conventions/context-convention.md with aib-refresh-context.md.
- Updated targeted entries in .aib_memory/context.md for Analysis glossary naming and GC range alignment.
- Updated .aib_brain/tools/initialize.py seeded context instruction to reference aib-refresh-context.md.
- Updated .aib_brain/tools/create-request.py comments to reference plan-<request_id>.md and aib-analyze.md.
- Removed UAT_scenarios from .aib_brain/tools/move-request-artifacts.py artifact handling and adjusted related wording.
- Removed obsolete UAT artifact tests from tests/test_artifact_placement.py.
- Updated .aib_brain/README.md request artifact table to remove the obsolete UAT_scenarios row.
- Appended curated bullets for this implementation run to logs/next_version_changes.md.

#### Tests
- unit/integration: full workspace tests via `python -m pytest tests/ -v` - pass (289 passed, 4 subtests passed).

#### Outcome
Implementation completed successfully with all planned findings addressed and no unresolved test failures. Context was refreshed and request lifecycle closure was completed by moving active artifacts first and then closing the request. Residual risk is low and limited to future drift if naming conventions change again.

#### Evidence
- .aib_brain/prompts/aib-analyze.md
- .aib_brain/conventions/analysis-convention.md
- .aib_brain/prompts/aib-refresh-context.md
- .aib_brain/conventions/context-convention.md
- .aib_brain/tools/initialize.py
- .aib_brain/tools/create-request.py
- .aib_brain/tools/move-request-artifacts.py
- tests/test_artifact_placement.py
- logs/next_version_changes.md
- Command output evidence:
```text
c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe -m pytest tests/ -v
289 passed, 4 subtests passed in 15.64s

c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe .aib_brain/tools/move-request-artifacts.py --workspace .
Exit code: 0

c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe .aib_brain/tools/close-request.py --workspace .
Closed request: R-20260516-2145
Exit code: 0
```

#### Notes (Optional)
The implementation followed the active request plan and preserved the required script invocation order: move-request-artifacts.py before close-request.py.
