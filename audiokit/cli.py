import base64
import json
import sys
from pathlib import Path
from typing import Optional

import httpx
import typer
from loguru import logger
from typer.core import TyperGroup

from audiokit.config import get_api_base_url, load_config, save_config
from audiokit.graph.manager import AudioGraphManager
from audiokit.nodes import get_available_nodes


class AliasedGroup(TyperGroup):
    def get_command(self, ctx, cmd_name):
        # First, try to get the command as defined
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        # Normalize: remove all '-' and '_' and compare names
        sanitized = cmd_name.replace("-", "").replace("_", "")
        for name, command in self.commands.items():
            if name.replace("-", "").replace("_", "") == sanitized:
                return command
        return None


# Create the main Typer app and sub-apps using the custom AliasedGroup with no_args_is_help=True,
# so that if a group is called without a subcommand, its help is shown.
app = typer.Typer(help="AudioKit CLI", cls=AliasedGroup, no_args_is_help=True)

# Define subcommand groups with alias support (show help if no subcommand is provided)
api_app = typer.Typer(
    help="API commands for the AudioKit AI server",
    cls=AliasedGroup,
    no_args_is_help=True,
)
graph_app = typer.Typer(
    help="Graph management commands", cls=AliasedGroup, no_args_is_help=True
)


def call_api(endpoint: str, files: dict = None, data: dict = None) -> dict:
    """
    Helper function for making API calls.
    """
    url = f"{get_api_base_url()}/{endpoint}"
    try:
        response = httpx.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API call to {endpoint} failed: {e}")
        raise typer.Exit(1)


# -------------------------
# API Endpoints Commands
# -------------------------


@api_app.command("denoise")
def denoise(input_file: Path, output_file: Path):
    """
    Reduce noise in an audio file using DeepFilterNet.
    """
    with input_file.open("rb") as f:
        result = call_api("denoise", files={"file": f})
    # Expecting a response like {'result': <base64 string>}
    audio_data = base64.b64decode(result["result"])
    with output_file.open("wb") as out:
        out.write(audio_data)
    typer.echo(f"Denoised audio saved to {output_file}")


@api_app.command("auto-master")
def auto_master(target_file: Path, reference_file: Path, output_file: Path):
    """
    Apply automatic mastering to an audio file using Matchering.
    """
    with target_file.open("rb") as f_target, reference_file.open("rb") as f_ref:
        result = call_api(
            "auto_master", files={"file": f_target, "reference_file": f_ref}
        )
    audio_data = base64.b64decode(result["result"])
    with output_file.open("wb") as out:
        out.write(audio_data)
    typer.echo(f"Mastered audio saved to {output_file}")


@api_app.command("separate")
def separate(input_file: Path, output_dir: Path):
    """
    Separate an audio file into stems using Demucs.
    """
    with input_file.open("rb") as f:
        result = call_api("separate", files={"file": f})
    output_dir.mkdir(parents=True, exist_ok=True)
    for stem, audio_enc in result.items():
        stem_path = output_dir / f"{stem}.wav"
        with stem_path.open("wb") as out:
            out.write(base64.b64decode(audio_enc))
        typer.echo(f"Saved stem: {stem_path}")


@api_app.command("transcribe")
def transcribe(input_file: Path):
    """
    Transcribe an audio file using Whisper.
    """
    with input_file.open("rb") as f:
        result = call_api("transcribe", files={"file": f})
    typer.echo("Transcription:")
    typer.echo(result["text"])


@api_app.command("clone-voice")
def clone_voice(input_file: Path):
    """
    Clone a voice from an audio sample.
    """
    with input_file.open("rb") as f:
        result = call_api("clone_voice", files={"file": f})
    typer.echo(result.get("result", "No result"))


@api_app.command("midi-to-audio")
def midi_to_audio(input_file: Path):
    """
    Convert MIDI to audio.
    """
    with input_file.open("rb") as f:
        result = call_api("midi_to_audio", files={"file": f})
    typer.echo(result.get("result", "No result"))


