# VoiceBlueprintPro — Master Handoff

Repository: https://github.com/DevTunaSoft/VoiceBlueprintPro
Default branch: `main`
Verified main HEAD: `5f63ac252d91607dae2ac6a5cf2156ef4bbfb2de`

## Product
Local-first voice production suite (voice cloning, design, dubbing, dictation). Desktop via Electron + Python backend; native Android/iOS clients; cross-device project archives.

## Nonnegotiables
- Electron only for desktop/web UI.
- Native iOS and Android mobile apps, shared contract `mobile/contract/SPEC.md`.
- Local-first, offline-capable, strict resource limits.
- English-only product direction; legacy locale scaffolding retained for tests.
- All user-facing strings through i18n in all locale catalogs.

## Key directories
- `electron/` desktop UI
- `backend/` Python API/services
- `mobile/android/`, `mobile/ios/`
- `mobile/contract/` generated contract artifacts
- `tests/` backend/frontend/mobile contract tests

## Versioning
Root `package.json` is single source of truth; `pyproject.toml` and `backend/core/version.py` mirror. Guarded by `tests/test_app_version.py`.

## Recent completed work on main
- Restored commit-identity helper module (`.github/scripts/cla_check.py`).
- Locale parity fix in shared i18n catalogs.
- Changelog style entry shortening.
- Structure doc count corrections.
- Mobile OpenAPI contract refresh.
- UTF-8 locale read fix in mobile contract test.
- Project bundle fixture repair and ARCH-001 preflight coverage (PR #6).

## Open PRs
- #6 Fix shared archive fixtures and trusted identity gate (draft)
- #7 Fix OmniVoice version stamping in mobile builds (draft)
- #8 Fix changelog entry length lint (draft)
- #9 Preserve pinned mobile model bytes on Windows (draft)
- #10 OpenCode autonomous handoff (draft)
- Dependabot PRs #1-#5

## Known blockers
- PR #7 Android packaging blocked on missing canonical contributor/support assets; do not fabricate.
- Some workflow-guard tests need updates to redesigned release workflow.
- Full CI on latest main pending.

## Recovery
1. `git clone https://github.com/DevTunaSoft/VoiceBlueprintPro.git`
2. Read `AGENTS.md`, `CLAUDE.md`, `docs/ROADMAP.md`.
3. Install deps per `.github/CONTRIBUTING.md` and `pyproject.toml`.
4. Run targeted tests before broad suites.
