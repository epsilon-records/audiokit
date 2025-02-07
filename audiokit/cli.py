import typer
from pathlib import Path
from typing import Optional, Literal
from .client import AudioKitClient
from audiokit_core.exceptions import AudioKitAPIError, AudioKitAuthError
from rich.table import Table
from rich.console import Console
import yaml
import csv
import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .plugins.base import manager  # Plugin system integration

app = typer.Typer(help="AudioKit Command Line Interface", pretty_exceptions_show_locals=False)

def _create_client(api_key: Optional[str] = None) -> AudioKitClient:
    """Helper to create and configure client"""
    client = AudioKitClient()
    if api_key:
        client.config.api_key = api_key
    return client

@app.command()
def analyze(
    file_path: Path = typer.Argument(..., exists=True, dir_okay=False, help="Path to audio file"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Request timeout in seconds"),
    api_key: str = typer.Option(None, "--key", "-k", envvar="AUDIOKIT_API_KEY", help="API key"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    output_format: Literal["table", "json", "yaml", "csv"] = typer.Option("table", help="Output format")
):
    """Analyze audio file with advanced output formatting"""
    try:
        client = _create_client(api_key)
        result = client.analyze_audio(file_path, timeout=timeout)
        
        console = Console()
        
        if output_format == "json":
            console.print_json(result.json())
        elif output_format == "yaml":
            console.print(yaml.dump(result.dict(), sort_keys=False))
        elif output_format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=result.dict().keys())
            writer.writeheader()
            writer.writerow(result.dict())
            console.print(output.getvalue())
        else:  # Default table format
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Feature", style="dim")
            table.add_column("Value")
            
            for feature, value in result.features.items():
                table.add_row(feature, str(value))
                
            console.print(table)
            
    except AudioKitAuthError:
        typer.secho("Authentication failed. Please check your API key.", fg="red")
        raise typer.Exit(code=1)
    except AudioKitAPIError as e:
        typer.secho(f"API Error: {str(e)}", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Unexpected error: {str(e)}", fg="red")
        raise typer.Exit(code=1)

@app.command()
def batch_analyze(
    paths: list[Path] = typer.Argument(..., exists=True, help="Paths to audio files or directories"),
    output_format: Literal["json", "yaml", "csv"] = typer.Option("json", help="Batch output format"),
    concurrency: int = typer.Option(4, help="Number of parallel requests"),
    api_key: str = typer.Option(None, "--key", "-k", envvar="AUDIOKIT_API_KEY"),
    timeout: int = typer.Option(30, "--timeout", "-t")
):
    """Batch process multiple audio files with parallel execution"""
    console = Console()
    client = _create_client(api_key)
    results = []
    errors = []

    # Collect all audio files
    audio_files = []
    for path in paths:
        if path.is_dir():
            audio_files.extend([f for f in path.glob("**/*") if f.is_file() and f.suffix in [".wav", ".mp3", ".flac"]])
        else:
            audio_files.append(path)

    # Process files with thread pool
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(client.analyze_audio, file, timeout): file
            for file in audio_files
        }
        
        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                results.append({
                    "file": str(file),
                    "duration": result.duration,
                    "features": result.features
                })
            except Exception as e:
                errors.append({"file": str(file), "error": str(e)})

    # Output results
    if output_format == "json":
        console.print_json(json.dumps({"results": results, "errors": errors}))
    elif output_format == "yaml":
        console.print(yaml.dump({"results": results, "errors": errors}, sort_keys=False))
    elif output_format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["file", "duration"] + list(results[0]["features"].keys()))
        writer.writeheader()
        for result in results:
            row = {"file": result["file"], "duration": result["duration"]}
            row.update(result["features"])
            writer.writerow(row)
        console.print(output.getvalue())

    # Show summary
    console.print(f"\n[bold]Processed {len(audio_files)} files:[/bold]")
    console.print(f"  Successful: {len(results)}")
    console.print(f"  Failed: {len(errors)}")
    
    if errors and output_format != "csv":
        console.print("\n[bold]Error details:[/bold]")
        for error in errors:
            console.print(f"  [red]{error['file']}:[/red] {error['error']}")

    if errors:
        raise typer.Exit(code=1)

@app.callback()
def main():
    """AudioKit CLI - Analyze and process audio files"""
    pass

if __name__ == "__main__":
    app() 