"""Trusted helpers for the commit-identity gate.

Provides the GitHub client, duplicate-head detection, and status writer used by
``identity_check.py``. Standard library only.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_FILE = _ROOT / "scripts" / "check_commit_identities.py"
try:
    _spec = importlib.util.spec_from_file_location("check_commit_identities", _AGENTS_FILE)
    _checker = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_checker)
    _classify_text = _checker.classify_text
except Exception:  # pragma: no cover - defensive fallback
    _classify_text = lambda text: []


class GitHub:
    def __init__(self, token: str, repo: str, api: str = "https://api.github.com"):
        self.token = token
        self.repo = repo
        self.api = api.rstrip("/")

    def _request(self, method, path, body=None):
        url = self.api + path
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req) as response:
                raw = response.read()
                payload = json.loads(raw) if raw else None
                return response.status, dict(response.headers), payload
        except HTTPError as exc:
            raw = exc.read()
            try:
                payload = json.loads(raw) if raw else None
            except Exception:
                payload = None
            return exc.code, dict(exc.headers), payload

    def get(self, path):
        status, _headers, payload = self._request("GET", path)
        if status >= 400:
            raise RuntimeError(f"GitHub API request failed: {status}")
        return payload

    def request(self, method, path, body=None, ok=(200, 201, 204)):
        status, headers, payload = self._request(method, path, body)
        return status, headers, payload

    def paginate(self, path, *, limit=100):
        results = []
        page = 1
        while len(results) < limit:
            separator = "&" if "?" in path else "?"
            query = f"{path}{separator}per_page=100&page={page}"
            status, _headers, payload = self._request("GET", query)
            if status >= 400:
                raise RuntimeError(f"GitHub API request failed: {status}")
            if not isinstance(payload, list) or not payload:
                break
            results.extend(payload)
            if len(payload) < 100:
                break
            page += 1
        return results[:limit]


def head_blockers(gh, pr):
    sha = (pr.get("head") or {}).get("sha")
    number = pr.get("number")
    open_prs = gh.paginate(f"/repos/{gh.repo}/pulls?state=open", limit=100)
    for candidate in open_prs or []:
        if candidate.get("number") == number:
            continue
        if sha and candidate.get("head", {}).get("sha") == sha:
            return True
    body = pr.get("body") or ""
    try:
        if _classify_text(body):
            return True
    except Exception:
        if re.search(r"generated\s+(with|by|using)\s+\[?(claude|cursor|copilot|codex|chatgpt|gemini|devin|jules|aider|cline|coderabbit)", body, re.I):
            return True
    return False


def set_status(gh, sha, state, description, context=None, **kwargs):
    body = {"state": state, "description": description}
    if context is not None:
        body["context"] = context
    body.update(kwargs)
    status, _headers, _payload = gh.request(
        "POST", f"/repos/{gh.repo}/statuses/{sha}", body=body
    )
    if status not in (200, 201, 204):
        raise RuntimeError("Could not write Commit identity policy status")