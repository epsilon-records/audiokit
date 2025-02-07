class AudioKitError(Exception):
    """Base exception for AudioKit errors"""

class AudioKitAPIError(AudioKitError):
    """Exception for API communication errors"""

class AudioKitAuthError(AudioKitError):
    """Exception for authentication failures"""

class AudioKitValidationError(AudioKitError):
    """Exception for input validation errors""" 