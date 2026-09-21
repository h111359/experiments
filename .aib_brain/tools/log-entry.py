#!/usr/bin/env python3
"""
log-entry.py: Append UTC-timestamped audit log entries to the shared active log.
Part of the AIB core tooling layer.
Responsibilities: write a single timestamped log entry to .aib_memory/log.md
regardless of workspace state; print the entry to stdout; create the log file
lazily on first write.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from common import ValidationError, ensure_workspace

# Log entry timestamp format: YYYYMMDD-HHmmss (UTC 24-hour).
_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"

# Filename for the single shared active runtime log.
_ACTIVE_LOG_FILENAME = "log.md"


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed namespace with workspace and message.
    """
    parser = argparse.ArgumentParser(
        description="Append a UTC-timestamped log entry to the shared active log."
    )
    parser.add_argument(
        "--workspace", default=".", help="Workspace root path (default: current directory)."
    )
    parser.add_argument(
        "--message", required=True, help="Log message text to append."
    )
    return parser.parse_args()


def _format_entry(message: str) -> str:
    """Format a single log entry with a UTC timestamp prefix.

    Args:
        message: The log message text.

    Returns:
        Formatted entry string: ``YYYYMMDD-HHmmss: <message>\\n``.
    """
    timestamp = datetime.now(timezone.utc).strftime(_TIMESTAMP_FORMAT)
    return f"{timestamp}: {message}\n"


def main() -> int:
    """Entry point: resolve shared log path, append entry, echo to stdout.

    Returns:
        0 on success; 1 when the workspace is invalid.
    """
    args = _parse_args()
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    log_path = workspace / ".aib_memory" / _ACTIVE_LOG_FILENAME
    entry = _format_entry(args.message)

    # Append entry to the shared log; the file is created lazily on first write.
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(entry)

    # Reconfigure stdout to UTF-8 so non-ASCII messages echo cleanly on Windows
    # where the default console codec is cp1252 and would otherwise raise.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    # Print entry to stdout without an extra trailing newline (entry already ends in \n).
    print(entry, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
