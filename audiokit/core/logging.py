"""
AudioKit Logging Configuration
===========================

Centralized logging configuration using Loguru.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from loguru import logger

# Remove default handler
logger.remove()

def get_logger(name: str = None):
    """Get a logger instance."""
    return logger.bind(name=name)

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure Loguru for AudioKit.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)
        log_format: Custom log format string
    """
    if log_format is None:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler with colors
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=True
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler with rotation and retention
        logger.add(
            str(log_path),
            format=log_format,
            level=log_level,
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="1 week",  # Keep logs for 1 week
            compression="zip",  # Compress rotated files
            serialize=True,  # JSON format for easier parsing
            backtrace=True,
            diagnose=True,
            enqueue=True
        )

# Configure default exception handling
@logger.catch(onerror=lambda _: sys.exit(1))
def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to ensure all errors are logged."""
    # Don't log KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    logger.opt(exception=(exc_type, exc_value, exc_traceback)).error(
        "Uncaught exception:"
    )

# Install global exception handler
sys.excepthook = handle_exception 

def setup_logging():
    log_level = config.get("AUDIOKIT_LOG_LEVEL", "INFO")
    log_file = config.get("AUDIOKIT_LOG_FILE")
    # ... rest of the logging setup ... 