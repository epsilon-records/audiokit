"""AudioKit client package for audio processing and analysis."""
from typing import Optional, Dict, Any, BinaryIO, Union, List
from pathlib import Path
import asyncio
import httpx
from .plugin import PluginManager
from .errors import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ProcessingError
)
from .batch import BatchProcessor, BatchItem

class AudioKit:
    """Main client class for interacting with AudioKit AI services."""
    
    def __init__(
        self, 
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """Initialize AudioKit client.
        
        Args:
            api_url: Base URL for AudioKit AI service
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Raises:
            ValidationError: If api_url is invalid
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
        self.plugins = PluginManager()
        self.batch = BatchProcessor(self)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers.
        
        Returns:
            Dict of HTTP headers
        """
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for request
            
        Returns:
            JSON response data
            
        Raises:
            APIError: If request fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit exceeded
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = {**self._build_headers(), **kwargs.pop("headers", {})}
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(
                    method,
                    url,
                    headers=headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 60))
                    raise RateLimitError(retry_after)
                elif attempt == self.max_retries - 1:
                    raise APIError(f"Request failed: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"Request failed: {str(e)}")
                await asyncio.sleep(2 ** attempt)

    async def analyze(
        self,
        audio: Union[str, Path, BinaryIO],
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze audio file and extract properties.
        
        Args:
            audio: Path to audio file or file-like object
            **kwargs: Additional options for analysis
            
        Returns:
            Dict containing audio analysis results
            
        Raises:
            ValidationError: If audio file is invalid
            ProcessingError: If analysis fails
            APIError: If request fails
        """
        files = {}
        
        try:
            if isinstance(audio, (str, Path)):
                path = Path(audio)
                if not path.exists():
                    raise ValidationError(f"File not found: {path}")
                files = {"file": open(path, "rb")}
            else:
                files = {"file": audio}
                
            return await self._make_request(
                "POST",
                "/analyze",
                files=files,
                **kwargs
            )
            
        except (OSError, IOError) as e:
            raise ValidationError(f"Invalid audio file: {str(e)}")
        finally:
            # Close file if we opened it
            if isinstance(audio, (str, Path)) and "file" in files:
                files["file"].close()

    async def process(
        self,
        audio: Union[str, Path, BinaryIO],
        output: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Union[bytes, None]:
        """Process audio file with effects and filters.
        
        Args:
            audio: Path to audio file or file-like object
            output: Optional output path, if None returns processed audio bytes
            **kwargs: Processing options
            
        Returns:
            Processed audio bytes if output is None, otherwise None
            
        Raises:
            ValidationError: If input/output paths are invalid
            ProcessingError: If processing fails
            APIError: If request fails
        """
        # TODO: Implement audio processing endpoint
        raise NotImplementedError("Audio processing not yet implemented")

    async def process_batch(self, items: List[BatchItem]) -> List[BatchItem]:
        """Process multiple audio files in batch.
        
        Args:
            items: List of batch items to process
            
        Returns:
            Processed batch items with results/errors
            
        Raises:
            BatchError: If batch processing fails
        """
        return await self.batch.process(items) 