# User-facing feature verification ledger

**Reviewed:** November 7, 2026. **Evidence baseline:** Full CI `af3f97d8` passed. Later changes require their own CI; "automated" is not "release verified."

| Feature | Functional verification | Required evidence / remaining real-device validation |
| --- | --- | --- |
| Windows x64 package and CPU runtime | [Packaging #42426554733](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42426554733): installer, startup, managed backend | User PC installation and uninstall, speech, microphone, speakers, GPU |
| Windows ARM64 packaging | Same run: native shell plus emulated x64 Python/CPU runtime passed | Real Snapdragon device, sustained performance, audio |
| Linux x64 / macOS Intel / Apple Silicon packaging | Same run: platform matrix passed | OS permissions, real hardware, inference and updates |
| Electron desktop Settings → Models | Same run captured a real packaged screenshot (1024×728) and navigated to model manager | Actual model download and fully loaded interface |
| Electron UI and test matrix | [Full CI #42439650200](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42439650200) passed UI crawlers, renderer, integration and smoke checks | Keyboard/screen-reader audit, all production workflows |
| Queue shutdown and cancellation | Same CI passed Python queue regression tests | Power-loss recovery, persisted job resume, latest fuzz rounds |
| Voice cloning, speech, transcription, dubbing | Source and inherited documentation exist | Real model download, generated output, human quality review |
| Project save/export and backup | Inherited implementations and source-level inspection | Interrupted writes, preservation after crash and restore on users' devices |
| Settings, diagnostics and support | Source-inspected About controls; desktop UI suite passed | Real diagnostic export and supported bug intake; GitHub Issues disabled |
| Upgrade, rollback, uninstall | Installer/update contract tests | Signing, migration, uninstall and rollback verification |

## Screenshot provenance

The actual packaged Windows screenshot `VoiceBlueprint Pro-model-manager-win-x64.png` (1024×728, Settings → Models) is inside the `electron-rehearsal-win32-x64` artifact of [CI rehearsal #42426554733](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42426554733). It includes a loading placeholder. The [homepage image gallery](../../README.md#inside-the-studio) instead contains inherited demonstration screenshots. Neither is proof of real model inference. GitHub Actions artifacts are retained temporarily.

## Evidence standard

For each feature, record commit SHA, hardware/OS, test command and logs, screen or media proof, source and output integrity, permission/licensing constraints, accessibility review and remaining known defects. Only call something **real-platform-verified** after exercising it on representative hardware.

[Back to user manual](README.md) · [Documentation standard](DOCUMENTATION_STANDARD.md)
