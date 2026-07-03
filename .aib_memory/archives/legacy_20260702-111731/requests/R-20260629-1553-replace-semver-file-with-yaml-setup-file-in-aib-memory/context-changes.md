# Context Changes for R-20260629-1553

## Solution

[I] aib-setup.yaml in .aib_memory/ is the human-editable YAML setup file with flat top-level keys memory_version and default_questions_number; replaces the empty vX.Y.Z file convention for memory-side version tracking; initialize.py generates it on workspace setup with inline defaults and restores it with memory_version merge on upgrade.

[I] read-setup.py retrieves a single named option from .aib_memory/aib-setup.yaml; prints bare value to stdout; exits with code 1 and prints an error to stderr when the requested key is absent or the file is missing.

## File Structure

[U]   tools/ — Python scripts: close-request.py, common.py, create-request.py, edit-context.py, file-inventory.py, finalize-input.py, initialize.py, input-header.py, log-entry.py, menu.py, move-request-artifacts.py, read-setup.py, verify-context.py, verify-input.py

[I]   aib-setup.yaml — human-editable YAML setup file; flat top-level keys: memory_version, default_questions_number
