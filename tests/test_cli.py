"""Tests for audio_extraction CLI (click interface).

Tests cover:
- Help output and option visibility
- Default input path behavior
- Custom input path handling
- Input validation (nonexistent paths, invalid formats)
- All CLI options/flags acceptance
- Dry-run mode behavior
- FFmpeg missing error handling
- Exit codes for success/failure scenarios
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from audio_extraction.cli import cli


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestHelpOutput:
    """Verify --help shows expected usage information."""

    def test_help_output(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output

    def test_help_shows_output_option(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--output" in result.output or "-o" in result.output

    def test_help_shows_format_option(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--format" in result.output or "-f" in result.output

    def test_help_shows_bitrate_option(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--bitrate" in result.output or "-b" in result.output

    def test_help_shows_jobs_option(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--jobs" in result.output or "-j" in result.output

    def test_help_shows_recursive_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--recursive" in result.output or "-r" in result.output

    def test_help_shows_overwrite_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--overwrite" in result.output

    def test_help_shows_dry_run_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--dry-run" in result.output

    def test_help_shows_verbose_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "--verbose" in result.output or "-v" in result.output


class TestInputPath:
    """Verify input path handling."""

    def test_default_input_is_cwd(self, runner, tmp_dir):
        """No positional arg defaults to current directory (\".\")."""
        # Create a video file in the isolated fs so there's something to find
        with runner.isolated_filesystem(temp_dir=tmp_dir):
            Path("video.mp4").write_bytes(b"\x00" * 100)
            with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
                 patch("audio_extraction.cli.extract_batch", return_value=[]):
                result = runner.invoke(cli, ["--dry-run"])
                # Should succeed and list the video file (default input is ".")
                assert result.exit_code == 0

    def test_custom_input_path(self, runner, video_dir):
        """Positional arg sets the input directory."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True):
            result = runner.invoke(cli, [str(video_dir), "--dry-run"])
            assert result.exit_code == 0
            # Should mention discovered files
            assert "movie.mp4" in result.output or "clip.avi" in result.output

    def test_input_path_not_found(self, runner, tmp_dir):
        """Nonexistent path produces error (click.Path(exists=True) enforces)."""
        nonexistent = str(tmp_dir / "does_not_exist")
        result = runner.invoke(cli, [nonexistent])
        assert result.exit_code != 0


class TestOutputOption:
    """Verify -o/--output directory option."""

    def test_output_dir_option(self, runner, video_dir, tmp_dir):
        """The -o flag sets the output directory."""
        output = tmp_dir / "audio_out"
        output.mkdir()
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.extract_batch", return_value=[]):
            result = runner.invoke(cli, [str(video_dir), "-o", str(output)])
            # Should pass the output_dir through to extract_batch
            assert result.exit_code == 0


class TestFormatOption:
    """Verify -f/--format option with click.Choice validation."""

    @pytest.mark.parametrize("fmt", ["mp3", "wav", "flac", "aac", "ogg"])
    def test_format_option_valid(self, runner, video_dir, fmt):
        """Each valid format should be accepted."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.extract_batch", return_value=[]):
            result = runner.invoke(cli, [str(video_dir), "-f", fmt])
            assert result.exit_code == 0

    @pytest.mark.parametrize("fmt", ["xyz", "mp5", "docx"])
    def test_format_option_invalid(self, runner, video_dir, fmt):
        """Invalid format should be rejected by click.Choice."""
        result = runner.invoke(cli, [str(video_dir), "-f", fmt])
        assert result.exit_code != 0


class TestFlags:
    """Verify boolean flags and options are accepted."""

    def test_recursive_flag(self, runner, video_dir):
        """-r flag is accepted."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.extract_batch", return_value=[]):
            result = runner.invoke(cli, [str(video_dir), "-r"])
            assert result.exit_code == 0

    def test_overwrite_flag(self, runner, video_dir):
        """--overwrite flag is accepted."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.extract_batch", return_value=[]):
            result = runner.invoke(cli, [str(video_dir), "--overwrite"])
            assert result.exit_code == 0

    def test_verbose_flag(self, runner, video_dir):
        """-v flag is accepted."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.extract_batch", return_value=[]):
            result = runner.invoke(cli, [str(video_dir), "-v"])
            assert result.exit_code == 0

    def test_jobs_option(self, runner, video_dir):
        """-j 4 is accepted."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.extract_batch", return_value=[]):
            result = runner.invoke(cli, [str(video_dir), "-j", "4"])
            assert result.exit_code == 0


class TestDryRun:
    """Verify --dry-run behavior."""

    def test_dry_run_no_files_created(self, runner, video_dir, tmp_dir):
        """--dry-run should not produce output files."""
        output = tmp_dir / "dry_output"
        output.mkdir()
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True):
            result = runner.invoke(cli, [str(video_dir), "--dry-run", "-o", str(output)])
            assert result.exit_code == 0
            # No audio files should exist in output dir
            audio_files = [f for f in output.iterdir() if f.suffix in (".mp3", ".wav", ".flac")]
            assert len(audio_files) == 0

    def test_dry_run_lists_planned(self, runner, video_dir):
        """--dry-run should show what would be extracted."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True):
            result = runner.invoke(cli, [str(video_dir), "--dry-run"])
            assert result.exit_code == 0
            # Should list discovered video files
            output_lower = result.output.lower()
            assert any(
                name in output_lower
                for name in ["movie.mp4", "clip.avi", "recording.mkv", "show.mov", "stream.webm"]
            )


class TestFFmpegMissing:
    """Verify behavior when FFmpeg is not installed."""

    def test_ffmpeg_not_installed(self, runner, video_dir):
        """Should show a clear error when FFmpeg is not found."""
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=False):
            result = runner.invoke(cli, [str(video_dir)])
            assert result.exit_code != 0
            output_lower = result.output.lower()
            assert "ffmpeg" in output_lower


class TestExitCodes:
    """Verify exit codes reflect success/failure."""

    def test_exit_code_zero_all_success(self, runner, video_dir):
        """Exit 0 when all extractions succeed."""
        files = [video_dir / "movie.mp4"]
        results = [
            {"input": files[0], "output": Path("/tmp/movie.mp3"), "success": True, "error": None}
        ]
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.discover_files", return_value=files), \
             patch("audio_extraction.cli.extract_batch", return_value=results):
            result = runner.invoke(cli, [str(video_dir)])
            assert result.exit_code == 0

    def test_exit_code_one_any_failure(self, runner, video_dir):
        """Exit 1 when any extraction fails."""
        files = [video_dir / "movie.mp4", video_dir / "clip.avi"]
        results = [
            {"input": files[0], "output": Path("/tmp/movie.mp3"), "success": True, "error": None},
            {"input": files[1], "output": None, "success": False, "error": "codec error"},
        ]
        with patch("audio_extraction.cli.check_ffmpeg_available", return_value=True), \
             patch("audio_extraction.cli.discover_files", return_value=files), \
             patch("audio_extraction.cli.extract_batch", return_value=results):
            result = runner.invoke(cli, [str(video_dir)])
            assert result.exit_code == 1
