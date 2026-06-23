"""Tests for run_per_skill_experiment.py timeout handling.

Reproduces the iter-3.1 bug where timeouts left empty eval dirs
with no run.jsonl marker, making post-hoc analysis ambiguous
between "ran to completion but produced nothing" and "timed out".
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parent
    / "run_per_skill_experiment.py"
)


def _load_module(monkeypatch, claude_shim: Path):
    """Import the script module with CLAUDE monkeypatched to a test shim."""
    spec = importlib.util.spec_from_file_location(
        "run_per_skill_experiment", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_per_skill_experiment"] = module
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "CLAUDE", str(claude_shim))
    return module


@pytest.fixture
def sleep_forever_shim(tmp_path: Path) -> Path:
    """A fake 'claude' CLI that sleeps 60s then exits 0.

    Tests will use a short timeout to force TimeoutExpired.
    """
    shim = tmp_path / "claude"
    shim.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, time\n"
        "time.sleep(60)\n"
        "sys.exit(0)\n"
    )
    shim.chmod(0o755)
    return shim


@pytest.fixture
def fast_ok_shim(tmp_path: Path) -> Path:
    """A fake 'claude' CLI that emits two stream-json lines and exits 0."""
    shim = tmp_path / "claude"
    shim.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, json\n"
        "for line in [json.dumps({'type': 'event', 'msg': 'one'}),\n"
        "             json.dumps({'type': 'event', 'msg': 'two'})]:\n"
        "    print(line)\n"
        "sys.exit(0)\n"
    )
    shim.chmod(0o755)
    return shim


def test_timeout_writes_marker_json(
    monkeypatch, tmp_path, sleep_forever_shim
):
    """On subprocess.TimeoutExpired, run_one must write eval_dir/timeout.json.

    Regression: iter-3.1 left 6/15 runs as empty eval_dir/config/ dirs
    with no marker file, indistinguishable from "ran but produced nothing".
    """
    module = _load_module(monkeypatch, sleep_forever_shim)
    monkeypatch.setattr(module, "TIMEOUT_S", 2)

    eval_dir = tmp_path / "eval"
    result = module.run_one(
        utterance="hello",
        with_skill=False,
        eval_dir=eval_dir,
    )

    marker = eval_dir / "timeout.json"
    assert marker.exists(), f"expected {marker} to exist after timeout"
    payload = json.loads(marker.read_text())
    assert payload["status"] == "timeout"
    assert payload["timeout_s"] == 2
    assert result["status"] == "timeout"


def test_completed_writes_run_jsonl(
    monkeypatch, tmp_path, fast_ok_shim
):
    """On normal completion, run_one writes eval_dir/run.jsonl.

    Companion to the timeout test; ensures the fix doesn't regress the
    happy path.
    """
    module = _load_module(monkeypatch, fast_ok_shim)
    monkeypatch.setattr(module, "TIMEOUT_S", 30)

    eval_dir = tmp_path / "eval"
    result = module.run_one(
        utterance="hello",
        with_skill=False,
        eval_dir=eval_dir,
    )

    run = eval_dir / "run.jsonl"
    assert run.exists(), f"expected {run} to exist on success"
    contents = run.read_text().strip().splitlines()
    assert len(contents) == 2
    assert result["status"] == "completed"
    assert result["total_events"] == 2