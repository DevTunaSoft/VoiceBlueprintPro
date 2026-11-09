# Voice and audio workflows

**Reviewed:** November 7, 2026. **Status:** Preliminary inherited workflows; real-generation, real transcription, microphone input, speaker playback, output quality and file export require target-device testing.

## Voice cloning and generation

1. Obtain clear authorization for every voice recording and preserve the original.
2. Complete [local runtime setup](installation.md) and choose a compatible, licensed model in [Models](models.md).
3. Open the voice-cloning or voice-design workspace available in your build. Layouts and engine settings may vary.
4. Enter a short script and provide reference audio only when the chosen engine supports or requires it.
5. Generate a small sample. Validate pronunciation, intelligibility, pauses, clipping, noise and actual playback rather than trusting only a completion message.
6. Export only after confirming file integrity and your license/consent rights.

## Transcription and dubbing

1. Choose the transcription, dictation or dubbing workflow supported by your installed engines.
2. Use authorized input audio/video and keep the source copy unchanged.
3. Configure only the language, alignment or speaker options available in your build.
4. Manually review text accuracy, speaker labels, timing, sync and final exports. Automated text is not guaranteed accurate.
5. If a job fails, save diagnostics and original media before retrying.

## Long-form projects and recovery

The inherited code includes queue controls and project workflows. The modernized job-queue shutdown/restart paths have automated cancellation and race regression tests, **not** proof of resuming a partially generated audiobook after power loss. Keep versioned project copies and input media backups for longer work. Avoid destructive cleanup or a forced reinstall when a job hangs.

See existing [audio-quality](../audio-quality.md), [transcription](../electron-transcriptions.md) and [dubbing](../electron-dubbing.md) technical guides; their UI claims must be checked against this fork.

[Back to user manual](README.md) · [Feature verification ledger](feature-verification.md)
