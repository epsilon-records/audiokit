"""
Test Audio Indexing
=================

Tests for audio indexing and search functionality.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from audiokit import ak
from audiokit.core.exceptions import IndexingError
from audiokit.core.config import config

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

def test_versioning(sample_audio_path):
    """Test document versioning system."""
    # First analysis
    analysis1 = ak.analyze_audio(str(sample_audio_path))
    
    # Second analysis
    analysis2 = ak.analyze_audio(str(sample_audio_path))
    
    # Search for documents
    results = ak.search_audio(f"file_name:{sample_audio_path.name}")
    
    assert len(results) == 2, "Should have two versions of the document"
    
    # Verify versions are sequential
    versions = [r["metadata"]["version"] for r in results]
    assert versions == [2, 1], "Versions should be in descending order"
    
    # Verify timestamps are sequential
    timestamps = [datetime.fromisoformat(r["metadata"]["timestamp"]) for r in results]
    assert timestamps[0] > timestamps[1], "Newer version should have later timestamp"

def test_operation_specific_versioning(sample_audio_path):
    """Test versioning across different operations."""
    # Analyze audio
    ak.analyze_audio(str(sample_audio_path))
    
    # Process audio
    ak.process_audio(str(sample_audio_path), extract_vocals=True)
    
    # Search for documents
    results = ak.search_audio(f"file_name:{sample_audio_path.name}")
    
    assert len(results) == 2, "Should have documents for both operations"
    
    # Verify operation types
    operations = set(r["metadata"]["operation"] for r in results)
    assert operations == {"analysis", "processing"}, "Should have both operation types"

def test_document_id_uniqueness(sample_audio_path):
    """Test document ID uniqueness."""
    # Perform multiple operations
    ak.analyze_audio(str(sample_audio_path))
    ak.process_audio(str(sample_audio_path), extract_vocals=True)
    ak.analyze_audio(str(sample_audio_path))
    
    # Search for documents
    results = ak.search_audio(f"file_name:{sample_audio_path.name}")
    
    # Verify unique IDs
    ids = [r["metadata"]["id"] for r in results]
    assert len(ids) == len(set(ids)), "All document IDs should be unique"
    
    # Verify ID structure
    for doc_id in ids:
        assert sample_audio_path.name in doc_id
        assert any(op in doc_id for op in ["analysis", "processing"])
        assert doc_id.count("-") == 2, "ID should have three components"

def test_metadata_completeness(sample_audio_path):
    """Test metadata completeness in indexed documents."""
    # Analyze audio
    ak.analyze_audio(str(sample_audio_path))
    
    # Search for document
    results = ak.search_audio(f"file_name:{sample_audio_path.name}")
    
    assert len(results) > 0, "Should find at least one document"
    
    # Verify required metadata fields
    metadata = results[0]["metadata"]
    required_fields = [
        "audio_path", "file_name", "operation", 
        "timestamp", "version", "id"
    ]
    
    for field in required_fields:
        assert field in metadata, f"Missing required metadata field: {field}"
    
    # Verify timestamp format
    try:
        datetime.fromisoformat(metadata["timestamp"])
    except ValueError:
        pytest.fail("Invalid timestamp format in metadata")

def test_version_rollover(sample_audio_path):
    """Test version number rollover handling."""
    # Simulate many versions
    for _ in range(100):
        ak.analyze_audio(str(sample_audio_path))
    
    # Search for documents
    results = ak.search_audio(f"file_name:{sample_audio_path.name}")
    
    # Verify versions are sequential
    versions = [r["metadata"]["version"] for r in results]
    assert versions == sorted(versions, reverse=True), "Versions should be in descending order"
    
    # Verify no version number conflicts
    assert len(versions) == len(set(versions)), "All version numbers should be unique"

def test_index_initialization():
    # Test that the index can be initialized
    from audiokit.core.indexing import AudioIndex
    try:
        index = AudioIndex()
        assert index is not None
    except Exception as e:
        pytest.fail(f"Index initialization failed: {str(e)}") 