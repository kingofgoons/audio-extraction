"""CLI entry point for audio-extraction."""

from pathlib import Path

import click
from rich.console import Console

from audio_extraction.discovery import discover_files, resolve_output_path
from audio_extraction.extractor import check_ffmpeg_available, extract_batch

console = Console()


@click.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True),
    default=".",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Output directory for audio files [default: same as input].",
)
@click.option(
    "-f",
    "--format",
    "audio_format",
    type=click.Choice(["mp3", "wav", "flac", "aac", "ogg"], case_sensitive=False),
    default="mp3",
    help="Output audio format.",
)
@click.option(
    "-b",
    "--bitrate",
    type=str,
    default=None,
    help="Audio bitrate (e.g. 192k, 320k). Default: copy source quality.",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=1,
    help="Number of parallel extraction jobs.",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    default=False,
    help="Recursively scan subdirectories for video files.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing output files.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be extracted without doing it.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Verbose output (show FFmpeg logs).",
)
def cli(
    input_path: str,
    output: str | None,
    audio_format: str,
    bitrate: str | None,
    jobs: int,
    recursive: bool,
    overwrite: bool,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Extract audio tracks from video files using FFmpeg.

    INPUT_PATH is a video file or directory containing video files.
    Defaults to the current directory.
    """
    # Check FFmpeg availability
    if not check_ffmpeg_available():
        console.print("[red]Error:[/red] FFmpeg not found in PATH.")
        console.print("Install FFmpeg: https://ffmpeg.org/download.html")
        raise SystemExit(1)

    input_p = Path(input_path)
    output_dir = Path(output) if output else None

    # Discover video files
    files = discover_files(input_p, recursive=recursive)

    if not files:
        console.print("No video files found.")
        raise SystemExit(0)

    # Resolve output directory
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Dry-run mode: show planned extractions
    if dry_run:
        console.print(f"[bold]Dry run:[/bold] {len(files)} file(s) to extract as {audio_format}")
        for f in files:
            out_path = resolve_output_path(f, output_dir, audio_format)
            console.print(f"  {f.name} -> {out_path.name}")
        raise SystemExit(0)

    # Determine effective output directory for batch mode
    if output_dir is None and input_p.is_dir():
        effective_output = input_p
    elif output_dir is None:
        effective_output = input_p.parent
    else:
        effective_output = output_dir

    # Run extraction
    results = extract_batch(
        input_files=files,
        output_dir=effective_output,
        format=audio_format,
        overwrite=overwrite,
        bitrate=bitrate,
        verbose=verbose,
        jobs=jobs,
    )

    # Print summary
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    console.print(f"\n[bold]Done:[/bold] {len(successes)} succeeded, {len(failures)} failed")

    if failures:
        console.print("\n[red]Failures:[/red]")
        for r in failures:
            console.print(f"  {r['input'].name}: {r['error']}")
        raise SystemExit(1)


def main() -> None:
    """Entry point for console_scripts."""
    cli()
