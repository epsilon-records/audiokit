import asyncio
import base64
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import httpx
import typer
import websockets  # Add this with other imports
from loguru import logger
from typer.core import TyperGroup

from audiokit.config import get_api_base_url, load_config, save_config
from audiokit.graph.manager import AudioGraphManager
from audiokit.nodes import get_available_nodes

# Add this before the main CLI functions
logger.remove()  # Remove default logger
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level.icon} {level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Add emojis to log levels
logger.level("INFO", icon="ℹ️")
logger.level("DEBUG", icon="🐛")
logger.level("WARNING", icon="⚠️")
logger.level("ERROR", icon="❌")
logger.level("CRITICAL", icon="💥")
logger.level("SUCCESS", icon="✅")
logger.level("TRACE", icon="🔍")


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


def call_api(
    endpoint: str, files: dict = None, data: dict = None, verbose: bool = False
) -> dict:
    """
    Helper function for making API calls.
    """
    url = f"{get_api_base_url()}/{endpoint}"
    try:
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        response = httpx.post(url, files=files, data=data, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API call to {endpoint} failed: {e}")
        raise typer.Exit(1)


async def call_api_async(
    endpoint: str, files: dict = None, data: dict = None, verbose: bool = False
) -> dict:
    """
    Async helper function for making API calls.
    """
    url = f"{get_api_base_url()}/{endpoint}"
    try:
        if verbose:
            logger.debug(f"Making async API call to {url}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, data=data, timeout=300)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"API call to {endpoint} failed: {e}")
        raise typer.Exit(1)


# -------------------------
# API Endpoints Commands
# -------------------------


@api_app.command("denoise-speech")
def denoise_speech(
    input_file: Path,
    output_file: Path,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed processing information"
    ),
):
    """
    Reduce noise in speech/vocal audio using DeepFilterNet.
    """
    start_time = time.time()

    if verbose:
        typer.echo(f"🔈 Input file: {input_file}")
        typer.echo(f"📏 File size: {input_file.stat().st_size / 1024:.2f} KB")
        typer.echo("🚀 Starting speech/vocal denoising process...")

    try:
        result = asyncio.run(async_denoise_speech(input_file, verbose))

        # Check if result contains audio data directly
        if isinstance(result, dict) and "audio" in result:
            audio_data = base64.b64decode(result["audio"])
        else:
            # If the result is already encoded
            audio_data = base64.b64decode(result)

        with open(output_file, "wb") as f:
            f.write(audio_data)

        if verbose:
            duration = time.time() - start_time
            typer.echo(f"✨ Processing completed in {duration:.2f}s")
            if isinstance(result, dict):
                if "metrics" in result:
                    typer.echo(f"📊 Metrics: {result['metrics']}")
                if "warnings" in result:
                    typer.echo(f"⚠️  Warnings: {result['warnings']}")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@api_app.command("denoise-music")
def denoise_music(
    input_file: Path,
    output_file: Path,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed processing information"
    ),
):
    """
    Denoise music by separating stems, denoising vocals/other, and recombining.
    Uses Demucs for stem separation and DeepFilterNet for selective denoising.
    """
    start_time = time.time()

    if verbose:
        typer.echo(f"🎵 Input file: {input_file}")
        typer.echo(f"📏 File size: {input_file.stat().st_size / 1024:.2f} KB")
        typer.echo("🚀 Starting music denoising process...")

    try:
        result = asyncio.run(async_denoise_music(input_file, verbose))

        # Check if result contains audio data directly
        if isinstance(result, dict) and "audio" in result:
            audio_data = base64.b64decode(result["audio"])
        else:
            # If the result is already encoded
            audio_data = base64.b64decode(result)

        with open(output_file, "wb") as f:
            f.write(audio_data)

        if verbose:
            duration = time.time() - start_time
            typer.echo(f"✨ Processing completed in {duration:.2f}s")
            if isinstance(result, dict):
                if "metrics" in result:
                    typer.echo(f"📊 Metrics: {result['metrics']}")
                if "warnings" in result:
                    typer.echo(f"⚠️  Warnings: {result['warnings']}")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


async def track_progress(task_id: str, verbose: bool = False):
    """Track progress via WebSocket with a progress bar"""
    try:
        if verbose:
            logger.debug("Starting WebSocket progress tracking")

        # Construct WebSocket URL correctly
        api_base = get_api_base_url()
        ws_url = api_base.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws/progress"

        if verbose:
            logger.debug(f"Connecting to WebSocket at {ws_url}")

        async with websockets.connect(ws_url) as websocket:
            # Subscribe to progress updates
            subscribe_message = {"type": "subscribe", "task_id": task_id}
            if verbose:
                logger.debug(f"Sending subscribe message: {subscribe_message}")
            await websocket.send(json.dumps(subscribe_message))

            # Initialize progress bar
            progress = typer.progressbar(
                length=100, label="🔄 Processing", show_pos=True
            )
            progress.render_progress()
            print()  # Add initial newline

            last_progress = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                    message_data = json.loads(message)

                    if verbose:
                        logger.debug(f"Received message: {message_data}")

                    if message_data.get("type") != "progress":
                        continue

                    current_progress = min(int(message_data["progress"]), 100)

                    # Update progress bar
                    if current_progress > last_progress:
                        update_amount = current_progress - last_progress
                        if verbose:
                            logger.debug(f"Progress update: {current_progress}%")
                        progress.update(update_amount)
                        print()  # Add newline after each update
                        last_progress = current_progress

                    # Exit when complete
                    if current_progress >= 100:
                        if verbose:
                            logger.debug("Progress complete")
                        progress.update(100 - progress.pos)
                        progress.render_finish()
                        print()  # Add final newline
                        break

                except asyncio.TimeoutError:
                    if verbose:
                        logger.debug("WebSocket timeout - waiting for more updates")
                    continue

    except Exception as e:
        logger.error(f"Failed to track progress: {e}")
        raise


async def async_denoise_speech(input_file: Path, verbose: bool = False):
    """Async helper for speech/vocal denoising with progress bar"""
    try:
        if verbose:
            logger.debug("Starting denoising process")

        with input_file.open("rb") as f:
            if verbose:
                logger.debug("Making API call")

            task_id = str(uuid.uuid4())

            if verbose:
                logger.debug(f"Using task ID: {task_id}")

            api_task = asyncio.create_task(
                call_api_async(
                    "denoise_speech",
                    files={"file": f},
                    data={"task_id": task_id},
                    verbose=verbose,
                )
            )

            progress_task = asyncio.create_task(track_progress(task_id, verbose))

            # Wait for both tasks to complete
            await asyncio.gather(api_task, progress_task)

            result = api_task.result()
            if "error" in result:
                raise Exception(result["error"])

            if not isinstance(result, dict) or "result" not in result:
                raise Exception("Invalid response format from API")

            return result["result"]  # Return the base64-encoded audio data

    except Exception as e:
        logger.error(f"Error during speech/vocal denoising: {e}")
        raise typer.Exit(1)


async def async_denoise_music(input_file: Path, verbose: bool = False):
    """Async helper for music denoising with progress bar"""
    try:
        if verbose:
            logger.debug("Starting music denoising")

        with input_file.open("rb") as f:
            if verbose:
                logger.debug("Making API call")

            task_id = str(uuid.uuid4())

            if verbose:
                logger.debug(f"Using task ID: {task_id}")

            api_task = asyncio.create_task(
                call_api_async(
                    "denoise_music",
                    files={"file": f},
                    data={"task_id": task_id},
                    verbose=verbose,
                )
            )

            progress_task = asyncio.create_task(track_progress(task_id, verbose))

            await asyncio.gather(api_task, progress_task)

            result = api_task.result()
            if "error" in result:
                raise Exception(result["error"])

            # Extract the base64 audio data from the result
            if isinstance(result, dict):
                if "result" in result:
                    return result["result"]  # Return just the base64 string
                elif "audio" in result:
                    return result["audio"]  # Alternative key name

            raise Exception("Invalid response format from API")

    except Exception as e:
        logger.error(f"Error during music denoising: {e}")
        raise typer.Exit(1)


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
