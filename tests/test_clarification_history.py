"""Verify clarification-history lifecycle and durable archival in AIB tools.

Tests exercise real request creation, input reset, rotation, and closure, with
injected I/O failures to ensure recoverable history never permits premature close.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from common import read_input_header, slugify, write_input_header


TOOLS_DIR = Path(__file__).resolve().parents[1] / ".aib_brain" / "tools"
REQUEST_ID = "R-20260917-1000"
HISTORY_STEM = "clarification_questions"
HISTORY = (
    "**Q001**: Which output format?\n"
    "> **Why this matters:** Determines the export implementation.\n"
    "- [ ] Option A: CSV *(recommended)*\n"
    "- [ ] Option B: JSON\n"
    "- [ ] Other: ___\n"
    "Status: Unanswered\n\n"
    "### Q001 — Response 1\nOption B, with Unicode: София.\n\n"
    "**Q002**: Which filename is required for the export?\n"
    "> **Why this matters:** Determines the generated file name.\n"
    "- Answer: ___\nStatus: Unanswered\n\n"
    "### Q001 — Response 2\nSupersedes: Q001 — Response 1\n"
    "Option A; retain the Unicode text.\n"
).encode("utf-8")


def _load_tool(name: str) -> ModuleType:
    """Load a hyphenated AIB script without invoking its entry point."""
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS_DIR / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_tool(
    module: ModuleType, workspace: Path, monkeypatch: pytest.MonkeyPatch, *args: str
) -> int:
    """Invoke a tool's real CLI entry point and return its exit status."""
    with monkeypatch.context() as patch:
        patch.setattr(sys, "argv", [module.__file__, "--workspace", str(workspace), *args])
        try:
            module.main()
        except SystemExit as exc:
            return int(exc.code or 0)
    return 0


def _active_request(workspace: Path) -> Path:
    """Set the fixture's active request and return its destination folder."""
    header = read_input_header(workspace)
    header["state"].update(request_id=REQUEST_ID, title="History test", status="analysis_ready")
    input_path = workspace / ".aib_memory" / "input.md"
    input_path.write_text(write_input_header(input_path.read_text(), header), encoding="utf-8")
    folder = workspace / ".aib_memory" / "requests" / f"{REQUEST_ID}-history-test"
    folder.mkdir()
    return folder


