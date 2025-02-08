"""Input/Output nodes."""

from typing import Any, Dict, Optional

import numpy as np
import sounddevice as sd

from .base import AudioNode


class AudioInputNode(AudioNode):
    """Audio input node (e.g., microphone)."""

    def __init__(self, node_id: str, **params):
        super().__init__(node_id, **params)
        self.channels = params.get("channels", 2)
        self.stream = sd.InputStream(
            channels=self.channels,
            samplerate=self.sample_rate,
            dtype=np.float32,
            blocksize=1024,
            latency="low",
        )
        self.stream.start()

    def process(self, input_data: Optional[np.ndarray] = None) -> np.ndarray:
        """Capture audio from input device."""
        data, overflowed = self.stream.read(1024)
        return data

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        params = super().get_parameters()
        params.update(
            {
                "channels": {
                    "type": int,
                    "description": "Number of input channels",
                    "default": 2,
                }
            }
        )
        return params


class AudioOutputNode(AudioNode):
    """Audio output node (e.g., speakers)."""

    def __init__(self, node_id: str, **params):
        super().__init__(node_id, **params)
        self.channels = params.get("channels", 2)
        # Eagerly instantiate and start the output stream
        self._stream = sd.OutputStream(
            channels=self.channels, samplerate=self.sample_rate, dtype=np.float32
        )
        self._stream.start()

    def process(self, input_data: Optional[np.ndarray] = None) -> np.ndarray:
        """Output audio to device."""
        if input_data is not None:
            self._stream.write(input_data)
        return input_data
