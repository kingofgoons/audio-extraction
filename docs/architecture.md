# Architecture

## Overview

Audio Extraction CLI uses a 3-layer architecture that separates CLI concerns from business logic and external process management.

```
┌─────────────────────────────────────────────────┐
│              CLI Layer (cli.py)                   │
│  Click argument parsing, validation, output      │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│         Discovery + Orchestration                │
│  File discovery (discovery.py), format mapping   │
│  (formats.py), batch coordination (extractor.py) │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│            FFmpeg (subprocess)                    │
│  Audio stream extraction and transcoding         │
└─────────────────────────────────────────────────┘
```

## Data Flow

```
Input (file or dir)
       │
       ▼
┌─────────────────┐
│  Discover Files  │  discovery.py: Walk directory, filter by video extension
└────────┬────────┘
         │ List[Path]
         ▼
┌─────────────────┐
│  Validate Input  │  Check FFmpeg available, verify paths exist
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Map Format      │  formats.py: video ext → audio ext + codec
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extract (batch) │  extractor.py: For each file → subprocess.run(ffmpeg ...)
└────────┬────────┘  Uses ThreadPoolExecutor when --jobs > 1
         │
         ▼
┌─────────────────┐
│  Report Results  │  cli.py: Rich output — successes, failures, summary
└─────────────────┘
```

## Component Responsibilities

### `cli.py` — CLI Entry Point
- Defines Click commands and options
- Validates input paths and format choices using Click types
- Orchestrates the extraction flow
- Renders output with Rich (progress bars, tables, status)

### `extractor.py` — Extraction Engine
- `check_ffmpeg_available()` — verifies FFmpeg is on PATH
- `extract_audio()` — extracts audio from a single file via subprocess
- `extract_batch()` — processes a list of files with continue-on-error semantics

### `formats.py` — Format Mappings
- Maps supported video extensions to identification
- Maps output format names to FFmpeg codec arguments
- Provides validation sets for Click choices

### `discovery.py` — File Discovery and Helpers
- Directory walking with video extension filtering
- Output path construction (input stem + new extension)
- Recursive and flat directory scanning

## Error Handling Strategy

The tool uses a **continue-on-error** approach for batch processing:

1. **Pre-flight check** — If FFmpeg is not installed, exit immediately with code 1 and a clear message.
2. **Per-file errors** — If a single file fails (corrupt, unsupported codec, permission denied), log the error and continue to the next file.
3. **Summary report** — After all files are processed, print a summary showing successes and failures.
4. **Exit codes:**
   - `0` — All files extracted successfully (or no video files found)
   - `1` — FFmpeg not available, or any extraction failed

## Concurrency Model

Parallel extraction uses `concurrent.futures.ThreadPoolExecutor`:

- Controlled by the `--jobs` flag (default: 1 = sequential)
- Each thread invokes a separate FFmpeg subprocess
- Thread-safe because each extraction operates on independent files
- FFmpeg itself is CPU-intensive, so thread count should match available cores
- Results are collected and reported after all futures complete

## Format Support Matrix

| Output Format | FFmpeg Codec | FFmpeg Args |
|---------------|-------------|-------------|
| `mp3` | libmp3lame | `-acodec libmp3lame` |
| `wav` | pcm_s16le | `-acodec pcm_s16le` |
| `flac` | flac | `-acodec flac` |
| `aac` | aac | `-acodec aac` |
| `ogg` | libvorbis | `-acodec libvorbis` |

All extractions use `-vn` (no video). Optional `-b:a` for bitrate control.
