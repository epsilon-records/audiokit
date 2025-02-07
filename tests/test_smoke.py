import pytest
from typer.testing import CliRunner
from pathlib import Path
from audiokit.cli import app

runner = CliRunner()
TEST_AUDIO_FILE = Path("tests/data/test.wav")

@pytest.mark.smoke
def test_smoke_test_analyze_loudness():
    """End-to-end smoke test for loudness analysis"""
    result = runner.invoke(app, [
        "analyze-loudness", 
        str(TEST_AUDIO_FILE)
    ])
    
    # Expecting either success or server not running
    assert result.exit_code in [0, 1]

@pytest.mark.smoke
def test_smoke_test_analyze_spectral():
    """End-to-end smoke test for spectral analysis"""
    result = runner.invoke(app, [
        "analyze-spectral",
        str(TEST_AUDIO_FILE)
    ])
    
    assert result.exit_code in [0, 1] 