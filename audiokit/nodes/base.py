"""Base audio processing node."""

from typing import Dict, Any, Optional
import numpy as np


class AudioNode:
    """Base class for audio processing nodes."""

    def __init__(self, node_id: str, **params):
        """Initialize the node."""
        self.id = node_id
        self.params = params
        self.input_buffer = None
        self.output_buffer = None
        self.sample_rate = params.get("sample_rate", 44100)

    def process(self, input_data: Optional[np.ndarray] = None) -> np.ndarray:
        """Process audio data."""
        raise NotImplementedError("Subclasses must implement process()")

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Get the node's parameters."""
        return {
            "sample_rate": {
                "type": int,
                "description": "Sample rate in Hz",
                "default": 44100,
            }
        }
