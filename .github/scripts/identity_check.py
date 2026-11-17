#!/usr/bin/env python3
"""Run base-owned identity policy against fetched PR commits as inert data.

The trusted pull_request_target workflow publishes a separate commit status.
An unprivileged fork workflow can forge a native job name, but cannot replace
this status with its read-only token. The native job remains an API-health gate.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))


class GitHub:
    """Minimal GitHub API client for the trusted identity status workflow."""

    def __init__(self, token: str, repo: str, api: str = "https://api.github.com"):
        self.token, self.repo, self.api = token, repo, api.rstrip("/")

    def request(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(f"{self.api}{path}", data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return response.status, json.loads(raw) if raw else None, response.headers
        except urllib.error.HTTPError as error:
            raw = error.read()
            try:
                payload = json.loads(raw) if raw else None
            except ValueError:
                payload = None
            return error.code, payload, error.headers

    def get(self, path: str):
        status, payload, _ = self.request("GET", path)
        if status != 200:
            raise RuntimeError(f"GitHub GET {path} failed with {status}")
        return payload

    def paginate(self, path: str, *, limit: int):
        items = []
        page = 1
        while len(items) < limit:
            separator = "&" if "?" in path else "?"
            status, payload, _ = self.request(
                "GET", f"{path}{separator}per_page={min(100, limit - len(items))}&page={page}"
            )
            if status != 200 or not isinstance(payload, list):
                raise RuntimeError(f"GitHub GET {path} failed with {status}")
            items.extend(payload)
            if len(payload) < min(100, limit - (len(items) - len(payload))):
                break
            page += 1
        return items[:limit]


def head_blockers(gh: GitHub, pr: dict) -> list[dict]:
    """Return other open PRs sharing this head SHA, which would reuse its status."""
    sha = pr["head"]["sha"]
    return [candidate for candidate in gh.paginate(
        f"/repos/{gh.repo}/pulls?state=open", limit=100
    ) if candidate.get("number") != pr.get("number")
        and candidate.get("head", {}).get("sha") == sha]


def set_status(gh: GitHub, sha: str, state: str, description: str, *, context: str) -> None:
    status, _, _ = gh.request("POST", f"/repos/{gh.repo}/statuses/{sha}", {
        "state": state, "description": description[:140], "context": context,
    })
    if status != 201:
        raise RuntimeError(f"Could not write {context} status ({status})")

ROOT = Path(__file__).resolve().parents[2]
STATUS_CONTEXT = "Commit identity policy"


def _snapshot(pr: dict) -> tuple:
    return (pr.get("state"), pr["head"]["sha"], pr["base"]["sha"], pr.get("body") or "")


def run(gh: GitHub, event: dict, root: Path = ROOT) -> bool:
    event_pr = event["pull_request"]
    number = int(event_pr["number"])
    pending_sha = event_pr["head"]["sha"]
    set_status(gh, pending_sha, "pending", "Checking commit identities", context=STATUS_CONTEXT)
    pr = gh.get(f"/repos/{gh.repo}/pulls/{number}")
    if pr["state"] != "open":
        return True
    sha, base = pr["head"]["sha"], pr["base"]["sha"]
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (sha, base)):
        raise RuntimeError("Invalid commit identity comparison")
    if sha != pending_sha:
        raise RuntimeError("PR head changed since this event; run the current target workflow")

    if head_blockers(gh, pr):
        set_status(gh, sha, "failure", "Close duplicate PR heads and rerun the survivor's identity check",
                   context=STATUS_CONTEXT)
        return False

    # Fetch objects only: never checkout PR files, run its workflows, or fall
    # back to its checker. The base checkout holds every executable policy file.
    environment = {key: value for key, value in os.environ.items() if key != "GITHUB_TOKEN"}
    policy_base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, env=environment, text=True).strip()
    if policy_base != base:
        raise RuntimeError("PR base changed since this policy checkout; run a fresh target workflow")
    subprocess.run(["git", "fetch", "--no-tags", "origin", f"refs/pull/{number}/head"],
                   cwd=root, env=environment, check=True)
    fetched = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"], cwd=root, env=environment, text=True).strip()
    if fetched != sha:
        raise RuntimeError("PR head changed during fetch; recheck")
    with tempfile.TemporaryDirectory(prefix="identity-event-") as directory:
        metadata = Path(directory) / "event.json"
        metadata.write_text(json.dumps({"pull_request": {"body": pr.get("body")}}), encoding="utf-8")
        result = subprocess.run([
            sys.executable, str(root / "scripts/check_commit_identities.py"),
            "--hash-file", str(root / "scripts/blocked_identity_hashes.txt"),
            "--range", f"{base}..{sha}", "--event", str(metadata),
        ], cwd=root, env=environment)
    if result.returncode not in (0, 1):
        raise RuntimeError("Commit identity policy could not be evaluated")
    if _snapshot(gh.get(f"/repos/{gh.repo}/pulls/{number}")) != _snapshot(pr):
        raise RuntimeError("PR metadata changed during identity evaluation; recheck")
    duplicates = head_blockers(gh, pr)
    passed = result.returncode == 0 and not duplicates
    set_status(gh, sha, "success" if passed else "failure",
               ("Close duplicate PR heads and rerun the survivor's identity check" if duplicates else
                "Commit identities are clean" if passed else "Blocked commit identities or agent attribution"),
               context=STATUS_CONTEXT)
    return passed


def main() -> int:
    if os.environ.get("GITHUB_EVENT_NAME") != "pull_request_target":
        raise RuntimeError("Identity enforcement requires trusted pull_request_target orchestration")
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as handle:
        event = json.load(handle)
    gh = GitHub(os.environ["GITHUB_TOKEN"], os.environ["GITHUB_REPOSITORY"],
                os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    print("Commit identity policy:", "passed" if run(gh, event) else "blocked")
    return 0  # eligibility is the status; API/execution failures raise


if __name__ == "__main__":
    sys.exit(main())
