# Troubleshooting and recovery

**Reviewed:** November 7, 2026. **Status:** Practical safe diagnostics; target-hardware fixes and migration recovery remain unverified.

## App stuck during startup

1. **Preserve files**: do not delete projects, models, cache or runtime directories.
2. Record the exact stage/error, app version, OS architecture and available disk space.
3. On Windows ARM64, confirm you are using a supported ARM64 shell with x64 Python CPU emulation; the AMD ROCm runtime is not supported there.
4. Confirm the local runtime destination before choosing **Install local runtime**. CI verifies that merely opening setup or choosing another folder does not trigger installation.
5. If retrying fails, preserve diagnostics; do not blindly remove Python/torch packages.

## Model or audio failure

1. Check **Settings → Models** for available engine categories and readiness; a tile by itself is not a complete model download.
2. Record model ID, storage, RAM/VRAM, the CPU/GPU runtime choice and any backend error.
3. For silence, confirm whether the app produced an output file, then check Windows/macOS/Linux output routing and system mute state.
4. Try a short non-sensitive test project if it is safe; avoid repeatedly submitting long jobs or deleting user data.
5. Keep copied logs private until you have reviewed them for credentials and personal information.

## Diagnostics and reporting

The inherited **Settings → About** source includes **Run self-check**, **Save Diagnostic Bundle** and **Copy Diagnostics** actions. These controls are source-inspected; full platform support must still be verified. Include precise reproduction steps and non-sensitive error messages; sanitize home paths, voice content and tokens before sharing.

GitHub Issues and Discussions are **disabled** for this fork. Do not rely on existing app buttons that navigate to dead Issues URLs. Code fixes may be submitted through [pull requests](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/pulls); vulnerabilities belong in the [private security reporting workflow](../../.github/SECURITY.md).

## Evidence and release caveats

- [Full CI #42439650200](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42439650200) passed Python, Electron, desktop UI, renderer, installer contracts and all four platform smoke jobs.
- [Packaging #42426554733](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42426554733) passed the five-platform package matrix and Windows local-runtime setup, including experimental Windows ARM64.
- The packaged Windows x64 Settings → Models screenshot still contained a loading placeholder. It verifies a real renderer route, **not** a working speech model.
- Real device installation/upgrade, GPU inference, project save/recovery, microphone and playback are still unverified.

[Back to user manual](README.md) · [Installation](installation.md) · [Feature verification ledger](feature-verification.md)
