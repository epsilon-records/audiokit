"""Interactive pipeline graph widget."""

import math
from typing import Dict, Optional, Tuple

from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.geometry import Offset
from textual.message import Message
from textual.widget import Widget

from ...graph import AudioGraphManager


class NodeDragMessage(Message):
    """Node drag message."""

    def __init__(self, node_id: str, position: Tuple[int, int]) -> None:
        self.node_id = node_id
        self.position = position
        super().__init__()


class ConnectionMessage(Message):
    """Connection creation/deletion message."""

    def __init__(self, from_id: str, to_id: str, action: str) -> None:
        self.from_id = from_id
        self.to_id = to_id
        self.action = action  # "create" or "delete"
        super().__init__()


class PipelineGraph(Widget):
    """Interactive pipeline graph visualization."""

    DEFAULT_CSS = """
    PipelineGraph {
        min-height: 20;
        border: solid $accent;
    }
    """

    def __init__(self, graph: AudioGraphManager):
        super().__init__()
        self.graph = graph
        self.node_positions: Dict[str, Tuple[int, int]] = {}
        self.dragging: Optional[str] = None
        self.drag_start: Optional[Tuple[int, int]] = None
        self.hover_node: Optional[str] = None
        self.selected_node: Optional[str] = None
        self.connecting_from: Optional[str] = None
        self.active_nodes = set()  # Nodes currently processing audio
        self.cpu_usage: Dict[str, float] = {}  # CPU usage per node
        self.signal_levels: Dict[str, float] = {}  # Signal levels per node

    def on_mount(self) -> None:
        """Initialize node positions."""
        self._layout_nodes()
        self.set_interval(1 / 30, self._update_metrics)  # 30 FPS update

    def _layout_nodes(self) -> None:
        """Layout nodes using force-directed algorithm."""
        nodes = list(self.graph.nodes.items())
        if not nodes:
            return

        # Initialize random positions if not set
        width = self.size.width - 8
        height = self.size.height - 4

        for node_id, _ in nodes:
            if node_id not in self.node_positions:
                x = 4 + width * (0.25 + 0.5 * math.random())
                y = 2 + height * (0.25 + 0.5 * math.random())
                self.node_positions[node_id] = (x, y)

        # Apply force-directed layout
        for _ in range(50):  # Number of iterations
            forces = {node_id: [0.0, 0.0] for node_id, _ in nodes}

            # Repulsive forces between all nodes
            for i, (id1, _) in enumerate(nodes):
                pos1 = self.node_positions[id1]
                for id2, _ in nodes[i + 1 :]:
                    pos2 = self.node_positions[id2]
                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    dist = math.sqrt(dx * dx + dy * dy) + 0.01
                    force = 100 / (dist * dist)  # Repulsive force
                    forces[id1][0] += force * dx / dist
                    forces[id1][1] += force * dy / dist
                    forces[id2][0] -= force * dx / dist
                    forces[id2][1] -= force * dy / dist

            # Attractive forces along connections
            for from_id, to_id in self.graph.connections:
                pos1 = self.node_positions[from_id]
                pos2 = self.node_positions[to_id]
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                dist = math.sqrt(dx * dx + dy * dy) + 0.01
                force = dist * 0.1  # Attractive force
                forces[from_id][0] += force * dx / dist
                forces[from_id][1] += force * dy / dist
                forces[to_id][0] -= force * dx / dist
                forces[to_id][1] -= force * dy / dist

            # Update positions
            for node_id in self.node_positions:
                x, y = self.node_positions[node_id]
                fx, fy = forces[node_id]
                # Constrain to bounds
                x = max(4, min(width + 4, x + fx * 0.1))
                y = max(2, min(height + 2, y + fy * 0.1))
                self.node_positions[node_id] = (x, y)

    def _update_metrics(self) -> None:
        """Update node metrics."""
        self.active_nodes = self.graph.get_active_nodes()
        self.cpu_usage = self.graph.get_node_cpu_usage()
        self.signal_levels = self.graph.get_node_signal_levels()
        self.refresh()

    def on_click(self, event: events.Click) -> None:
        """Handle mouse clicks."""
        # Check for node clicks
        clicked_node = None
        for node_id, pos in self.node_positions.items():
            if self._is_over_node(event.offset, pos):
                clicked_node = node_id
                break

        if clicked_node:
            if event.button == 1:  # Left click
                if self.connecting_from:
                    # Complete connection
                    if clicked_node != self.connecting_from:
                        self.post_message(
                            ConnectionMessage(
                                self.connecting_from, clicked_node, "create"
                            )
                        )
                    self.connecting_from = None
                else:
                    # Start connection or select node
                    if event.shift:
                        self.connecting_from = clicked_node
                    else:
                        self.selected_node = clicked_node
            elif event.button == 3:  # Right click
                # Delete connection if it exists
                if self.selected_node and clicked_node:
                    self.post_message(
                        ConnectionMessage(self.selected_node, clicked_node, "delete")
                    )

        self.refresh()

    def render(self) -> Panel:
        """Render the pipeline graph."""
        # Create canvas
        width = self.size.width - 4
        height = self.size.height - 2
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # Draw connections
        for from_id, to_id in self.graph.connections:
            if from_id in self.node_positions and to_id in self.node_positions:
                x1, y1 = self.node_positions[from_id]
                x2, y2 = self.node_positions[to_id]
                active = from_id in self.active_nodes and to_id in self.active_nodes
                signal = min(
                    self.signal_levels.get(from_id, 0), self.signal_levels.get(to_id, 0)
                )
                self._draw_connection(canvas, x1, y1, x2, y2, active, signal)

        # Draw temporary connection while dragging
        if self.connecting_from and self.hover_node:
            x1, y1 = self.node_positions[self.connecting_from]
            x2, y2 = self.node_positions[self.hover_node]
            self._draw_connection(canvas, x1, y1, x2, y2, False, 0, temp=True)

        # Draw nodes
        for node_id, pos in self.node_positions.items():
            x, y = pos
            node = self.graph.nodes[node_id]
            node_type = node.__class__.__name__

            # Determine node style
            style = "bold cyan"
            if node_id == self.selected_node:
                style = "bold white on blue"
            elif node_id == self.hover_node:
                style = "bold white on cyan"
            elif node_id == self.connecting_from:
                style = "bold yellow"
            elif node_id in self.active_nodes:
                style = "bold green"

            # Add metrics
            cpu = self.cpu_usage.get(node_id, 0)
            signal = self.signal_levels.get(node_id, 0)
            label = (
                f"{node_id} ({node_type})\n" f"CPU: {cpu:.1f}% | Level: {signal:.1f}dB"
            )

            self._draw_node(canvas, x, y, label, style)

        # Convert to Rich text
        text = Text()
        for row in canvas:
            text.append("".join(row) + "\n")

        title = "Pipeline Graph"
        if self.connecting_from:
            title += " (Shift+Click to connect nodes)"
        elif self.selected_node:
            title += f" (Selected: {self.selected_node})"

        return Panel(text, title=title, border_style="cyan")

    def _draw_connection(
        self,
        canvas: list,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        active: bool,
        signal: float,
        temp: bool = False,
    ) -> None:
        """Draw a connection line with optional signal flow animation."""
        style = "green" if active else "gray"
        char = "═" if active else "─"

        # Draw basic line
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return

        x_inc = dx / steps
        y_inc = dy / steps

        x, y = x1, y1
        for i in range(int(steps)):
            if 0 <= int(y) < len(canvas) and 0 <= int(x) < len(canvas[0]):
                canvas[int(y)][int(x)] = f"[{style}]{char}[/]"
            x += x_inc
            y += y_inc

        # Draw signal level
        if not temp:
            signal_char = "═" if signal > 0 else "─"
            signal_style = "green" if signal > 0 else "gray"
            signal_steps = int(abs(signal) * 0.5)
            signal_x_inc = dx / signal_steps if signal_steps > 0 else 0
            signal_y_inc = dy / signal_steps if signal_steps > 0 else 0
            signal_x, signal_y = x1, y1
            for i in range(signal_steps):
                if 0 <= int(signal_y) < len(canvas) and 0 <= int(signal_x) < len(
                    canvas[0]
                ):
                    canvas[int(signal_y)][int(signal_x)] = (
                        f"[{signal_style}]{signal_char}[/]"
                    )
                signal_x += signal_x_inc
                signal_y += signal_y_inc

    def _draw_node(self, canvas: list, x: int, y: int, label: str, style: str) -> None:
        """Draw a node with its label."""
        if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
            canvas[y][x] = f"[{style}]●[/]"

        # Draw label below node
        lines = label.split("\n")
        for i, line in enumerate(lines):
            if y + 1 + i < len(canvas):
                for j, char in enumerate(line):
                    if x - len(line) // 2 + j < len(canvas[0]):
                        canvas[y + 1 + i][x - len(line) // 2 + j] = (
                            f"[{style}]{char}[/]"
                        )

    def _is_over_node(self, offset: Offset, pos: Tuple[int, int]) -> bool:
        """Check if mouse is over a node."""
        return abs(offset.x - pos[0]) < 2 and abs(offset.y - pos[1]) < 2
