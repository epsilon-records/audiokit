"""AudioKit client package."""
from typing import Optional, BinaryIO, Union
from pathlib import Path
import httpx
from .errors import APIError, AuthError, ValidationError
from .config import load_config, ClientConfig
import yaml
import logging

logger = logging.getLogger(__name__)

class AudioKit:
    """Client for AudioKit AI service."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        config_path: Optional[Path] = None
    ):
        """Initialize AudioKit client.
        
        Args:
            api_url: API URL (overrides config)
            api_key: API key (overrides config)
            config_path: Path to config file
        """
        # Load config if provided, otherwise try default locations
        config = {}
        config_locations = [
            config_path if config_path else None,
            Path("config.yml"),
            Path("audiokit/config.yml"),
            Path.home() / ".audiokit/config.yml"
        ]
        
        # Try each config location
        for loc in config_locations:
            if loc and loc.exists():
                try:
                    with open(loc) as f:
                        config = yaml.safe_load(f)
                    break
                except Exception:
                    continue
        
        # Set API URL (command line takes precedence)
        self.api_url = api_url or config.get('api_url', 'http://localhost:8000')
        
        # Set API key (command line takes precedence)
        self.api_key = api_key or config.get('api_key')
        
        # Load other settings
        self.timeout = float(config.get('timeout', 30.0))
        self.max_file_size = int(config.get('max_file_size', 52428800))  # 50MB default
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def analyze(
        self,
        audio: Union[str, Path, BinaryIO]
    ) -> dict:
        """Analyze audio file.
        
        Args:
            audio: Path to audio file or file-like object
            
        Returns:
            Analysis results
            
        Raises:
            ValidationError: If audio file is invalid
            AuthError: If authentication fails
            APIError: If request fails
        """
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        files = {}
        try:
            # Handle file input
            if isinstance(audio, (str, Path)):
                path = Path(audio)
                if not path.exists():
                    raise ValidationError(f"File not found: {path}")
                if not path.suffix.lower() in ('.wav', '.mp3', '.ogg', '.flac'):
                    raise ValidationError(f"Unsupported audio format: {path.suffix}")
                # Add content type based on file extension
                content_type = {
                    '.wav': 'audio/wav',
                    '.mp3': 'audio/mpeg',
                    '.ogg': 'audio/ogg',
                    '.flac': 'audio/flac'
                }.get(path.suffix.lower())
                files = {"file": (path.name, open(path, "rb"), content_type)}
            else:
                files = {"file": audio}
                
            # Make request
            try:
                response = await self.client.post(
                    f"{self.api_url}/analyze",
                    headers=headers,
                    files=files
                )
                
                # Handle errors
                if response.status_code == 401:
                    raise AuthError("Invalid API key")
                elif response.status_code == 403:
                    raise AuthError("API key does not have required permissions")
                elif response.status_code == 400:
                    error_detail = response.json().get('detail', 'Bad request')
                    raise ValidationError(f"Invalid request: {error_detail}")
                response.raise_for_status()
                
                result = response.json()
                if result.get('errors'):
                    logger.warning("Some analysis operations failed:")
                    for error in result['errors']:
                        logger.warning(f"- {error}")
                return result
                
            except httpx.HTTPStatusError as e:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = f": {error_data.get('detail', '')}"
                except:
                    pass
                raise APIError(
                    f"API request failed: {str(e)}{error_detail}",
                    status_code=e.response.status_code
                )
            except httpx.RequestError as e:
                raise APIError(f"Request failed: {str(e)}")
                
        except Exception as e:
            raise APIError(f"Analysis failed: {str(e)}")
        finally:
            # Clean up file handle if we opened it
            if isinstance(audio, (str, Path)) and "file" in files:
                files["file"][1].close() 