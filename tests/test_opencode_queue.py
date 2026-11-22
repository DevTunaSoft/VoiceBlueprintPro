"""Pure-contract and fake-agent tests for the OpenCode queue (never launch AI)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / "tools/opencode_queue.py"
spec = importlib.util.spec_from_file_location("vbp_queue", MODULE)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "ROOT", tmp_path)
    monkeypatch.setattr(q, "STATE_DIR", tmp_path / ".opencode-queue")
    monkeypatch.setattr(q, "STATE_FILE", tmp_path / ".opencode-queue/queue.json")
    monkeypatch.setattr(q, "RECEIPTS", tmp_path / ".opencode-queue/receipts")
    monkeypatch.setattr(q, "LOCK_FILE", tmp_path / ".opencode-queue/supervisor.lock")
    q.initialize()
    return tmp_path


def test_200_unique_tasks_dependency_graph_and_serial_head(isolated):
    state = q.read_state()
    tasks = state["tasks"]
    assert len(tasks) == 200
    assert len({t["id"] for t in tasks}) == 200
    assert len({t["track"] for t in tasks}) == 20
    assert all(t["attempts"] == 0 for t in tasks)
    assert q.ready_task(tasks)["id"] == "VBP-01-01"
    assert tasks[1]["depends_on"] == ["VBP-01-01"]
    q.validate(tasks)


def test_init_is_idempotent_and_preserves_progress(isolated):
    state = q.read_state()
    state["tasks"][0]["status"] = "done"
    q.atomic_write(q.STATE_FILE, state)
    q.initialize()
    assert q.read_state()["tasks"][0]["status"] == "done"


def test_circular_dependency_rejected(isolated):
    tasks = q.read_state()["tasks"]
    tasks[0]["depends_on"] = ["VBP-01-10"]
    with pytest.raises(ValueError, match="dependency cycle"):
        q.validate(tasks)


def test_two_instances_cannot_hold_lock(isolated):
    with q.ExclusiveLock():
        with pytest.raises(RuntimeError, match="already owns"):
            with q.ExclusiveLock():
                pass
    assert not q.LOCK_FILE.exists()


def test_atomic_write_retains_valid_state(isolated):
    state = q.read_state()
    q.atomic_write(q.STATE_FILE, state)
    assert len(q.read_state()["tasks"]) == 200
    assert not q.STATE_FILE.with_name("queue.json.tmp").exists()


def test_receipts_fail_closed_and_validate_identity(isolated):
    path = q.RECEIPTS / "VBP-01-01.json"
    assert not q.check_receipt(path, "VBP-01-01")[0]
    path.write_text(json.dumps({"task_id": "other", "status": "PASS",
                                "evidence": ["test passed"]}), encoding="utf8")
    assert not q.check_receipt(path, "VBP-01-01")[0]
    path.write_text(json.dumps({"task_id": "VBP-01-01", "status": "PASS",
                                "evidence": []}), encoding="utf8")
    assert not q.check_receipt(path, "VBP-01-01")[0]
    path.write_text(json.dumps({"task_id": "VBP-01-01", "status": "PASS",
                                "evidence": ["test passed"]}), encoding="utf8")
    assert q.check_receipt(path, "VBP-01-01")[0]


def test_worker_retries_twice_then_advances_independent_track(isolated, monkeypatch):
    monkeypatch.setattr(q.shutil, "which", lambda command: "/fake/opencode")
    seen = []

    def fake_execute(task, _model, _timeout):
        seen.append((task["id"], task["attempts"]))
        return False, [], "synthetic failure"

    monkeypatch.setattr(q, "execute", fake_execute)
    q.work(None, 60, once=True)
    q.work(None, 60, once=True)
    state = q.read_state()
    assert seen == [("VBP-01-01", 1), ("VBP-01-01", 2)]
    assert state["tasks"][0]["status"] == "blocked"
    assert q.ready_task(state["tasks"])["id"] == "VBP-02-01"


def test_worker_recovers_interrupted_task_with_one_remaining_attempt(isolated, monkeypatch):
    state = q.read_state()
    state["tasks"][0].update(status="running", attempts=1)
    q.atomic_write(q.STATE_FILE, state)
    monkeypatch.setattr(q.shutil, "which", lambda command: "/fake/opencode")
    monkeypatch.setattr(q, "execute", lambda task, model, timeout: (True, ["focused test pass"], ""))
    q.work(None, 60, once=True)
    assert q.read_state()["tasks"][0]["status"] == "done"
    assert q.read_state()["tasks"][0]["attempts"] == 2


def test_worker_never_executes_two_tasks_in_once_mode(isolated, monkeypatch):
    monkeypatch.setattr(q.shutil, "which", lambda command: "/fake/opencode")
    executed = []

    def fake_execute(task, model, timeout):
        executed.append(task["id"])
        return True, ["verified no-op"], ""

    monkeypatch.setattr(q, "execute", fake_execute)
    q.work(None, 60, once=True)
    assert executed == ["VBP-01-01"]
    assert q.queue_status(q.read_state())["counts"]["done"] == 1


def test_cross_workstream_dependencies_prevent_premature_phase(isolated):
    by_id = {task["id"]: task for task in q.read_state()["tasks"]}
    assert by_id["VBP-05-01"]["depends_on"] == ["VBP-04-01"]
    assert by_id["VBP-17-01"]["depends_on"] == ["VBP-04-01", "VBP-10-01"]
    assert by_id["VBP-19-01"]["depends_on"] == ["VBP-15-01", "VBP-16-01"]
    assert by_id["VBP-20-01"]["depends_on"] == ["VBP-06-01", "VBP-10-01"]
    assert all(q.ready_task(q.read_state()["tasks"])["id"] == "VBP-01-01" for _ in range(2))
