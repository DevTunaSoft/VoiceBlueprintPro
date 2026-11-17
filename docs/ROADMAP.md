# VoiceBlueprintPro — canonical development task ledger and recovery handoff

**Updated:** 2026-11-17. **Repository:** `DevTunaSoft/VoiceBlueprintPro`. **Base:** `main` at `5be8a73bfd40dd11839dc2a17fb6d88f891f8b7d`; active work: `fix/project-export-validation-race`.
**Audited starting SHA:** `5be8a73bfd40dd11839dc2a17fb6d88f891f8b7d`.
**Last verified engineering SHA:** `d9629c9` (PR #6; focused export and changelog-fragment checks pass). This ledger update follows that commit.

This file is the **single canonical development task ledger**. Keep feature-level evidence in
[the user-facing verification record](user-guide/feature-verification.md), architectural facts
in [STRUCTURE.md](STRUCTURE.md), and usage instructions in the [user manual](user-guide/README.md).
Do not maintain a second task backlog in those documents.

## Operating scope and architecture

- Independent, local-first VoiceBlueprintPro speech/voice studio; supported product targets are **Windows desktop and Android**.
  Legacy macOS, Linux and iOS content remains in the repository and some workflows, but is not an accepted new release target.
- Electron desktop UI (`electron/`), Python backend (`backend/`), Android client (`mobile/android/`),
  project archive interchange (`backend/services/project_bundle.py`), and shared tests (`tests/`).
- Keep modules focused, resource limits strict, processing bounded, and offline use possible.
  No new always-on polling, paid services, unnecessary frameworks, or memory-expensive conversions.
- Historic documentation and agent instructions may still refer to retired platforms or names;
  reconcile them against the currently authorized Windows/Android direction before changing any release pipeline.

## Source-backed tasks

| Task | Scope / measurable acceptance criteria | Branch / PR; starting → ending SHA | Status and evidence | Blocker / next action |
| --- | --- | --- | --- | --- |
| **CI-001** | Main commits never cancel each other's CI; newer PR revisions still cancel their superseded runs. Preserve job gates and permissions. | `main`, no PR; `cf22c0e` → `652dc36` | **PASS (source contract only):** changed `.github/workflows/ci.yml`, re-fetched blob and checked against existing `tests/test_ci_queue_hygiene.py` contract. Multiple prior main CI runs were cancelled on repeated pushes. **NOT RUN:** pytest and post-change Actions completion. | Confirm `python -m pytest -q tests/test_ci_queue_hygiene.py` and full Actions completion on `652dc36` or a descendant. Avoid unnecessary commits while a full run completes. |
| **ARCH-001** | Reject oversized, invalid, duplicate-case and excessive-count export asset inputs *before* hashing. Preserve valid imports and atomic output. | PR #6, `fix/project-export-validation-race`; `5be8a73` → `d9629c9` | **PASS (local):** `python -m pytest -q tests/test_project_bundle.py` → 37 passed. Hashing reads at most `MAX_MEMBER + 1`; archive writing reads at most declared size plus one sentinel byte and rejects changed content before atomic publication. **NOT RUN:** current-sha GitHub Actions. | Keep per-member and total archive limits; resolve PR #6's required-check blockers before merge. |
| **PORT-002** | All shared project archive fixtures use the documented `voiceblueprint.project` format and remain readable by desktop, iOS and Android contract tests. | PR #6, `fix/project-export-validation-race`; `5be8a73` → `d9629c9` | **PASS (local):** corrected both checked-in `.vsproject` manifests; `python -m pytest -q tests/test_project_bundle.py` → 37 passed. **FAIL (local mobile-contract baseline):** `python -m pytest -q tests/test_mobile_contract.py` → 8 failed, 46 passed, 2 skipped; errors include missing `uvicorn`, mismatched bundled model pin and missing Electron contributor files. **FAIL (GitHub Actions):** Android build failed in pre-existing native OmniVoice compilation (`OMNIVOICE_VERSION` undeclared); this is outside the fixture changes. **NOT RUN:** device installation/interchange tests. | Android native build must be repaired and fixture contracts rerun before claiming mobile parity. |
| **CI-003** | Trusted PR identity policy evaluates current metadata and safely publishes the required status; native job must fail closed on API/policy errors. | PR #6, `fix/project-export-validation-race`; `fcc6206` → `87eca3b` | **PASS (local):** `python -m pytest -q tests/test_identity_gate.py tests/test_commit_identities.py` → 119 passed; `python scripts/check_commit_identities.py --range origin/main..HEAD` → 3 commits clean. **BLOCKED (GitHub Actions):** `pull_request_target` intentionally runs policy from base `main`, where `.github/scripts/identity_check.py` still imports absent `cla_check`; the PR's repair cannot execute until the base-owned policy is repaired or otherwise authorized. Both runs fail before evaluation. No merge/bypass was attempted. **FAIL (local repository baseline):** `python -m pytest -q tests/test_changelog_fragments.py` → 1 failed, 9 passed because two existing `CHANGELOG.md` entries exceed the lint limit. | Maintainer action required to repair the base-owned identity bootstrap; then rerun the PR gates. Keep PR #6 draft until required checks are green. |
| **CI-002** | Current full Windows/Electron/Python CI finishes with a trustworthy pass or categorized failure list. | `main`; latest run pending | **UNVERIFIED.** Historical run `43088446274` reported 12,616 passed, 77 failed and 7 errors; this is not current-sha validation. | Review [Actions](https://github.com/DevTunaSoft/VoiceBlueprintPro/actions); identify reproducible first failures, fix root causes with regression tests. |
| **PORT-001** | Windows-to-Android project interchange preserves editable content and asset fingerprints; malformed archives fail safely. | `main`; prior bundle implementation | **UNVERIFIED** on devices. Historical portable fixture incompatibilities remain. | Run bundle contracts and Android tests, check real fixture files, repair smallest confirmed incompatibility. |
| **PLAT-001** | Windows x64/ARM64 and Android install, audio, offline models and memory limits verified on representative hardware. | `main`; release not published | **NOT RUN** for current commit and real hardware. | Establish measured target hardware memory budget and run end-to-end generation/install/uninstall tests before release claims. |

## Coordination / CI safeguards

- Current GitHub issues search returned no open issues and roadmap issue
  [#3425](https://github.com/DevTunaSoft/VoiceBlueprintPro/issues/3425) was unavailable (404) during the audit.
  Treat it as a **stale pointer**, not a live tracker; this file holds the current roadmap until issue access is restored.
- Open PRs are Dependabot action updates (#1–#5); checks are failing, including commit identity and runtime tests. Do not duplicate those dependency tasks or merge them as-is.
- `ci.yml` runs on PR, main push, merge queue and manual dispatch. CI-001 isolates each main SHA's
  concurrency group and cancels only superseded PR runs; `security.yml` already isolates main SHA runs.
  Expensive packaging is manual-only in `electron-build.yml`. Assess other workflows separately rather than broadly rewriting triggers.
- The connected repository API supports file commits and read-only Actions inspection.
  The execution container could not clone GitHub (DNS resolution failed); therefore source-level
  assertions are not a substitute for running the repository's test suite.

## Recovery / handoff procedure

1. Read this file, `AGENTS.md`, `CLAUDE.md`, the relevant implementation/test files, and the live
   `main` SHA. Compare against the latest commit before applying patches.
2. Read open PRs, issues (if available), Actions workflows and statuses. Do not repeat already landed work.
3. Resolve **CI-003**'s base-owned identity-check bootstrap blocker; do not bypass the required status or merge without authorization.
4. Repair the independent Android native build failure, then run iOS/Android project fixture tests for **PORT-002 / PORT-001**.
5. Make one coherent change per cycle; use tracked SHA reads and explicit rollback via a
   reverting commit if regression evidence warrants it. Do not force-push or discard unrelated changes.
6. Record test commands, actual results, changed files, SHA, failures and next actions here.
   Never mark production-ready based only on historical tests.

## Status labels

**PASS** = operation or check actually verified; **FAIL** = executed and failed;
**BLOCKED** = genuine access/dependency impediment; **NOT RUN** = execution not attempted;
**UNVERIFIED** = evidence insufficient. A source-contract PASS is not a runtime PASS.
