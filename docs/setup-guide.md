# Setup Guide

## Prerequisites

### Python 3.10+

Verify your Python version:

```bash
python3 --version
```

If you need to install or upgrade, use your system's package manager or [pyenv](https://github.com/pyenv/pyenv).

### FFmpeg

FFmpeg must be available on your system PATH.

#### macOS (Homebrew)

```bash
brew install ffmpeg
```

#### Ubuntu / Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows (Chocolatey)

```bash
choco install ffmpeg
```

#### Verify Installation

```bash
ffmpeg -version
```

You should see version information and a list of supported codecs. The tool requires FFmpeg 4.0+.

## Installation

### Clone the Repository

```bash
git clone <repo-url>
cd audio-extraction
```

### Install in Development Mode

```bash
make dev
```

This installs the package in editable mode with all development dependencies (pytest, ruff, etc.).

Alternatively, install manually:

```bash
pip install -e ".[dev]"
```

### Verify Installation

```bash
audio-extraction --help
```

You should see the full CLI help output with all available options.

## Usage Examples

### Basic Extraction

Extract audio from all video files in a directory:

```bash
audio-extraction ~/Movies
```

This produces `.mp3` files alongside the original videos.

### Specify Output Format

```bash
audio-extraction ~/Movies --format wav
audio-extraction ~/Movies --format flac
audio-extraction ~/Movies --format aac
```

### Specify Output Directory

```bash
audio-extraction ~/Movies --output ~/Audio
```

All extracted audio files are written to `~/Audio`.

### Process a Single File

```bash
audio-extraction video.mp4
audio-extraction recording.mkv --format wav --output ~/Desktop
```

### Parallel Extraction

Process multiple files concurrently:

```bash
audio-extraction ~/Movies --jobs 4
```

### Dry Run (Preview)

See what would be extracted without doing it:

```bash
audio-extraction ~/Movies --dry-run
```

### Overwrite Existing Files

By default, existing output files are skipped. To re-extract:

```bash
audio-extraction ~/Movies --overwrite
```

### Verbose Mode

See the FFmpeg commands being executed:

```bash
audio-extraction ~/Movies --verbose
```

## Troubleshooting

### "FFmpeg not found"

The tool checks for FFmpeg at startup. If you see this error:

1. Verify FFmpeg is installed: `ffmpeg -version`
2. Ensure it's on your PATH: `which ffmpeg` (macOS/Linux) or `where ffmpeg` (Windows)
3. If installed via a non-standard path, add it to your PATH environment variable

### "No video files found"

The tool looks for files with these extensions: `.mp4`, `.avi`, `.mkv`, `.mov`, `.webm`, `.flv`, `.wmv`, `.m4v`, `.ts`, `.mts`

- Check that your input path contains video files with supported extensions
- Use `--verbose` to see which directory is being scanned

### "Permission denied"

- Check file permissions on the input video files
- Ensure you have write access to the output directory
- On macOS, grant Terminal access to the folder in System Settings > Privacy & Security

### Extraction produces empty or corrupt files

- The input video may not contain an audio stream — check with `ffprobe <file>`
- The file may be corrupt — try playing it with a media player first
- Use `--verbose` to see the FFmpeg command and run it manually for detailed error output

### High memory usage with large batches

- Reduce `--jobs` to limit parallel FFmpeg processes
- FFmpeg subprocesses inherit memory pressure — fewer parallel jobs = lower peak RAM
