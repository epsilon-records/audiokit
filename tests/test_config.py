import os
from audiokit.core.config import config

def test_pinecone_api_key_loading():
    """Test that Pinecone API key is loaded correctly."""
    assert config.pinecone_api_key is not None
    assert config.pinecone_api_key.startswith("pcsk_")
    assert len(config.pinecone_api_key) > 30  # Basic length check 