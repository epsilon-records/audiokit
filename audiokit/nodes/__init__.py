"""Audio processing nodes."""

from typing import Dict, Any
from .base import AudioNode
from .io import AudioInputNode, AudioOutputNode
from .effects import AudioFilterNode


def get_available_nodes() -> Dict[str, type]:
    """Get all available node types."""
    return {
        "AudioInputNode": AudioInputNode,
        "AudioOutputNode": AudioOutputNode,
        "AudioFilterNode": AudioFilterNode,
    }


__all__ = [
    "AudioNode",
    "AudioInputNode",
    "AudioOutputNode",
    "AudioFilterNode",
    "get_available_nodes",
]
