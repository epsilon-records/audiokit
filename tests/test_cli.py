"""
Test Command Line Interface
=========================

Tests for CLI commands and options.
"""

import pytest
from typer.testing import CliRunner
from audiokit.cli import app

runner = CliRunner()

def test_analyze_command(sample_audio_path):
    """Test audio analysis command."""
    result = runner.invoke(app, ["analyze", str(sample_audio_path)])
    assert result.exit_code == 0
    assert "Analysis Results" in result.stdout

def test_analyze_json_output(sample_audio_path):
    """Test JSON output format."""
    result = runner.invoke(app, [
        "analyze",
        str(sample_audio_path),
        "--format", "json"
    ])
    assert result.exit_code == 0
    assert '"bpm_key":' in result.stdout

def test_process_command(sample_audio_path, tmp_path):
    """Test audio processing command."""
    output_dir = tmp_path / "processed"
    result = runner.invoke(app, [
        "process",
        str(sample_audio_path),
        "--output", str(output_dir),
        "--stems"
    ])
    assert result.exit_code == 0
    assert "Processing Results" in result.stdout

def test_generate_command():
    """Test content generation command."""
    result = runner.invoke(app, [
        "generate",
        "instrument",
        "warm analog synth"
    ])
    assert result.exit_code == 0
    assert "audio_path" in result.stdout

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