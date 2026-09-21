"""Regression coverage for Unicode output in AIB analysis preflight tools.

Part of the AIB test suite; exercise real CLI processes and their output bytes.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from common import configure_utf8_output, parse_input_header
from conftest import INPUT_MD_IDLE, TOOLS_DIR
from test_verify_context import VALID_CONTEXT

TITLES = ("POS to NSR", "POS→NSR", "Продажби 日本語", "Sales 🚀 café")
ENCODINGS = ("cp1252", "utf-8", None)
REQUEST_ID = "R-20260917-1000"


def _seed_input(workspace: Path, title: str) -> bytes:
    """Write an active Unicode request in workspace and return its original bytes."""
    content = INPUT_MD_IDLE.replace("request_id: ~", f"request_id: {REQUEST_ID}")
    content = content.replace("title: ~", f"title: {title}")
    content = content.replace("status: idle", "status: analysis_ready")
    content += "Preserve this request body: → 日本語.\n"
    input_path = workspace / ".aib_memory" / "input.md"
    input_path.write_text(content, encoding="utf-8", newline="\n")
    return input_path.read_bytes()


def _environment(encoding: str | None) -> dict[str, str]:
    """Return a child environment with controlled output encoding and no bytecode."""
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    # Disable Python UTF-8 mode so Windows can also exercise its locale default.
    environment["PYTHONUTF8"] = "0"
    environment.pop("PYTHONIOENCODING", None)
    if encoding is not None:
        environment["PYTHONIOENCODING"] = encoding
    return environment


def _command(workspace: Path, script: str, *arguments: str) -> list[str]:
    """Return the prompt's normal Python CLI command targeting a test workspace."""
    return [sys.executable, "-B", str(TOOLS_DIR / script), "--workspace", str(workspace), *arguments]


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("encoding", ENCODINGS)
@pytest.mark.parametrize("output_mode", ("pipe", "redirect", "text"))
def test_header_read_preserves_unicode(
    workspace_dir: Path, title: str, encoding: str | None, output_mode: str,
) -> None:
    """Read headers in each environment/output mode without altering request bytes."""
    original = _seed_input(workspace_dir, title)
    command = _command(workspace_dir, "input-header.py", "--operation", "read")
    environment = _environment(encoding)
    if output_mode == "redirect":
        output_path = workspace_dir / "header-output.txt"
        with output_path.open("wb") as output_file:
            result = subprocess.run(command, env=environment, stdout=output_file, stderr=subprocess.PIPE)
        output = output_path.read_bytes().decode("utf-8")
    elif output_mode == "text":
        result = subprocess.run(command, env=environment, capture_output=True, encoding="utf-8")
        output = result.stdout
    else:
        result = subprocess.run(command, env=environment, capture_output=True)
        output = result.stdout.decode("utf-8")
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    assert output.splitlines() == [
        f"request_id={REQUEST_ID}", f"title={title}", "state=analysis_ready",
        "minimum_questions=5", "input_verification_enabled=true",
        "input_verification_result=null", "context_verification_enabled=true",
        "context_verification_result=null",
    ]
    assert (workspace_dir / ".aib_memory" / "input.md").read_bytes() == original


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("encoding", ENCODINGS)
def test_analyze_preflight_proceeds_with_unicode(
    workspace_dir: Path, title: str, encoding: str | None,
) -> None:
    """Run S01 header reads and enabled verifiers, preserving title/body through S01.2."""
    original = _seed_input(workspace_dir, title)
    (workspace_dir / ".aib_memory" / "context.md").write_text(VALID_CONTEXT, encoding="utf-8")
    environment = _environment(encoding)
    for script, arguments in (
        ("input-header.py", ("--operation", "read")),
        ("verify-input.py", ()),
        ("verify-context.py", ()),
        ("input-header.py", ("--operation", "read")),
    ):
        result = subprocess.run(
            _command(workspace_dir, script, *arguments), env=environment,
            capture_output=True, encoding="utf-8",
        )
        assert result.returncode == 0, (script, result.stdout, result.stderr)
        assert not result.stderr
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines())
    assert fields["request_id"] == REQUEST_ID
    assert fields["title"] == title
    assert fields["state"] == "analysis_ready"
    assert fields["input_verification_result"] == "valid"
    assert fields["context_verification_result"] == "valid"
    updated = (workspace_dir / ".aib_memory" / "input.md").read_text(encoding="utf-8")
    assert updated.split("## Input", 1)[1] == original.decode("utf-8").split("## Input", 1)[1]


