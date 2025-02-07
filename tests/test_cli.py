from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from audiokit.cli import app
from pathlib import Path
from audiokit_core.exceptions import AudioKitAPIError, AudioKitAuthError

runner = CliRunner()

def test_analyze_success():
    with patch("audiokit.cli.AudioKitClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.analyze_audio.return_value = MagicMock(
            duration=30.5,
            features={"tempo": 120, "key": "C major"}
        )
        
        test_file = Path("test.mp3")
        result = runner.invoke(app, ["analyze", str(test_file)])
        
        assert result.exit_code == 0
        assert "Successfully analyzed" in result.output

def test_analyze_auth_error():
    with patch("audiokit.cli.AudioKitClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.analyze_audio.side_effect = AudioKitAuthError("Invalid API key")
        
        test_file = Path("test.mp3")
        result = runner.invoke(app, ["analyze", str(test_file)])
        
        assert result.exit_code == 1
        assert "Authentication failed" in result.output

def test_analyze_api_error():
    with patch("audiokit.cli.AudioKitClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.analyze_audio.side_effect = AudioKitAPIError("Server error")
        
        test_file = Path("test.mp3")
        result = runner.invoke(app, ["analyze", str(test_file)])
        
        assert result.exit_code == 1
        assert "API Error" in result.output

def test_analyze_verbose_output():
    with patch("audiokit.cli.AudioKitClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.analyze_audio.return_value = MagicMock(
            duration=30.5,
            features={"tempo": 120, "key": "C major"}
        )
        
        test_file = Path("test.mp3")
        result = runner.invoke(app, ["analyze", str(test_file), "--verbose"])
        
        assert result.exit_code == 0
        assert "Duration: 30.5s" in result.output
        assert "Features:" in result.output
        assert "- tempo: 120" in result.output
        assert "- key: C major" in result.output

def test_analyze_missing_file():
    result = runner.invoke(app, ["analyze", "nonexistent.mp3"])
    assert result.exit_code == 2
    assert "does not exist" in result.output

def test_cli_basic():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0 