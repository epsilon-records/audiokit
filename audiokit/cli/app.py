"""AudioKit Terminal User Interface."""

from rich.graph import Graph
from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Footer, Header, Log, Tree

from ..graph import AudioGraphManager
from ..nodes import get_available_nodes


class PipelineGraph(Widget):
    """Visual representation of the audio pipeline."""

    def __init__(self, graph: AudioGraphManager):
        super().__init__()
        self.graph = graph

    def render(self) -> Panel:
        """Render the pipeline graph."""
        # Create graph visualization
        graph = Graph()

        # Add nodes
        for node_id, node in self.graph.nodes.items():
            node_type = node.__class__.__name__
            graph.add_node(node_id, node_type)

        # Add connections
        for from_id, to_id in self.graph.connections:
            graph.add_edge(from_id, to_id)

        return Panel(graph, title="Pipeline Graph", border_style="cyan")


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


class AudioKitApp(App):
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
        yield Container(PipelineGraph(AudioGraphManager()), Log(), classes="main")
        yield Footer()

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


def run():
    """Run the AudioKit TUI."""
    app = AudioKitApp()
    app.run()


if __name__ == "__main__":
    run()
