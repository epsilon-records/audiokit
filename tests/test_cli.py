import pytest
from typer.testing import CliRunner
from audiokit.cli import app
from audiokit.core.logging import get_logger
from audiokit.core.config import config
import os
from time import time, sleep
from rich.console import Console  # import Rich's Console to enable recording
import re

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

@pytest.fixture(autouse=True)
def patch_console(monkeypatch):
    """
    Monkeypatch the global console in audiokit.cli to use a recording Console.
    """
    import audiokit.cli as cli  # import the module that created the console
    recording_console = Console(force_terminal=True, record=True)
    monkeypatch.setattr(cli, "console", recording_console)
    return recording_console

runner = CliRunner()

def strip_ansi(text: str) -> str:
    # Regular expression for ANSI escape sequences
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def test_cli_analyze(sample_audio_path, patch_console):
    """Test CLI analyze command"""
    logger.info("Testing CLI analyze command")
    
    result = runner.invoke(
        app, ["analyze", str(sample_audio_path)], catch_exceptions=False
    )
    # Allow a brief pause to let all output be recorded.
    sleep(0.2)
    final_output = patch_console.export_text(clear=False)
    if not final_output:
        final_output = result.stdout
    
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

def test_cli_process(sample_audio_path, tmp_path, patch_console):
    """Test CLI process command"""
    logger.info("Testing CLI process command")
    result = runner.invoke(
        app, [
            "process", 
            str(sample_audio_path),
            "--output", str(tmp_path),
            "--vocals"
        ],
        catch_exceptions=False
    )
    sleep(0.2)
    final_output = patch_console.export_text(clear=False)
    if not final_output:
        final_output = result.stdout
    
    logger.debug("CLI process command rendered output: {}", final_output)
    logger.debug("CLI process command exit code: {}", result.exit_code)
    
    assert result.exit_code == 0
    assert "Processing Results" in final_output 