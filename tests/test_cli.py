"""
Test Command Line Interface
=========================

Tests for CLI commands and options.
"""

import json
import pytest
from typer.testing import CliRunner
from pathlib import Path
from audiokit.cli import app

runner = CliRunner()

def test_analyze_command_basic(sample_audio_path):
    """Test basic audio analysis command."""
    result = runner.invoke(app, ["analyze", str(sample_audio_path)])
    assert result.exit_code == 0
    assert "Analysis Results" in result.stdout

def test_analyze_command_json_output(sample_audio_path):
    """Test JSON output format for analysis."""
    result = runner.invoke(app, [
        "analyze",
        str(sample_audio_path),
        "--format", "json"
    ])
    assert result.exit_code == 0
    
    # Verify JSON output is valid
    data = json.loads(result.stdout)
    assert "bpm_key" in data
    assert "genre" in data
    assert "instruments" in data

def test_process_command_basic(sample_audio_path, tmp_path):
    """Test basic audio processing command."""
    output_dir = tmp_path / "processed"
    result = runner.invoke(app, [
        "process",
        str(sample_audio_path),
        "--output", str(output_dir),
        "--extract-vocals"
    ])
    assert result.exit_code == 0
    assert "Processing complete" in result.stdout
    assert (output_dir / "vocals.wav").exists()

def test_process_command_multiple_operations(sample_audio_path, tmp_path):
    """Test multiple processing operations."""
    output_dir = tmp_path / "processed"
    result = runner.invoke(app, [
        "process",
        str(sample_audio_path),
        "--output", str(output_dir),
        "--extract-vocals",
        "--reduce-noise"
    ])
    assert result.exit_code == 0
    assert (output_dir / "vocals.wav").exists()
    assert (output_dir / "cleaned.wav").exists()

def test_generate_command_instrument():
    """Test instrument generation command."""
    result = runner.invoke(app, [
        "generate",
        "instrument",
        "warm analog synth",
        "--output", "synth.wav"
    ])
    assert result.exit_code == 0
    assert Path("synth.wav").exists()

def test_generate_command_moodboard(sample_audio_path):
    """Test moodboard generation command."""
    result = runner.invoke(app, [
        "generate",
        "moodboard",
        str(sample_audio_path),
        "--output", "moodboard"
    ])
    assert result.exit_code == 0
    assert Path("moodboard").exists()
    assert any(Path("moodboard").glob("*.png"))

def test_cli_help():
    """Test CLI help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AudioKit CLI" in result.stdout
    
    # Test help for subcommands
    for cmd in ["analyze", "process", "generate"]:
        result = runner.invoke(app, [cmd, "--help"])
        assert result.exit_code == 0
        assert cmd.title() in result.stdout

def test_cli_version():
    """Test version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "AudioKit version" in result.stdout

def test_batch_command(tmp_path):
    """Test batch processing command."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "test1.wav").touch()
    (input_dir / "test2.wav").touch()
    
    result = runner.invoke(app, [
        "batch",
        str(input_dir),
        "--op", "analyze"
    ])
    assert result.exit_code == 0 