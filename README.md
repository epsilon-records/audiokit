
# AudioKit SDK

AudioKit SDK is an AI-driven toolkit for audio processing, featuring BPM/key detection, genre classification, and more.

## Installation

```bash
pip install -r requirements.txt
```

## Features
- BPM and Key Detection
- Genre and Mood Classification
- Modular and Scalable

## Usage

```python
from audiokit.ai.bpm_key_detection import BPMKeyDetection

detector = BPMKeyDetection()
result = detector.predict("sample_song.wav")
print(result)
```
