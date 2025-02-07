import pytest
from typer.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
import requests
from audiokit.cli import app

runner = CliRunner()
TEST_AUDIO_FILE = Path("tests/data/test.wav")

@pytest.fixture
def mock_requests():
    with patch("requests.post") as mock_post:
        yield mock_post

def test_analyze_loudness_api_error(mock_requests):
    """Test error handling for API errors"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "detail": "Invalid audio format"
    }
    mock_requests.return_value = mock_response

    result = runner.invoke(app, [
        "analyze-loudness", 
        str(TEST_AUDIO_FILE)
    ])
    
    assert result.exit_code == 1
    assert "Error: Invalid audio format" in result.output

def test_analyze_loudness_network_error(mock_requests):
    """Test error handling for network errors"""
    mock_requests.side_effect = requests.exceptions.ConnectionError("Network error")

    result = runner.invoke(app, [
        "analyze-loudness", 
        str(TEST_AUDIO_FILE)
    ])
    
    assert result.exit_code == 1
    assert "Error: Network error" in result.output 