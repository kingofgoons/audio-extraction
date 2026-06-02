"""File discovery utilities for locating video files."""

from pathlib import Path

from audio_extraction.formats import AUDIO_FORMATS, is_video_file


def discover_files(input_path: Path, recursive: bool = False) -> list[Path]:
    """Discover video files from a path.

    If input_path is a file, returns it in a list (if it's a video file).
    If input_path is a directory, scans for video files.
    If recursive is True, walks subdirectories.

    Returns a sorted list of discovered video file paths.
    """
    if input_path.is_file():
        if is_video_file(input_path):
            return [input_path]
        return []

    if not input_path.is_dir():
        return []

    files: list[Path] = []
    if recursive:
        for path in input_path.rglob("*"):
            if path.is_file() and is_video_file(path):
                files.append(path)
    else:
        for path in input_path.iterdir():
            if path.is_file() and is_video_file(path):
                files.append(path)

    return sorted(files)


def resolve_output_path(
    input_file: Path, output_dir: Path | None, format: str
) -> Path:
    """Determine the output file path for an extracted audio file.

    Uses the same filename stem as the input with the new audio extension.
    If output_dir is None, places the output alongside the input file.
    If output_dir is specified, places the output there.
    """
    extension = AUDIO_FORMATS.get(format, f".{format}")
    output_name = input_file.stem + extension

    if output_dir is None:
        return input_file.parent / output_name

    return output_dir / output_name
