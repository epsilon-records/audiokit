def handle_cli_error(error: Exception):
    """Standardized CLI error handling"""
    if isinstance(error, NotImplementedError):
        typer.secho(str(error), fg=typer.colors.YELLOW)
    else:
        typer.secho(f"Error: {str(error)}", fg=typer.colors.RED)
    raise typer.Exit(code=1)

def handle_api_error(response):
    """Handle API response errors"""
    try:
        error = response.json()
        typer.secho(f"API Error ({response.status_code}): {error.get('detail')}", 
                   fg=typer.colors.RED)
    except:
        typer.secho(f"Unknown API Error ({response.status_code})", 
                   fg=typer.colors.RED)
    raise typer.Exit(code=1) 