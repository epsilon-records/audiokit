
import unittest
from audiokit.ai.bpm_key_detection import BPMKeyDetection

class TestBPMKeyDetection(unittest.TestCase):
    def test_prediction(self):
        detector = BPMKeyDetection()
        result = detector.predict("sample_song.wav")
        self.assertIn("bpm", result)
        self.assertIn("key", result)
