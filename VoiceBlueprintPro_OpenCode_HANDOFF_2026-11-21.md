# VoiceBlueprintPro — OpenCode Engineering Handoff

**Audit date:** 2026-11-21 (US Central)
**Repository:** https://github.com/DevTunaSoft/VoiceBlueprintPro
**Default branch:** `main`
**Verified remote main HEAD:** `5be8a73bfd40dd11839dc2a17fb6d88f891f8b7d`
**Status:** Development ongoing; release readiness **UNVERIFIED**.

> This handoff is a point-in-time evidence snapshot. OpenCode must fetch current remote state and reconcile every detail before acting. Do not bypass repository protections, reuse stale branch pointers, or merge unreviewed PRs.

## A. Product intent and nonnegotiable standards

Independent, local-first **VoiceBlueprintPro** voice production suite. Current authorized release targets: **Windows desktop and Android**, **English-only product direction**. Existing historical platform and locale scaffolding is present and may be required by tests; reconcile rather than destructively delete. Electron is the desktop UI, Python the backend, native Android under `mobile/android`, and cross-device project interchange under `backend/services/project_bundle.py`. Retain historical licensing/attribution while removing misleading old-project branding.

- Clean, small, modular, maintainable patches; no needless rewrites, dependencies, services, polling, or memory-heavy conversions.
- Respect per-asset/total ZIP limits, bounded logs, safe path handling, atomic writes, consent, offline-first model use, privacy and credential protections.
- Measure resource usage where practical; never invent numbers or claim CPU/RAM gains based solely on source changes.
- Use actual tests, exact exit status and CI evidence. Keep unverified work labelled **NOT RUN** / **UNVERIFIED**.
- Read `AGENTS.md`, `CLAUDE.md`, `docs/ROADMAP.md` before changing code. **Potential conflict:** Those older files prescribe macOS/Linux/iOS and 21 translation catalogs, while current owner direction is Windows+Android and English-only. Preserve compatibility and tests until a deliberate, verified migration; do not silently broaden release targets or destroy inherited functionality.
- Follow branch/PR and required review/green-CI rules, update docs with code, and never merge or push straight to `main` unless repository policy explicitly permits that workflow. Earlier assistant commits were made directly on main; do **not** infer this is desired future policy.

## B. Verified remote baseline

The GitHub connector confirmed `main` at `5be8a73bfd40dd11839dc2a17fb6d88f891f8b7d`. Recent main commits (all already landed; **do not redo**):

| Commit | Existing work |
| --- | --- |
| `5be8a73` | Replaced `docs/ROADMAP.md` with canonical task ledger/handoff |
| `652dc36` | Changed `.github/workflows/ci.yml` grouping so main SHA runs do not cancel one another; PR revisions still cancel |
| `cf22c0e` | Recorded project export resource-preflight verification debt |
| `a44d7a3` | Added tests for export preflight size/name/member-count checks |
| `8e51c10` | Preflight reject invalid/oversize archive assets before hashing |
| `471d5ef`, `5cab243`, `7765540` | Isolate captured frontend log snapshots; ring buffer regression tests |

Main's `docs/ROADMAP.md` is the **single canonical task ledger**. Update that file instead of inventing a second persistent task-tracking system. This handoff is for OpenCode onboarding, not an authoritative replacement.

**GitHub issue search:** zero open issues were returned in audit; old roadmap issue `#3425` returned 404 previously. Work from actual repository and live PRs.

## C. Existing open PRs — critical duplication protection

As of audit, eight PRs were open:

- **#6** https://github.com/DevTunaSoft/VoiceBlueprintPro/pull/6 — **draft**, shared project archive fixtures and trusted identity gate, head `2d5623b6e99e1312c84aaace8b85ec217de6bcdb`; author reports focused project bundle **34 passed**, identity policy **119 passed**, but merge status `unstable`. **Reconcile/use this PR before any new archive-fixture or identity work.**
- **#7** https://github.com/DevTunaSoft/VoiceBlueprintPro/pull/7 — **draft**, mobile OmniVoice version stamping, head `20ba9b9648914c42432677e7f5c4ee82bf084887`; reports Android JNI compilation and focused tests, but packaging fails at `:app:bundleCatalogs` owing to missing source assets. No invented replacements. Also identity gate baseline issues.
- **#8** https://github.com/DevTunaSoft/VoiceBlueprintPro/pull/8 — changelog lint fixes.
- **#9** https://github.com/DevTunaSoft/VoiceBlueprintPro/pull/9 — LF bytes for pinned mobile model lexicon on Windows.
- **#1–#5** — dependency-update PRs for GitHub Actions; do not duplicate bumps. #5 is CodeQL upload-sarif upgrade.

