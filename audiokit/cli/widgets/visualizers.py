"""Audio visualization widgets."""

from typing import Optional

import numpy as np
import plotext as plt
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from scipy import signal
from textual.widget import Widget


class WaveformDisplay(Widget):
    """Real-time waveform display."""

    class Config:
        """Waveform display configuration."""

        def __init__(self):
            self.window_size = 1024
            self.plot_width = 80
            self.plot_height = 8
            self.style = "line"  # "line", "dots", "bars"
            self.color = "cyan"
            self.background = "black"

    DEFAULT_CSS = """
    WaveformDisplay {
        height: 10;
        width: 100%;
        border: solid blue;
    }
    """

    def __init__(self, config: Optional[Config] = None):
        super().__init__()
        self.config = config or self.Config()
        self.buffer = np.zeros(self.config.window_size)

    def on_mount(self) -> None:
        """Configure plot."""
        plt.clf()
        plt.plot_size(self.config.plot_width, self.config.plot_height)
        plt.theme("dark")

    def update_buffer(self, data: np.ndarray) -> None:
        """Update the display buffer."""
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Mix to mono
        self.buffer = np.roll(self.buffer, -len(data))
        self.buffer[-len(data) :] = data
        self.refresh()

    def render(self) -> Panel:
        """Render the waveform."""
        plt.clf()
        if self.config.style == "line":
            plt.plot(self.buffer, color=self.config.color)
        elif self.config.style == "dots":
            plt.scatter(range(len(self.buffer)), self.buffer, color=self.config.color)
        elif self.config.style == "bars":
            plt.bar(range(len(self.buffer)), self.buffer, color=self.config.color)
        plt.title("Waveform")
        plt.xlim(0, self.config.window_size)
        plt.ylim(-1, 1)
        return Panel(plt.build(), title="Waveform", border_style="blue")


class SpectrumAnalyzer(Widget):
    """Real-time spectrum analyzer."""

    class Config:
        """Spectrum analyzer configuration."""

        def __init__(self):
            self.fft_size = 2048
            self.sample_rate = 44100
            self.plot_width = 80
            self.plot_height = 10
            self.smoothing = 0.8
            self.min_freq = 20
            self.max_freq = 20000
            self.min_db = -80
            self.max_db = 0
            self.scale = "log"  # "log" or "linear"
            self.color_map = "viridis"

    DEFAULT_CSS = """
    SpectrumAnalyzer {
        height: 12;
        width: 100%;
        border: solid magenta;
    }
    """

    def __init__(self, config: Optional[Config] = None):
        super().__init__()
        self.config = config or self.Config()
        self.buffer = np.zeros(self.config.fft_size)
        self.spectrum = np.zeros(self.config.fft_size // 2)

    def on_mount(self) -> None:
        """Configure plot."""
        plt.clf()
        plt.plot_size(self.config.plot_width, self.config.plot_height)
        plt.theme("dark")

    def update_buffer(self, data: np.ndarray) -> None:
        """Update the spectrum display."""
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Mix to mono
        self.buffer = np.roll(self.buffer, -len(data))
        self.buffer[-len(data) :] = data

        # Calculate spectrum
        window = signal.windows.hann(self.config.fft_size)
        spectrum = np.abs(np.fft.rfft(self.buffer * window))
        spectrum = 20 * np.log10(spectrum + 1e-10)

        # Smooth spectrum
        self.spectrum = (
            self.config.smoothing * self.spectrum
            + (1 - self.config.smoothing) * spectrum
        )
        self.refresh()

    def render(self) -> Panel:
        """Render the spectrum analyzer."""
        plt.clf()

        # Calculate frequency axis
        freqs = np.linspace(
            self.config.min_freq, self.config.max_freq, len(self.spectrum)
        )

        # Plot spectrum
        if self.config.scale == "log":
            plt.plot(freqs, self.spectrum)
        else:
            plt.plot(freqs, self.spectrum)
        plt.title("Spectrum Analyzer")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude (dB)")
        plt.xlim(self.config.min_freq, self.config.max_freq)
        plt.ylim(self.config.min_db, self.config.max_db)

        return Panel(plt.build(), title="Spectrum", border_style="magenta")


class VUMeter(Widget):
    """Professional VU meter with multiple styles."""

    DEFAULT_CSS = """
    VUMeter {
        height: 5;
        width: 100%;
        border: solid yellow;
    }
    """

    STYLES = {
        "classic": {
            "chars": "▁▂▃▄▅▆▇█",
            "colors": ["gray", "green", "yellow", "red"],
            "thresholds": [-60, -12, -6, 0],
        },
        "modern": {
            "chars": "⣀⣄⣤⣦⣶⣷⣿",
            "colors": ["blue", "cyan", "green", "yellow", "red"],
            "thresholds": [-50, -40, -30, -20, -10],
        },
        "minimal": {
            "chars": "─═║│",
            "colors": ["gray", "green", "yellow"],
            "thresholds": [-40, -20, -3],
        },
        "retro": {
            "chars": "◦⊙●",
            "colors": ["gray", "yellow", "red"],
            "thresholds": [-40, -20, -3],
        },
        "digital": {
            "chars": "0123456789ABCDEF",
            "colors": ["blue", "cyan", "green", "yellow", "red"],
            "thresholds": [-50, -40, -30, -20, -10],
        },
        "pro": {
            "chars": "▏▎▍▌▋▊▉█",
            "colors": ["gray", "blue", "cyan", "green", "yellow", "red"],
            "thresholds": [-60, -48, -36, -24, -12, -6],
        },
    }

    def __init__(self, style="classic"):
        super().__init__()
        self.style = style
        self.level = -60
        self.peak = -60
        self.peak_hold_time = 30
        self.peak_hold_counter = 0
        self.style_config = self.STYLES[style]

    def update_level(self, level: float) -> None:
        """Update meter level."""
        self.level = 20 * np.log10(abs(level) + 1e-10)
        if self.level > self.peak:
            self.peak = self.level
            self.peak_hold_counter = self.peak_hold_time
        elif self.peak_hold_counter > 0:
            self.peak_hold_counter -= 1
        else:
            self.peak = max(self.level, self.peak - 0.5)
        self.refresh()

    def render(self) -> Panel:
        """Render the VU meter."""
        width = self.size.width - 4
        meter = Text()

        # Get style configuration
        chars = self.style_config["chars"]
        colors = self.style_config["colors"]
        thresholds = self.style_config["thresholds"]

        # Calculate meter segments
        segments = width // len(chars[0])
        db_per_segment = 60 / segments

        # Draw meter
        for i in range(segments):
            db = -60 + i * db_per_segment
            char_idx = int((len(chars) - 1) * i / segments)

            # Determine color based on level
            color = colors[0]
            for threshold, col in zip(thresholds, colors):
                if db > threshold:
                    color = col

            # Draw segment
            if db <= self.level:
                meter.append(chars[char_idx], color)
            else:
                meter.append(chars[0], "gray")

        # Add peak indicator
        peak_pos = int((self.peak + 60) / db_per_segment)
        if 0 <= peak_pos < segments:
            meter.stylize("reverse", peak_pos, peak_pos + 1)

        # Add numeric display
        level_text = f"{self.level:>6.1f} dB"
        peak_text = f"Peak: {self.peak:>6.1f} dB"

        return Panel(
            Group(meter, Text(f"{level_text} | {peak_text}", justify="right")),
            title=f"VU Meter ({self.style})",
            border_style="yellow",
        )
