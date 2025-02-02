"""Generate test audio files for testing."""

import numpy as np
import soundfile as sf

def create_sample_audio():
    """Create a simple test audio file."""
    # Generate a 1-second sine wave at 440 Hz
    sample_rate = 44100
    t = np.linspace(0, 1, sample_rate)
    audio = np.sin(2 * np.pi * 440 * t)
    
    # Save as WAV file
    sf.write('sample.wav', audio, sample_rate)

if __name__ == "__main__":
    create_sample_audio() 