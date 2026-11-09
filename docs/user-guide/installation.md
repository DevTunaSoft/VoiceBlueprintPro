# Installation and first run

**Reviewed:** November 7, 2026. **Evidence:** Automated packaged setup passed; real-device installation, upgrade, signing and real-model generation remain unverified.

## Before installing

1. Preserve copies of existing projects, voice samples, model settings and audio. Do not overwrite an upstream VoiceBlueprint installation with an experimental fork build.
2. Check your device's platform and CPU architecture. Most Windows Intel/AMD machines are **x64**; Snapdragon Windows machines are **ARM64**.
3. Plan for substantial free storage for Python, the app and models. The inherited [Windows hardware reference](../install/windows.md) suggests roughly 10 GB as a starting point; larger models need more.
4. Expect development installers to be unsigned. Do not disable operating-system protection merely to launch a test build.

## Experimental Windows setup

1. Open the [VoiceBlueprint Pro Electron packaging workflow](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/workflows/electron-build.yml) and select a completed rehearsal.
2. Verify the *individual package job* for Windows x64 or ARM64 passed; do not infer success from an overall workflow badge.
3. Under **Artifacts**, download `electron-rehearsal-win32-x64` for Intel/AMD or `electron-rehearsal-win32-arm64` for a Windows ARM64 device. GitHub sign-in may be required. Artifacts expire.
4. Extract the ZIP and inspect the installer. During migration, its filename is still `VoiceBlueprint-*-win-x64.exe` or `VoiceBlueprint-*-win-arm64.exe`. Only run software you trust.
5. Follow installation prompts and review the local runtime destination. The first-run **Install local runtime** action installs only after a user action; the destination picker by itself does not begin setup.
6. After the runtime is ready, open **Settings → Models**. Review licenses, resource needs and compatibility before downloading a model.
7. Test one small, authorized audio task and verify file playback and export on your own hardware. **Real-device voice/audio acceptance has not yet been demonstrated.**

[Packaging evidence #42426554733](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42426554733) covers five package jobs: Windows x64, experimental Windows ARM64, Linux x64, macOS Intel and macOS Apple Silicon. CI includes an isolated Windows managed-runtime setup.

## Special cases

**Windows ARM64:** Native ARM64 Electron shell, but emulated x64 Python 3.11 with CPU PyTorch. AMD ROCm is unsupported. CI packaging passed; real Snapdragon-device installation/performance is not yet verified.

**macOS Intel:** Its packaged first-run checks use a different local-runtime support route from Apple Silicon. Do not assume a native managed local inference environment is offered. Linux and macOS distribution and permissions need separate device-level verification.

## After first launch

Check the app window and version; some inherited visible branding may still read VoiceBlueprint. Confirm selected storage locations, model readiness, audio devices and network configuration. A green automated smoke test is not proof of a real voice-generated output.

## Updates and uninstall

Real-device update rollback, app-ID migration, preservation of project files and uninstall behavior are **not verified**. Do not delete a runtime, cache or project folder to force a repair. Keep independent backups and record errors before retrying.

[Back to user manual](README.md) · [Models](models.md) · [Troubleshooting](troubleshooting.md)
