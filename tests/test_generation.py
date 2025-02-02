"""
Test Audio Generation Features
===========================

Tests for AI-powered audio generation including instrument synthesis
and moodboard generation.
"""

import pytest
from pathlib import Path
from audiokit.ai.generation import AudioGenerator
from audiokit.core.exceptions import ModelError

def test_generate_instrument():
    """Test instrument sound generation from text description."""
    generator = AudioGenerator()
    description = "warm analog synth with slow attack and long release"
    
    result = generator.generate_instrument(description)
    
    assert isinstance(result, dict)
    assert "audio_path" in result
    assert "parameters" in result
    assert Path(result["audio_path"]).exists()
    
    # Validate generated parameters
    params = result["parameters"]
    assert "timbre" in params
    assert "attack" in params
    assert "decay" in params
    assert isinstance(params["attack"], (int, float))
    assert 0 <= params["attack"] <= 1

def test_generate_instrument_invalid_description():
    """Test generation with invalid/empty description."""
    generator = AudioGenerator()
    with pytest.raises(ModelError):
        generator.generate_instrument("")

def test_generate_moodboard(sample_audio_path):
    """Test moodboard generation from audio."""
    generator = AudioGenerator()
    result = generator.generate_moodboard(str(sample_audio_path))
    
    assert isinstance(result, dict)
    assert "images" in result
    assert "mood" in result
    assert "colors" in result
    
    # Validate image paths
    assert isinstance(result["images"], list)
    assert len(result["images"]) > 0
    assert all(Path(img).exists() for img in result["images"])
    
    # Validate colors
    assert isinstance(result["colors"], list)
    assert all(isinstance(c, str) and c.startswith("#") for c in result["colors"])

def test_generate_moodboard_invalid_audio():
    """Test moodboard generation with invalid audio."""
    generator = AudioGenerator()
    with pytest.raises(ModelError):
        generator.generate_moodboard("nonexistent.wav")

def test_batch_generation():
    """Test batch generation of multiple instruments."""
    generator = AudioGenerator()
    descriptions = [
        "bright digital synth",
        "deep bass drone",
        "plucky acoustic guitar"
    ]
    
    results = []
    for desc in descriptions:
        result = generator.generate_instrument(desc)
        results.append(result)
        
    assert len(results) == len(descriptions)
    assert all(Path(r["audio_path"]).exists() for r in results) 