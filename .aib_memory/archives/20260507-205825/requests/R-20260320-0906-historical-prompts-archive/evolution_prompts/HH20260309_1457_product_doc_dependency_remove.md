## Goal

AIB executio should not depend on Product_Documentation.md file

## Context

- If exists, consult the questionnaire file which is same name as the current one with difference - ending with ".questionnaire.md"
- Currently at least `.aib_brain\tools\initialize.py` and `.aib_brain\tools\common.py` depend on `.aib_brain\Product_Documentation.md`

## Objectives

- Instead of dynamic loading, `.aib_brain\templates\references-template.md` to be updated once with default locations of the documents and to be used for seeding.

## Rules

## Format (optional)

