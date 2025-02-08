"""AudioKit Terminal User Interface."""

import numpy as np
import typer
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.events import Click
from textual.widget import Widget
from textual.widgets import Footer, Header, Input, Log, Tree
from textual.widgets.tree import TreeNode

from ..graph import AudioGraphManager
from ..nodes import get_available_nodes
from .widgets import AudioMonitor, PipelineGraph
from .widgets.context_menu import NodeContextMenu


class NodeList(Widget):
    """List of available nodes and their parameters."""

    DEFAULT_CSS = """
    NodeList {
        layout: grid;
        grid-size: 1;
        grid-rows: auto 1fr;
    }
    
    NodeList Input {
        dock: top;
        margin: 1 1;
    }
    """

    ICONS = {
        "input": "🎤",  # Microphone for input nodes
        "output": "🔊",  # Speaker for output nodes
        "effect": "🎛️",  # Knobs for effect nodes
        "generator": "🎹",  # Piano for generator nodes
        "analyzer": "📊",  # Graph for analyzer nodes
        "mixer": "🎚️",  # Fader for mixer nodes
        "parameter": "⚙️",  # Gear for parameters
        "category": "📁",  # Folder for categories
        "active": "🟢",
        "inactive": "⚪",
    }

    BINDINGS = [
        Binding("ctrl+f", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear"),
    ]

    def __init__(self):
        super().__init__()
        self.search_input = Input(placeholder="Search nodes...")
        self._tree = Tree(Text.assemble("📦 ", ("Available Nodes", "bold")))
        self.active_nodes = set()  # Track active nodes
        self._filter_text = ""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield self.search_input
        yield self._tree

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self._filter_text = event.value.lower()
        self._refresh_tree()

    def on_click(self, event: Click) -> None:
        """Handle node clicks."""
        if isinstance(event.target, TreeNode):
            node_id = event.target.data.get("node_id")
            if node_id:
                if event.button == 2:  # Right click
                    # Show context menu
                    menu = NodeContextMenu(node_id, event.screen_offset)
                    self.mount(menu)
                else:
                    # Toggle node active state
                    if node_id in self.active_nodes:
                        self.active_nodes.remove(node_id)
                    else:
                        self.active_nodes.add(node_id)
                    self._refresh_tree()

    def on_node_context_menu_selected(self, event: NodeContextMenu.Selected) -> None:
        """Handle context menu selection."""
        if event.action == "Add to Pipeline":
            # TODO: Implement pipeline integration
            self.notify(f"Adding {event.node_id} to pipeline...")
        elif event.action == "View Documentation":
            # TODO: Show node documentation
            self.notify(f"Viewing docs for {event.node_id}...")
        elif event.action == "Configure Parameters":
            # TODO: Open parameter configuration
            self.notify(f"Configuring {event.node_id}...")
        elif event.action == "Copy Node ID":
            # TODO: Copy to clipboard
            self.notify(f"Copied {event.node_id} to clipboard")

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.search_input.focus()

    def action_clear_search(self) -> None:
        """Clear the search input."""
        self.search_input.value = ""
        self._filter_text = ""
        self._refresh_tree()

    def _refresh_tree(self) -> None:
        """Refresh the tree with current filter and states."""
        self._tree.clear()
        categories = {}
        for name, node_class in get_available_nodes().items():
            # Apply search filter
            if self._filter_text and self._filter_text not in name.lower():
                continue

            category = getattr(node_class, "category", "misc")
            if category not in categories:
                categories[category] = []
            categories[category].append((name, node_class))

        for category, nodes in sorted(categories.items()):
            label = Text.assemble(
                (self.ICONS["category"], "bold"), f" {category.title()}"
            )
            category_branch = self._tree.root.add(label)
            # Set expanded state after creation
            category_branch.expanded = not bool(self._filter_text)

            for name, node_class in sorted(nodes):
                node_type = name.lower()
                icon = next(
                    (v for k, v in self.ICONS.items() if k in node_type),
                    self.ICONS["effect"],
                )

                # Add status indicator
                status_icon = self.ICONS[
                    "active" if name in self.active_nodes else "inactive"
                ]

                branch = category_branch.add(
                    Text.assemble(
                        (icon, "bold"),
                        (status_icon, "bold"),
                        f" [yellow]{name}[/yellow]",
                    ),
                    data={"node_id": name},  # Store node ID for click handling
                )

                if node_class.__doc__:
                    branch.add(
                        "📝 " + node_class.__doc__.strip(),
                    )

                params = node_class.get_parameters()
                if params:
                    label = Text.assemble(
                        (self.ICONS["parameter"], "bold"), " Parameters"
                    )
                    param_branch = branch.add(label)
                    param_branch.expanded = False

                    for param, info in params.items():
                        param_branch.add(
                            Text.assemble(
                                "⚡ ",
                                (param, "bold cyan"),
                                ": ",
                                (info["description"], "italic"),
                                "\n  ",
                                ("default: ", "dim"),
                                (str(info["default"]), "green"),
                            ),
                        )


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
