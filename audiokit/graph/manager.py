"""Audio processing graph manager."""

from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import sounddevice as sd
from loguru import logger

from ..nodes.base import AudioNode


class AudioGraphManager:
    """Manages a graph of audio processing nodes."""

    def __init__(self):
        """Initialize the graph manager."""
        self.nodes: Dict[str, AudioNode] = {}
        self.connections: List[Tuple[str, str]] = []
        self.stream: Optional[sd.Stream] = None
        self.monitor_callback: Optional[Callable[[np.ndarray, np.ndarray], None]] = None
        self._setup_audio()
        logger.debug("Created new AudioGraphManager")

    def _setup_audio(self) -> None:
        """Set up audio stream."""

        def callback(
            indata: np.ndarray,
            outdata: np.ndarray,
            frames: int,
            time: sd.CallbackFlags,
            status: sd.CallbackFlags,
        ) -> None:
            """Audio callback."""
            if status:
                print(f"Audio callback status: {status}")

            # Process audio through graph
            output = self._process_audio(indata)
            outdata[:] = output

            # Send audio to monitor if callback is set
            if self.monitor_callback:
                self.monitor_callback(indata, outdata)

        self.stream = sd.Stream(
            channels=2,
            callback=callback,
            samplerate=44100,
            blocksize=1024,
            dtype=np.float32,
        )
        self.stream.start()

    def add_node(self, node: Any) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        logger.debug(f"Added node {node.id} to graph")

    def connect(self, from_id: str, to_id: str) -> None:
        """Connect two nodes in the graph."""
        if from_id not in self.nodes:
            raise ValueError(f"Source node {from_id} not found")
        if to_id not in self.nodes:
            raise ValueError(f"Target node {to_id} not found")

        self.connections.append((from_id, to_id))
        logger.debug(f"Connected {from_id} to {to_id}")

    def get_node(self, node_id: str) -> Any:
        """Get a node by its ID."""
        return self.nodes.get(node_id)

    def get_connections(self) -> list:
        """Get all connections in the graph."""
        return self.connections

    def process(self) -> None:
        """Process audio through the graph."""
        # TODO: Implement audio processing
        pass

    def set_monitor_callback(
        self, callback: Callable[[np.ndarray, np.ndarray], None]
    ) -> None:
        """Set callback for audio monitoring."""
        self.monitor_callback = callback

    def _process_audio(self, input_data: np.ndarray) -> np.ndarray:
        """Process audio through the graph."""
        # ... rest of implementation ...
