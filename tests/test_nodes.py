"""Test audio processing nodes."""

import pytest
import numpy as np
from audiokit.nodes import AudioNode, AudioInputNode, AudioOutputNode, AudioFilterNode


def test_audio_node_base():
    """Test base AudioNode class."""
    node = AudioNode("test")
    assert node.id == "test"
    assert node.params == {}

    with pytest.raises(NotImplementedError):
        node.process()


def test_audio_filter_node():
    """Test AudioFilterNode processing."""
    node = AudioFilterNode("filter", cutoff=1000, resonance=0.7)

    # Test with silence
    silence = np.zeros((1024, 2))
    output = node.process(silence)
    assert output.shape == silence.shape
    assert np.allclose(output, silence)

    # Test with sine wave
    t = np.linspace(0, 1, 1024)
    sine = np.sin(2 * np.pi * 440 * t)
    sine = np.column_stack((sine, sine))

    output = node.process(sine)
    assert output.shape == sine.shape
    assert not np.allclose(output, sine)  # Filter should modify signal


def test_audio_io_nodes():
    """Test audio I/O nodes."""
    input_node = AudioInputNode("input", channels=2)
    output_node = AudioOutputNode("output", channels=2)

    # Test input node
    input_data = input_node.process()
    assert input_data.shape[1] == 2  # Stereo

    # Test output node
    test_data = np.zeros((1024, 2))
    output_data = output_node.process(test_data)
    assert np.array_equal(output_data, test_data)
