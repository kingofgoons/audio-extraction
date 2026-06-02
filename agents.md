# agents.md — Audio Extraction CLI

**Read this file at the start of every session before doing anything else.**

---

## PROJECT

A **CLI tool for extracting audio tracks from video files** using FFmpeg. Supports batch processing of directories, multiple output formats, parallel extraction via thread pools, and rich terminal output.

**Tech stack:** Python 3.10+, Click (CLI framework), Rich (terminal output), FFmpeg (subprocess).

---

## FOLDER LAYOUT

```
audio-extraction/
├── agents.md                      ← THIS FILE (read at session start)
├── README.md                      ← Project overview + quick start
├── pyproject.toml                 ← Project metadata, dependencies, entry point
├── Makefile                       ← Dev commands: install, test, lint, clean
├── .gitignore                     ← Python standard + IDE files
├── src/
│   └── audio_extraction/
│       ├── __init__.py            ← Package version
│       ├── __main__.py            ← `python -m audio_extraction` support
│       ├── cli.py                 ← Click CLI entry point
│       ├── extractor.py           ← Core extraction logic (FFmpeg wrapper)
│       ├── formats.py             ← Supported format mappings
│       └── discovery.py           ← File discovery, validation helpers
├── tests/
│   ├── conftest.py                ← Shared fixtures (temp dirs, mock video files)
│   ├── test_cli.py                ← CLI integration tests
│   ├── test_extractor.py          ← Unit tests for extraction logic
│   ├── test_formats.py            ← Format mapping tests
│   └── test_discovery.py          ← File discovery tests
└── docs/
    ├── architecture.md            ← System design + data flow
    └── setup-guide.md             ← Installation and usage guide
```

---

## KEY RULES

1. **Always use subprocess for FFmpeg calls.** Never use Python FFmpeg bindings (like `ffmpeg-python`). The `subprocess.run` approach keeps dependencies minimal and gives full control over the FFmpeg command line.

2. **Continue-on-error for batch processing.** A failure on one file must not stop processing of remaining files. Collect errors and report a summary at the end.

3. **All CLI options validated via Click types/choices.** Use `click.Choice` for format selection, `click.Path(exists=True)` for inputs. Never validate manually what Click can validate declaratively.

4. **Tests must cover all output formats parametrically.** Use `@pytest.mark.parametrize` to test extraction across mp3, wav, flac, aac, ogg — not individual test methods per format.

5. **No hardcoded paths.** Use Click defaults and `pathlib.Path` types. The default input should come from Click's default mechanism, not string literals in business logic.

6. **FFmpeg must be checked for availability before extraction.** Run `ffmpeg -version` at startup. If unavailable, exit with a clear error message — don't let the first extraction attempt fail cryptically.

---

## HOW TO RUN

### Install (development mode)
```bash
make dev
```

### Basic usage
```bash
audio-extraction --help
audio-extraction ~/Movies                       # Extract all videos to mp3
audio-extraction ~/Movies -f wav -o ~/Audio     # Extract as WAV to specific dir
audio-extraction video.mp4 --dry-run            # Preview without extracting
```

### Run tests
```bash
make test
```

### Run linter
```bash
make lint
```

---

## AVAILABLE SKILLS

Use the `skill` tool to invoke these when working on this project:

| Skill | When to use |
|---|---|
| `cortex-code-guide` | Understanding Cortex Code features, commands, and configuration |
| `code-quality-check` | Running security scans, linting, type checking before PRs |
| `skill-development` | Creating new skills or capturing session workflows |
