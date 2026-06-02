"""Core audio extraction logic using FFmpeg."""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from audio_extraction.formats import AUDIO_FORMATS, CODEC_MAP


def check_ffmpeg_available() -> bool:
    """Check if FFmpeg is available in PATH.

    Returns True if ffmpeg can be invoked, False otherwise.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def extract_audio(
    input_file: Path,
    output_dir: Path,
    format: str = "mp3",
    bitrate: str | None = None,
    overwrite: bool = False,
    verbose: bool = False,
) -> Path:
    """Extract audio from a single video file using FFmpeg.

    Args:
        input_file: Path to the input video file.
        output_dir: Directory to write the output audio file.
        format: Output audio format (mp3, wav, flac, aac, ogg).
        bitrate: Optional bitrate (e.g. "192k", "320k").
        overwrite: If True, overwrite existing output files.
        verbose: If True, show FFmpeg output.

    Returns:
        Path to the output audio file.

    Raises:
        RuntimeError: If FFmpeg exits with a non-zero return code.
    """
    extension = AUDIO_FORMATS.get(format, f".{format}")
    output_file = output_dir / (input_file.stem + extension)

    # Skip if output exists and not overwriting
    if output_file.exists() and not overwrite:
        return output_file

    codec = CODEC_MAP.get(format, format)

    cmd = [
        "ffmpeg",
        "-i",
        str(input_file),
        "-vn",
        "-acodec",
        codec,
    ]

    if bitrate:
        cmd.extend(["-b:a", bitrate])

    cmd.extend(["-y", str(output_file)])

    result = subprocess.run(
        cmd,
        capture_output=not verbose,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error_msg = result.stderr if result.stderr else "Unknown error"
        raise RuntimeError(f"FFmpeg failed for {input_file.name}: {error_msg}")

    return output_file


def extract_batch(
    input_files: list[Path],
    output_dir: Path,
    format: str = "mp3",
    jobs: int = 1,
    overwrite: bool = False,
    bitrate: str | None = None,
    verbose: bool = False,
) -> list[dict]:
    """Extract audio from multiple video files.

    Catches per-file errors and continues processing remaining files.
    Uses ThreadPoolExecutor when jobs > 1.

    Args:
        input_files: List of video file paths to process.
        output_dir: Directory to write output audio files.
        format: Output audio format.
        jobs: Number of parallel jobs (1 = sequential).
        overwrite: If True, process even when output already exists.
        bitrate: Optional bitrate.
        verbose: If True, show FFmpeg output.

    Returns:
        List of dicts with keys: input, output, success, error.
    """
    if not input_files:
        return []

    def _process_file(input_file: Path) -> dict:
        try:
            output_path = extract_audio(
                input_file=input_file,
                output_dir=output_dir,
                format=format,
                bitrate=bitrate,
                overwrite=overwrite,
                verbose=verbose,
            )
            return {
                "input": input_file,
                "output": output_path,
                "success": True,
                "error": None,
            }
        except RuntimeError as e:
            return {
                "input": input_file,
                "output": None,
                "success": False,
                "error": str(e),
            }

    if jobs > 1:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_process_file, input_files))
    else:
        results = [_process_file(f) for f in input_files]

    return results
