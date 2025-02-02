"""
AudioKit Configuration
====================

Configuration management and environment settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import logger after other imports to avoid circular dependency
from .logging import get_logger
logger = get_logger(__name__)

class Config:
    """Global configuration settings."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        self.log_level = self.get("AUDIOKIT_LOG_LEVEL", "INFO")
        self.log_file = self.get("AUDIOKIT_LOG_FILE")
        self.models_dir = self.get("AUDIOKIT_MODELS_DIR", "models")
        self.output_dir = self.get("AUDIOKIT_OUTPUT_DIR", "output")
        self.temp_dir = self.get("AUDIOKIT_TEMP_DIR", "temp")
        
        # API credentials
        self.soundcharts_app_id = self.get("SOUNDCHARTS_APP_ID")
        self.soundcharts_api_key = self.get("SOUNDCHARTS_API_KEY")
        
        # Pinecone configuration
        self.pinecone_api_key = self.get("PINECONE_API_KEY")
        logger.debug(f"Pinecone API key: {'*' * 8}{self.pinecone_api_key[-4:]}" if self.pinecone_api_key else "No API key found")
        self.pinecone_index_name = self.get("PINECONE_INDEX_NAME", "audiokit-brain")
        self.pinecone_dimension = int(self.get("PINECONE_DIMENSION", "1536"))
        self.pinecone_metric = self.get("PINECONE_METRIC", "cosine")
        
        # Create necessary directories
        self._setup_directories()
        logger.debug("Configuration initialized")
    
    def _setup_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_path in [self.models_dir, self.output_dir, self.temp_dir]:
            path = Path(dir_path)
            if not path.exists():
                logger.debug("Creating directory: {}", path)
                path.mkdir(parents=True, exist_ok=True)
    
    def get_model_path(self, model_name: str) -> Path:
        """Get path to a model file."""
        return Path(self.models_dir) / model_name
    
    def get_output_path(self, filename: str) -> Path:
        """Get path for an output file."""
        return Path(self.output_dir) / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """Get path for a temporary file."""
        return Path(self.temp_dir) / filename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "log_level": self.log_level,
            "log_file": self.log_file,
            "models_dir": self.models_dir,
            "output_dir": self.output_dir,
            "temp_dir": self.temp_dir
        }

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value from environment."""
        return os.getenv(key, default)
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 't', 'y', 'yes')

# Global configuration instance
config = Config() 