def test_history_survives_creation_reset_and_closure(
    workspace_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pre-request multiround transcript survives input reset and archives once."""
    memory = workspace_dir / ".aib_memory"
    active = memory / f"{HISTORY_STEM}.md"
    active.write_bytes(HISTORY)
    input_path = memory / "input.md"
    with input_path.open("a", encoding="utf-8") as handle:
        handle.write("### Goal\nImplement the clarified export.\n")

    assert _run_tool(
        _load_tool("create-request.py"), workspace_dir, monkeypatch, "--title", "History lifecycle"
    ) == 0
    header = read_input_header(workspace_dir)
    request_id = header["state"]["request_id"]
    folder = memory / "requests" / f"{request_id}-{slugify(header['state']['title'])}"
    assert active.read_bytes() == HISTORY

    assert _run_tool(_load_tool("finalize-input.py"), workspace_dir, monkeypatch) == 0
    assert active.read_bytes() == HISTORY
    assert "Implement the clarified export" not in input_path.read_text()
    assert list(folder.glob("input-archive-*.md"))

    move = _load_tool("move-request-artifacts.py")
    assert _run_tool(move, workspace_dir, monkeypatch) == 0
    assert _run_tool(move, workspace_dir, monkeypatch) == 0
    assert _run_tool(_load_tool("close-request.py"), workspace_dir, monkeypatch) == 0
    assert (folder / f"{HISTORY_STEM}_{request_id}.md").read_bytes() == HISTORY
    assert active.read_bytes() == b""
    assert read_input_header(workspace_dir)["state"]["status"] == "idle"


@pytest.mark.parametrize("initial", [None, b""])
def test_missing_or_empty_history(
    workspace_dir: Path, monkeypatch: pytest.MonkeyPatch, initial: bytes | None
) -> None:
    """Closure tolerates requests without questions and leaves empty history files."""
    folder = _active_request(workspace_dir)
    active = workspace_dir / ".aib_memory" / f"{HISTORY_STEM}.md"
    if initial is not None:
        active.write_bytes(initial)
    assert _run_tool(_load_tool("close-request.py"), workspace_dir, monkeypatch) == 0
    assert active.read_bytes() == b""
    assert (folder / f"{HISTORY_STEM}_{REQUEST_ID}.md").read_bytes() == b""


@pytest.mark.parametrize("prior", [b"", b"older", b"older\n", b"older\r\n"])
def test_archive_appends_new_history_without_duplicate_successful_content(
    workspace_dir: Path, monkeypatch: pytest.MonkeyPatch, prior: bytes
) -> None:
    """Existing bytes and separators survive multiple batches and safety-net calls."""
    folder = _active_request(workspace_dir)
    active = workspace_dir / ".aib_memory" / f"{HISTORY_STEM}.md"
    archive = folder / f"{HISTORY_STEM}_{REQUEST_ID}.md"
    archive.write_bytes(prior)
    active.write_bytes(HISTORY)
    move = _load_tool("move-request-artifacts.py")
    assert _run_tool(move, workspace_dir, monkeypatch) == 0
    expected = prior + (b"\n" if prior and not prior.endswith(b"\n") else b"") + HISTORY
    assert archive.read_bytes() == expected
    active.write_bytes(b"### Q002 - Response 1\nexport.csv\n")
    expected += active.read_bytes()
    assert _run_tool(move, workspace_dir, monkeypatch) == 0
    assert _run_tool(_load_tool("close-request.py"), workspace_dir, monkeypatch) == 0
    assert archive.read_bytes() == expected
    assert active.read_bytes() == b""


@pytest.mark.parametrize("newer", [None, b"newer\n"])
def test_staged_recovery_preserves_order(
    workspace_dir: Path, monkeypatch: pytest.MonkeyPatch, newer: bytes | None
) -> None:
    """An interrupted rotation drains staging before newer active entries."""
    folder = _active_request(workspace_dir)
    memory = workspace_dir / ".aib_memory"
    staging = memory / f"{HISTORY_STEM}-staging-{REQUEST_ID}.md"
    active = memory / f"{HISTORY_STEM}.md"
    archive = folder / f"{HISTORY_STEM}_{REQUEST_ID}.md"
    archive.write_bytes(b"earlier\n")
    staging.write_bytes(HISTORY)
    if newer is not None:
        active.write_bytes(newer)
    assert _run_tool(_load_tool("close-request.py"), workspace_dir, monkeypatch) == 0
    assert archive.read_bytes() == b"earlier\n" + HISTORY + (newer or b"")
    assert active.read_bytes() == b""
    assert not staging.exists()


@pytest.mark.parametrize("bad_path", ["active", "staging", "archive"])
@pytest.mark.parametrize("kind", ["directory", "symlink"])
def test_invalid_history_path_blocks_close(
    workspace_dir: Path, monkeypatch: pytest.MonkeyPatch, bad_path: str, kind: str
) -> None:
    """Unexpected history path types preserve the request and ordinary artifacts."""
    folder = _active_request(workspace_dir)
    memory = workspace_dir / ".aib_memory"
    active = memory / f"{HISTORY_STEM}.md"
    paths = {
        "active": active,
        "staging": memory / f"{HISTORY_STEM}-staging-{REQUEST_ID}.md",
        "archive": folder / f"{HISTORY_STEM}_{REQUEST_ID}.md",
    }
    if bad_path != "active":
        active.write_bytes(HISTORY)
    target = memory / "preserved.md"
    target.write_bytes(HISTORY)
    if kind == "directory":
        paths[bad_path].mkdir()
    else:
        try:
            paths[bad_path].symlink_to(target)
        except (OSError, NotImplementedError):
            pytest.skip("Symlink creation not permitted on this platform")
    plan = memory / f"plan-{REQUEST_ID}.md"
    plan.write_bytes(b"plan")
    assert _run_tool(_load_tool("close-request.py"), workspace_dir, monkeypatch) == 2
    assert read_input_header(workspace_dir)["state"]["status"] == "analysis_ready"
    assert plan.read_bytes() == b"plan"
    assert target.read_bytes() == HISTORY
    if bad_path != "active":
        assert active.read_bytes() == HISTORY


@pytest.mark.parametrize("stream", ["log", HISTORY_STEM])
@pytest.mark.parametrize("failure", ["rename", "recreate", "append", "read", "fsync", "cleanup"])
@pytest.mark.parametrize("entrypoint", ["move", "close"])
def test_io_failures_block_close_and_preserve_recovery(
    workspace_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture,
    stream: str, failure: str, entrypoint: str,
) -> None:
    """Rotation, append, sync, and cleanup errors retain recoverable bytes and state."""
    folder = _active_request(workspace_dir)
    memory = workspace_dir / ".aib_memory"
    active = memory / f"{stream}.md"
    staging = memory / f"{stream}-staging-{REQUEST_ID}.md"
    archive = folder / f"{stream}_{REQUEST_ID}.md"
    active.write_bytes(HISTORY)
    plan = memory / f"plan-{REQUEST_ID}.md"
    plan.write_bytes(b"plan")
    move = _load_tool("move-request-artifacts.py")
    tool = move if entrypoint == "move" else _load_tool("close-request.py")
    if entrypoint == "close":
        monkeypatch.setattr(tool, "_load_move_module", lambda: move)

    with monkeypatch.context() as patch:
        _inject_failure(patch, move, active, staging, archive, failure)
        assert _run_tool(tool, workspace_dir, monkeypatch) == 2
    diagnostic = "log-archive" if stream == "log" else "clarification-history-archive"
    assert diagnostic in capsys.readouterr().err
    assert read_input_header(workspace_dir)["state"]["request_id"] == REQUEST_ID
    assert plan.read_bytes() == b"plan"
    assert any(path.exists() and path.read_bytes() == HISTORY for path in (active, staging))

    # Retrying after the fault is fixed may replay an ambiguously committed snapshot.
    assert _run_tool(tool, workspace_dir, monkeypatch) == 0
    assert HISTORY in archive.read_bytes()
    recovered = archive.read_bytes()
    assert active.read_bytes() == b""
    assert not staging.exists()
    if entrypoint == "move":
        assert _run_tool(tool, workspace_dir, monkeypatch) == 0
        assert archive.read_bytes() == recovered
    else:
        assert read_input_header(workspace_dir)["state"]["status"] == "idle"


def _inject_failure(
    patch: pytest.MonkeyPatch, move: ModuleType, active: Path, staging: Path,
    archive: Path, failure: str,
) -> None:
    """Inject a path-scoped I/O failure without affecting the other audit stream."""
    if failure == "fsync":
        original_append = move._append_snapshot

        def append_with_sync_failure(source: Path, destination: Path) -> None:
            """Fail fsync only while the selected stream is being appended."""
            if source != staging:
                return original_append(source, destination)
            with pytest.MonkeyPatch.context() as sync_patch:
                def fail_sync(descriptor: int) -> None:
                    """Simulate an archive durability failure."""
                    raise OSError("injected fsync failure")
                sync_patch.setattr(move.os, "fsync", fail_sync)
                original_append(source, destination)

        patch.setattr(move, "_append_snapshot", append_with_sync_failure)
        return

    owner, method, target = {
        "rename": (move.os, "replace", active),
        "recreate": (Path, "touch", active),
        "append": (Path, "open", archive),
        "read": (Path, "open", staging),
        "cleanup": (Path, "unlink", staging),
    }[failure]
    original = getattr(owner, method)

    def fail_for_path(path: Path, *args: object, **kwargs: object) -> object:
        """Fail the selected filesystem operation and delegate unrelated paths."""
        if Path(path) == target:
            raise OSError(f"injected {failure} failure")
        return original(path, *args, **kwargs)

    patch.setattr(owner, method, fail_for_path)
