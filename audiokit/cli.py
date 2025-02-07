import typer
from pathlib import Path
from typing import Optional
from .client import AudioKitClient
from audiokit_core.exceptions import AudioKitAPIError, AudioKitAuthError

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
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Analyze audio file through AudioKit AI"""
    client = _create_client(api_key)
    
    try:
        result = client.analyze_audio(file_path, timeout=timeout)
        if verbose:
            typer.echo(f"Analysis results for {file_path}:")
            typer.echo(f"Duration: {result.duration}s")
            typer.echo("Features:")
            for feature, value in result.features.items():
                typer.echo(f"  - {feature}: {value}")
        else:
            typer.echo(f"Successfully analyzed {file_path}")
    except AudioKitAuthError:
        typer.secho("Authentication failed. Please check your API key.", fg="red")
        raise typer.Exit(code=1)
    except AudioKitAPIError as e:
        typer.secho(f"API Error: {str(e)}", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Unexpected error: {str(e)}", fg="red")
        raise typer.Exit(code=1)

@app.callback()
def main():
    """AudioKit CLI - Analyze and process audio files"""
    pass

if __name__ == "__main__":
    app() 