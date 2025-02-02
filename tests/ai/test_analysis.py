"""
Test Audio Analysis Features
==========================

Tests for BPM detection, genre classification, and instrument identification.
"""

import pytest
from audiokit.ai.analysis import AudioAnalyzer

def test_bpm_key_detection(valid_audio_path):
    """Test BPM and key detection."""
    analyzer = AudioAnalyzer()
    result = analyzer.detect_bpm_key(str(valid_audio_path))
    
    assert isinstance(result, dict)
    assert "bpm" in result
    assert "key" in result
    assert isinstance(result["bpm"], (int, float))
    assert isinstance(result["key"], str)

def test_genre_classification(valid_audio_path):
    """Test genre and mood classification."""
    analyzer = AudioAnalyzer()
    result = analyzer.classify_genre(str(valid_audio_path))
    
    assert isinstance(result, dict)
    assert "genre" in result
    assert "mood" in result
    assert isinstance(result["genre"], str)
    assert isinstance(result["mood"], str)

def test_instrument_identification(valid_audio_path):
    """Test instrument identification."""
    analyzer = AudioAnalyzer()
    result = analyzer.identify_instruments(str(valid_audio_path))
    
    assert isinstance(result, dict)
    assert len(result) > 0
    assert all(isinstance(v, float) and 0 <= v <= 1 for v in result.values())

def test_invalid_audio_file(nonexistent_audio_path):
    """Test handling of invalid audio file."""
    analyzer = AudioAnalyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.detect_bpm_key(str(nonexistent_audio_path))

def test_audio_analysis_complete(valid_audio_path):
    """Test complete audio analysis pipeline."""
    analyzer = AudioAnalyzer()
    result = analyzer.analyze_audio(str(valid_audio_path))
    
    assert isinstance(result, dict)
    assert "bpm_key" in result
    assert "genre" in result
    assert "instruments" in result 