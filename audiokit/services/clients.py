"""
External Service Clients
======================
Clients for external API integrations.
"""

import httpx
from typing import Optional, Dict, Any

from ..core.logging import get_logger
from ..core.exceptions import ConfigurationError

logger = get_logger(__name__)

class SoundchartsClient:
    """Client for Soundcharts API integration."""
    
    BASE_URL = "https://customer.api.soundcharts.com/api/v2"
    
    def __init__(self, app_id: str, api_key: str):
        """Initialize Soundcharts client."""
        if not app_id or not api_key:
            logger.error("Missing Soundcharts credentials")
            raise ConfigurationError("Soundcharts credentials not provided")
            
        self.headers = {
            "x-app-id": app_id,
            "x-api-key": api_key
        }
        logger.debug("Initialized Soundcharts client")
    
    @logger.catch(reraise=True)
    def get_song_metadata(self, song_uuid: str) -> Optional[Dict[str, Any]]:
        """Fetch song metadata from Soundcharts."""
        url = f"{self.BASE_URL}/song/{song_uuid}/metadata"
        logger.info("Fetching song metadata for UUID: {}", song_uuid)
        
        try:
            response = httpx.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            logger.success("Successfully fetched song metadata")
            return data
        except httpx.exceptions.RequestException as e:
            logger.error("Failed to fetch song metadata: {}", str(e))
            return None
    
    @logger.catch(reraise=True)
    def get_playlist_metadata(self, playlist_uuid: str) -> Optional[Dict[str, Any]]:
        """Fetch playlist metadata from Soundcharts."""
        url = f"{self.BASE_URL}/playlist/{playlist_uuid}/metadata"
        logger.info("Fetching playlist metadata for UUID: {}", playlist_uuid)
        
        try:
            response = httpx.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            logger.success("Successfully fetched playlist metadata")
            return data
        except httpx.exceptions.RequestException as e:
            logger.error("Failed to fetch playlist metadata: {}", str(e))
            return None 