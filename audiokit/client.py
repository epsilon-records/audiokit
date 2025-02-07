from pathlib import Path
import requests
from typing import Optional, Union
from .exceptions import AudioKitAPIError, AudioKitAuthError
from .config import ClientConfig
from .models import AudioAnalysisResult  # Client-specific model

class AudioKitClient:
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Configure HTTP session with default headers and auth"""
        self.session.headers.update({
            "User-Agent": f"AudioKitClient/{self.config.version}",
            "Accept": "application/json"
        })
        if self.config.api_key:
            self.session.headers["X-API-Key"] = self.config.api_key

    def analyze_audio(
        self,
        audio_path: Union[str, Path],
        timeout: int = 30
    ) -> AudioAnalysisResult:
        """Analyze audio file through the AI server."""
        url = f"{self.config.server_url}/analyze"
        
        try:
            with open(audio_path, "rb") as f:
                response = self.session.post(
                    url,
                    files={"file": f},
                    timeout=timeout
                )
        except requests.exceptions.RequestException as e:
            raise AudioKitAPIError(f"Network error: {str(e)}") from e

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> AudioAnalysisResult:
        """Process API responses with error handling"""
        if response.status_code == 401:
            raise AudioKitAuthError("Invalid API key or authentication")
        if not response.ok:
            raise AudioKitAPIError(
                f"API Error {response.status_code}: {response.text}"
            )
        
        raw_response = response.json()
        return AudioAnalysisResult(**raw_response)

class AsyncAudioKitClient:
    """Asyncio-compatible client using aiohttp"""
    # Implementation omitted for brevity 

class AudioAnalysisResult:
    """Client-facing analysis results"""
    def __init__(self, raw_data: dict):
        self.duration = raw_data['duration']
        self.features = raw_data['features']
        # Add client-specific post-processing 