# AIC (AI Creator)

## Purpose

AIC is a lightweight, specification-first AI development operating system.

Goal:

```text
Intent
→ Clarify
→ Analyze
→ Decisions
→ Plan
→ Implement
→ Review
→ Close
```

Never:

```text
Intent
→ Code
```

---

## Principles

- Specification First
- Decision First
- Plan First
- Traceability
- Context Compression
- Token Efficiency
- Model Agnostic
- Repository Local Memory
- File-System Driven

---

## Inputs

Always read:

```text
1. ai_packet.md
2. Current request
3. Relevant project files (only when required)
```

Never load the entire repository unless explicitly needed.

---

## Execution Model

### Clarify

Execute when:

- requirements are incomplete
- ambiguity exists
- multiple valid solutions exist

Output:

```text
questions.md
```

Rules:

- never assume missing requirements
- ask only necessary questions
- prefer multiple choice answers
- stop until answers are provided

---

### Analyze

Execute when:

- request is sufficiently understood

Activities:

- identify affected areas
- identify risks
- identify assumptions
- identify dependencies
- identify decisions required
- identify missing information

Output:

```text
analysis.md
```

---

### Decisions

Capture important decisions.

Format:

```text
D-001

Decision:
...

Reason:
...
```

Rules:

- decisions survive longer than requests
- avoid storing unnecessary history
- store only decisions affecting future work

---

### Plan

Create implementation plan.

Output:

```text
plan.md
```

Plan must contain:

- ordered steps
- affected files
- validation steps
- risks

Rules:

- implementation must follow plan
- avoid implementation during planning

---

### Implement

Execute approved plan.

Output:

```text
implementation.md
```

Rules:

- implement only planned changes
- document deviations
- minimize scope creep
- preserve existing behavior unless requested

---

### Review

Verify:

- requirements satisfied
- decisions respected
- plan completed
- risks addressed

Output:

```text
review.md
```

---

### Close

Generate final summary.

Output:

```text
summary.md
```

Include:

- objective achieved
- files changed
- decisions created
- risks remaining
- follow-up actions

---

## Context Strategy

Use context layers.

```text
L0 Current Request
L1 Current Plan
L2 Active Decisions
L3 Relevant Requirements
L4 Relevant Technical Design
L5 Relevant Files
```

Load the minimum layer required.

---

## AI Packet

Primary external AI artifact:

```text
ai_packet.md
```

Contains:

- product summary
- current request
- relevant requirements
- relevant decisions
- technical context
- relevant files
- constraints
- risks
- open questions

Target size:

```text
1000-3000 tokens
```

---

## Constraints

Must:

- maintain traceability
- document decisions
- create plans before implementation
- prefer deterministic workflows
- minimize token usage

Must Not:

- skip clarification when needed
- bypass planning
- assume missing requirements
- load unnecessary context
- generate large verbose documents

---

## Success Criteria

Successful execution means:

```text
Intent understood
Questions resolved
Analysis completed
Decisions documented
Plan created
Implementation completed
Review passed
Request closed
```

AIC is a workflow engine for AI-assisted software development focused on clarity, traceability, portability, and token efficiency.
