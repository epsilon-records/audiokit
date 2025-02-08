"""Custom widgets for AudioKit TUI."""

from typing import Optional

import numpy as np
import plotext as plt
from rich.panel import Panel
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ..graph import AudioGraphManager


class AudioMeter(Widget):
    """Real-time audio level meter."""

    level = reactive(0.0)

    def __init__(self, channels: int = 2):
        super().__init__()
        self.channels = channels
        self.peak_hold = np.zeros(channels)

    def render(self) -> Panel:
        """Render the meter."""
        width = self.size.width - 4
        meter = Text()

        for ch in range(self.channels):
            level_width = int(self.level * width)
            peak_width = int(self.peak_hold[ch] * width)

            meter.append("▐" * level_width, "green")
            meter.append("▐" * (peak_width - level_width), "yellow")
            meter.append("▐" * (width - peak_width), "gray")
            meter.append("\n")

        return Panel(meter, title="Levels", border_style="blue")


class WaveformDisplay(Static):
    """Real-time waveform display."""

    def __init__(self):
        super().__init__()
        self.buffer = np.zeros(1024)
        plt.clf()
        plt.plot_size(60, 20)

    def update_buffer(self, data: np.ndarray):
        """Update the display buffer."""
        self.buffer = data
        self.refresh()

    def render(self) -> Panel:
        """Render the waveform."""
        plt.clf()
        plt.plot(self.buffer)
        plt.title("Waveform")
        return Panel(plt.build(), border_style="magenta")


class PipelineGraph(Widget):
    """Enhanced pipeline graph visualization."""

    def __init__(self, graph: AudioGraphManager):
        super().__init__()
        self.graph = graph
        self.selected_node: Optional[str] = None

    def render(self) -> Panel:
        """Render the graph with interactive elements."""
        # Create ASCII graph representation
        nodes = list(self.graph.nodes.items())
        edges = self.graph.connections

        # Calculate node positions
        width = self.size.width - 4
        height = self.size.height - 4
        positions = {}

        for i, (node_id, node) in enumerate(nodes):
            x = (i + 1) * width // (len(nodes) + 1)
            y = height // 2
            positions[node_id] = (x, y)

        # Draw connections
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        for from_id, to_id in edges:
            x1, y1 = positions[from_id]
            x2, y2 = positions[to_id]
            self._draw_line(canvas, x1, y1, x2, y2)

        # Draw nodes
        for node_id, pos in positions.items():
            x, y = pos
            node_type = self.graph.nodes[node_id].__class__.__name__
            style = "bold cyan" if node_id == self.selected_node else "cyan"
            self._draw_node(canvas, x, y, node_id, node_type, style)

        # Convert to Rich text
        text = Text()
        for row in canvas:
            text.append("".join(row) + "\n")

        return Panel(text, title="Pipeline Graph", border_style="cyan")

    def _draw_line(self, canvas, x1, y1, x2, y2):
        """Draw a line between two points."""
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return

        x_inc = dx / steps
        y_inc = dy / steps

        x, y = x1, y1
        for _ in range(int(steps)):
            if 0 <= int(y) < len(canvas) and 0 <= int(x) < len(canvas[0]):
                canvas[int(y)][int(x)] = "─" if abs(dx) > abs(dy) else "│"
            x += x_inc
            y += y_inc

    def _draw_node(self, canvas, x, y, node_id, node_type, style):
        """Draw a node with its label."""
        label = f"[{style}]{node_id}[/]"
        if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
            canvas[y][x] = "●"

        if y + 1 < len(canvas):
            for i, char in enumerate(label):
                if x + i < len(canvas[0]):
                    canvas[y + 1][x + i] = char
