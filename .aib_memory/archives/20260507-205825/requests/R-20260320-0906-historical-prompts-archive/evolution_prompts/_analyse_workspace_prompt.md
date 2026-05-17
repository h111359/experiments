# Concepts Analysis

This document defines concepts analysis of the workspace written in a document `Concepts_Analysis_20260308.md`.

The purpose of the analysis is to evaluate the clarity, completeness, consistency, logic, integrity, and practicality of the workspace concepts and definitions.

## Scope and Inputs

### Source documents

The analysis MUST review all the files in the workspace (except this file)

### Cross-file interpretation rule

The analysis should treat the workspace documents as a single evolving set:

- When two statements differ, the analysis MUST flag the inconsistency and propose a unifying resolution (do not silently choose one).

## Required Finding Tags (Issue Types)

Every finding MUST be labeled with exactly one of the following tags.

1. **[requirement-gap]**: Absence of critical information that would permit multiple or conflicting implementation options.
2. **[requirement-ambiguity]**: Unclear, vague, or imprecise statements that can be interpreted in multiple ways.
3. **[requirement-conflict]**: Contradictions or incompatibilities within one file or across multiple files.
4. **[requirement-completeness]**: Areas where the concepts do not sufficiently address the stated objective, leaving logical steps missing.
5. **[requirement-redundancy]**: Repetitive/overlapping statements that add noise or could cause duplication/inconsistent maintenance.
6. **[requirement-consistency]**: Inconsistent terminology, formatting, naming, definitions, or conventions.
7. **[spelling-grammar]**: Spelling or grammar errors

## Output Quality Rules

The analysis document MUST:

- Be concise and well-structured.
- Focus on *main issues* across all source documents (do not list every minor nit).
- Provide evidence for each finding via specific references (file + section heading and/or short excerpt).
- Propose actionable solutions inline each finding that improve logic, completeness, consistency, integrity, and practicality.

The analysis document MUST NOT:

- Invent requirements that are not implied by the source documents.
- Resolve ambiguity by assumption without calling it out.
- Produce “how-to implement” technical designs unless the sources already request them; prefer “what” and “constraints”.

## Required Structure for the analysis

The result MUST follow this structure and headings (in this order):

---

### 1. Introduction

Include:

- Scope of the analysis (what is being assessed).
- Documents reviewed.

---

### 2. Findings

Provide findings under each category below. Each category should summarize issues collectively across documents, and then list specific, actionable examples.

#### 2.1 Requirement Gaps

#### 2.2 Requirement Ambiguities

#### 2.3 Requirement Conflicts

#### 2.4 Requirement Completeness

#### 2.5 Requirement Redundancies

#### 2.6 Requirement Consistencies

#### 3 Clarifying Questions

---

---

## Finding Entry Format (Required)

Every listed finding in section **2. Findings** MUST use the following per-item format.

**Finding ID:** <CATEGORY>-<NN> (e.g., GAP-01, AMB-02, CONFLICT-01)
**Type:** [requirement-gap] | [requirement-ambiguity] | [requirement-conflict] | [requirement-completeness] | [requirement-redundancy] | [requirement-consistency]
**Summary:** One sentence describing the problem.
**Evidence:**
- Source: <file>
- Location: <section heading / subsection>
- Excerpt: “<short quote>” (optional but preferred)
**Why it matters:** One short paragraph describing the practical impact.
**Suggested resolution direction:** One short paragraph describing the *kind* of update needed (the concrete edits belong in Proposed Solutions).
**Suggested resolution:** 
- State *what to change* (not only “clarify it”).
- Specify *where to change it* (which source file(s) and which section(s)).


## Clarifying Questions Format

If the analysis identifies high-impact gaps/ambiguities that require stakeholder input, the analysis MAY include Clarifying Questions. For each questions should be generated several most probable answers labeled with A, B, C, D … + option for Other answer (where the user to write own answer). The rationale for the question shall be included. Recommended option shall be marked. The user shall edit the questionnaire file by checking the answer they prefer or provide free text answer. The format of the questions shall be such so the user to be able with minimal edition to mark the desired answer - for example the A/B/C/D/Other to be formatted as markdown checklist.

Rules:

- Maximum 13 questions per analysis iteration.
- Prefer “What should be achieved / decided?” over “How should we implement?”.
- Use checkbox options and include an “Other” option.

