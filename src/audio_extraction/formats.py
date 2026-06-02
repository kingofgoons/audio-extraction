"""Format definitions for video input and audio output."""

from pathlib import Path

# Supported video input file extensions
VIDEO_EXTENSIONS: set[str] = {
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".webm",
    ".flv",
    ".wmv",
    ".m4v",
    ".ts",
    ".mts",
}

# Mapping from output format name to file extension
AUDIO_FORMATS: dict[str, str] = {
    "mp3": ".mp3",
    "wav": ".wav",
    "flac": ".flac",
    "aac": ".aac",
    "ogg": ".ogg",
}

# Mapping from output format name to FFmpeg codec
CODEC_MAP: dict[str, str] = {
    "mp3": "libmp3lame",
    "wav": "pcm_s16le",
    "flac": "flac",
    "aac": "aac",
    "ogg": "libvorbis",
}


def is_video_file(path: Path) -> bool:
    """Check if a file has a recognized video extension."""
    return path.suffix.lower() in VIDEO_EXTENSIONS
