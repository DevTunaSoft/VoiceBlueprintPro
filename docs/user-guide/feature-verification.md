# User-facing feature verification ledger

**Reviewed:** November 11, 2026. **Evidence baseline:** Historical full CI `af3f97d8` passed before current rebranding. New Windows/Android changes have not yet passed the full current CI; "automated" is not "release verified."

| Feature | Functional verification | Required evidence / remaining real-device validation |
| --- | --- | --- |
| Windows x64 package and CPU runtime | [Packaging #42426554733](https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/42426554733): installer, startup, managed backend | User PC installation and uninstall, speech, microphone, speakers, GPU |
| Windows ARM64 packaging | Same run: native shell plus emulated x64 Python/CPU runtime passed | Real Snapdragon device, sustained performance, audio |
| Android build and packaging | Android workflows and Play listing updated for VoiceBlueprintPro; no current release validation yet | APK install/upgrade, native model inference, battery and memory behavior on physical Android devices |
| Electron desktop Settings → Models | Same run captured a real packaged screenshot (1024×728) and navigated to model manager | Actual model download and fully loaded interface |
| Electron UI and test matrix | [Full CI #42439650200](https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/42439650200) passed UI crawlers, renderer, integration and smoke checks | Keyboard/screen-reader audit, all production workflows |
| Queue shutdown and cancellation | Same CI passed Python queue regression tests | Power-loss recovery, persisted job resume, latest fuzz rounds |
| Voice cloning, speech, transcription, dubbing | Source and inherited documentation exist | Real model download, generated output, human quality review |
| Project save/export and backup | Inherited implementations and source-level inspection | Interrupted writes, preservation after crash and restore on users' devices |
| Settings, diagnostics and support | Source-inspected About controls; desktop UI suite passed | Real diagnostic export and supported bug intake; GitHub Issues disabled |
| Upgrade, rollback, uninstall | Installer/update contract tests | Signing, migration, uninstall and rollback verification |

## November 11 engineering checkpoint (current main)

**Scope:** Windows desktop and Android only; older Linux/macOS/iOS artifacts are historical and not supported targets.

- Source fixes include the missing About-panel icon, renamed preference reset keys, synthetic analytics URL test, bounded desktop backend/setup log buffers and bounded frontend console capture. The console buffer retains at most 500 captured messages, each at most 4,096 characters, omitting oversized values. These are code limits, **not measured app RAM**.
- Project bundle import now preserves the specific archive-format validation reason instead of relabeling it as malformed JSON. Import tests using existing portable fixture bundles still have unresolved compatibility failures; do not claim phone/desktop project handoff works.
- Android Google Play title corrected to `VoiceBlueprintPro: Offline AI` (29 characters against the 30-character Play limit).
- Last completed broad Python run [CI #43088446274](https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/43088446274) reported 12,616 passed, 77 failed and 7 errors. It also failed renderer/desktop tests; its many stale-platform and missing-fixture assertions need separate reconciliation.
- Current commit and [Actions](https://github.com/DevTunaSoft/VoiceBlueprintPro/actions) must be checked for fresh CI evidence. Windows/Android real-device inference and peak memory remain **NOT RUN / UNVERIFIED**.

## November 11 project export resource-preflight checkpoint

- Commits [8e51c10](https://github.com/DevTunaSoft/VoiceBlueprintPro/commit/8e51c10f514dde3b7ca637636d3c349245002a74) and [a44d7a3](https://github.com/DevTunaSoft/VoiceBlueprintPro/commit/a44d7a3107be829807567132d7243fbca2a87eda) reject oversized, excessive-count, invalid-extension and duplicate-case asset names before hashing rejected files.
- Three focused regression tests were added to `tests/test_project_bundle.py`, with a digest guard ensuring rejected inputs are not hashed. Source and test changes were read back from GitHub.
- **Execution status: NOT RUN**. Full Python CI, real-device import/export interoperability and measured peak RAM/disk I/O are **UNVERIFIED**. Prior shared fixture incompatibilities remain open. Run `pytest -q tests/test_project_bundle.py` before considering these changes runtime-verified.

## Screenshot provenance

The actual packaged Windows screenshot `VoiceBlueprint Pro-model-manager-win-x64.png` (1024×728, Settings → Models) is inside the `electron-rehearsal-win32-x64` artifact of [CI rehearsal #42426554733](https://github.com/DevTunaSoft/VoiceBlueprintPro/actions/runs/42426554733). It includes a loading placeholder. The [homepage image gallery](../../README.md#inside-the-studio) instead contains inherited demonstration screenshots. Neither is proof of real model inference. GitHub Actions artifacts are retained temporarily.

## Evidence standard

For each feature, record commit SHA, hardware/OS, test command and logs, screen or media proof, source and output integrity, permission/licensing constraints, accessibility review and remaining known defects. Only call something **real-platform-verified** after exercising it on representative hardware.

[Back to user manual](README.md) · [Documentation standard](DOCUMENTATION_STANDARD.md)
