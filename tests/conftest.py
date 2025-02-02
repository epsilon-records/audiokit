"""
Test Configuration and Fixtures
=============================

Shared fixtures and configuration for AudioKit tests.
"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables before any tests run
load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def log_api_keys():
    """Log API keys used in tests."""
    logger.debug("log_api_keys fixture is running")
    from audiokit.core.config import config
    logger.info("Using Pinecone API key: {}", config.pinecone_api_key)
    logger.info("Using Pinecone index: {}", config.pinecone_index_name)
    logger.info("Using OpenRouter API key: {}", config.openrouter_api_key)
    yield

@pytest.fixture
def fixture_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_audio_path(fixture_dir) -> Path:
    """Return path to sample audio file."""
    return fixture_dir / "sample.wav"

@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """Setup test environment."""
    # Store original working directory
    original_cwd = os.getcwd()
    
    # Create test output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Set environment variables for testing
    os.environ["AUDIOKIT_TEST"] = "true"
    os.environ["AUDIOKIT_OUTPUT_DIR"] = str(output_dir)
    
    yield
    
    # Cleanup
    os.chdir(original_cwd)
    os.environ.pop("AUDIOKIT_TEST", None)
    os.environ.pop("AUDIOKIT_OUTPUT_DIR", None) 