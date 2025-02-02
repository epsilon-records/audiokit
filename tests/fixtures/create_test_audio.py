"""Generate test audio files for testing."""

import numpy as np
import soundfile as sf
from pathlib import Path

def create_sample_audio(fixture_dir: Path):
    """Create a simple test audio file."""
    # Create fixtures directory if it doesn't exist
    fixture_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a 1-second sine wave at 440 Hz
    sample_rate = 44100
    duration = 1  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create a more complex sound with harmonics
    audio = np.sin(2 * np.pi * 440 * t)  # fundamental frequency
    audio += 0.5 * np.sin(2 * np.pi * 880 * t)  # first harmonic
    audio += 0.25 * np.sin(2 * np.pi * 1320 * t)  # second harmonic
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Save as WAV file
    output_path = fixture_dir / "sample.wav"
    sf.write(str(output_path), audio, sample_rate)
    return output_path

if __name__ == "__main__":
    fixture_dir = Path(__file__).parent
    create_sample_audio(fixture_dir) 