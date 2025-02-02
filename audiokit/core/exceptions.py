"""
AudioKit Exceptions
=================

Custom exceptions for the AudioKit SDK.
"""

class AudioKitError(Exception):
    """Base exception for all AudioKit errors."""
    pass

class AudioFileError(AudioKitError):
    """Raised when there are issues with audio files."""
    pass

class ProcessingError(AudioKitError):
    """Raised when audio processing fails."""
    pass

class ValidationError(AudioKitError):
    """Raised when input validation fails."""
    pass

class ModelError(AudioKitError):
    """Raised when AI model operations fail."""
    pass

class ConfigurationError(AudioKitError):
    """Raised when there are configuration issues."""
    pass

class IndexingError(AudioKitError):
    """Raised when there are issues with audio indexing and search operations."""
    pass 