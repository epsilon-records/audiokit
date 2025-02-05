import os
import requests

# Configure backend URL (can be overridden via environment variable)
BACKEND_URL = os.getenv("AUDIOKIT_AI_URL", "http://localhost:8000")


def analyze_audio(file: str) -> dict:
    """Request audio analysis from the backend."""
    response = requests.post(f"{BACKEND_URL}/analyze", json={"file_path": file})
    response.raise_for_status()
    return response.json()


def process_audio(file: str) -> dict:
    """Send an audio processing request to the backend."""
    response = requests.post(f"{BACKEND_URL}/process", json={"file_path": file})
    response.raise_for_status()
    return response.json()


def generate_content(params: dict) -> dict:
    """Request audio content generation from the backend."""
    response = requests.post(f"{BACKEND_URL}/generate", json=params)
    response.raise_for_status()
    return response.json()
