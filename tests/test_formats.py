"""Tests for audio_extraction.formats module.

Tests cover:
- VIDEO_EXTENSIONS contains common video formats
- AUDIO_FORMATS mapping correctness
- CODEC_MAP completeness (every audio format has a codec)
- is_video_file() for video/non-video extensions
- Case insensitivity of is_video_file()
"""

from pathlib import Path

import pytest

from audio_extraction.formats import (
    AUDIO_FORMATS,
    CODEC_MAP,
    VIDEO_EXTENSIONS,
    is_video_file,
)


class TestVideoExtensions:
    """Verify VIDEO_EXTENSIONS set is correct."""

    @pytest.mark.parametrize("ext", [".mp4", ".avi", ".mkv", ".mov", ".webm"])
    def test_video_extensions_contains_common(self, ext):
        """Common video extensions must be in the set."""
        assert ext in VIDEO_EXTENSIONS


class TestAudioFormats:
    """Verify AUDIO_FORMATS mapping."""

    @pytest.mark.parametrize(
        "fmt,ext",
        [
            ("mp3", ".mp3"),
            ("wav", ".wav"),
            ("flac", ".flac"),
            ("aac", ".aac"),
            ("ogg", ".ogg"),
        ],
    )
    def test_audio_formats_mapping(self, fmt, ext):
        """Each format maps to correct file extension."""
        assert AUDIO_FORMATS[fmt] == ext


class TestCodecMap:
    """Verify CODEC_MAP completeness."""

    def test_codec_map_complete(self):
        """Every audio format must have a corresponding codec entry."""
        for fmt in AUDIO_FORMATS:
            assert fmt in CODEC_MAP, f"Missing codec for format: {fmt}"
            assert isinstance(CODEC_MAP[fmt], str)
            assert len(CODEC_MAP[fmt]) > 0

    @pytest.mark.parametrize(
        "fmt,codec",
        [
            ("mp3", "libmp3lame"),
            ("wav", "pcm_s16le"),
            ("flac", "flac"),
            ("aac", "aac"),
            ("ogg", "libvorbis"),
        ],
    )
    def test_codec_map_values(self, fmt, codec):
        """Verify specific codec assignments."""
        assert CODEC_MAP[fmt] == codec


class TestIsVideoFile:
    """Verify is_video_file() function."""

    @pytest.mark.parametrize("name", [
        "movie.mp4", "clip.avi", "show.mkv", "film.mov", "stream.webm",
        "broadcast.flv", "windows.wmv", "apple.m4v",
    ])
    def test_is_video_file_true(self, name):
        """Returns True for recognized video extensions."""
        assert is_video_file(Path(name)) is True

    @pytest.mark.parametrize("name", [
        "song.mp3", "image.jpg", "document.pdf", "data.csv",
        "archive.zip", "script.py", "readme.txt",
    ])
    def test_is_video_file_false(self, name):
        """Returns False for non-video extensions."""
        assert is_video_file(Path(name)) is False

    @pytest.mark.parametrize("name", [
        "VIDEO.MP4", "Clip.Mkv", "SHOW.AVI", "movie.Mp4", "stream.WEBM",
    ])
    def test_is_video_file_case_insensitive(self, name):
        """Extension matching is case-insensitive."""
        assert is_video_file(Path(name)) is True
