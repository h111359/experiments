#!/usr/bin/env python3
"""Create and register a new active request with default iteration 01."""

from __future__ import annotations

import re

from pathlib import Path

from common import (
    ACTIVE,
    CLOSED,
    ValidationError,
    ensure_workspace,
    format_markdown_table,
    load_template,
    now_compact_request_id,
    now_iso,
    parse_args,
    parse_markdown_table,
    read_text,
    requests_register_path,
    slugify,
    update_requests_register,
    validate_request_md,
    write_text,
)


def main() -> None:
    args = parse_args("Create a new AIB request")
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)

        register_path = requests_register_path(workspace)
        if not register_path.exists():
            raise ValidationError("Missing requests_register.md; run initialize first")

        title = (args.title or "").strip()
        if not title:
            raise ValidationError("--title is required")
        if not re.search(r"[a-zA-Z]", title):
            raise ValidationError("Title must contain at least one letter to generate a meaningful slug.")

        header, rows = parse_markdown_table(read_text(register_path))
        if not header:
            header = ["request_id", "title", "folder", "state", "created_at", "closed_at"]

        col = {name: idx for idx, name in enumerate(header)}
        active_rows = [r for r in rows if r[col["state"]] == ACTIVE]
        if active_rows:
            raise ValidationError("Cannot create request while another request is Active")

        req_id = args.request_id.strip() if args.request_id else now_compact_request_id()
        folder_name = f"{req_id}-{slugify(title)}"
        folder_rel = f".aib_memory/requests/{folder_name}"
        request_folder = workspace / folder_rel

        if any(r[col["request_id"]] == req_id for r in rows):
            raise ValidationError(f"Request ID already exists: {req_id}")
        if any(r[col["folder"]] == folder_rel for r in rows):
            raise ValidationError(f"Request folder already registered: {folder_rel}")

        created = now_iso()

        rows.append([req_id, title, folder_rel, ACTIVE, created, ""])
        rows = sorted(rows, key=lambda r: r[col["request_id"]])
        update_requests_register(workspace, rows)

        request_folder.mkdir(parents=True, exist_ok=False)

        request_content = load_template(workspace / ".aib_brain", "request-template.md")
        write_text(request_folder / "request.md", request_content)
        validate_request_md(request_folder / "request.md")

        iterations_intro = "# Iterations\n\n"
        iterations_table = format_markdown_table(
            ["iteration_id", "state", "created_at", "closed_at", "summary"],
            [["01", ACTIVE, created, "", args.summary or "Initial iteration"]],
        )
        write_text(request_folder / "iterations.md", iterations_intro + iterations_table)

        implementation_content = "# Implementation Log\n\nAppend-only entries. Add a new section for every execution update.\n"
        write_text(request_folder / "implementation.md", implementation_content)

        print(f"Created request: {req_id}")
        print(f"Folder: {folder_rel}")

    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
