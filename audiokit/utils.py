def handle_cli_error(error: Exception):
    """Standardized CLI error handling"""
    if isinstance(error, NotImplementedError):
        click.secho(str(error), fg="yellow")
    else:
        click.secho(f"Error: {str(error)}", fg="red")
    sys.exit(1)

def handle_api_error(response):
    """Handle API response errors"""
    try:
        error = response.json()
        click.secho(f"API Error ({response.status_code}): {error.get('detail')}", fg="red")
    except:
        click.secho(f"Unknown API Error ({response.status_code})", fg="red")
    sys.exit(1) 