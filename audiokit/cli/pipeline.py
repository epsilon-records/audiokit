"""CLI commands for audio pipeline configuration."""

import typer
import yaml
from pathlib import Path
from rich import print
from rich.console import Console
from loguru import logger
from ..graph import AudioGraphManager
from ..nodes import get_available_nodes


app = typer.Typer(help="Audio processing pipeline management")
console = Console()


@app.command()
def create(
    config_file: Path = typer.Argument(
        ..., exists=True, help="YAML configuration file for the pipeline"
    ),
):
    """Create a pipeline from YAML configuration."""
    try:
        config = yaml.safe_load(config_file.read_text())
        graph = AudioGraphManager()

        # Create nodes
        for node_config in config["nodes"]:
            node_type = node_config["type"]
            node_id = node_config["id"]
            params = node_config.get("params", {})
            node = get_available_nodes()[node_type](node_id, **params)
            graph.add_node(node)

        # Create connections
        for conn in config["connections"]:
            graph.connect(conn["from"], conn["to"])

        logger.info(f"Created pipeline from {config_file}")
        print(f"[green]✓[/green] Successfully created pipeline from {config_file}")
        return graph

    except Exception as e:
        print(f"[red]✗[/red] Failed to create pipeline: {str(e)}")
        raise typer.Exit(1)


@app.command()
def list_nodes():
    """List available audio processing nodes."""
    nodes = get_available_nodes()
    console.print("\n[bold cyan]Available Audio Nodes[/bold cyan]")

    for name, node_class in nodes.items():
        console.print(f"\n[yellow]{name}[/yellow]")
        if node_class.__doc__:
            console.print(f"  {node_class.__doc__.strip()}")

        # Show parameters
        params = node_class.get_parameters()
        if params:
            console.print("\n  Parameters:")
            for param_name, param_info in params.items():
                console.print(f"    • {param_name}: {param_info['description']}")


@app.command()
def template(
    output_file: Path = typer.Argument(..., help="Output YAML file"),
    type: str = typer.Option("basic", help="Template type (basic/filter/effect)"),
):
    """Generate a template pipeline configuration."""
    templates = {
        "basic": {
            "nodes": [
                {
                    "id": "input",
                    "type": "AudioInputNode",
                    "params": {"channels": 2, "sample_rate": 44100},
                },
                {
                    "id": "output",
                    "type": "AudioOutputNode",
                    "params": {"channels": 2},
                },
            ],
            "connections": [{"from": "input", "to": "output"}],
        },
        "filter": {
            "nodes": [
                {
                    "id": "input",
                    "type": "AudioInputNode",
                    "params": {"channels": 2, "sample_rate": 44100},
                },
                {
                    "id": "filter",
                    "type": "AudioFilterNode",
                    "params": {"cutoff": 1000, "resonance": 0.7},
                },
                {
                    "id": "output",
                    "type": "AudioOutputNode",
                    "params": {"channels": 2},
                },
            ],
            "connections": [
                {"from": "input", "to": "filter"},
                {"from": "filter", "to": "output"},
            ],
        },
    }

    if type not in templates:
        print(f"[red]✗[/red] Unknown template type: {type}")
        print(f"Available types: {', '.join(templates.keys())}")
        raise typer.Exit(1)

    output_file.write_text(yaml.dump(templates[type], default_flow_style=False))
    print(f"[green]✓[/green] Generated {type} template at {output_file}")


@app.command()
def validate(
    config_file: Path = typer.Argument(..., exists=True),
    strict: bool = typer.Option(False, help="Enable strict validation"),
):
    """Validate a pipeline configuration."""
    try:
        config = yaml.safe_load(config_file.read_text())
        nodes = get_available_nodes()

        # Validate nodes
        for node in config["nodes"]:
            if node["type"] not in nodes:
                print(f"[red]✗[/red] Invalid node type: {node['type']}")
                raise typer.Exit(1)

            if strict:
                # Validate parameters
                node_class = nodes[node["type"]]
                valid_params = node_class.get_parameters()
                for param in node.get("params", {}):
                    if param not in valid_params:
                        print(
                            f"[red]✗[/red] Invalid parameter for {node['type']}: {param}"
                        )
                        raise typer.Exit(1)

        print("[green]✓[/green] Configuration is valid")

    except Exception as e:
        print(f"[red]✗[/red] Validation failed: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
