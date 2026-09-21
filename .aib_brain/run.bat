@rem run.bat: Launch the AIB menu with Python bytecode generation disabled.
@rem Part of the AIB core interaction layer.
@echo off
setlocal
set PYTHONDONTWRITEBYTECODE=1
set SCRIPT_DIR=%~dp0
set WORKSPACE_DIR=%SCRIPT_DIR%..
python -B "%SCRIPT_DIR%tools\menu.py" --workspace "%WORKSPACE_DIR%"
