import pytest
from pathlib import Path
from audiokit import ak

def test_extract_vocals(sample_audio_path, tmp_path):
    """Test vocal extraction"""
    output_path = tmp_path / "vocals.wav"
    result = ak.process_audio(
        str(sample_audio_path),
        extract_vocals=True,
        output_dir=str(tmp_path)
    )
    assert "vocals" in result
    assert Path(result["vocals"]).exists()

def test_separate_stems(sample_audio_path, tmp_path):
    """Test stem separation"""
    result = ak.process_audio(
        str(sample_audio_path),
        separate_stems=True,
        output_dir=str(tmp_path)
    )
    assert "stems" in result
    assert all(Path(p).exists() for p in result["stems"].values())

def test_reduce_noise(sample_audio_path, tmp_path):
    """Test noise reduction"""
    output_path = tmp_path / "cleaned.wav"
    result = ak.process_audio(
        str(sample_audio_path),
        reduce_noise=True,
        output_dir=str(tmp_path)
    )
    assert "cleaned" in result
    assert Path(result["cleaned"]).exists() 