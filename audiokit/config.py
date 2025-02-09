"""Configuration management for AudioKit CLI."""

import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "api_base_url": "http://localhost:8000/api/v1",
    "log_level": "INFO",
}

CONFIG_DIR = Path.home() / ".audiokit"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """
    Load configuration with the following precedence:
    1. Environment variables (AUDIOKIT_API_BASE, etc.)
    2. User config file (~/.audiokit/config.json)
    3. Default values
    """
    # Start with default config
    config = DEFAULT_CONFIG.copy()

    # Load from config file if it exists
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open() as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}")

    # Override with environment variables if set
    if api_base := os.getenv("AUDIOKIT_API_BASE"):
        config["api_base_url"] = f"{api_base}/api/v1"

    return config


def save_config(config: dict) -> None:
    """Save configuration to user config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        json.dump(config, f, indent=2)


def get_api_base_url() -> str:
    """Get the API base URL from config."""
    return load_config()["api_base_url"]
