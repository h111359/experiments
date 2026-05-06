#  Initial request

Make the check for existence of .aib_memory/ folder automatic. If it does not exist - initialize, otherwise don't change it. There is no need of menu entry for the initialization - it should happen automatically when run.bat is executed.

The menu should be dynamic - it should show only the possible next steps. If there is no active request, the option for closing of the active request should not be visible. And vice versa - when there is an active request, the option for creating of request should not be visible. Same for iterations - when there is no active iteration, the option for closing the iteration should not be visible and vise versa - when there is active iteration - the option for creation of new iteration should not be visible.

The following instructions shown in the menu should be described in README.md in .aib_brain and should not waste the space in the menu:
```
AI Builder terminal command menu
Launch with .aib_brain/run.bat (Windows) or .aib_brain/run.sh (Linux/macOS).
Use Up/Down arrows + Enter, or press the action number directly.
Press Q to quit from the menu.
```

The following instructions shown in the menu should be described in README.md in .aib_brain and should not waste the space in the menu:
```
AI Builder
Command menu for .aib_brain/tools scripts (launchers in .aib_brain)
```

The menu should write in concise way which is the active request and the active iteration (or to display there is no such)


# Improved version of the request

## Goal
Improve AI Builder startup and the interactive command menu so it is self-initializing (when needed) and state-aware.

## Background
The current menu is static, includes usage instructions in the UI, and requires manual initialization of `.aib_memory`, which can be forgotten.

## Scope
- Automatic initialization on launch:
  - When launching the menu via `.aib_brain/run.bat` or `.aib_brain/run.sh`, automatically check whether `.aib_memory/` exists.
  - If `.aib_memory/` does not exist, initialize it (create `.aib_memory` and seed default registries/docs).
  - If `.aib_memory/` exists, do not modify any files under it.
  - Remove the “Initialize AIB memory” action from the interactive menu.

- Dynamic menu:
  - If there is no active request: show “Create request” and hide “Close request”, “Create iteration”, “Close iteration”.
  - If there is an active request: hide “Create request” and show “Close request”.
  - If there is no active iteration: hide “Close iteration” and show “Create iteration”.
  - If there is an active iteration: hide “Create iteration” and show “Close iteration”.

- Menu content cleanup:
  - Remove these blocks from the menu UI and include them in `.aib_brain/README.md`:

AI Builder terminal command menu
Launch with .aib_brain/run.bat (Windows) or .aib_brain/run.sh (Linux/macOS).
Use Up/Down arrows + Enter, or press the action number directly.
Press Q to quit from the menu.

AI Builder
Command menu for .aib_brain/tools scripts (launchers in .aib_brain)

- Active state display:
  - Display active request ID (or “No active request”).
  - Display active iteration ID for that request (or “No active iteration”).

## Out of scope
- No new menu pages, filters, or UI modes beyond dynamic visibility and status display.
- No changes to request/iteration lifecycle rules beyond computing visibility.

## Constraints
- Do not modify an existing `.aib_memory/` folder.

## Success criteria
- Running `.aib_brain/run.bat` (or `.aib_brain/run.sh`) in a workspace with no `.aib_memory/` creates `.aib_memory/` and opens the menu successfully.
- Running the launcher when `.aib_memory/` already exists does not modify any `.aib_memory` contents.
- The menu shows only valid next actions based on active request/iteration state.
- The menu does not display the two instruction blocks, and `.aib_brain/README.md` contains them.
- The menu displays active request and iteration concisely.