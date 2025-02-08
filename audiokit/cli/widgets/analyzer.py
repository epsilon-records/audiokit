"""Audio analysis widgets."""

import librosa
import numpy as np
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.widget import Widget


class AudioAnalyzer(Widget):
    """Real-time audio analysis widget."""

    DEFAULT_CSS = """
    AudioAnalyzer {
        height: 15;
        width: 100%;
        border: solid purple;
    }
    """

    def __init__(self):
        super().__init__()
        self.sample_rate = 44100
        self.buffer_size = 4096
        self.buffer = np.zeros(self.buffer_size)
        self.features = {
            "rms": 0.0,
            "centroid": 0.0,
            "flatness": 0.0,
            "rolloff": 0.0,
            "onset_strength": 0.0,
            "tempo": 0.0,
            "pitch": 0.0,
        }
        self.onset_detector = librosa.onset.onset_strength
        self.tempo_detector = librosa.beat.tempo

    def update_buffer(self, data: np.ndarray) -> None:
        """Update analysis buffer."""
        if len(data.shape) > 1:
            data = data.mean(axis=1)  # Mix to mono
        self.buffer = np.roll(self.buffer, -len(data))
        self.buffer[-len(data) :] = data
        self._analyze()
        self.refresh()

    def _analyze(self) -> None:
        """Perform audio analysis."""
        # Basic features
        self.features["rms"] = np.sqrt(np.mean(self.buffer**2))

        # Spectral features
        if np.any(self.buffer):
            spec = np.abs(librosa.stft(self.buffer))
            self.features["centroid"] = librosa.feature.spectral_centroid(S=spec)[0, 0]
            self.features["flatness"] = librosa.feature.spectral_flatness(S=spec)[0, 0]
            self.features["rolloff"] = librosa.feature.spectral_rolloff(S=spec)[0, 0]

            # Rhythm features
            onset_env = self.onset_detector(y=self.buffer, sr=self.sample_rate)
            self.features["onset_strength"] = np.mean(onset_env)
            self.features["tempo"] = self.tempo_detector(
                onset_envelope=onset_env, sr=self.sample_rate
            )[0]

            # Pitch detection
            pitches, magnitudes = librosa.piptrack(y=self.buffer, sr=self.sample_rate)
            if magnitudes.any():
                max_mag_idx = magnitudes.argmax()
                self.features["pitch"] = pitches.flatten()[max_mag_idx]

    def render(self) -> Panel:
        """Render analysis results."""
        content = []

        # Format features
        content.append(Text("Audio Analysis:", style="bold magenta"))
        content.append(Text(f"RMS Level: {self.features['rms']:.2f} dB"))
        content.append(Text(f"Spectral Centroid: {self.features['centroid']:.0f} Hz"))
        content.append(Text(f"Spectral Flatness: {self.features['flatness']:.2f}"))
        content.append(Text(f"Spectral Rolloff: {self.features['rolloff']:.0f} Hz"))
        content.append(Text(f"Onset Strength: {self.features['onset_strength']:.2f}"))
        content.append(Text(f"Tempo: {self.features['tempo']:.0f} BPM"))

        if self.features["pitch"] > 0:
            note = librosa.hz_to_note(self.features["pitch"])
            content.append(Text(f"Pitch: {note} ({self.features['pitch']:.1f} Hz)"))

        return Panel(
            Group(*content),
            title="Audio Analysis",
            border_style="purple",
        )
