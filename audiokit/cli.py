import typer
from . import analyze_audio

app = typer.Typer(help="AudioKit CLI for audio analysis and processing")


@app.command()
def analyze(file: str) -> None:
    """Analyze the provided audio file."""
    result = analyze_audio(file)
    typer.echo(f"Analysis Result: {result}")


if __name__ == "__main__":
    app()
