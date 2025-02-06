"""Error types for AudioKit client."""
from typing import Optional, Any, Dict

class AudioKitError(Exception):
    """Base exception for AudioKit errors."""
    def __init__(
        self, 
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class APIError(AudioKitError):
    """Raised when API request fails."""
    pass

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass

class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            code="RATE_LIMIT",
            details={"retry_after": retry_after}
        )

class ValidationError(AudioKitError):
    """Raised when input validation fails."""
    pass

class ProcessingError(AudioKitError):
    """Raised when audio processing fails."""
    pass 