"""
Test Audio Processing Features
===========================

Tests for audio processing operations like stem separation and noise reduction.
"""

import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
from audiokit.ai.processing import AudioProcessor
from audiokit.core.exceptions import ProcessingError

def test_extract_vocals(sample_audio_path, tmp_path):
    """Test vocal extraction from audio."""
    processor = AudioProcessor()
    output_path = tmp_path / "vocals.wav"
    
    result_path = processor.extract_vocals(
        str(sample_audio_path),
        str(output_path)
    )
    
    # Verify output file exists and is valid audio
    assert Path(result_path).exists()
    data, samplerate = sf.read(result_path)
    assert len(data) > 0
    assert samplerate > 0

def test_reduce_noise(sample_audio_path, tmp_path):
    """Test noise reduction processing."""
    processor = AudioProcessor()
    output_path = tmp_path / "cleaned.wav"
    
    result_path = processor.reduce_noise(
        str(sample_audio_path),
        str(output_path)
    )
    
    # Verify output file exists and is valid audio
    assert Path(result_path).exists()
    data, samplerate = sf.read(result_path)
    assert len(data) > 0
    assert samplerate > 0

def test_process_with_invalid_output_path(sample_audio_path):
    """Test processing with invalid output path."""
    processor = AudioProcessor()
    with pytest.raises(ProcessingError):
        processor.extract_vocals(
            str(sample_audio_path),
            "/nonexistent/directory/vocals.wav"
        )

def test_batch_processing(sample_audio_path, tmp_path):
    """Test batch processing of multiple files."""
    processor = AudioProcessor()
    
    # Create multiple test files
    test_files = []
    for i in range(3):
        test_file = tmp_path / f"test_{i}.wav"
        sf.write(str(test_file), np.zeros(1000), 44100)
        test_files.append(test_file)
    
    # Process all files
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    for test_file in test_files:
        output_path = output_dir / f"processed_{test_file.name}"
        result = processor.reduce_noise(str(test_file), str(output_path))
        assert Path(result).exists()

def test_processing_preserves_metadata(sample_audio_path, tmp_path):
    """Test that processing preserves audio metadata."""
    processor = AudioProcessor()
    output_path = tmp_path / "processed.wav"
    
    # Get original metadata
    orig_data, orig_sr = sf.read(sample_audio_path)
    
    # Process audio
    result_path = processor.reduce_noise(
        str(sample_audio_path),
        str(output_path)
    )
    
    # Check processed file metadata
    proc_data, proc_sr = sf.read(result_path)
    assert proc_sr == orig_sr
    assert proc_data.shape[0] == orig_data.shape[0] 