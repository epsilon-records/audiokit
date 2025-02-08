"""AudioKit Terminal User Interface."""

import numpy as np
import typer
from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Footer, Header, Log, Tree

from ..graph import AudioGraphManager
from ..nodes import get_available_nodes
from .widgets import AudioMonitor, PipelineGraph


class NodeList(Widget):
    """List of available nodes and their parameters."""

    def render(self) -> Panel:
        """Render the node list."""
        tree = Tree("Available Nodes")

        for name, node_class in get_available_nodes().items():
            branch = tree.add(f"[yellow]{name}[/yellow]")
            if node_class.__doc__:
                branch.add(node_class.__doc__.strip())

            params = node_class.get_parameters()
            if params:
                param_branch = branch.add("Parameters")
                for param, info in params.items():
                    param_branch.add(
                        f"{param}: [italic]{info['description']}[/italic] "
                        f"(default: {info['default']})"
                    )

        return Panel(tree, title="Node Library", border_style="green")


class AudioKitTUI(App):
    """AudioKit Terminal User Interface."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }
    
    .sidebar {
        width: 100%;
        height: 100%;
        background: $panel;
    }
    
    .main {
        width: 100%;
        height: 100%;
    }
    
    .monitor {
        dock: bottom;
        height: 15;
    }
    
    Log {
        height: 30%;
        dock: bottom;
    }
    """

    BINDINGS = [
        ("l", "toggle_log", "Toggle Log"),
        ("n", "new_pipeline", "New Pipeline"),
        ("o", "open_pipeline", "Open Pipeline"),
        ("s", "save_pipeline", "Save Pipeline"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Container(NodeList(), classes="sidebar")
        yield Container(
            PipelineGraph(AudioGraphManager()), AudioMonitor(), Log(), classes="main"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up audio monitoring."""
        self.monitor = self.query_one(AudioMonitor)
        # Start audio monitoring thread
        self.graph = self.query_one(PipelineGraph).graph
        self.graph.set_monitor_callback(self._on_audio_update)

    def _on_audio_update(self, input_data: np.ndarray, output_data: np.ndarray) -> None:
        """Handle audio monitoring updates."""
        self.monitor.update_input_levels(input_data)
        self.monitor.update_output_levels(output_data)

    def action_toggle_log(self) -> None:
        """Toggle the log visibility."""
        log = self.query_one(Log)
        log.visible = not log.visible

    def action_new_pipeline(self) -> None:
        """Create a new pipeline."""
        self.query_one(Log).write("Creating new pipeline...")
        # TODO: Implement pipeline creation

    def action_open_pipeline(self) -> None:
        """Open an existing pipeline."""
        self.query_one(Log).write("Opening pipeline...")
        # TODO: Implement pipeline loading

    def action_save_pipeline(self) -> None:
        """Save the current pipeline."""
        self.query_one(Log).write("Saving pipeline...")
        # TODO: Implement pipeline saving


def run_tui():
    """Run the AudioKit TUI."""
    app = AudioKitTUI()
    app.run()


cli = typer.Typer()


@cli.command()
def pipeline():
    """Manage audio processing pipelines."""
    run_tui()


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """AudioKit Terminal User Interface."""
    if ctx.invoked_subcommand is None:
        # No subcommand was specified, run the TUI
        run_tui()


if __name__ == "__main__":
    cli()
