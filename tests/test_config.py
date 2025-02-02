import pytest
from audiokit.core.config import Config
from pathlib import Path
import os

def test_config_initialization():
    # Set test environment variables
    os.environ["AUDIOKIT_LOG_LEVEL"] = "DEBUG"
    config = Config()
    assert config.log_level == "DEBUG"
    assert isinstance(config.models_dir, str)
    assert isinstance(config.output_dir, str)
    assert isinstance(config.temp_dir, str)
    # Clean up
    os.environ.pop("AUDIOKIT_LOG_LEVEL")

def test_config_get_method():
    config = Config()
    assert config.get("NON_EXISTENT_KEY", "default") == "default"
    assert config.get_bool("NON_EXISTENT_BOOL", True) is True

def test_config_directories():
    config = Config()
    assert Path(config.models_dir).exists()
    assert Path(config.output_dir).exists()
    assert Path(config.temp_dir).exists() 