@api_app.command("config")
def configure(api_base: Optional[str] = None):
    """
    View or update AudioKit configuration.

    If api_base is provided, updates the API base URL.
    Otherwise, displays current configuration.
    """
    config = load_config()

    if api_base:
        config["api_base_url"] = f"{api_base}/api/v1"
        save_config(config)
        typer.echo(f"Updated API base URL to: {config['api_base_url']}")
    else:
        typer.echo("Current configuration:")
        typer.echo(json.dumps(config, indent=2))


# -------------------------
# Graph Management Commands
# -------------------------

# Instantiate a global AudioGraphManager to manage our nodes and connections.
graph_manager = AudioGraphManager()


@graph_app.command("add-node")
def add_node(node_type: str, node_id: str, params: str = "{}"):
    """
    Add a node to the audio processing graph.

    Example:
      ak graph add-node AudioFilterNode filter --params '{"cutoff": 1000, "resonance": 0.7}'
    """
    available_nodes = get_available_nodes()
    if node_type not in available_nodes:
        typer.echo(
            f"Unknown node type: {node_type}. Available: {', '.join(available_nodes.keys())}"
        )
        raise typer.Exit(1)
    try:
        parameters = json.loads(params)
    except Exception:
        typer.echo("Failed to parse params JSON.")
        raise typer.Exit(1)
    node_class = available_nodes[node_type]
    node_instance = node_class(node_id, **parameters)
    graph_manager.nodes[node_id] = node_instance
    typer.echo(
        f"Added node '{node_id}' of type '{node_type}' with params {parameters}."
    )


@graph_app.command("list")
def list_nodes():
    """
    List all nodes in the audio processing graph.
    """
    if not graph_manager.nodes:
        typer.echo("No nodes in the graph.")
        raise typer.Exit()
    for node_id, node in graph_manager.nodes.items():
        typer.echo(f"{node_id}: {node.__class__.__name__} with params {node.params}")


@graph_app.command("connect")
def connect(from_node: str, to_node: str):
    """
    Connect two nodes in the audio processing graph.
    """
    if from_node not in graph_manager.nodes or to_node not in graph_manager.nodes:
        typer.echo("Both nodes must exist to create a connection.")
        raise typer.Exit(1)
    graph_manager.connections.append((from_node, to_node))
    typer.echo(f"Connected {from_node} -> {to_node}.")


@graph_app.command("stats")
def graph_stats():
    """
    Display statistics for the audio processing graph.
    """
    active_nodes = graph_manager.get_active_nodes()
    cpu_usage = graph_manager.get_node_cpu_usage()
    signal_levels = graph_manager.get_node_signal_levels()
    typer.echo("Active nodes: " + ", ".join(active_nodes))
    typer.echo("CPU Usage: " + json.dumps(cpu_usage, indent=2))
    typer.echo("Signal levels: " + json.dumps(signal_levels, indent=2))


def interactive_prompt():
    """
    Enter an interactive prompt for ak commands.
    Type 'exit' or press Ctrl-C to quit and return to the terminal.
    """
    typer.echo("Entering ak> interactive prompt. Type 'exit' or press Ctrl-C to quit.")
    while True:
        try:
            line = input("ak> ")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nExiting interactive prompt.")
            break

        # If the user types "help", display the top-level help.
        if line.strip().lower() == "help":
            app(args=["--help"], standalone_mode=False)
            continue

        # Check for exit commands.
        if line.strip().lower() in ["exit", "quit"]:
            break

        # Skip empty lines.
        if not line.strip():
            continue

        # Simulate running a command by splitting the input into arguments
        args = line.split()
        try:
            # Use standalone_mode=False so that Typer does not call sys.exit()
            app(args=args, standalone_mode=False)
        except SystemExit as se:
            # Catch system exit from Typer. Display the error and continue.
            typer.echo(f"Error: Command failed with exit code {se.code}")
        except Exception as e:
            typer.echo(f"Error: {e}")


def main():
    app.add_typer(api_app, name="api")
    app.add_typer(graph_app, name="graph")
    # If command-line arguments are provided, run them once then drop into the interactive prompt.
    if len(sys.argv) > 1:
        try:
            # Use standalone_mode=False to prevent Typer from calling sys.exit()
            app(args=sys.argv[1:], standalone_mode=False)
        except SystemExit:
            # Catch SystemExit so that interactive_prompt() is reached
            pass
    interactive_prompt()


if __name__ == "__main__":
    main()
