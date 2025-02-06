"""Error types for AudioKit client."""
from typing import Optional

class AudioKitError(Exception):
    """Base exception for AudioKit errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class APIError(AudioKitError):
    """Raised when API request fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(
            f"API error: {message}",
            status_code=status_code or 500
        )

class AuthError(AudioKitError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class ValidationError(AudioKitError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}", status_code=400)

class RateLimitError(AudioKitError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str):
        super().__init__(message, status_code=429)

class ProcessingError(AudioKitError):
    """Raised when audio processing fails."""
    pass

class ServerError(AudioKitError):
    """Raised for server-side errors"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500) 