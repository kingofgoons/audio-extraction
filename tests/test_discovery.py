"""Tests for audio_extraction.discovery module.

Tests cover:
- discover_files() with single file input
- discover_files() with flat directory
- discover_files() ignoring non-video files
- discover_files() with empty directory
- discover_files() with recursive=True
- discover_files() with recursive=False (flat only)
- resolve_output_path() in same directory
- resolve_output_path() with custom output directory
- resolve_output_path() format extension handling
"""


import pytest

from audio_extraction.discovery import discover_files, resolve_output_path


class TestDiscoverSingleFile:
    """Verify discover_files() with file input."""

    def test_discover_single_file(self, tmp_dir):
        """File input returns [file] if it's a video."""
        video = tmp_dir / "movie.mp4"
        video.write_bytes(b"\x00" * 100)
        result = discover_files(video)
        assert result == [video]

    def test_discover_single_file_non_video(self, tmp_dir):
        """File input returns [] if it's not a video."""
        text_file = tmp_dir / "notes.txt"
        text_file.write_text("hello")
        result = discover_files(text_file)
        assert result == []


class TestDiscoverDirectory:
    """Verify discover_files() with directory input."""

    def test_discover_directory_flat(self, video_dir):
        """Finds video files in a flat directory."""
        result = discover_files(video_dir)
        assert len(result) == 5  # movie.mp4, clip.avi, recording.mkv, show.mov, stream.webm
        assert all(f.is_file() for f in result)

    def test_discover_directory_ignores_non_video(self, tmp_dir):
        """Skips non-video files (.txt, .jpg, .pdf)."""
        (tmp_dir / "movie.mp4").write_bytes(b"\x00" * 100)
        (tmp_dir / "notes.txt").write_text("text")
        (tmp_dir / "photo.jpg").write_bytes(b"\x00" * 50)
        (tmp_dir / "report.pdf").write_bytes(b"\x00" * 50)

        result = discover_files(tmp_dir)
        assert len(result) == 1
        assert result[0].name == "movie.mp4"

    def test_discover_directory_empty(self, tmp_dir):
        """Returns empty list for empty directory."""
        result = discover_files(tmp_dir)
        assert result == []

    def test_discover_directory_no_videos(self, tmp_dir):
        """Returns empty list when directory has no video files."""
        (tmp_dir / "song.mp3").write_bytes(b"\x00" * 100)
        (tmp_dir / "readme.md").write_text("# Hello")
        result = discover_files(tmp_dir)
        assert result == []


class TestDiscoverRecursive:
    """Verify recursive vs non-recursive discovery."""

    def test_discover_recursive(self, nested_video_dir):
        """Finds files in subdirectories when recursive=True."""
        result = discover_files(nested_video_dir, recursive=True)
        # root_video.mp4, season1/episode1.mp4, season1/episode2.avi, extras/behind_scenes.mkv
        assert len(result) == 4
        names = {f.name for f in result}
        assert "root_video.mp4" in names
        assert "episode1.mp4" in names
        assert "episode2.avi" in names
        assert "behind_scenes.mkv" in names

    def test_discover_non_recursive_flat(self, nested_video_dir):
        """Does not descend into subdirectories when recursive=False."""
        result = discover_files(nested_video_dir, recursive=False)
        # Only root_video.mp4 at the top level
        assert len(result) == 1
        assert result[0].name == "root_video.mp4"


class TestResolveOutputPath:
    """Verify resolve_output_path() behavior."""

    def test_resolve_output_path_same_dir(self, tmp_dir):
        """When output_dir is None, output goes alongside input."""
        input_file = tmp_dir / "movie.mp4"
        result = resolve_output_path(input_file, output_dir=None, format="mp3")
        assert result == tmp_dir / "movie.mp3"
        assert result.parent == input_file.parent

    def test_resolve_output_path_custom_dir(self, tmp_dir):
        """When output_dir is specified, output goes there."""
        input_file = tmp_dir / "movie.mp4"
        output_dir = tmp_dir / "audio"
        result = resolve_output_path(input_file, output_dir=output_dir, format="mp3")
        assert result == output_dir / "movie.mp3"
        assert result.parent == output_dir

    @pytest.mark.parametrize(
        "fmt,expected_ext",
        [
            ("mp3", ".mp3"),
            ("wav", ".wav"),
            ("flac", ".flac"),
            ("aac", ".aac"),
            ("ogg", ".ogg"),
        ],
    )
    def test_resolve_output_path_format_extension(self, tmp_dir, fmt, expected_ext):
        """Output file gets correct extension per format."""
        input_file = tmp_dir / "video.mp4"
        result = resolve_output_path(input_file, output_dir=None, format=fmt)
        assert result.suffix == expected_ext
        assert result.stem == "video"
