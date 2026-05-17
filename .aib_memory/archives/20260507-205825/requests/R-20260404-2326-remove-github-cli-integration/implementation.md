# Implementation Log

Append-only entries. Add a new section for every execution update.

Files consulted before implementation:
- `.aib_memory/requests_register.md`
- `.aib_memory/requests/R-20260404-2326-remove-github-cli-integration/01-analysis.md`
- `.aib_memory/requests/R-20260404-2326-remove-github-cli-integration/iterations.md`
- `.aib_memory/references.md`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/conventions/product-documentation-convention.md`
- `.aib_brain/conventions/arch-01-convention.md`
- `.aib_brain/conventions/cmp-01-convention.md`
- `.aib_brain/conventions/rqt-02-convention.md`
- `.aib_brain/conventions/knw-01-convention.md`
- `.aib_brain/tools/menu.py`
- `.aib_brain/tools/initialize.py`
- `tests/test_menu.py`
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md`
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md`
- `.aib_memory/docs/03 Requirements/RQT-02.md`
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md`
- `.aib_memory/context.md`
- `.aib_brain/Concepts.md`

## Implementation Log

### Entry 2026-04-05 12:00 — Iteration 01

#### Scope

Full removal of GitHub Copilot CLI integration from the AIB codebase, plus four prompt file renames, `context.md` registration and seeding, wiring of `aib-context.md` into the renamed documentation prompt, CLI menu display string fixes, and product documentation updates across ARCH-01, CMP-01, RQT-02, and KNW-01.

#### Changes

- Renamed `.aib_brain/prompts/aib-create-analysis.md` → `aib-analysis.md`
- Renamed `.aib_brain/prompts/aib-create-plan.md` → `aib-plan.md`
- Renamed `.aib_brain/prompts/aib-create-questionnaire.md` → `aib-questionnaire.md`
- Renamed `.aib_brain/prompts/aib-update-documentation.md` → `aib-documentation.md`
- Removed `_PROMPT_TITLE_OVERRIDES`, `_PROMPT_DESC_OVERRIDES`, `_PROMPT_ORDER` dicts from `menu.py`
- Removed `_COPILOT_CLI_AVAILABLE` global and `_detect_copilot_cli()` function from `menu.py`
- Removed `discover_prompt_actions()` function from `menu.py`
- Removed `run_prompt_action()` function from `menu.py`
- Added `active_request_title: str | None = None` field to `MenuState` dataclass
- Updated `resolve_menu_state()` to extract and return `active_request_title` from register
- Updated `render_menu()`: removed `cli_available` param, removed prompt section blocks, removed `print("AI Builder")`, removed `print("--- Script actions ---")`, added title to active request display
- Updated `choose_action()`: removed `prompt_actions`, `cli_available`, and all prompt-navigation logic
- Removed `TestDetectCopilotCli`, `TestRunPromptAction`, `TestDiscoverPromptActions` test classes from `tests/test_menu.py`
- Removed `_detect_copilot_cli`, `discover_prompt_actions`, `run_prompt_action` from `test_menu.py` imports; moved `import sys` to top
- Updated internal cross-reference in `aib-analysis.md`: `aib-create-questionnaire.md` → `aib-questionnaire.md`
- Updated reference in `aib-implement.md`: `aib-update-documentation.md` → `aib-documentation.md`
- Added post-update step to `aib-documentation.md` invoking `aib-context.md`
- Updated `initialize.py` to seed `.aib_memory/context.md` stub on workspace initialization
- Added `REF-0029` row for `.aib_memory/context.md` (`type=other`, `edit_allowed=N`) to `.aib_memory/references.md`
- Updated `.aib_brain/Concepts.md`: removed GitHub Copilot CLI from vendor-agnostic example; renamed all five prompt file references to new names
- Updated `ARCH-01.md`: removed Copilot CLI detection and prompt-action gating from AIB Command Menu description; added change log entry
- Updated `CMP-01.md`: removed copilot CLI gating from CMP-ART-0006 description
- Updated `RQT-02.md`: removed copilot CLI stdin passthrough clause from FR-008
- Updated `KNW-01.md`: revised TERM-0013 definition and examples; incremented version to 2; added change log entry
- Updated `.aib_memory/context.md`: removed stale Copilot CLI references from FR-008 description, AIB Command Menu description, module breakdown, test description, and configuration section

#### Tests

- Unit/integration: `python -m pytest tests/ -v` — 80 tests collected, 80 passed, 0 failed
- Three removed test classes covered `_detect_copilot_cli`, `run_prompt_action`, and `discover_prompt_actions` (all deleted functions) — their removal is intentional

#### Outcome

All scope items from iteration 01 implemented successfully. Menu is simplified to script actions only with active request ID and title display. All prompt files renamed to vendor-neutral names and all internal references updated. Tests pass without modification beyond removing tests for deleted code.

#### Evidence

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.0.1
collected 80 items
80 passed in 3.02s
```

#### Notes (Optional)

Assumption A3 applied: `context.md` registered as `type=other` with `edit_allowed=N` (not `product-doc`) to avoid convention-enforcement preflight complexity. Context.md content updated inline during documentation step, equivalent to executing `aib-context.md`.
