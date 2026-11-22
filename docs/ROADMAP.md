# VoiceBlueprintPro — canonical development task ledger and recovery handoff

**Updated:** 2026-11-21. **Repository:** `DevTunaSoft/VoiceBlueprintPro`. **Default/working branch:** `main`.
**Audited starting SHA:** `cf22c0e20d984e05bc3f972207aa9b8e88ccaac4`.
**Last verified engineering SHA:** `238e8b9663c8edd22b98f4409aa8200d1ed5ec04`.
The documentation commit that updates this ledger follows that SHA; verify the actual branch head before resuming.

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
| **CI-001** | Main commits never cancel each other's CI; newer PR revisions still cancel their superseded runs. Preserve job gates and permissions. | `main`, no PR; `cf22c0e` → `d6d922b` | **PASS (source contract + bootstrap + Actions observation):** restored missing `.github/scripts/cla_check.py`; `tests/test_identity_gate.py` → 12 passed. Full run `44976652665` on `24b483c` completed with independent per-SHA main groups; no cancellation starvation. | No further action. Main failures come from test/fixture drift recorded under CI-002, not concurrency. |
| **ARCH-001** | Reject oversized, invalid, duplicate-case and excessive-count export asset inputs *before* hashing. Preserve valid imports and atomic output. | `main`, no PR; `cf22c0e` baseline includes `8e51c10`, `a44d7a3` and `cf22c0e` | **PASS (execution).** `python -m pytest -q tests/test_project_bundle.py` → 34 passed. Repaired two stale `.vsproject` fixtures whose manifests used retired `voicestudio.project` instead of `voiceblueprint.project` (7 failures). `write_bundle` rechecks size and SHA-256 after `archive.write` and replaces via pending file, so the validation→export race cannot produce a bad archive. | Verify Swift/Kotlin fixture consumers on device under PORT-001; no remaining local action for ARCH-001. |
| **CI-002** | Current full Windows/Electron/Python CI finishes with a trustworthy pass or categorized failure list. | `main`; run `44976652665` on `24b483c` | **CATEGORIZED, NOT GREEN.** Python: 72 failed / 12,638 passed / 6 errors. Renderer: 4/39 smokes failed. Electron typecheck/tests failed. Groups: stale binary fixtures (fixed in `238e8b9`), files and locales absent from this repository, brand/identifier drift, workflow snapshot drift, stale iOS/GGUF expectations, smoke-text drift. | Reconcile remaining groups one coherent change per cycle. Do not call main release-verified. |
| **PORT-001** | Windows-to-Android project interchange preserves editable content and asset fingerprints; malformed archives fail safely. | `main`; prior bundle implementation | **UNVERIFIED** on devices. Historical portable fixture incompatibilities remain. | Run bundle contracts and Android tests, check real fixture files, repair smallest confirmed incompatibility. |
| **PLAT-001** | Windows x64/ARM64 and Android install, audio, offline models and memory limits verified on representative hardware. | `main`; release not published | **NOT RUN** for current commit and real hardware. | Establish measured target hardware memory budget and run end-to-end generation/install/uninstall tests before release claims. |

## Coordination / CI safeguards

- Current GitHub issues search returned no open issues and roadmap issue
  [#3425](https://github.com/DevTunaSoft/VoiceBlueprintPro/issues/3425) was unavailable (404) during the audit.
  Treat it as a **stale pointer**, not a live tracker; this file holds the current roadmap until issue access is restored.
- [PR #5](https://github.com/DevTunaSoft/VoiceBlueprintPro/pull/5) is open for a CodeQL action dependency bump.
  Inspect review, base SHA and checks before merging; no duplicate PR or dependency update for that task.
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
3. **CI-001 verification done:** run `44976652665` on `24b483c` completed; no concurrency
   starvation. Its other failures are grouped under CI-002, not CI-001.
4. **ARCH-001 closed** at `238e8b9`; continue with **PORT-001** device checks. Retain strict
   per-member and total archive limits; fix stale fixtures instead of relaxing validation.
5. Make one coherent change per cycle; use tracked SHA reads and explicit rollback via a
   reverting commit if regression evidence warrants it. Do not force-push or discard unrelated changes.
6. Record test commands, actual results, changed files, SHA, failures and next actions here.
   Never mark production-ready based only on historical tests.

## Status labels

**PASS** = operation or check actually verified; **FAIL** = executed and failed;
**BLOCKED** = genuine access/dependency impediment; **NOT RUN** = execution not attempted;
**UNVERIFIED** = evidence insufficient. A source-contract PASS is not a runtime PASS.
