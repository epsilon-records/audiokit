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

runner = CliRunner()

def wait_for_output_stabilize(get_output, timeout=2.0, poll_interval=0.1):
    """
    Wait for output from a callable to stabilize.
    
    Args:
        get_output: A callable returning the current output string
        timeout: Maximum time to wait
        poll_interval: Time between polls
    
    Returns:
        The stabilized output string.
    """
    start_time = time()
    last_output = get_output()
    while time() - start_time < timeout:
        sleep(poll_interval)
        current_output = get_output()
        if current_output == last_output:
            return current_output
        last_output = current_output
    logger.warning("Output did not stabilize within timeout period")
    return last_output

# Automatically patch the cli's Console for testing
@pytest.fixture(autouse=True)
def patch_console(monkeypatch):
    """
    Monkeypatch the global console in audiokit.cli to use a recording console.
    """
    import audiokit.cli as cli  # import the module that created the console
    # Create a Console that forces terminal behavior and records all output:
    recording_console = Console(force_terminal=True, record=True)
    monkeypatch.setattr(cli, "console", recording_console)
    return recording_console

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
    
    # Wait for the recorded console output (from the patched Rich Console) to stabilize.
    final_output = wait_for_output_stabilize(lambda: patch_console.export_text(clear=False))
    # Fallback to using the captured output from runner.invoke if nothing is recorded.
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
    
    final_output = wait_for_output_stabilize(lambda: patch_console.export_text(clear=False))
    
    logger.debug("CLI process command rendered output: {}", final_output)
    logger.debug("CLI process command exit code: {}", result.exit_code)
    
    assert result.exit_code == 0
    assert "Processing Results" in final_output 