import pytest
import respx
import httpx
from audiokit.services.clients import SoundchartsClient

def test_soundcharts_get_song_metadata(mock_http_calls):
    """Test Soundcharts song metadata retrieval using respx"""
    # Setup a route to mock the expected Soundcharts API endpoint.
    # Adjust the URL pattern as needed based on your client's implementation.
    route = respx.get("https://soundcharts.example.com/.*").mock(
        return_value=httpx.Response(200, json={"test": "data"})
    )

    client = SoundchartsClient("test_app_id", "test_api_key")
    result = client.get_song_metadata("test_uuid")
    
    assert result == {"test": "data"}
    assert route.called 