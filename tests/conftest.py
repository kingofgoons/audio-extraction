"""Shared test fixtures for audio-extraction tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def video_dir(tmp_dir):
    """Create a directory with multiple fake video files (flat)."""
    for name in ["movie.mp4", "clip.avi", "recording.mkv", "show.mov", "stream.webm"]:
        (tmp_dir / name).write_bytes(b"\x00" * 512)
    return tmp_dir


@pytest.fixture
def nested_video_dir(tmp_dir):
    """Create a directory with subdirectories containing video files."""
    # Root level
    (tmp_dir / "root_video.mp4").write_bytes(b"\x00" * 512)

    # Subdirectory 1
    sub1 = tmp_dir / "season1"
    sub1.mkdir()
    (sub1 / "episode1.mp4").write_bytes(b"\x00" * 512)
    (sub1 / "episode2.avi").write_bytes(b"\x00" * 512)

    # Subdirectory 2 (nested deeper)
    sub2 = sub1 / "extras"
    sub2.mkdir()
    (sub2 / "behind_scenes.mkv").write_bytes(b"\x00" * 512)

    # Non-video files to ensure they're ignored
    (tmp_dir / "readme.txt").write_text("not a video")
    (sub1 / "thumbnail.jpg").write_bytes(b"\x00" * 100)

    return tmp_dir