Before work: `gh pr list --state open`, `gh pr view N --json ...`, `gh pr checks N`, and inspect review comments. Check branches and SHAs afresh; they may have changed.

## D. CI evidence — IMPORTANT

At the audit, **`main` remained unchanged since November 11**. Scheduled `docs-drift` runs through November 21 passed; this is **not** a full build pass.

- Main CI https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/43104614762 on `5be8a73`: **FAIL**. Jobs: `Tests (Python)` FAIL, `Tests (Electron)` FAIL, `Electron renderer smokes` FAIL, required `Tests (backend + frontend)` FAIL; `Desktop UI (Windows)` PASS and `UI crawler (2/3)` PASS; several jobs cancelled; `Changed paths` cancelled. Inspect logs rather than speculate.
- Main Security https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/43104614855: **FAIL** at workflow level even though secrets, CodeQL, dependency audit, and bandit jobs showed success; `Changed paths` cancelled. Diagnose orchestration rather than dismiss it as green.
- A later PR #7 check https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/44184243278 failed CI; mobile run https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/44184243343 failed; Security https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/44184243258 passed; commit-identity https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/44184235290 failed. These are **PR-branch results**, not main validation.
- Main CI cancellation change `652dc36` is source-verified, not proven by passing full suite; its existing contract is in `tests/test_ci_queue_hygiene.py`.
- The previous ledger cites historical run with **12,616 passing tests, 77 failures, 7 errors**. Historical figures, not fresh results.

Suggested first commands (run in local clone; adapt to environment):

```powershell
git status --short --branch
git remote -v
git fetch origin --prune
git log -5 --oneline origin/main
gh pr list --state open
gh run list --branch main --limit 15
gh run view 43104614762 --json jobs,conclusion,headSha,htmlURL
gh run view 43104614855 --json jobs,conclusion,headSha,htmlURL
python -m pytest -q tests/test_ci_queue_hygiene.py tests/test_project_bundle.py
```

Don't run a suite blindly without checking installed dependencies, repo instructions and Python environment. Never pretend a test ran because its command was written.

## E. Canonical next task order

1. **CI-001 / CI-002 — root-cause CI readiness.** Inspect failing main jobs, underlying job logs, current `ci.yml`, `security.yml`, `.github/scripts/ci_scope.py`, `tests/test_ci_queue_hygiene.py`. Reproduce focused failures locally; make one minimal change with regression coverage. Keep required checks and secret scanning. Avoid cascades of commits that starve test results.
2. **PORT-001 / ARCH-001 — project archives.** First inspect **PR #6** and its evidence. Run `tests/test_project_bundle.py`, portable fixtures and Android/desktop contract tests. Retain archive security/resource bounds. Check streaming, interrupted exports, cleanup and original asset integrity.
3. **Android packaging.** Inspect **PR #7** and missing-assets errors. Do not recreate assets from guesses. Validate native builds and preserve English-only direction.
4. **Windows end-to-end acceptance.** Packaged startup, fresh install/uninstall, real audio input/output, model inference, restore, GPU fallback, peak memory and crash recovery. CI mocks do not count as physical acceptance.
5. Branding/docs alignment, platform/locale policy reconciliation, measured performance and manual improvements after reliability is established.

## F. Mandatory execution / no-loop protocol

- Establish clean working tree; preserve uncommitted changes. Fetch origin/main and candidate PR refs. Check branch protection and current required statuses.
- For each task record ID, baseline SHA, prior PR/branch, criteria, failing command, signature, hypothesis, fix, regression result, new SHA and next action **in `docs/ROADMAP.md`**.
- After two identical failures, change approach; after two nonproductive cycles, switch task and document blocker.
- Prefer feature branches and draft PRs; compare active PRs before creating new ones. Never merge without required checks and review resolution. Commit only verified focused work; do not promise future progress after execution session ends.
- Avoid retry loops, fake benchmarks, dependency upgrades unrelated to blockers, background daemons, Docker/Ollama requirements or paid APIs.
- Focused test, then integration/regression, then Actions and real Windows/Android acceptance when hardware exists.
- Each checkpoint: **PASS/FAIL/BLOCKED/NOT RUN/UNVERIFIED**, test command and environment, SHA, PR, CI URL, files, root cause, remaining blocker and next step.

## G. Resume location

**Start:** fresh Git fetch + inspect `main` at `5be8a73`, current open PRs (especially #6 and #7), and main CI failures `43104614762` and `43104614855`. The best first correction is the highest-impact **reproduced** failure, not another unexecuted log-buffer or preflight test. Update `docs/ROADMAP.md` when evidence changes.

This handoff is archived on a documentation branch, not yet integrated into `main`; check the associated PR before merging.
