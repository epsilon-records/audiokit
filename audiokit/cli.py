"""Command-line interface for AudioKit."""
import sys
import json
from pathlib import Path
from typing import Optional
import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from . import AudioKit
from .errors import AudioKitError
from .errors import AuthError, APIError, ValidationError

app = typer.Typer(help="AudioKit CLI for audio analysis and processing")
console = Console()

def display_analysis(result: dict):
    """Display analysis results in a formatted table.
    
    Args:
        result: Analysis results dictionary
    """
    table = Table(
        title="Audio Analysis Results",
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    # Add rows for each property
    for key, value in result.items():
        if isinstance(value, float):
            # Format floating point numbers
            formatted_value = f"{value:.2f}"
        else:
            formatted_value = str(value)
        table.add_row(key.replace("_", " ").title(), formatted_value)
    
    console.print(table)

def display_error(error: str, title: str = "Error", style: str = "red", help_text: Optional[str] = None):
    """Display error message in formatted panel.
    
    Args:
        error: Error message to display
        title: Panel title
        style: Error style/color
        help_text: Optional help text to display below error
    """
    message = f"[{style}]{error}[/{style}]"
    if help_text:
        message += f"\n\n[yellow]{help_text}[/yellow]"
    
    panel = Panel(
        message,
        title=title,
        border_style=style
    )
    console.print(panel)

@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="Input audio file"),
    api_key: Optional[str] = typer.Option(None, help="API key", envvar="AUDIOKIT_API_KEY"),
    api_url: Optional[str] = typer.Option(None, help="API URL", envvar="AUDIOKIT_API_URL"),
    config: Optional[Path] = typer.Option(None, help="Path to config file")
):
    """Analyze audio file."""
    async def _analyze():
        try:
            async with AudioKit(
                api_url=api_url,
                api_key=api_key,
                config_path=config
            ) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(description="Analyzing audio...", total=None)
                    
                    try:
                        result = await client.analyze(input_file)
                        console.print("\nAnalysis Results:", style="green")
                        console.print_json(data=result)
                    except AuthError as e:
                        display_error(str(e))
                        sys.exit(1)
                    except APIError as e:
                        help_text = None
                        if e.status_code == 413:
                            help_text = "The file size exceeds the server's limit."
                        display_error(
                            f"API error: {str(e)}",
                            help_text=help_text
                        )
                        sys.exit(1)
                    except ValidationError as e:
                        display_error(f"Validation error: {str(e)}")
                        sys.exit(1)
                        
        except Exception as e:
            display_error(f"Unexpected error: {str(e)}")
            sys.exit(1)
            
    asyncio.run(_analyze())

@app.command()
def process(
    input_file: Path = typer.Argument(..., help="Input audio file"),
    output_file: Path = typer.Argument(..., help="Output audio file"),
    api_key: Optional[str] = typer.Option(None, help="API key", envvar="AUDIOKIT_API_KEY"),
    api_url: str = typer.Option(
        "http://localhost:8000",
        help="API URL",
        envvar="AUDIOKIT_API_URL"
    ),
    params: Optional[Path] = typer.Option(None, help="Processing parameters JSON file")
):
    """Process audio file with optional parameters."""
    async def _process():
        try:
            # Load parameters if provided
            parameters = {}
            if params:
                parameters = json.loads(params.read_text())
                
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(description="Processing audio...", total=None)
                
                async with AudioKit(api_url=api_url, api_key=api_key) as client:
                    await client.process(input_file, output_file, **parameters)
                    
                    console.print(f"\nProcessed audio saved to: {output_file}", style="green")
                    
        except AudioKitError as e:
            display_error(e.message)
            sys.exit(1)
        except Exception as e:
            display_error(f"Unexpected error: {str(e)}")
            sys.exit(1)
            
    asyncio.run(_process())

@app.command()
def config(
    set_key: Optional[str] = typer.Option(None, "--set-key", help="Set API key"),
    set_url: Optional[str] = typer.Option(None, "--set-url", help="Set API URL"),
    show: bool = typer.Option(False, "--show", help="Show current configuration")
):
    """Manage AudioKit configuration."""
    config_file = Path.home() / ".audiokit" / "config.json"
    config_file.parent.mkdir(exist_ok=True)
    
    # Load existing config
    config = {}
    if config_file.exists():
        config = json.loads(config_file.read_text())
        
    # Update config
    if set_key:
        config["api_key"] = set_key
    if set_url:
        config["api_url"] = set_url
        
    # Save if changes made
    if set_key or set_url:
        config_file.write_text(json.dumps(config, indent=2))
        console.print("Configuration updated", style="green")
        
    # Show current config
    if show:
        if config:
            table = Table(title="AudioKit Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            for key, value in config.items():
                if key == "api_key" and value:
                    value = f"{value[:8]}..." 
                table.add_row(key, value)
            console.print(table)
        else:
            console.print("No configuration found", style="yellow")

if __name__ == "__main__":
    app() 