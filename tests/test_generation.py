import pytest
from audiokit import ak

def test_generate_instrument():
    """Test instrument generation"""
    description = "warm analog synth pad"
    result = ak.generate_content(instrument_description=description)
    assert "instrument" in result
    assert "audio_path" in result["instrument"]

def test_generate_moodboard(sample_audio_path):
    """Test moodboard generation"""
    result = ak.generate_content(audio_path=str(sample_audio_path))
    assert "moodboard" in result
    assert "images" in result["moodboard"] 