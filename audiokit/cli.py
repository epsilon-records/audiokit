"""
AudioKit Command Line Interface
=============================

A powerful CLI for audio processing and analysis.

Usage:
    ak analyze path/to/audio.wav
    ak process path/to/audio.wav --stems --vocals --denoise
    ak generate instrument "warm analog synth pad"
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from typing import Optional, List

from . import ak
from .core.logging import get_logger, setup_logging

# Initialize logger
logger = get_logger(__name__)
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="audiokit",
    help="AudioKit CLI - AI-powered audio processing toolkit",
    add_completion=False
)

def setup_cli():
    """Configure CLI environment."""
    # Setup logging with CLI-specific format
    setup_logging(
        log_format=(
            "<green>{time:HH:mm:ss}</green> "
            "<blue>{name}</blue> "
            "<cyan>{message}</cyan>"
        )
    )
    logger.debug("CLI initialized")

@app.command()
@logger.catch(reraise=True)
def analyze(
    audio_path: Path = typer.Argument(
        ...,
        help="Path to the audio file to analyze",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True
    ),
    output_format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table/json)"
    )
):
    """Analyze an audio file and display comprehensive results."""
    with console.status("[bold green]Analyzing audio...") as status:
        try:
            logger.info("Starting analysis of: {}", audio_path)
            results = ak.analyze_audio(str(audio_path))
            
            if output_format == "json":
                logger.debug("Outputting results as JSON")
                console.print_json(data=results)
                return
            
            # Create rich table output
            logger.debug("Creating results table")
            table = Table(title=f"Analysis Results: {audio_path.name}")
            table.add_column("Feature", style="cyan")
            table.add_column("Value", style="green")
            
            for category, details in results.items():
                if isinstance(details, dict):
                    for key, value in details.items():
                        table.add_row(f"{category.upper()} - {key}", str(value))
                else:
                    table.add_row(category.upper(), str(details))
            
            console.print(table)
            logger.success("Analysis complete")
            
        except Exception as e:
            logger.exception("Analysis failed")
            console.print(f"[red]Error analyzing audio:[/red] {str(e)}")
            raise typer.Exit(1)

@app.command()
@logger.catch(reraise=True)
def process(
    audio_path: Path = typer.Argument(
        ...,
        help="Path to the audio file to process",
        exists=True,
    ),
    output_dir: Path = typer.Option(
        "output",
        "--output", "-o",
        help="Output directory for processed files"
    ),
    stems: bool = typer.Option(
        False,
        "--stems",
        help="Separate audio into stems"
    ),
    vocals: bool = typer.Option(
        False,
        "--vocals",
        help="Extract vocals"
    ),
    denoise: bool = typer.Option(
        False,
        "--denoise",
        help="Apply noise reduction"
    )
):
    """Process audio with various operations."""
    with console.status("[bold green]Processing audio...") as status:
        try:
            logger.info("Processing audio: {}", audio_path)
            with logger.contextualize(operation="processing"):
                results = ak.process_audio(
                    str(audio_path),
                    output_dir=str(output_dir),
                    extract_vocals=vocals,
                    separate_stems=stems,
                    reduce_noise=denoise
                )
                
                # Create results table
                table = Table(title="Processing Results")
                table.add_column("Operation", style="cyan")
                table.add_column("Output File", style="green")
                
                for op, path in results.items():
                    if isinstance(path, dict):
                        for stem, stem_path in path.items():
                            table.add_row(f"{op.upper()} - {stem}", stem_path)
                    else:
                        table.add_row(op.upper(), path)
                
                console.print(table)
                logger.success("Processing complete")
            
        except Exception as e:
            logger.exception("Processing failed")
            console.print(f"[red]Error processing audio:[/red] {str(e)}")
            raise typer.Exit(1)

@app.command()
@logger.catch(reraise=True)
def generate(
    type: str = typer.Argument(
        ...,
        help="Type of content to generate (instrument/moodboard)"
    ),
    description: str = typer.Argument(
        ...,
        help="Description or audio path for generation"
    ),
    output_dir: Path = typer.Option(
        "output",
        "--output", "-o",
        help="Output directory for generated content"
    )
):
    """Generate audio content or related assets."""
    with console.status("[bold green]Generating content..."):
        try:
            logger.info("Generating {} content", type)
            with logger.contextualize(generation_type=type):
                if type == "instrument":
                    results = ak.generate_content(instrument_description=description)
                elif type == "moodboard":
                    results = ak.generate_content(audio_path=description)
                else:
                    msg = f"Unknown generation type: {type}"
                    logger.error(msg)
                    console.print(f"[red]{msg}")
                    raise typer.Exit(1)
                
                console.print_json(data=results)
                logger.success("Generation complete")
            
        except Exception as e:
            logger.exception("Generation failed")
            console.print(f"[red]Error generating content:[/red] {str(e)}")
            raise typer.Exit(1)

@app.command()
@logger.catch(reraise=True)
def batch(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing audio files to process",
        exists=True,
        file_okay=False,
        dir_okay=True
    ),
    operation: str = typer.Option(
        "analyze",
        "--op", "-o",
        help="Operation to perform (analyze/process/generate)"
    )
):
    """Process multiple audio files in batch."""
    audio_files = list(input_dir.glob("*.wav")) + list(input_dir.glob("*.mp3"))
    logger.info("Found {} audio files to process", len(audio_files))
    
    with Progress() as progress:
        task = progress.add_task(
            f"[cyan]Processing {len(audio_files)} files...",
            total=len(audio_files)
        )
        
        for audio_file in audio_files:
            try:
                with logger.contextualize(file=audio_file.name):
                    logger.debug("Processing file: {}", audio_file)
                    if operation == "analyze":
                        ak.analyze_audio(str(audio_file))
                    elif operation == "process":
                        ak.process_audio(str(audio_file))
                    
                    progress.advance(task)
                    
            except Exception as e:
                logger.exception("Failed to process file")
                console.print(f"[red]Error processing {audio_file.name}:[/red] {str(e)}")

@app.callback()
def main():
    """AudioKit CLI - AI-powered audio processing toolkit."""
    setup_cli()

if __name__ == "__main__":
    app()
