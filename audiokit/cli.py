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
import json

from . import ak
from .core.logging import get_logger, setup_logging
from .core.config import config

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
    from audiokit import ak  # Import here to access disable_progress
    
    # Temporarily disable progress if needed
    original_progress_setting = ak.disable_progress
    ak.disable_progress = True
    
    try:
        with console.status("[bold green]Analyzing audio...") as status:
            logger.info("Starting analysis of: {}", audio_path)
            results = ak.analyze_audio(str(audio_path))
            
            if output_format == "json":
                logger.debug("Outputting results as JSON")
                console.print_json(data=results)
                return
            
            # Format the output using Rich
            console.print(f"\n[bold green]Analysis Results: {audio_path.name}[/bold green]")
            
            # Create table for BPM/Key
            bpm_key_table = Table(title="BPM & Key", show_header=True, header_style="bold magenta")
            bpm_key_table.add_column("Feature", style="dim")
            bpm_key_table.add_column("Value")
            bpm_key_table.add_row("BPM", str(results["bpm_key"]["bpm"]))
            bpm_key_table.add_row("Key", results["bpm_key"]["key"])
            
            # Create table for Genre/Mood
            genre_table = Table(title="Genre & Mood", show_header=True, header_style="bold blue")
            genre_table.add_column("Feature", style="dim")
            genre_table.add_column("Value")
            genre_table.add_row("Genre", results["genre"]["genre"])
            genre_table.add_row("Mood", results["genre"]["mood"])
            
            # Create table for Instruments
            instruments_table = Table(title="Instruments", show_header=True, header_style="bold yellow")
            instruments_table.add_column("Instrument", style="dim")
            instruments_table.add_column("Confidence")
            for instrument, confidence in results["instruments"].items():
                instruments_table.add_row(instrument, f"{confidence:.2f}")
            
            # Print all tables
            console.print(bpm_key_table)
            console.print(genre_table)
            console.print(instruments_table)
            
            logger.success("Analysis complete")
            
    finally:
        # Restore original progress setting
        ak.disable_progress = original_progress_setting

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

@app.command()
@logger.catch(reraise=True)
def search(
    query: str = typer.Argument(
        ...,
        help="Natural language search query"
    ),
    n_results: int = typer.Option(
        5,
        "--limit", "-n",
        help="Number of results to return"
    ),
    output_format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table/json)"
    )
):
    """Search audio analyses with natural language."""
    with console.status("[bold green]Searching..."):
        try:
            logger.info("Executing search query: {}", query)
            results = ak.search_audio(query, n_results)
            
            if output_format == "json":
                console.print_json(data=results)
                return
            
            # Create results table
            table = Table(title="Search Results")
            table.add_column("Score", style="cyan", justify="right")
            table.add_column("File", style="blue")
            table.add_column("Details", style="green")
            
            for result in results:
                score = f"{result['score']:.2f}"
                file = result['metadata']['file_name']
                details = json.dumps(result['content'], indent=2)
                table.add_row(score, file, details)
            
            console.print(table)
            logger.success("Search complete")
            
        except Exception as e:
            logger.exception("Search failed")
            console.print(f"[red]Error searching:[/red] {str(e)}")
            raise typer.Exit(1)

@app.command()
@logger.catch(reraise=True)
def similar(
    audio_path: Path = typer.Argument(
        ...,
        help="Path to reference audio file",
        exists=True,
        file_okay=True,
        dir_okay=False
    ),
    n_results: int = typer.Option(
        5,
        "--limit", "-n",
        help="Number of similar files to find"
    ),
    output_format: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format (table/json)"
    )
):
    """Find similar audio files."""
    with console.status("[bold green]Finding similar audio..."):
        try:
            logger.info("Finding similar audio to: {}", audio_path)
            results = ak.find_similar(str(audio_path), n_results)
            
            if output_format == "json":
                console.print_json(data=results)
                return
            
            # Create results table
            table = Table(title=f"Similar to: {audio_path.name}")
            table.add_column("Similarity", style="cyan", justify="right")
            table.add_column("File", style="blue")
            table.add_column("Analysis", style="green")
            
            for result in results:
                similarity = f"{result['score']:.2f}"
                file = result['metadata']['file_name']
                analysis = json.dumps(result['content'], indent=2)
                table.add_row(similarity, file, analysis)
            
            console.print(table)
            logger.success("Similar audio search complete")
            
        except Exception as e:
            logger.exception("Similar audio search failed")
            console.print(f"[red]Error finding similar audio:[/red] {str(e)}")
            raise typer.Exit(1)

@app.callback()
def main():
    """AudioKit CLI - AI-powered audio processing toolkit."""
    # Setup logging with default configuration
    setup_logging()
    logger.info("AudioKit CLI initialized")

if __name__ == "__main__":
    app()
