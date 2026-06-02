# Audio Extraction CLI

Extract audio tracks from video files using FFmpeg — fast, simple, and batch-friendly.

## Features

- **Batch processing** — Point at a directory to extract audio from all video files
- **Multiple output formats** — MP3, WAV, FLAC, AAC, OGG
- **Parallel extraction** — Process multiple files concurrently with `--jobs`
- **Dry-run mode** — Preview what would be extracted without doing it
- **Continue on error** — One failed file doesn't stop the batch
- **Rich output** — Progress bars and colored terminal output
- **Overwrite control** — Skip existing files or force re-extraction

## Quick Start

### Prerequisites

- **Python 3.10+**
- **FFmpeg** — must be available on your PATH

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

### Install

```bash
git clone <repo-url>
cd audio-extraction
make dev
```

### Basic Usage

```bash
# Extract audio from all videos in a directory (default: mp3)
audio-extraction ~/Movies

# Extract as WAV to a specific output directory
audio-extraction ~/Movies --format wav --output ~/Audio

# Process a single file
audio-extraction video.mp4

# Preview without extracting
audio-extraction ~/Movies --dry-run
```

## CLI Usage

```
audio-extraction [OPTIONS] [INPUT]

Arguments:
  INPUT                    Video file or directory [default: current directory]

Options:
  -o, --output DIR         Output directory [default: same as input]
  -f, --format FORMAT      Audio format: mp3, wav, flac, aac, ogg [default: mp3]
  -b, --bitrate RATE       Audio bitrate (e.g. 192k, 320k)
  -j, --jobs N             Number of parallel extractions [default: 1]
  -r, --recursive          Recursively scan subdirectories
      --overwrite          Overwrite existing output files
      --dry-run            Show what would be extracted without doing it
  -v, --verbose            Verbose output (show FFmpeg commands)
      --help               Show this message and exit
```

## Supported Formats

### Input (video)

| Extension | Format |
|-----------|--------|
| `.mp4`    | MPEG-4 |
| `.avi`    | AVI    |
| `.mkv`    | Matroska |
| `.mov`    | QuickTime |
| `.webm`   | WebM   |
| `.flv`    | Flash Video |
| `.wmv`    | Windows Media |
| `.m4v`    | MPEG-4 Video |
| `.ts`     | MPEG Transport Stream |
| `.mts`    | AVCHD |

### Output (audio)

| Extension | Format | Codec |
|-----------|--------|-------|
| `.mp3`    | MP3    | libmp3lame |
| `.wav`    | WAV    | pcm_s16le |
| `.flac`   | FLAC   | flac |
| `.aac`    | AAC    | aac |
| `.ogg`    | OGG    | libvorbis |

## Examples

```bash
# Extract all MP4 files from Downloads as FLAC
audio-extraction ~/Downloads --format flac

# Parallel extraction with 4 workers
audio-extraction ~/Movies --jobs 4

# Overwrite existing audio files
audio-extraction ~/Movies --overwrite

# Verbose mode to see FFmpeg commands
audio-extraction video.mp4 --verbose
```

## Development

```bash
# Install in development mode with test dependencies
make dev

# Run tests
make test

# Run linter
make lint

# Clean build artifacts
make clean
```
