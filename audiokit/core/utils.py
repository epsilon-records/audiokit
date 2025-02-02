"""
AudioKit Utilities
================

Common utility functions and helpers.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager
import tempfile

from .logging import get_logger
from .exceptions import AudioFileError

logger = get_logger(__name__)

def validate_audio_file(path: str) -> Path:
    """
    Validate an audio file exists and is readable.
    
    Args:
        path: Path to audio file
        
    Returns:
        Path object for the audio file
        
    Raises:
        AudioFileError: If file is invalid or unreadable
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            raise AudioFileError(f"File not found: {path}")
        
        if not file_path.is_file():
            raise AudioFileError(f"Not a file: {path}")
            
        if not os.access(file_path, os.R_OK):
            raise AudioFileError(f"File not readable: {path}")
            
        return file_path
        
    except Exception as e:
        logger.error("Error validating audio file: {}", str(e))
        raise AudioFileError(f"Invalid audio file: {str(e)}") from e

@contextmanager
def temp_file(suffix: Optional[str] = None) -> Path:
    """
    Create a temporary file that is automatically cleaned up.
    
    Args:
        suffix: Optional file suffix
        
    Yields:
        Path to temporary file
    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        temp_path = Path(temp.name)
        logger.debug("Created temporary file: {}", temp_path)
        yield temp_path
    finally:
        try:
            temp.close()
            temp_path.unlink()
            logger.debug("Cleaned up temporary file: {}", temp_path)
        except Exception as e:
            logger.warning("Failed to cleanup temporary file: {}", str(e))

def find_audio_files(directory: str, recursive: bool = False) -> List[Path]:
    """
    Find all audio files in a directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of paths to audio files
    """
    logger.debug("Searching for audio files in: {}", directory)
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.error("Directory not found: {}", directory)
        return []
    
    pattern = "**/*.wav" if recursive else "*.wav"
    audio_files = list(dir_path.glob(pattern))
    logger.debug("Found {} audio files", len(audio_files))
    
    return audio_files

def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    if not dir_path.exists():
        logger.debug("Creating directory: {}", dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path 