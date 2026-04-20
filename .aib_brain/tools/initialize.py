#!/usr/bin/env python3
"""Initialize AIB memory structures and default artifacts."""

from __future__ import annotations

from pathlib import Path

from common import (
    ValidationError,
    ensure_workspace,
    load_template,
    print_error_and_exit,
    seed_references_from_product_doc,
    parse_args,
    write_text,
)


def main() -> None:
    args = parse_args("Initialize AIB memory structure")
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)

        memory_root = workspace / ".aib_memory"
        (memory_root / "requests").mkdir(parents=True, exist_ok=True)
        (memory_root / "logs").mkdir(parents=True, exist_ok=True)

        brain_dir = workspace / ".aib_brain"

        register_file = workspace / ".aib_memory" / "requests_register.md"
        if register_file.exists():
            print("requests_register.md already exists — skipping overwrite.")
        else:
            requests_register = load_template(brain_dir, "requests_register-template.md")
            write_text(register_file, requests_register)

        references_file = workspace / ".aib_memory" / "references.md"
        if references_file.exists() and not args.force:
            print("references.md already exists — skipping overwrite.")
        else:
            references_md, _ = seed_references_from_product_doc(workspace)
            write_text(references_file, references_md)

        context_file = workspace / ".aib_memory" / "context.md"
        if context_file.exists():
            print("context.md already exists — skipping overwrite.")
        else:
            write_text(context_file, "# Context\n\nThis file is managed by the `aib-context.md` prompt. Run it to populate workspace context.\n")

        # Seed input.md as the primary ephemeral user-agent communication channel.
        input_file = workspace / ".aib_memory" / "input.md"
        if input_file.exists():
            print("input.md already exists — skipping overwrite.")
        else:
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

        print("Initialized .aib_memory structure successfully.")

    except ValidationError as exc:
        print_error_and_exit(str(exc))


if __name__ == "__main__":
    main()
