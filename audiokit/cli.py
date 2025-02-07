import typer
from .plugins.base import manager

app = typer.Typer(help="AudioKit Extensible CLI", pretty_exceptions_show_locals=False)

@app.callback()
def main():
    """AudioKit command line interface"""
    pass

if __name__ == "__main__":
    app() 