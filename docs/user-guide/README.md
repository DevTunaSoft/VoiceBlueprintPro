# VoiceBlueprint Pro — Beginner's User Manual

**Reviewed:** November 7, 2026 · **Status:** Living fork-specific guide. Automated packaging is tested; real-user-machine acceptance is not complete.

VoiceBlueprint Pro is an independent modernization fork of [VoiceBlueprint](https://github.com/DevTunaSoft/VoiceBlueprint-Pro). The desktop app processes audio with local runtimes and installed models. During migration, its executable and some screens still use the **VoiceBlueprint** name.

## Start here: Seven steps to start

1. **Use a fork-owned build.** No stable VoiceBlueprint Pro release is published. For experimental builds, use the [installer guide](installation.md) and inspect the individual GitHub Actions packaging job for your operating system.
2. **Save your existing work.** Back up recordings, scripts, projects and model data. Do not replace an existing upstream installation.
3. **Choose storage.** The local runtime and models can require substantial disk space. Record the destination before installation.
4. **Install the local runtime.** The first-run screen offers **Install local runtime** on supported platforms. The packaged acceptance test verifies that visiting setup or changing location alone does not install anything.
5. **Open Settings → Models.** Review speech, transcription and related model categories. A category tile does not prove a model has been downloaded.
6. **Try authorized audio.** After installing a compatible licensed engine, start with a short recording or script and inspect the result. Real speech generation and hardware audio remain unverified on users' devices.
7. **Preserve evidence of problems.** Use [Troubleshooting and recovery](troubleshooting.md) before changing runtime directories or reinstalling.

## Manual chapters

| Task | Page | Evidence level |
| --- | --- | --- |
| Download and run an experimental package | [Installation and first run](installation.md) | Automated CI setup tests, not real-device acceptance |
| Understand CPU, GPU and model requirements | [Models and resources](models.md) | Settings route tested; real model inference pending |
| Clone, synthesize, transcribe or dub | [Voice and audio workflows](workflows.md) | Preliminary inherited workflow documentation |
| Investigate startup or audio failures | [Troubleshooting and recovery](troubleshooting.md) | Source-inspected diagnostics and safe recovery guidance |
| See exactly what passed | [Feature verification ledger](feature-verification.md) | Specific run IDs, limitations and missing acceptance |

## Visual guide and evidence

The [GitHub homepage GUI gallery](../../README.md#inside-the-studio) shows existing Electron-renderer screenshots inherited by the fork. An independent **actual packaged Windows x64 Settings → Models screenshot**, 1024×728, was captured in [Actions run #42426554733](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/actions/runs/42426554733), under `electron-rehearsal-win32-x64`. It shows a loading placeholder, not a successfully downloaded model. The artifact may expire.

## Terms and privacy

A **runtime** is the Python software environment that runs compatible models. A **model** is a set of trained files used for a speech task. **Inference** is processing text or audio with a model. **VRAM** is graphics-card memory. **Reference audio** is a voice recording used to guide generation; use it only with permission.

Keep private recordings and diagnostic exports confidential. Confirm model-specific licenses separately from the app's AGPL license. Remote services may send data off the device. A functioning window or successful CI test is not proof of microphone input, speaker output or real speech-generation quality.

## Support and status

GitHub Issues and Discussions are **currently disabled** for this fork, so inherited bug-report buttons may lead to non-working destinations. Preserve diagnostic bundles for a verified maintainer channel; submit source fixes through [pull requests](https://github.com/DevTunaSoft/VoiceBlueprint-Pro/pulls). Vulnerabilities require the [private security reporting policy](../../.github/SECURITY.md).

Every changed feature must update this manual and the [documentation quality standard](DOCUMENTATION_STANDARD.md) with reproducible evidence. No invented UI controls, performance claims or fake screenshots.

## Documentation acceptance rule

A user-facing feature is not documented as released until its exact UI controls, prerequisites, expected output, failure recovery, accessibility and privacy behavior have reproducible test evidence on the applicable hardware. The [verification ledger](feature-verification.md) records remaining gaps; incomplete areas stay explicitly marked unverified.
