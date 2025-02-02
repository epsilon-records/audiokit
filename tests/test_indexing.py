import pytest
from audiokit import ak
from audiokit.core.indexing import audio_index
from audiokit.core.logging import get_logger

logger = get_logger(__name__)

def test_index_data(sample_audio_path):
    """Test data indexing"""
    logger.info("Testing data indexing")
    test_data = {"test": "data"}
    audio_index.index_data(str(sample_audio_path), test_data, "test")
    
    results = audio_index.search_audio("test", 1)
    assert len(results) > 0
    assert results[0]["content"] == test_data

def test_search_audio(sample_audio_path):
    """Test audio search"""
    results = ak.search_audio("test query")
    assert isinstance(results, list)

def test_find_similar(sample_audio_path):
    """Test finding similar audio"""
    results = ak.find_similar(str(sample_audio_path))
    assert isinstance(results, list) 