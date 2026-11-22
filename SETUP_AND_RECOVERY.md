# Setup and Recovery

## Clone
```bash
git clone https://github.com/DevTunaSoft/VoiceBlueprintPro.git
cd VoiceBlueprintPro
```

## Backend
```bash
uv sync
uv run python scripts/export_openapi.py
```

## Electron
```bash
bun install
bun run dev
```

## Tests
```bash
uv run python -m pytest -q tests/test_project_bundle.py
uv run python -m pytest -q tests/test_mobile_contract.py
```

## Recovery checklist
- Check `git status`, branches, worktrees, stashes.
- Fetch origin and reconcile.
- Do not force-push or delete branches.
- Preserve unfinished work on WIP branches.
