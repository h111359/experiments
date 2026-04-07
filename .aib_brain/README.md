# AIB Workspace Guide

This README explains how to work with AI Builder (AIB) from the `.aib_brain` folder.

## Purpose

Use AIB tools to manage requests and iterations in a consistent way from the workspace root.

## Prerequisites

- Python 3.10+ available in your terminal.
- Open terminal in the repository root (the folder that contains `.aib_brain`).
- `.aib_brain/tools` scripts available (already part of this repository).

## Quick Start

Run the interactive command menu.

### Windows

```bat
.aib_brain\run.bat
```

### Linux/macOS

```sh
sh .aib_brain/run.sh
```

Menu usage and launch instructions (kept here to avoid wasting menu space):

```text
AI Builder terminal command menu
Launch with .aib_brain/run.bat (Windows) or .aib_brain/run.sh (Linux/macOS).
Use Up/Down arrows + Enter, or press the action number directly.
Press Q to quit from the menu.
```

```text
AI Builder
Command menu for .aib_brain/tools scripts (launchers in .aib_brain)
```

The menu supports:
- Up/Down arrows and Enter
- Numeric shortcuts for actions
- `Q` to quit

## Common Commands

Most users should use the interactive menu above. If needed, you can run tools directly.

### Windows examples

```bat
python .aib_brain\tools\initialize.py --workspace .
python .aib_brain\tools\create-request.py --workspace . --title "My request title"
python .aib_brain\tools\create-iteration.py --workspace . --summary "Follow-up work"
python .aib_brain\tools\close-iteration.py --workspace .
python .aib_brain\tools\close-request.py --workspace .
```

### Linux/macOS examples

```sh
python3 .aib_brain/tools/initialize.py --workspace .
python3 .aib_brain/tools/create-request.py --workspace . --title "My request title"
python3 .aib_brain/tools/create-iteration.py --workspace . --summary "Follow-up work"
python3 .aib_brain/tools/close-iteration.py --workspace .
python3 .aib_brain/tools/close-request.py --workspace .
```

## Typical Daily Flow

1. Initialize once (or when missing state): `initialize.py`
2. Start work: `create-request.py`
3. Add progress steps: `create-iteration.py`
4. Finish current step: `close-iteration.py`
5. Finish whole request: `close-request.py`

## Using `aib-*` Prompts For Iteration Work

Use prompt files in `.aib_brain/prompts/` to generate and execute iteration artifacts for the active request.

Available prompt files:
- `.aib_brain/prompts/aib-create-analysis.md`
- `.aib_brain/prompts/aib-create-questionnaire.md`
- `.aib_brain/prompts/aib-create-plan.md`
- `.aib_brain/prompts/aib-reverse-engineer.md`
- `.aib_brain/prompts/aib-implement.md`
- `.aib_brain/prompts/aib-update-documentation.md`

Recommended order per iteration:
1. Run `aib-create-analysis.md` to create `<ITERATION_ID>-analysis.md`.
2. Run `aib-create-questionnaire.md` if clarification is needed, then answer the generated questionnaire.
3. Run `aib-create-plan.md` to create a concrete execution plan.
4. Run `aib-implement.md` to execute the change and update `implementation.md`.
5. Run `aib-update-documentation.md` when documentation updates are in scope.

How to run a prompt in chat-based tools:
1. Ensure you are in a valid AIB state (`initialize` done, active request exists, active iteration exists).
2. Open the prompt file from `.aib_brain/prompts/`.
3. Ask the AI agent to execute that file directly (example: `Execute .aib_brain/prompts/aib-create-plan.md`).
4. Verify the output file is created under `.aib_memory/requests/<request-folder>/` with the current iteration prefix.

Optional CLI-style invocation example:

```sh
copilot -sp "Execute .aib_brain/prompts/aib-create-analysis.md"
copilot -sp "Execute .aib_brain/prompts/aib-create-questionnaire.md"
copilot -sp "Execute .aib_brain/prompts/aib-create-plan.md"
copilot -sp "Execute .aib_brain/prompts/aib-implement.md"
copilot -sp "Execute .aib_brain/prompts/aib-update-documentation.md"
```

## Troubleshooting

- `python` or `python3` not found:
  - Install Python and ensure it is on PATH.
  - On Windows, open a new terminal after installation.
- Permission error when running `run.sh`:
  - Use `sh .aib_brain/run.sh` as shown above.
- Wrong workspace path behavior:
  - Run commands from repository root and keep `--workspace .`.
- Menu starts but action fails:
  - Confirm script exists under `.aib_brain/tools`.
  - Re-run from repository root so relative paths resolve correctly.

## Notes

- This README is updated on explicit request.
- Paths are repository-relative for portability.

## When to Create a New Iteration vs a New Request

Use this decision guide to decide whether your next work unit opens a new **iteration** inside the current request or requires a brand-new **request**.

### Create a new Iteration when

- The goal and scope **have not changed** — you are continuing or extending the work of the active request.
- A prior iteration produced open questions, partial results, or follow-up tasks that are still within the original scope.
- The change is a **refinement, correction, or sub-task** of what was already approved in `request.md`.

**Example:** Iteration 01 produced an analysis with open questions to the user. After the user answers, you open Iteration 02 to create the plan — same goal, different artifact.

### Create a new Request when

- The **goal or scope has fundamentally changed** compared to the current request.
- The work addresses a **different problem, feature, or issue** that is independent of the current request.
- The active request has been **closed** (requests must be Active to receive new iterations).

**Example:** While implementing issue-31, you discover an unrelated bug in another subsystem. Open a new request for the bug rather than extending issue-31's scope.

### Decision checklist

| Question | Yes → | No → |
| --- | --- | --- |
| Is the active request still `Active`? | Consider a new iteration | Must create new request |
| Does this work fall within the original `## Scope` in `request.md`? | New iteration | New request |
| Is this a follow-up to an unresolved item in the latest iteration? | New iteration | New request |
| Is this an independent goal unrelated to the current request? | New request | New iteration |
