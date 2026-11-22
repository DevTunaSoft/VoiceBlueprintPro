"""Persistent, single-worker OpenCode queue for VoiceBlueprintPro (stdlib only).

Usage: py -3 tools/opencode_queue.py init|status|run [--model PROVIDER/MODEL]
Run from the repository root; the supervisor must remain running to advance work.
The 200-item plan is a conditional engineering checklist, not 200 proven defects.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".opencode-queue"
STATE_FILE = STATE_DIR / "queue.json"
RECEIPTS = STATE_DIR / "receipts"
LOCK_FILE = STATE_DIR / "supervisor.lock"
MAX_ATTEMPTS = 2
STEPS = (
    "audit", "reproduce", "requirements", "implement", "unit-tests",
    "negative-tests", "recovery-tests", "integration", "documentation", "acceptance",
)
# Unique workstream scopes. Tasks within a track form a dependency chain.
# Linked PRs must be checked before work; no replacement implementation is authorized.
TRACKS = (
    ("ci", "CI workflow and required checks", ".github/workflows/ci.yml", ""),
    ("identity", "Trusted commit and PR identity gates", ".github/scripts/cla_check.py", "6"),
    ("security", "Security scan orchestration", ".github/workflows/security.yml", ""),
    ("archive", "Project archive validation and portability", "backend/services/project_bundle.py", "6"),
    ("fixtures", "Shared project interchange fixtures", "mobile/contract/project-fixtures", "6"),
    ("android-build", "Android Gradle build and packaging", "mobile/android", "7"),
    ("android-assets", "Canonical Android packaging assets", "mobile/contract/support-artwork", "7"),
    ("android-stamp", "Native OmniVoice version stamping", "scripts/android_version_code.py", "7"),
    ("android-model", "Android offline model contract", "mobile/contract", "9"),
    ("desktop-ui", "Electron desktop user interface", "electron/src/renderer", ""),
    ("desktop-tests", "Electron UI regression and smoke suite", "electron/tests", ""),
    ("desktop-package", "Windows package and installer", "electron/electron-builder.config.mjs", ""),
    ("diagnostics", "Bounded renderer diagnostics", "electron/src/shared/utils/consoleBuffer.js", ""),
    ("backend-api", "Python API behavior and recovery", "backend/api", ""),
    ("backend-core", "Core backend resource and failure handling", "backend/core", ""),
    ("audio", "Audio generation quality and fallback", "omnivoice", ""),
    ("projects", "Electron project save, import, export", "docs/electron-projects.md", "6"),
    ("privacy", "Consent, sensitive data and offline privacy", "docs/electron-privacy.md", ""),
    ("performance", "Measured CPU/RAM/disk cost", "docs/performance.md", ""),
    ("manual", "Windows and Android user manual", "docs/user-guide", ""),
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def plan() -> list[dict]:
    tasks = []
    for number, (track, title, scope, pr) in enumerate(TRACKS, 1):
        previous = None
        for stage, step in enumerate(STEPS, 1):
            ident = f"VBP-{number:02d}-{stage:02d}"
            # Each track is an ordered chain; unrelated tracks can progress independently.
            tasks.append({
                "id": ident, "title": f"{title}: {step}", "track": track,
                "scope": scope, "phase": step, "existing_pr": pr or None,
                "depends_on": [previous] if previous else [],
                "criteria": (
                    f"Evaluate {step} for {title}; use current repository evidence. "
                    "Record an actionable result with actual commands, exit codes, "
                    "source/PR SHA, and resource/security implications. "
                    "If no change is needed, document verified no-op rather than inventing work."
                ),
                "status": "pending", "attempts": 0, "updated": utc(),
                "evidence": [], "blocker": "",
            })
            previous = ident
    assert len(tasks) == 200 and len({t["id"] for t in tasks}) == 200
    return tasks


def atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    try:
        with temp.open("w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def validate(tasks: list[dict]) -> None:
    if len(tasks) != 200:
        raise ValueError("queue must contain exactly 200 tasks")
    ids = [task["id"] for task in tasks]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate task IDs")
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        if t["status"] not in {"pending", "running", "done", "blocked"}:
            raise ValueError("unknown status")
        if not isinstance(t["attempts"], int) or not 0 <= t["attempts"] <= MAX_ATTEMPTS:
            raise ValueError("invalid attempt count")
        if t["id"] in t["depends_on"] or any(dep not in by_id for dep in t["depends_on"]):
            raise ValueError("missing or self dependency")
    visited, visiting = set(), set()

    def walk(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("dependency cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for parent in by_id[task_id]["depends_on"]:
            walk(parent)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        walk(task_id)


def read_state() -> dict:
    if not STATE_FILE.is_file():
        raise FileNotFoundError("run 'py -3 tools/opencode_queue.py init' first")
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    validate(state["tasks"])
    return state


def initialize() -> None:
    if STATE_FILE.exists():
        state = read_state()
        print(f"Preserved existing queue: {len(state['tasks'])} tasks")
        return
    tasks = plan()
    validate(tasks)
    atomic_write(STATE_FILE, {"version": 1, "created": utc(), "tasks": tasks})
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    print("Initialized 200 unique ordered tasks; one active worker, 20 independent tracks.")


def ready_task(tasks: list[dict]) -> dict | None:
    statuses = {t["id"]: t["status"] for t in tasks}
    return next((t for t in tasks if t["status"] == "pending"
                 and all(statuses[dep] == "done" for dep in t["depends_on"])), None)


def queue_status(state: dict) -> dict:
    counts = {status: sum(t["status"] == status for t in state["tasks"])
              for status in ("pending", "running", "done", "blocked")}
    task = ready_task(state["tasks"])
    return {"counts": counts, "next": task["id"] if task else None,
            "running": [t["id"] for t in state["tasks"] if t["status"] == "running"]}


class ExclusiveLock:
    def __enter__(self):
        STATE_DIR.mkdir(exist_ok=True)
        try:
            fd = os.open(LOCK_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise RuntimeError(
                f"Supervisor already owns {LOCK_FILE}; check process before removing stale lock"
            ) from exc
        try:
            with os.fdopen(fd, "w") as stream:
                stream.write(str(os.getpid()))
            return self
        except BaseException:
            LOCK_FILE.unlink(missing_ok=True)
            raise

    def __exit__(self, *_):
        LOCK_FILE.unlink(missing_ok=True)


def task_prompt(task: dict, receipt: Path, attempt: int) -> str:
    return (
        "You are the autonomous VoiceBlueprintPro lead engineer, working in this repo.\n"
        "Read AGENTS.md, CLAUDE.md, docs/ROADMAP.md and the OpenCode handoff on PR #10. "
        "Reconcile current main, open PRs, status and existing work before editing. "
        "Use feature branches/draft PRs, required review, CI and approvals. "
        "Never push directly to main or invent assets. Do not ask for routine confirmation. "
        "Preserve clean modular code, strict resource limits, Windows+Android, offline-first.\n"
        f"Task {task['id']}: {task['title']}\n"
        f"Scope: {task['scope']}; existing PR: {task['existing_pr'] or 'none'}.\n"
        f"Acceptance: {task['criteria']}\n"
        f"Attempt: {attempt}/{MAX_ATTEMPTS}. If a prior attempt failed, use a different strategy.\n"
        "Do the task now; run focused tests and report actual evidence. "
        "Do not fabricate changes if no defect exists. If unable to proceed, "
        "mark BLOCKED and explain exact blocker; do not claim PASS. "
        "Update the existing canonical docs/ROADMAP.md ledger, avoiding duplicate entries.\n"
        f"At finish, write valid JSON to {receipt.relative_to(ROOT).as_posix()} "
        "with keys task_id (exact ID), status (PASS or BLOCKED), "
        "evidence (nonempty array of precise verifiable evidence strings), "
        "blocker (text if blocked). Complete receipt as last action. "
        "Do not write a receipt claiming PASS without executed evidence.\n"
    )


def check_receipt(path: Path, task_id: str) -> tuple[bool, list[str], str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("task_id") != task_id:
            return False, [], "receipt task ID mismatch"
        evidence = value.get("evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(x, str) or not x.strip() for x in evidence
        ):
            return False, [], "missing verifiable evidence"
        if value.get("status") == "PASS":
            return True, evidence, ""
        if value.get("status") == "BLOCKED":
            return False, evidence, str(value.get("blocker") or "agent reported blocker")
        return False, evidence, "invalid receipt status"
    except (OSError, ValueError, TypeError) as exc:
        return False, [], f"missing or invalid receipt: {type(exc).__name__}"


def execute(task: dict, model: str | None, timeout: int) -> tuple[bool, list[str], str]:
    receipt = RECEIPTS / f"{task['id']}.json"
    receipt.unlink(missing_ok=True)
    command = ["opencode", "run"]
    if model:
        command += ["--model", model]
    command.append(task_prompt(task, receipt, task["attempts"]))
    try:
        outcome = subprocess.run(command, cwd=ROOT, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return False, [], f"OpenCode exceeded {timeout}s timeout"
    except OSError as exc:
        return False, [], f"OpenCode launch failure: {exc}"
    if outcome.returncode != 0:
        return False, [], f"OpenCode exited {outcome.returncode}"
    return check_receipt(receipt, task["id"])


def work(model: str | None, timeout: int, once: bool) -> None:
    if shutil.which("opencode") is None:
        raise RuntimeError("opencode executable not found on PATH")
    with ExclusiveLock():
        state = read_state()
        # The previous process died while a task was active. The attempt was
        # already charged before invocation; recover without double-running it.
        for task in state["tasks"]:
            if task["status"] == "running":
                task["status"] = "blocked" if task["attempts"] >= MAX_ATTEMPTS else "pending"
                task["blocker"] = "Recovered interrupted supervisor execution"
        atomic_write(STATE_FILE, state)
        while (task := ready_task(state["tasks"])) is not None:
            task["status"] = "running"
            task["attempts"] += 1
            task["updated"] = utc()
            atomic_write(STATE_FILE, state)
            print(f"Running {task['id']} attempt {task['attempts']}: {task['title']}", flush=True)
            ok, evidence, reason = execute(task, model, timeout)
            task["evidence"] = evidence
            task["blocker"] = reason
            task["status"] = "done" if ok else (
                "blocked" if task["attempts"] >= MAX_ATTEMPTS else "pending"
            )
            task["updated"] = utc()
            atomic_write(STATE_FILE, state)
            print(f"{task['id']} => {task['status']}: {reason or 'receipt received'}", flush=True)
            if once:
                break
        else:
            print("No ready tasks; completed queue or outstanding dependencies/blockers.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "status", "run"))
    parser.add_argument("--model", default=None, help="Configured OpenCode provider/model")
    parser.add_argument("--timeout", type=int, default=7200, help="Maximum seconds per task")
    parser.add_argument("--once", action="store_true", help="Execute one task attempt")
    args = parser.parse_args()
    if args.timeout < 30:
        parser.error("--timeout must be at least 30 seconds")
    try:
        if args.command == "init":
            initialize()
        elif args.command == "status":
            print(json.dumps(queue_status(read_state()), indent=2))
        else:
            work(args.model, args.timeout, args.once)
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        print(f"QUEUE ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
