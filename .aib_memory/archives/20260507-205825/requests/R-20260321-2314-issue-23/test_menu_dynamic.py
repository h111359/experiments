import sys
import tempfile
import unittest
from pathlib import Path


def _find_workspace_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(10):
        if (current / ".aib_brain" / "tools").exists():
            return current
        current = current.parent
    raise RuntimeError("Workspace root not found (expected .aib_brain/tools)")


WORKSPACE_ROOT = _find_workspace_root(Path(__file__).parent)
MENU_TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"

sys.path.insert(0, str(MENU_TOOLS_DIR))

import menu  # noqa: E402


class TestMenuDynamicVisibility(unittest.TestCase):
    def test_filter_visible_actions_no_request(self) -> None:
        actions = [
            {"script": menu.SCRIPT_CREATE_REQUEST, "title": "Create request"},
            {"script": menu.SCRIPT_CLOSE_REQUEST, "title": "Close request"},
            {"script": menu.SCRIPT_CREATE_ITERATION, "title": "Create iteration"},
            {"script": menu.SCRIPT_CLOSE_ITERATION, "title": "Close iteration"},
            {"script": "other.py", "title": "Other"},
        ]
        state = menu.MenuState(None, None, None)
        visible = menu.filter_visible_actions(actions, state)
        scripts = [a["script"] for a in visible]
        self.assertEqual(scripts, [menu.SCRIPT_CREATE_REQUEST, "other.py"])

    def test_filter_visible_actions_active_request_no_iteration(self) -> None:
        actions = [
            {"script": menu.SCRIPT_CREATE_REQUEST, "title": "Create request"},
            {"script": menu.SCRIPT_CLOSE_REQUEST, "title": "Close request"},
            {"script": menu.SCRIPT_CREATE_ITERATION, "title": "Create iteration"},
            {"script": menu.SCRIPT_CLOSE_ITERATION, "title": "Close iteration"},
        ]
        state = menu.MenuState("R-20260321-2314", ".aib_memory/requests/R-20260321-2314-x", None)
        visible = menu.filter_visible_actions(actions, state)
        scripts = [a["script"] for a in visible]
        self.assertEqual(scripts, [menu.SCRIPT_CLOSE_REQUEST, menu.SCRIPT_CREATE_ITERATION])

    def test_filter_visible_actions_active_request_active_iteration(self) -> None:
        actions = [
            {"script": menu.SCRIPT_CREATE_REQUEST, "title": "Create request"},
            {"script": menu.SCRIPT_CLOSE_REQUEST, "title": "Close request"},
            {"script": menu.SCRIPT_CREATE_ITERATION, "title": "Create iteration"},
            {"script": menu.SCRIPT_CLOSE_ITERATION, "title": "Close iteration"},
        ]
        state = menu.MenuState("R-20260321-2314", ".aib_memory/requests/R-20260321-2314-x", "02")
        visible = menu.filter_visible_actions(actions, state)
        scripts = [a["script"] for a in visible]
        self.assertEqual(scripts, [menu.SCRIPT_CLOSE_REQUEST, menu.SCRIPT_CLOSE_ITERATION])


class TestMenuStateResolution(unittest.TestCase):
    def test_resolve_menu_state_from_tables(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td)

            # requests_register.md with one active request
            memory = workspace / ".aib_memory"
            requests_dir = memory / "requests"
            request_folder_rel = ".aib_memory/requests/R-20260321-2314-example"
            request_folder = workspace / request_folder_rel
            request_folder.mkdir(parents=True, exist_ok=True)

            (memory / "requests_register.md").write_text(
                "# Requests Register\n\n"
                "| request_id | title | folder | state | created_at | closed_at |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                f"| R-20260321-2314 | Issue 23 | {request_folder_rel} | Active | 2026-03-21 23:14:52 +0200 |  |\n",
                encoding="utf-8",
                newline="\n",
            )

            # iterations.md with one active iteration
            (request_folder / "iterations.md").write_text(
                "# Iterations\n\n"
                "| iteration_id | state | created_at | closed_at | summary |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| 01 | Completed | 2026-03-21 23:14:52 +0200 | 2026-03-21 23:44:12 +0200 | Initial |\n"
                "| 02 | Active | 2026-03-21 23:44:22 +0200 |  | Follow-up |\n",
                encoding="utf-8",
                newline="\n",
            )

            state = menu.resolve_menu_state(workspace)
            self.assertEqual(state.active_request_id, "R-20260321-2314")
            self.assertEqual(state.active_iteration_id, "02")


if __name__ == "__main__":
    unittest.main()
