"""Audio effect nodes."""

from typing import Dict, Any, Optional
import numpy as np
from scipy import signal
from .base import AudioNode


class AudioFilterNode(AudioNode):
    """Basic audio filter node."""

    def __init__(self, node_id: str, **params):
        super().__init__(node_id, **params)
        self.cutoff = params.get("cutoff", 1000)
        self.resonance = params.get("resonance", 0.707)
        self._update_coefficients()

    def _update_coefficients(self):
        """Update filter coefficients."""
        nyquist = self.sample_rate / 2
        normal_cutoff = self.cutoff / nyquist
        self.b, self.a = signal.butter(2, normal_cutoff, btype="low", analog=False)

    def process(self, input_data: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply filter to audio."""
        if input_data is None:
            return np.zeros((1024, 2))
        return signal.lfilter(self.b, self.a, input_data)

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        params = super().get_parameters()
        params.update(
            {
                "cutoff": {
                    "type": float,
                    "description": "Filter cutoff frequency in Hz",
                    "default": 1000,
                },
                "resonance": {
                    "type": float,
                    "description": "Filter resonance (Q factor)",
                    "default": 0.707,
                },
            }
        )
        return params


class CompressorNode(AudioNode):
    """Dynamic range compressor."""

    def __init__(self, node_id: str, **params):
        super().__init__(node_id, **params)
        self.threshold = params.get("threshold", -20)  # dB
        self.ratio = params.get("ratio", 4.0)
        self.attack = params.get("attack", 5)  # ms
        self.release = params.get("release", 50)  # ms
        self.makeup = params.get("makeup", 0)  # dB

        # Convert times to samples
        self.attack_samples = int(self.attack * self.sample_rate / 1000)
        self.release_samples = int(self.release * self.sample_rate / 1000)
        self.envelope = 0

    def process(self, input_data: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply compression to audio."""
        if input_data is None:
            return np.zeros((1024, 2))

        # Calculate signal level in dB
        level_db = 20 * np.log10(np.abs(input_data) + 1e-10)

        # Calculate gain reduction
        gain_reduction = np.minimum(
            0, (level_db - self.threshold) * (1 - 1 / self.ratio)
        )

        # Apply envelope
        for i in range(len(gain_reduction)):
            if gain_reduction[i] < self.envelope:
                self.envelope += (
                    gain_reduction[i] - self.envelope
                ) / self.attack_samples
            else:
                self.envelope += (
                    gain_reduction[i] - self.envelope
                ) / self.release_samples

        # Apply gain reduction and makeup gain
        output = input_data * np.power(10, (self.envelope + self.makeup) / 20)
        return output

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        params = super().get_parameters()
        params.update(
            {
                "threshold": {
                    "type": float,
                    "description": "Threshold level in dB",
                    "default": -20,
                },
                "ratio": {
                    "type": float,
                    "description": "Compression ratio",
                    "default": 4.0,
                },
                "attack": {
                    "type": float,
                    "description": "Attack time in ms",
                    "default": 5,
                },
                "release": {
                    "type": float,
                    "description": "Release time in ms",
                    "default": 50,
                },
                "makeup": {
                    "type": float,
                    "description": "Makeup gain in dB",
                    "default": 0,
                },
            }
        )
        return params


class DelayNode(AudioNode):
    """Delay effect with feedback."""

    def __init__(self, node_id: str, **params):
        super().__init__(node_id, **params)
        self.delay_time = params.get("delay_time", 500)  # ms
        self.feedback = params.get("feedback", 0.3)
        self.mix = params.get("mix", 0.5)

        # Initialize delay buffer
        self.buffer_size = int(self.delay_time * self.sample_rate / 1000)
        self.buffer = np.zeros((self.buffer_size, 2))
        self.write_pos = 0

    def process(self, input_data: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply delay effect to audio."""
        if input_data is None:
            return np.zeros((1024, 2))

        output = np.zeros_like(input_data)

        for i in range(len(input_data)):
            # Read from delay buffer
            read_pos = (self.write_pos - self.buffer_size) % self.buffer_size
            delayed = self.buffer[read_pos]

            # Write to delay buffer with feedback
            self.buffer[self.write_pos] = input_data[i] + delayed * self.feedback
            self.write_pos = (self.write_pos + 1) % self.buffer_size

            # Mix dry and wet signals
            output[i] = input_data[i] * (1 - self.mix) + delayed * self.mix

        return output

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        params = super().get_parameters()
        params.update(
            {
                "delay_time": {
                    "type": float,
                    "description": "Delay time in milliseconds",
                    "default": 500,
                },
                "feedback": {
                    "type": float,
                    "description": "Feedback amount (0-1)",
                    "default": 0.3,
                },
                "mix": {
                    "type": float,
                    "description": "Wet/dry mix (0-1)",
                    "default": 0.5,
                },
            }
        )
        return params
