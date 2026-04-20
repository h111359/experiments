## Version 1.0.0

### Issue #1

Added semver named file for indicating the version of AIB



## Version 1.0.1

Added file `docs\Copilot_Issue_Assignment_Rules.md` with the expected behavior of GitHub copilot when working on an Issue.

Changed the location of several files:
- `docs\Concepts.md`
- `docs\Product_Documentation.md`

Created `docs\Development_and_Deployment_Specification.md` first version describing how the AI Builder product life cycle is organized. 

### Issue [#3](https://github.com/The-Coca-Cola-Company/AI_Builder/issues/3): Remove inquiry for workspace, process and iteration - use defaults

Updated the interactive menu to use default workspace/request/iteration values without prompting, and removed destructive-action confirmation prompts in menu runs.

## Version 1.0.2

Changed the location of several files:
- `.aib_brain\Concepts.md`
- `.aib_brain\conventions\Product_Documentation.md`

Improvements in `.aib_brain\conventions\questionnaire-convention.md`

Added the files `.aib_brain\Concepts.md`, `.aib_brain\conventions\product-documentation-convention.md` and `.aib_brain\conventions\Product_Documentation.md`

## Version 1.0.3

Removing estimation and ownership topics from `.aib_brain\conventions\plan-convention.md` - not in the scope of AIB to maintain them

Improvement of `.aib_brain\prompts\aib-create-plan.md` to force reading the documentation

In `.aib_brain\prompts\aib-create-questionnaire.md` - remove the hard writen path to documentation - it should be dynamically defined in `.aib_memory\references.md`

## Version 1.0.4

Updated prompt definitions to enforce reading documentation files listed in `.aib_memory\references.md` during prompt execution.

Updated `.aib_brain\prompts\aib-implement.md` and `.aib_brain\prompts\aib-update-documentation.md` to restrict edits to documentation paths marked with `edit_allowed=Y` unless explicitly instructed otherwise.
