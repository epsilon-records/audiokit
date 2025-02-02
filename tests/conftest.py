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
import sys
from audiokit.core.logging import get_logger

# Load environment variables before any tests run
load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment."""
    # Set environment variables for testing
    os.environ["AUDIOKIT_TEST"] = "true"
    os.environ["AUDIOKIT_LOG_LEVEL"] = "WARNING"  # Reduce log noise during tests
    
    # Initialize logging
    get_logger()

@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_audio_path(fixture_dir) -> Path:
    """Return path to sample audio file."""
    return fixture_dir / "sample.wav"

@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    logger = get_logger('tests')
    logger.remove()  # Remove any existing handlers
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="DEBUG"
    ) 