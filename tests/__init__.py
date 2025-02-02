# This file makes the tests directory a Python package 

"""Test package initialization.""" 

import pytest
from pathlib import Path
import numpy as np
import soundfile as sf

@pytest.fixture(scope="session")
def audio_fixtures_dir(tmp_path_factory):
    """Create a directory with test audio files."""
    fixture_dir = tmp_path_factory.mktemp("audio_fixtures")
    
    # Create valid test audio
    sample_path = fixture_dir / "sample.wav"
    sample_rate = 44100
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    sf.write(str(sample_path), audio, sample_rate)
    
    # Create corrupted audio
    corrupted_path = fixture_dir / "corrupted.wav"
    corrupted_path.write_bytes(b"not a valid wav file")
    
    # Create path for nonexistent file
    nonexistent_path = fixture_dir / "nonexistent.wav"
    
    return {
        "valid": sample_path,
        "corrupted": corrupted_path,
        "nonexistent": nonexistent_path
    }

@pytest.fixture
def valid_audio_path(audio_fixtures_dir):
    """Return path to valid sample audio file."""
    return audio_fixtures_dir["valid"]

@pytest.fixture
def corrupted_audio_path(audio_fixtures_dir):
    """Return path to corrupted audio file."""
    return audio_fixtures_dir["corrupted"]

@pytest.fixture
def nonexistent_audio_path(audio_fixtures_dir):
    """Return path to nonexistent audio file."""
    return audio_fixtures_dir["nonexistent"] 