#!/usr/bin/env python3
"""
close-request.py: Close an active request and reset input.md to the seed template.
Part of the AIB tool scripts.
Responsibilities: mark the active request as Closed in requests_register.md,
auto-close any open iterations, and reset input.md to 'No active request'.
"""

from __future__ import annotations

from pathlib import Path

from common import (
    ACTIVE,
    CLOSED,
    COMPLETED,
    ValidationError,
    ensure_workspace,
    format_markdown_table,
    now_iso,
    parse_args,
    parse_markdown_table,
    read_text,
    requests_register_path,
    update_requests_register,
    write_text,
)


def main() -> None:
    args = parse_args("Close request")
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)

        register = requests_register_path(workspace)
        if not register.exists():
            raise ValidationError("Missing requests_register.md; run initialize first")

        header, rows = parse_markdown_table(read_text(register))
        col = {name: idx for idx, name in enumerate(header)}

        req_id = (args.request_id or "").strip()
        if req_id:
            matches = [r for r in rows if r[col["request_id"]] == req_id]
            if not matches:
                raise ValidationError(f"Request not found: {req_id}")
            target = matches[0]
        else:
            active = [r for r in rows if r[col["state"]] == ACTIVE]
            if len(active) == 0:
                raise ValidationError("No active request found; provide --request-id")
            if len(active) > 1:
                raise ValidationError("Multiple active requests found")
            target = active[0]

        if target[col["state"]] == CLOSED:
            raise ValidationError("Request already closed")

        folder_rel = target[col["folder"]]
        iterations_path = workspace / folder_rel / "iterations.md"
        if iterations_path.exists():
            it_header, it_rows = parse_markdown_table(read_text(iterations_path))
            it_col = {name: idx for idx, name in enumerate(it_header)}
            active_iterations = [r for r in it_rows if r[it_col["state"]] == ACTIVE]
            if active_iterations:
                now = now_iso()
                for r in active_iterations:
                    r[it_col["state"]] = COMPLETED
                    r[it_col["closed_at"]] = now
                content = "# Iterations\n\n" + format_markdown_table(it_header, it_rows)
                write_text(iterations_path, content)
                for r in active_iterations:
                    print(f"Auto-closed iteration {r[it_col['iteration_id']]} before closing request.")

        target[col["state"]] = CLOSED
        target[col["closed_at"]] = now_iso()

        update_requests_register(workspace, rows)

        # Reset input.md to the seed template so the Active request line reads
        # "No active request" after the request is closed. Skip silently if the
        # file does not exist (e.g. workspace not yet initialized).
        input_file = workspace / ".aib_memory" / "input.md"
        if input_file.exists():
            input_seed = (
                "## Active request\n"
                "No active request\n\n"
                "## Options\n"
                "- [ ] No changes — provide answer only\n"
                "- [ ] Skip analysis document generation\n"
                "- Question threshold: [ ] 1 (all)  [ ] 2  [x] 3  [ ] 4  [ ] 5 (mandatory only)\n\n"
                "## Input\n\n"
            )
            write_text(input_file, input_seed)

        print(f"Closed request: {target[col['request_id']]}")

    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
