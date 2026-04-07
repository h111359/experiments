#!/usr/bin/env python3
"""Create and register next active iteration for a request."""

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
    args = parse_args("Create a new iteration")
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)
        req_row = resolve_active_request_or_explicit(workspace, args.request_id)

        folder_rel = req_row[2]
        request_folder = workspace / folder_rel
        iterations_path = request_folder / "iterations.md"
        if not iterations_path.exists():
            raise ValidationError(f"Missing iterations.md: {folder_rel}")

        header, rows = parse_markdown_table(read_text(iterations_path))
        col = {name: idx for idx, name in enumerate(header)}
        for required in ["iteration_id", "state", "created_at", "closed_at", "summary"]:
            if required not in col:
                raise ValidationError(f"iterations.md missing column: {required}")

        # Enforce single active iteration.
        active = [r for r in rows if r[col["state"]] == ACTIVE]
        if len(active) > 1:
            raise ValidationError("Multiple active iterations detected")

        if rows:
            max_id = max(int(r[col["iteration_id"]]) for r in rows)
        else:
            max_id = 0

        new_id = f"{max_id + 1:02d}"
        now = now_iso()

        for r in rows:
            if r[col["state"]] == ACTIVE:
                r[col["state"]] = COMPLETED
                r[col["closed_at"]] = now

        rows.append([new_id, ACTIVE, now, "", args.summary or "Follow-up iteration"])
        rows = sorted(rows, key=lambda r: int(r[col["iteration_id"]]))

        content = "# Iterations\n\n" + format_markdown_table(header, rows)
        write_text(iterations_path, content)

        print(f"Created iteration {new_id} for request folder: {folder_rel}")

    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
