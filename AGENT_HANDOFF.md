# Agent Handoff

## Start here
1. `git fetch origin`
2. Read `AGENTS.md`, `CLAUDE.md`, `docs/ROADMAP.md`, `MASTER_HANDOFF.md`.
3. Check open PRs: `gh pr list --state open`.
4. Check CI: `gh run list --branch main --limit`.

## Rules
- Never merge without required checks/review.
- Use feature branches and draft PRs.
- Keep changes minimal and recurrence-proof.
- Run targeted tests first.
- Update `docs/ROADMAP.md` as canonical ledger.

## Current highest-priority work
1. Resolve PR #7 Android packaging asset gap (canonical assets only).
2. Update workflow-guard tests to redesigned release workflow.
3. Watch PR #6/#7 CI and merge when green.
4. Run full CI on latest main.

## Do not duplicate
- PR #6 already contains project bundle fixture repair.
- PR #7 already contains OmniVoice version stamping.
- Main already contains commit-identity bootstrap fix.
