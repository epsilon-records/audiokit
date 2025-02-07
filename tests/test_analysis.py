import pytest
from typer.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests
from audiokit.cli import app

runner = CliRunner()
TEST_AUDIO_FILE = Path("tests/data/test.wav")
TEST_API_URL = "http://localhost:8000"

@pytest.fixture
def mock_requests():
    with patch("requests.post") as mock_post:
        yield mock_post

def test_analyze_loudness_success(mock_requests):
    """Test loudness analysis command"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "loudness": [0.1, 0.2, 0.3],
        "window_size": 0.1
    }
    mock_requests.return_value = mock_response

    result = runner.invoke(app, [
        "analyze-loudness", 
        str(TEST_AUDIO_FILE),
        "--window-size", "0.1"
    ])
    
    assert result.exit_code == 0
    mock_requests.assert_called_once_with(
        f"{TEST_API_URL}/analyze/loudness",
        files={"audio_file": pytest.any},
        params={"window_size": 0.1}
    )

def test_analyze_spectral_success(mock_requests):
    """Test spectral analysis command"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "analysis": {
            "mfcc": [0.1, 0.2],
            "centroid": 440.0
        }
    }
    mock_requests.return_value = mock_response

    result = runner.invoke(app, [
        "analyze-spectral",
        str(TEST_AUDIO_FILE),
        "--feature", "mfcc",
        "--feature", "centroid"
    ])
    
    assert result.exit_code == 0
    mock_requests.assert_called_once_with(
        f"{TEST_API_URL}/analyze/spectral",
        files={"audio_file": pytest.any},
        params={"features": ["mfcc", "centroid"]}
    )

def test_bpm_analysis_success(mock_requests):
    """Test BPM analysis command"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "bpm": 120.0,
        "method": "librosa"
    }
    mock_requests.return_value = mock_response

    result = runner.invoke(app, [
        "bpm",
        str(TEST_AUDIO_FILE),
        "--method", "librosa"
    ])
    
    assert result.exit_code == 0
    assert "Estimated BPM: 120.00" in result.output
    mock_requests.assert_called_once_with(
        f"{TEST_API_URL}/analyze/bpm",
        files={"audio_file": pytest.any},
        params={"method": "librosa"}
    )

def test_key_detection_success(mock_requests):
    """Test key detection command"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "key": "C major",
        "confidence": 0.95
    }
    mock_requests.return_value = mock_response

    result = runner.invoke(app, [
        "key",
        str(TEST_AUDIO_FILE),
        "--method", "krumhansl"
    ])
    
    assert result.exit_code == 0
    assert "Detected Key: C major" in result.output
    mock_requests.assert_called_once_with(
        f"{TEST_API_URL}/analyze/key",
        files={"audio_file": pytest.any},
        params={"method": "krumhansl"}
    )

def test_upload_success(mock_requests):
    """Test file upload command"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    result = runner.invoke(app, [
        "upload",
        str(TEST_AUDIO_FILE)
    ])
    
    assert result.exit_code == 0
    assert "File uploaded successfully" in result.output
    mock_requests.assert_called_once_with(
        f"{TEST_API_URL}/upload",
        files={"file": pytest.any}
    ) 