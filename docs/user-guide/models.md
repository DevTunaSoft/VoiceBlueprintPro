# Models and resources

**Reviewed:** November 7, 2026. **Verification:** Settings → Models and local-runtime readiness have automated packaged evidence; real model downloads, engine compatibility and actual generation remain unverified.

## Choose a model safely

1. Start the app with its local runtime ready.
2. Navigate to **Settings → Models**. This path is included in packaged Electron acceptance.
3. Review the categories offered by your build (including TTS, ASR, Dictation, Diarisation, Translation and LLM). A visible category is not proof a model is installed.
4. Select an appropriate engine only after checking the model's author, license, operating-system support, processor requirements, memory and available disk.
5. For your first run, prefer a lightweight CPU-compatible model if you do not have supported GPU acceleration.
6. Use a small authorized sample and verify that a valid output can actually be played or opened. These real audio checks are **not yet part of public release acceptance evidence**.

## Platform limits

- Windows x64 hosted CI chooses CPU PyTorch explicitly; this does not mean all user GPUs are certified.
- Windows ARM64 uses x64 Python 3.11 emulation with CPU PyTorch; AMD ROCm selection is unsupported.
- macOS and Linux engine availability differs by device, backend and available model wheels.
- Some models require multi-gigabyte downloads and more memory than the app shell itself.

## Common problems

**Model cannot download:** Check connectivity, free storage, compatible runtime and any model provider authorization. Save error messages before retrying.

**Model cannot load:** Record its ID, Python/torch variant, RAM or VRAM, operating system and full error. Do not swap random GPU wheel variants.

**Audio silent or distorted:** First confirm a generated output exists; test the output device and review the audio format before blaming model inference.

For additional technical context see the inherited [model download guide](../downloading-models.md), then [Troubleshooting](troubleshooting.md). It may still describe upstream installation options; those are not fork distribution channels.
