"""Command-line interface for AudioKit."""
import asyncio
from pathlib import Path
import typer
from rich.console import Console
from . import AudioKit

app = typer.Typer()
console = Console()

@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="Input audio file"),
    api_key: str = typer.Option(None, help="API key for authentication"),
    api_url: str = typer.Option("http://localhost:8000", help="API URL")
):
    """Analyze audio file and display properties."""
    client = AudioKit(api_url=api_url, api_key=api_key)
    result = asyncio.run(client.analyze(str(input_file)))
    console.print(result)

@app.command()
def process(
    input_file: Path = typer.Argument(..., help="Input audio file"),
    output_file: Path = typer.Option(..., help="Output audio file"),
    api_key: str = typer.Option(None, help="API key for authentication"),
    api_url: str = typer.Option("http://localhost:8000", help="API URL")
):
    """Process audio file with AI models."""
    client = AudioKit(api_url=api_url, api_key=api_key)
    result = asyncio.run(client.process(str(input_file), str(output_file)))
    console.print(result)

if __name__ == "__main__":
    app() 