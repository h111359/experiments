# AIB Workspace Guide

This guide explains how to work with AI Builder (AIB) from the `.aib_brain` folder.

## Purpose

Use AIB tools to manage requests in a consistent way from the workspace root.

## Prerequisites

- Python 3.10+ available in your terminal.
- Open terminal in the repository root (the folder that contains `.aib_brain`).

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
The menu supports:
- Up/Down arrows and Enter
- Numeric shortcuts for actions
- `Q` to quit

## Typical Daily Flow

The canonical workflow:

1. **Initialize** once (or when `.aib_memory/` is missing): `initialize.py`
2. **Write intent**: Write your request description into the `## Input` section of `.aib_memory/input.md`.
3. _(Optional)_ **Analyze**: `Execute .aib_brain/prompts/aib-analysis.md` in VS Code chat — the prompt auto-creates a request from your input, archives `input.md`, resets it with the active request ID, generates `analysis.md`, and updates `request.md`.
4. **Implement**: `Execute .aib_brain/prompts/aib-implement.md` in VS Code chat — if no Active request exists, the prompt auto-triggers the analysis flow first.
5. **Close**: Handled automatically at the end of `aib-implement.md` — no user action required.

> **"No changes" toggle**: If you check the `No changes — provide answer only` option in `input.md` before running `aib-analysis.md`, the prompt writes only a timestamped `answer-<timestamp>.md` in the request folder and resets `input.md` with the active request ID. No other files are modified — `request.md` and `analysis.md` are left unchanged.

## Using `aib-*` Prompts

Use prompt files in `.aib_brain/prompts/` to generate and execute AIB artifacts for the active request.

Available prompt files:
- `.aib_brain/prompts/aib-analysis.md`
- `.aib_brain/prompts/aib-implement.md`
- `.aib_brain/prompts/aib-context.md`

Recommended order per request:
1. _(Optional)_ Run `aib-analysis.md` to create `analysis.md` and update `request.md` with plan and assumptions.
2. Run `aib-implement.md` to execute the change and update `implementation.md`.
3. `aib-context.md` is called automatically at the end of `aib-implement.md`; run it manually to regenerate `.aib_memory/context.md` at any other time.

## How to Run a Prompt in VS Code Chat

1. Ensure you are in a valid AIB state (`initialize` done, active request exists).
2. Open VS Code Copilot chat.
3. Type or paste the invocation command and send it to the AI agent.
4. Verify the output file is created under `.aib_memory/requests/<request-folder>/`.

### Copy-paste invocations for VS Code chat

```
Execute .aib_brain/prompts/aib-analysis.md
```

```
Execute .aib_brain/prompts/aib-implement.md
```

```
Execute .aib_brain/prompts/aib-context.md
```

## Use Case Scenarios

### Scenario 1 — Standard analysis → implement flow

You have a new feature or change request and want to go through the full analysis-implement cycle.

1. Write your request description into the `## Input` section of `.aib_memory/input.md`.
2. In VS Code chat: `Execute .aib_brain/prompts/aib-analysis.md` — the prompt auto-creates a request, archives input, and generates analysis.
3. Review and refine `request.md` in the newly created request folder if needed.
4. In VS Code chat: `Execute .aib_brain/prompts/aib-implement.md`
5. The request is closed automatically at the end of implement — no user action required.

### Scenario 2 — Direct implement without a formal analysis

The change is small and well-understood; no separate analysis is needed.

1. Write your request description into the `## Input` section of `.aib_memory/input.md`.
2. In VS Code chat: `Execute .aib_brain/prompts/aib-implement.md` — if no Active request exists, it automatically creates one from your input and proceeds.
3. The request is closed automatically at the end of implement — no user action required.

### Scenario 3 — Regenerate / update workspace context

You want an up-to-date synthesis of the workspace in `.aib_memory/context.md` — either after implementing a change or as a standalone refresh.

1. `aib-implement.md` automatically runs `aib-context.md` at the end of each implementation run.
2. To regenerate at any other time (no active request required): In VS Code chat: `Execute .aib_brain/prompts/aib-context.md`
3. The file `.aib_memory/context.md` is fully replaced with an up-to-date synthesis.

### Scenario 4 — Reverse-engineer workspace into context

You have an existing codebase with no AIB product context and want to populate `context.md` from the workspace.

1. Ensure AIB is initialized (`initialize.py`).
2. Open a request describing the reverse-engineering task.
3. In VS Code chat: `Execute .aib_brain/prompts/aib-context.md`
4. Review and validate the generated `.aib_memory/context.md`.
5. Close the request.

## Troubleshooting

- `python` or `python3` not found:
  - Install Python and ensure it is on PATH.
  - On Windows, open a new terminal after installation.
- Permission error when running `run.sh`:
  - Use `sh .aib_brain/run.sh` as shown above.
- Menu starts but action fails:
  - Re-run from repository root so relative paths resolve correctly.
- Prompt file not found when executing in VS Code chat:
  - Verify the prompt file name matches one of the files listed in the "Available prompt files" section above.

## Notes

- This README is updated on explicit request.
- Paths are repository-relative for portability.