@pytest.mark.parametrize("encoding", ENCODINGS)
@pytest.mark.parametrize("invalid_input", (None, "## Input\n", "---\nstate:\n", "---\nrequest_id: old\n---\n"))
def test_header_errors_still_fail(
    workspace_dir: Path, encoding: str | None, invalid_input: str | None,
) -> None:
    """Missing or malformed input must still fail without modifying existing data."""
    input_path = workspace_dir / ".aib_memory" / "input.md"
    if invalid_input is None:
        input_path.unlink()
    else:
        input_path.write_text(invalid_input, encoding="utf-8", newline="\n")
    result = subprocess.run(
        _command(workspace_dir, "input-header.py", "--operation", "read"),
        env=_environment(encoding), capture_output=True, encoding="utf-8",
    )
    assert result.returncode == 1
    assert result.stderr
    assert "UnicodeEncodeError" not in result.stderr
    assert not result.stdout
    if invalid_input is None:
        assert not input_path.exists()
    else:
        assert input_path.read_text(encoding="utf-8") == invalid_input


@pytest.mark.parametrize("encoding", ENCODINGS)
def test_unicode_validation_errors_remain_readable(workspace_dir: Path, encoding: str | None) -> None:
    """Invalid state containing Unicode reports validation failure, not encoding failure."""
    _seed_input(workspace_dir, "POS→NSR")
    input_path = workspace_dir / ".aib_memory" / "input.md"
    content = input_path.read_text(encoding="utf-8").replace("status: analysis_ready", "status: 無効")
    input_path.write_text(content, encoding="utf-8")
    result = subprocess.run(
        _command(workspace_dir, "verify-input.py"), env=_environment(encoding),
        capture_output=True, encoding="utf-8",
    )
    assert result.returncode == 1
    assert "[FAIL] check_state_value_valid" in result.stdout
    assert "無効" in result.stdout
    assert not result.stderr
    header = parse_input_header(input_path.read_text(encoding="utf-8"))
    assert header["state"]["title"] == "POS→NSR"
    assert header["state"]["input_verification_result"] == "invalid"


@pytest.mark.parametrize("encoding", ENCODINGS)
def test_unicode_stderr_preserves_workspace_path(tmp_path: Path, encoding: str | None) -> None:
    """A nonexistent Unicode workspace still returns the original readable CLI error."""
    missing_workspace = tmp_path / "不存在→🚀"
    result = subprocess.run(
        _command(missing_workspace, "input-header.py", "--operation", "read"),
        env=_environment(encoding), capture_output=True, encoding="utf-8",
    )
    assert result.returncode == 1
    assert not result.stdout
    assert result.stderr.strip() == f"ERROR: Workspace does not exist: {missing_workspace}"


@pytest.mark.parametrize("text_only", (False, True))
def test_output_configuration_supports_embedded_streams(
    monkeypatch: pytest.MonkeyPatch, text_only: bool,
) -> None:
    """Both CP1252 byte streams and StringIO retain Unicode without replacing streams."""
    buffers = [io.BytesIO(), io.BytesIO()]
    streams = [io.StringIO() if text_only else io.TextIOWrapper(buffer, encoding="cp1252") for buffer in buffers]
    with monkeypatch.context() as patched:
        patched.setattr(sys, "stdout", streams[0])
        patched.setattr(sys, "stderr", streams[1])
        original_stdin = sys.stdin
        configure_utf8_output()
        assert sys.stdin is original_stdin
        assert sys.stdout is streams[0]
        assert sys.stderr is streams[1]
        for stream in streams:
            stream.write("POS→NSR 日本語 🚀")
            stream.flush()
    for stream, buffer in zip(streams, buffers):
        output = stream.getvalue() if text_only else buffer.getvalue().decode("utf-8")
        assert output == "POS→NSR 日本語 🚀"
        stream.close()
