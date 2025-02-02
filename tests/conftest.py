import pytest
from pathlib import Path
import numpy as np
import soundfile as sf
import os
from dotenv import load_dotenv
from audiokit.core.logging import get_logger

logger = get_logger(__name__)

# Load environment variables before any tests run
load_dotenv()

@pytest.fixture(scope="session")
def sample_audio_path(tmp_path_factory):
    """Create a sample audio file for testing"""
    path = tmp_path_factory.mktemp("audio") / "sample.wav"
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    sf.write(str(path), audio, sample_rate)
    
    logger.debug("Created test audio file: {}", path)
    assert path.exists(), "Test audio file was not created"
    assert path.stat().st_size > 0, "Test audio file is empty"
    
    return path

@pytest.fixture(scope="session")
def corrupted_audio_path(tmp_path_factory):
    """Create a corrupted audio file for testing"""
    path = tmp_path_factory.mktemp("audio") / "corrupted.wav"
    path.write_bytes(b"not a valid wav file")
    return path

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment."""
    # Set environment variables for testing
    os.environ["AUDIOKIT_TEST"] = "true"
    os.environ["AUDIOKIT_LOG_LEVEL"] = "DEBUG"  # Ensure DEBUG level
    
    # Initialize logging
    get_logger()

@pytest.fixture(autouse=True)
def change_to_temp_dir(tmp_path, monkeypatch):
    """
    Automatically change the current working directory to a temporary subdirectory
    within the test's tmp_path. This ensures that any files (e.g. .wav files) generated
    by the tests using relative paths are created in this folder rather than in the project root.
    """
    generated_dir = tmp_path / "generated_audio"
    generated_dir.mkdir()
    monkeypatch.chdir(generated_dir)
    print("Current working directory changed to:", os.getcwd()) 