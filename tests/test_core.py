"""
Test Core AudioKit Functionality
==============================

Tests for core features and utilities.
"""

import pytest
from pathlib import Path
from audiokit.core.exceptions import AudioFileError, ValidationError
from audiokit import AudioKit

def test_validate_audio_file_success(sample_audio_path):
    """Test successful audio file validation."""
    ak = AudioKit()
    result = ak._validate_audio_file(str(sample_audio_path))
    assert isinstance(result, Path)
    assert result.exists()
    assert result.suffix.lower() in ['.wav', '.mp3', '.flac']

def test_validate_audio_file_not_found():
    """Test validation with non-existent file."""
    ak = AudioKit()
    with pytest.raises(ValidationError, match="Audio file not found"):
        ak._validate_audio_file("nonexistent.wav")

def test_validate_audio_file_invalid_format(tmp_path):
    """Test validation with invalid audio format."""
    invalid_file = tmp_path / "test.txt"
    invalid_file.touch()
    
    ak = AudioKit()
    with pytest.raises(ValidationError, match="Unsupported audio format"):
        ak._validate_audio_file(str(invalid_file))

def test_analyze_audio_complete(sample_audio_path):
    """Test complete audio analysis pipeline."""
    ak = AudioKit()
    result = ak.analyze_audio(str(sample_audio_path))
    
    # Check all expected analysis components are present
    assert isinstance(result, dict)
    assert "bpm_key" in result
    assert "genre" in result
    assert "instruments" in result
    
    # Validate BPM/Key results
    assert "bpm" in result["bpm_key"]
    assert "key" in result["bpm_key"]
    assert isinstance(result["bpm_key"]["bpm"], (int, float))
    assert isinstance(result["bpm_key"]["key"], str)
    
    # Validate genre results
    assert isinstance(result["genre"]["genre"], str)
    assert isinstance(result["genre"]["mood"], str)
    
    # Validate instrument detection
    assert isinstance(result["instruments"], dict)
    assert len(result["instruments"]) > 0
    assert all(isinstance(v, float) and 0 <= v <= 1 
              for v in result["instruments"].values())

def test_analyze_audio_with_invalid_file():
    """Test analysis with invalid audio file."""
    ak = AudioKit()
    with pytest.raises(ValidationError):
        ak.analyze_audio("nonexistent.wav")

def test_analyze_audio_with_corrupted_file(tmp_path):
    """Test analysis with corrupted audio file."""
    corrupted_file = tmp_path / "corrupted.wav"
    corrupted_file.write_bytes(b"not a valid wav file")
    
    ak = AudioKit()
    with pytest.raises(AudioFileError):
        ak.analyze_audio(str(corrupted_file)) 