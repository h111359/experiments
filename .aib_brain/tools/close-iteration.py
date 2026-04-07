#!/usr/bin/env python3
"""Close active or selected iteration for a request."""

from __future__ import annotations

from pathlib import Path

from common import (
    ACTIVE,
    COMPLETED,
    ValidationError,
    ensure_workspace,
    format_markdown_table,
    now_iso,
    parse_args,
    parse_markdown_table,
    read_text,
    resolve_active_request_or_explicit,
    write_text,
)


def main() -> None:
    args = parse_args("Close iteration")
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)
        req_row = resolve_active_request_or_explicit(workspace, args.request_id)

        folder_rel = req_row[2]
        iterations_path = workspace / folder_rel / "iterations.md"
        if not iterations_path.exists():
            raise ValidationError(f"Missing iterations.md in {folder_rel}")

        header, rows = parse_markdown_table(read_text(iterations_path))
        col = {name: idx for idx, name in enumerate(header)}

        target_id = (args.iteration_id or "").strip()
        now = now_iso()

        if target_id:
            matching = [r for r in rows if r[col["iteration_id"]] == target_id]
            if not matching:
                raise ValidationError(f"Iteration not found: {target_id}")
            target_rows = matching
        else:
            target_rows = [r for r in rows if r[col["state"]] == ACTIVE]
            if not target_rows:
                raise ValidationError("No active iteration found; provide --iteration-id")

        for r in target_rows:
            r[col["state"]] = COMPLETED
            r[col["closed_at"]] = now

        content = "# Iterations\n\n" + format_markdown_table(header, rows)
        write_text(iterations_path, content)

        print(f"Closed iteration(s): {', '.join(r[col['iteration_id']] for r in target_rows)}")

    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
