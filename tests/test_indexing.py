"""
Test Audio Indexing
=================

Tests for audio indexing and search functionality.
"""

import pytest
from pathlib import Path
from audiokit import ak
from audiokit.core.exceptions import IndexingError

def test_analysis_indexing(sample_audio_path):
    """Test indexing of analysis results."""
    # Analyze and index audio
    analysis = ak.analyze_audio(str(sample_audio_path))
    
    # Search for the analyzed file
    results = ak.search_audio(f"file_name:{sample_audio_path.name}")
    
    assert len(results) > 0
    assert results[0]["metadata"]["file_name"] == sample_audio_path.name
    assert results[0]["content"] == analysis

def test_similar_audio_search(sample_audio_path):
    """Test finding similar audio files."""
    # Analyze first file
    ak.analyze_audio(str(sample_audio_path))
    
    # Create and analyze a similar file
    similar_path = sample_audio_path.parent / "similar.wav"
    similar_path.write_bytes(sample_audio_path.read_bytes())
    ak.analyze_audio(str(similar_path))
    
    # Find similar files
    results = ak.find_similar(str(sample_audio_path))
    
    assert len(results) > 0
    assert results[0]["metadata"]["file_name"] == "similar.wav"
    assert results[0]["score"] > 0.8  # High similarity expected

def test_natural_language_search(sample_audio_path):
    """Test natural language search."""
    # Analyze audio
    ak.analyze_audio(str(sample_audio_path))
    
    # Search with natural language
    results = ak.search_audio("Find songs with drums")
    
    assert len(results) > 0
    assert "instruments" in results[0]["content"]
    assert "drums" in results[0]["content"]["instruments"]

def test_invalid_search():
    """Test handling of invalid search."""
    with pytest.raises(IndexingError):
        ak.search_audio("")

def test_similar_nonexistent_file():
    """Test finding similar files with nonexistent reference."""
    with pytest.raises(IndexingError):
        ak.find_similar("nonexistent.wav") 