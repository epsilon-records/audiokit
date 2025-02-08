"""Audio processing graph manager."""

from typing import Any
from loguru import logger


class AudioGraphManager:
    """Manages a graph of audio processing nodes."""

    def __init__(self):
        """Initialize the graph manager."""
        self.nodes = {}
        self.connections = []
        logger.debug("Created new AudioGraphManager")

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
