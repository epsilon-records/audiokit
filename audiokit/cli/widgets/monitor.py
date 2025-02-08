"""Real-time audio monitoring widgets."""

import numpy as np
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget

from audiokit.cli.widgets.visualizers import SpectrumAnalyzer, VUMeter, WaveformDisplay


class AudioMonitor(Widget):
    """Real-time audio monitoring widget."""

    DEFAULT_CSS = """
    AudioMonitor {
        height: auto;
        width: 100%;
        border: solid green;
    }
    """

    class LevelUpdate(Message):
        """Level update message."""

        def __init__(self, levels: np.ndarray) -> None:
            self.levels = levels
            super().__init__()

    def __init__(self):
        super().__init__()
        self.input_levels = np.zeros(2)
        self.output_levels = np.zeros(2)
        self.peak_hold = np.zeros(2)
        self.decay_rate = 0.95

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield VUMeter(style="modern")
        yield WaveformDisplay()
        yield SpectrumAnalyzer()

    def on_mount(self) -> None:
        """Initialize components."""
        self.vu_meter = self.query_one(VUMeter)
        self.waveform = self.query_one(WaveformDisplay)
        self.spectrum = self.query_one(SpectrumAnalyzer)
        self.set_interval(1 / 30, self.update_displays)

    def update_levels(self) -> None:
        """Update level meters with decay."""
        self.input_levels *= self.decay_rate
        self.output_levels *= self.decay_rate
        self.peak_hold = np.maximum(
            self.peak_hold * self.decay_rate,
            np.maximum(self.input_levels, self.output_levels),
        )
        self.refresh()

    def render(self) -> Panel:
        """Render the monitor."""
        width = self.size.width - 4
        content = []

        # Input meters
        content.append(Text("Input:"))
        for ch in range(2):
            meter = Text()
            level_width = int(self.input_levels[ch] * width)
            peak_width = int(self.peak_hold[ch] * width)

            meter.append("▐" * level_width, "green")
            meter.append("▐" * (peak_width - level_width), "yellow")
            meter.append("▐" * (width - peak_width), "gray")
            content.append(meter)

        content.append(Text(""))  # Spacer

        # Output meters
        content.append(Text("Output:"))
        for ch in range(2):
            meter = Text()
            level_width = int(self.output_levels[ch] * width)
            peak_width = int(self.peak_hold[ch] * width)

            meter.append("▐" * level_width, "green")
            meter.append("▐" * (peak_width - level_width), "yellow")
            meter.append("▐" * (width - peak_width), "gray")
            content.append(meter)

        return Panel(
            Group(*content),
            title="Audio Monitor",
            border_style="green",
        )

    def update_input_levels(self, data: np.ndarray) -> None:
        """Update input visualization."""
        self.waveform.update_buffer(data)
        self.spectrum.update_buffer(data)
        self.vu_meter.update_level(np.abs(data).max())

    def update_output_levels(self, data: np.ndarray) -> None:
        """Update output visualization."""
        # Could add output visualizers here
        pass

    def update_displays(self) -> None:
        """Update all displays."""
        self.update_levels()
        self.refresh()
