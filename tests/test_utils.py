import pytest
from pathlib import Path
from audiokit.core.utils import validate_audio_file

def test_validate_audio_file(sample_audio_path):
    """Test valid audio file validation"""
    result = validate_audio_file(str(sample_audio_path))
    assert isinstance(result, Path)
    assert result.exists()

def test_validate_nonexistent_file():
    """Test validation of non-existent file"""
    with pytest.raises(Exception):
        validate_audio_file("nonexistent.wav") 