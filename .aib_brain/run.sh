#!/usr/bin/env sh
# run.sh: Launch the AIB menu with Python bytecode generation disabled.
# Part of the AIB core interaction layer.
export PYTHONDONTWRITEBYTECODE=1
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
WORKSPACE_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
python3 -B "$SCRIPT_DIR/tools/menu.py" --workspace "$WORKSPACE_DIR"
