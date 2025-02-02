import pytest
from unittest.mock import Mock, patch
from audiokit.services.clients import SoundchartsClient

@patch('requests.get')
def test_soundcharts_get_song_metadata(mock_get):
    """Test Soundcharts song metadata retrieval"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    mock_get.return_value = mock_response
    
    client = SoundchartsClient("test_app_id", "test_api_key")
    result = client.get_song_metadata("test_uuid")
    
    assert result == {"test": "data"}
    mock_get.assert_called_once() 