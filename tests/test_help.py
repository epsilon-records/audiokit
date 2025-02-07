import pytest
from typer.testing import CliRunner
from audiokit.cli import app

runner = CliRunner()

def test_cli_help():
    """Test that help command works"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AudioKit Extensible CLI" in result.output 