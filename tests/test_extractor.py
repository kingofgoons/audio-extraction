"""Tests for audio_extraction.extractor (FFmpeg wrapper logic).

Tests cover:
- FFmpeg availability check (check_ffmpeg_available)
- Single file extraction command building (parametrized by format)
- Codec mapping verification (parametrized by format)
- Bitrate flag handling (parametrized by bitrate value)
- Success/failure return values
- Batch processing: sequential, parallel, skip existing, overwrite, continue-on-error
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from audio_extraction.extractor import (
    check_ffmpeg_available,
    extract_audio,
    extract_batch,
)
from audio_extraction.formats import CODEC_MAP


class TestCheckFFmpegAvailable:
    """Verify detection of FFmpeg installation."""

    def test_check_ffmpeg_available(self):
        """Returns True when ffmpeg subprocess succeeds."""
        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert check_ffmpeg_available() is True

    def test_check_ffmpeg_missing(self):
        """Returns False when ffmpeg raises FileNotFoundError."""
        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("ffmpeg not found")
            assert check_ffmpeg_available() is False


class TestExtractAudioCommand:
    """Verify FFmpeg command construction for each format."""

    @pytest.mark.parametrize("fmt", ["mp3", "wav", "flac", "aac", "ogg"])
    def test_extract_audio_builds_correct_command(self, fmt, tmp_dir):
        """Verify FFmpeg command is built correctly for each format."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format=fmt,
            )

            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "ffmpeg"
            assert "-i" in cmd
            assert str(input_file) in cmd
            # Output file should have the correct extension
            expected_output = str(output_dir / f"video.{fmt}")
            assert expected_output in cmd

    @pytest.mark.parametrize("fmt", ["mp3", "wav", "flac", "aac", "ogg"])
    def test_extract_audio_uses_correct_codec(self, fmt, tmp_dir):
        """Verify correct codec is specified via -acodec for each format."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format=fmt,
            )

            cmd = mock_run.call_args[0][0]
            expected_codec = CODEC_MAP[fmt]
            # The codec should appear after -acodec flag
            acodec_idx = cmd.index("-acodec")
            assert cmd[acodec_idx + 1] == expected_codec


class TestExtractAudioBitrate:
    """Verify bitrate flag handling."""

    @pytest.mark.parametrize("bitrate", ["128k", "192k", "320k"])
    def test_extract_audio_bitrate_included(self, bitrate, tmp_dir):
        """When bitrate is specified, -b:a flag should be in the command."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format="mp3",
                bitrate=bitrate,
            )

            cmd = mock_run.call_args[0][0]
            assert "-b:a" in cmd
            ba_idx = cmd.index("-b:a")
            assert cmd[ba_idx + 1] == bitrate

    def test_extract_audio_bitrate_none_excluded(self, tmp_dir):
        """When bitrate is None, -b:a flag should not appear."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format="mp3",
                bitrate=None,
            )

            cmd = mock_run.call_args[0][0]
            assert "-b:a" not in cmd


class TestExtractAudioResult:
    """Verify return values for success/failure."""

    def test_extract_audio_success(self, tmp_dir):
        """Returns the output Path on successful extraction."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format="mp3",
            )

            assert isinstance(result, Path)
            assert result.suffix == ".mp3"
            assert result.stem == "video"

    def test_extract_audio_failure(self, tmp_dir):
        """Raises RuntimeError on FFmpeg failure."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="codec not supported"
            )
            with pytest.raises(RuntimeError, match="FFmpeg failed"):
                extract_audio(
                    input_file=input_file,
                    output_dir=output_dir,
                    format="mp3",
                )


class TestExtractAudioSkipExisting:
    """Verify skip/overwrite behavior for existing output files."""

    def test_skip_existing_no_overwrite(self, tmp_dir):
        """Skips extraction when output exists and overwrite=False."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()
        # Pre-create the output file
        existing = output_dir / "video.mp3"
        existing.write_bytes(b"fake audio data")

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            result = extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format="mp3",
                overwrite=False,
            )
            # Should NOT call FFmpeg
            mock_run.assert_not_called()
            # Should return the existing path
            assert result == existing

    def test_overwrite_existing(self, tmp_dir):
        """Calls FFmpeg when output exists and overwrite=True."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)
        output_dir = tmp_dir / "out"
        output_dir.mkdir()
        # Pre-create the output file
        existing = output_dir / "video.mp3"
        existing.write_bytes(b"fake audio data")

        with patch("audio_extraction.extractor.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format="mp3",
                overwrite=True,
            )

            # FFmpeg SHOULD be called
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            # -y flag should be present for overwrite
            assert "-y" in cmd


class TestExtractBatch:
    """Verify batch processing behavior."""

    def test_extract_batch_sequential(self, tmp_dir):
        """jobs=1 processes files sequentially."""
        files = []
        for name in ["a.mp4", "b.avi", "c.mkv"]:
            f = tmp_dir / name
            f.write_bytes(b"\x00" * 100)
            files.append(f)

        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.extract_audio") as mock_extract:
            mock_extract.return_value = output_dir / "a.mp3"
            results = extract_batch(
                input_files=files,
                output_dir=output_dir,
                format="mp3",
                jobs=1,
            )
            assert mock_extract.call_count == 3
            assert len(results) == 3
            assert all(r["success"] for r in results)

    def test_extract_batch_parallel(self, tmp_dir):
        """jobs>1 uses ThreadPoolExecutor for parallel processing."""
        files = []
        for name in ["a.mp4", "b.avi", "c.mkv"]:
            f = tmp_dir / name
            f.write_bytes(b"\x00" * 100)
            files.append(f)

        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.extract_audio") as mock_extract:
            mock_extract.return_value = output_dir / "a.mp3"
            results = extract_batch(
                input_files=files,
                output_dir=output_dir,
                format="mp3",
                jobs=4,
            )
            # Should still process all files
            assert mock_extract.call_count == 3
            assert len(results) == 3

    def test_extract_batch_skip_existing(self, tmp_dir):
        """extract_audio handles skip logic — batch passes overwrite=False."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)

        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.extract_audio") as mock_extract:
            # Simulate that extract_audio returns the existing path (skip behavior)
            mock_extract.return_value = output_dir / "video.mp3"
            extract_batch(
                input_files=[input_file],
                output_dir=output_dir,
                format="mp3",
                jobs=1,
                overwrite=False,
            )
            # extract_audio is called (it handles skip internally)
            mock_extract.assert_called_once()
            call_kwargs = mock_extract.call_args[1]
            assert call_kwargs["overwrite"] is False

    def test_extract_batch_overwrite(self, tmp_dir):
        """Passes overwrite=True through to extract_audio."""
        input_file = tmp_dir / "video.mp4"
        input_file.write_bytes(b"\x00" * 100)

        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.extract_audio") as mock_extract:
            mock_extract.return_value = output_dir / "video.mp3"
            extract_batch(
                input_files=[input_file],
                output_dir=output_dir,
                format="mp3",
                jobs=1,
                overwrite=True,
            )
            mock_extract.assert_called_once()
            call_kwargs = mock_extract.call_args[1]
            assert call_kwargs["overwrite"] is True

    def test_extract_batch_continue_on_error(self, tmp_dir):
        """One failure does not stop the batch from processing remaining files."""
        files = []
        for name in ["a.mp4", "b.avi", "c.mkv"]:
            f = tmp_dir / name
            f.write_bytes(b"\x00" * 100)
            files.append(f)

        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        with patch("audio_extraction.extractor.extract_audio") as mock_extract:
            # First call raises, rest succeed
            mock_extract.side_effect = [
                RuntimeError("codec error"),
                output_dir / "b.mp3",
                output_dir / "c.mp3",
            ]
            results = extract_batch(
                input_files=files,
                output_dir=output_dir,
                format="mp3",
                jobs=1,
            )
            # All three should be attempted
            assert mock_extract.call_count == 3
            assert len(results) == 3
            # First should be a failure
            assert results[0]["success"] is False
            assert results[0]["error"] is not None
            # Rest should succeed
            assert results[1]["success"] is True
            assert results[2]["success"] is True

    def test_extract_batch_empty_input(self, tmp_dir):
        """Empty file list returns empty results."""
        output_dir = tmp_dir / "out"
        output_dir.mkdir()

        results = extract_batch(
            input_files=[],
            output_dir=output_dir,
            format="mp3",
        )
        assert results == []
