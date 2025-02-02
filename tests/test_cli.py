import pytest
from typer.testing import CliRunner
from audiokit.cli import app
from audiokit.core.logging import get_logger
from audiokit.core.config import config
import os
from time import time, sleep
from rich.console import Console  # import Rich's Console to enable recording
import re
import io

# Use the package logger consistently
logger = get_logger(__name__)

@pytest.fixture(autouse=True)
def setup_config():
    """Setup test environment configuration."""
    # Ensure environment variables are set for testing
    os.environ["AUDIOKIT_LOG_LEVEL"] = "INFO"
    os.environ["AUDIOKIT_LOG_FILE"] = ""
    yield
    # Clean up environment variables after test
    os.environ.pop("AUDIOKIT_LOG_LEVEL", None)
    os.environ.pop("AUDIOKIT_LOG_FILE", None)

runner = CliRunner()

class AccumulatingStream(io.StringIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accumulated = []

    def write(self, s):
        self.accumulated.append(s)
        return super().write(s)

    def get_accumulated(self):
        return ''.join(self.accumulated)

def strip_ansi(text: str) -> str:
    # Regular expression for ANSI escape sequences
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def test_cli_analyze(sample_audio_path):
    """Test CLI analyze command"""
    logger.info("Testing CLI analyze command")
    
    # Create an accumulating stream and override the runner's output stream method.
    accum_stream = AccumulatingStream()
    original_method = runner._get_output_stream
    runner._get_output_stream = lambda: accum_stream
    result = runner.invoke(
        app, ["analyze", str(sample_audio_path)], catch_exceptions=False
    )
    runner._get_output_stream = original_method
    final_output = accum_stream.get_accumulated()
    
    logger.debug("CLI analyze command rendered output: {}", final_output)
    logger.debug("CLI analyze command exit code: {}", result.exit_code)
    
    # Strip any ANSI escape sequences from the final output.
    final_output_clean = strip_ansi(final_output)
    
    # Assert the command executed successfully and the expected output is rendered.
    assert result.exit_code == 0
    assert "BPM & Key" in final_output_clean
    assert "Genre & Mood" in final_output_clean
    assert "Instruments" in final_output_clean
    assert "120" in final_output_clean        # BPM
    assert "C Major" in final_output_clean      # Key
    assert "Pop" in final_output_clean          # Genre
    assert "Energetic" in final_output_clean    # Mood
    assert "0.95" in final_output_clean         # Piano
    assert "0.85" in final_output_clean         # Guitar
    assert "0.90" in final_output_clean         # Drums

def test_cli_process(sample_audio_path, tmp_path):
    """Test CLI process command"""
    logger.info("Testing CLI process command")
    # Create an accumulating stream and override the runner's output stream method.
    accum_stream = AccumulatingStream()
    original_method = runner._get_output_stream
    runner._get_output_stream = lambda: accum_stream
    result = runner.invoke(
        app, [
            "process", 
            str(sample_audio_path),
            "--output", str(tmp_path),
            "--vocals"
        ],
        catch_exceptions=False
    )
    runner._get_output_stream = original_method
    final_output = accum_stream.get_accumulated()
    
    logger.debug("CLI process command rendered output: {}", final_output)
    logger.debug("CLI process command exit code: {}", result.exit_code)
    
    assert result.exit_code == 0
    assert "Processing Results" in final_output 