# AIB Workspace Guide

AI Builder (AIB) helps you manage development requests through a structured, AI-assisted workflow.

## Prerequisites

- Python 3.10+ in your terminal.
- Terminal open at the repository root.

## Quick Start

Launch the interactive menu:

```bat
.aib_brain\run.bat        # Windows
```
```sh
sh .aib_brain/run.sh      # Linux / macOS
```

The menu shows copy-paste prompt commands for all AIB actions.

## Daily Flow

1. Write your intent into the `## Input` section of `.aib_memory/input.md`.
2. _(Optional)_ Run analysis in AI chat: `Execute .aib_brain/prompts/aib-analysis.md`
3. Run implement in AI chat: `Execute .aib_brain/prompts/aib-implement.md`
   — If no active request exists, the prompt auto-creates one from `input.md` and proceeds.
   — The request is closed automatically when implementation completes.

## Prompt Invocations

```
Execute .aib_brain/prompts/aib-analysis.md
```
```
Execute .aib_brain/prompts/aib-implement.md
```
```
Execute .aib_brain/prompts/aib-context.md
```

## Use Cases

**Full analysis → implement flow**
1. Write request into `input.md → ## Input`.
2. Run `aib-analysis.md` — auto-creates request, generates `analysis.md` and `request.md`.
3. Review `request.md`; adjust if needed.
4. Run `aib-implement.md` — executes scope and closes request automatically.

**Direct implement (no formal analysis)**
1. Write request into `input.md → ## Input`.
2. Run `aib-implement.md` — auto-creates request from input and implements.

**Regenerate workspace context**
- Run `aib-context.md` at any time (no active request required) to refresh `.aib_memory/context.md`.

**"No changes" toggle**
Check `No changes — provide answer only` in `input.md` before running `aib-analysis.md`. The prompt writes only a timestamped `answer-<timestamp>.md` in the request folder and resets `input.md`; no other files are modified.

## Workspace Instructions (`instructions.md`)

`.aib_memory/instructions.md` is a persistent directives file read by every AIB prompt before it executes. Write any workspace-specific rules here — coding conventions, naming rules, always/never behaviors. If absent or empty, all prompts continue normally.

**Do not store secrets, credentials, or PII in this file.**

## Question Threshold

Controls when `aib-analysis.md` raises a decision to you versus resolving it autonomously. Set in `input.md → ## Options` (default `[x] 3`). Reset to default after each analysis run.

| Level | Name | AI behavior |
| --- | --- | --- |
| 1 | Trivial | Resolve autonomously |
| 2 | Minor | Resolve autonomously |
| 3 | Moderate | Raise Q-block if threshold ≤ 3 (default) |
| 4 | Significant | Raise Q-block if threshold ≤ 4 |
| 5 | Critical | Always raise Q-block |

## Request Folder Artifacts

| Artifact | Created by | Description |
| --- | --- | --- |
| `request.md` | `aib-analysis.md` | Request specification (12 mandatory sections). Active copy lives at `.aib_memory/request.md`; moved to request subfolder after implementation. |
| `analysis.md` | `aib-analysis.md` | Reasoning artifact (not read by `implement`). |
| `implementation.md` | `aib-implement.md` | Append-only implementation log. |
| `inputs/input-archive-*.md` | `aib-analysis.md` | Archived `input.md` per analysis run. Never read by prompts after archiving. |
| `UAT_scenarios.md` | `aib-analysis.md` | Manual test scenarios (created when automated assertions are insufficient). |
| `answer-<timestamp>.md` | `aib-analysis.md` | Written when "No changes" toggle is set. |

