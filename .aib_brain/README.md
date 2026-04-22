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

## Workspace Instructions

The file `.aib_memory/instructions.md` is a persistent, workspace-level instructions file that is read by every AIB prompt (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) before executing its main logic.

**Purpose:** Encode workspace-specific behavioral directives that the AI must always observe, regardless of which prompt is being executed. This is analogous to the GitHub Copilot `.github/copilot-instructions.md` pattern but requires no external dependency.

**Location:** `.aib_memory/instructions.md`

**How to populate:** Open the file and write any free-form Markdown directives you want all AIB prompts to respect. No schema enforcement is applied — any content is valid. Examples of useful directive categories:

- Coding conventions not already captured in `.aib_brain/conventions/` (e.g., preferred library choices, naming rules specific to this workspace).
- Always/never behaviors (e.g., "always use 4-space indentation", "never use `import *`").
- Domain-specific constraints the AI must respect in every interaction.
- Preferred output format or verbosity instructions.

**Graceful absence:** If `instructions.md` is absent or empty, all prompts continue executing normally — no error is raised and no execution is halted.

**Security note:** Do NOT store secrets, credentials, API keys, tokens, or any personally identifiable information (PII) in `instructions.md`. The file is plain text and is not encrypted.

## Question Threshold

The `Question threshold` setting controls when `aib-analysis.md` surfaces a decision point as a user-facing Q-block versus resolving it autonomously. The threshold value is stored in `.aib_memory/input.md ## Options` (checkbox row, reset to default `[x] 3` after each analysis run) and can be changed by the developer before running analysis.

**Format in `input.md`:**
```
- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5
```

**5-Level Severity Scale:**

| Level | Name | Definition | AI Behavior | Concrete Example |
| --- | --- | --- | --- | --- |
| 1 | Trivial | No meaningful impact on outcome, cost, or risk; best practice is universally established and unambiguous. | Resolve autonomously; document reasoning inline in the relevant `request.md` section. | Choosing a variable name convention when one is already defined in a convention file. |
| 2 | Minor | Preference-level fork where either option satisfies the success criteria; impact is cosmetic or reversible within a single task. | Resolve autonomously; document reasoning inline in the relevant `request.md` section. | Deciding whether to use a bullet list or a numbered list for a non-schema documentation section. |
| 3 | Moderate | Fork with meaningful impact on implementation scope, test coverage, or documentation approach; multiple valid options exist and none is clearly dominant without product-owner input. | Raise Q-block if threshold ≤ 3 (default behavior). | Deciding whether a new optional artifact should be committed to VCS or excluded via `.gitignore`. |
| 4 | Significant | Architectural or business decision with cross-component impact; the wrong choice may require rework across multiple files or workflows. | Raise Q-block if threshold ≤ 4. | Deciding whether a new configuration value should live in `input.md`, a new config file, or a tool script constant. |
| 5 | Critical | Irreversible or high-risk decision that affects product safety, security, data integrity, or compliance; wrong choice cannot be safely undone. | Always raise Q-block regardless of threshold setting. | Deciding whether to drop a column from the requests register that is referenced by existing closed requests. |

**Boundary rules:**
- A decision rated below the configured threshold MUST be resolved autonomously by the AI with inline reasoning documented in the relevant `request.md` section.
- A decision rated at or above the configured threshold MUST be surfaced as a Q-block.
- Level 5 decisions MUST always raise a Q-block regardless of threshold.
- The threshold row is reset to `[x] 3` each time `aib-analysis.md` resets `input.md` at the end of a run.
- Before raising any Q-block, the AI MUST verify the answer is not already present in `context.md`, convention files, or the required-read set from `references.md`. If found, it applies the answer directly and MUST NOT create a Q-block.

## Request Folder Artifacts

Each request folder under `.aib_memory/requests/<request-folder>/` may contain the following artifacts:

| Artifact | Created by | Required | Description |
| --- | --- | --- | --- |
| `request.md` | `aib-analysis.md` (auto-request branch) | Yes | AI-generated request specification with 12 mandatory sections. |
| `analysis.md` | `aib-analysis.md` | Optional | Reasoning artifact (not read by `implement`). Contains Executive Summary, Domain Knowledge, Technical Context, Research, External Benchmarking, Minimal Spikes, AI Copilot Suggestions, Testing, and Multi-Perspective Stakeholder Review. |
| `implementation.md` | `aib-implement.md` | Yes (after first implement run) | Append-only implementation log. |
| `inputs/input-archive-*.md` | `aib-analysis.md` | Yes (one per analysis run) | Archived copy of `input.md` content at analysis time. MUST NOT be read by any prompt beyond archiving. |
| `UAT_scenarios.md` | `aib-analysis.md` | Optional | Created when the request requires manual testing scenarios that cannot be expressed as automated assertions. Documents UAT test cases for human execution. |
| `answer-<timestamp>.md` | `aib-analysis.md` | Optional | Written when the "No changes — provide answer only" toggle is set; contains the timestamped answer. |
