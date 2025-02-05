import pytest
from pathlib import Path
import numpy as np
import soundfile as sf
import os
from dotenv import load_dotenv
from audiokit.core.logging import get_logger
import respx
import httpx
from llama_index.llms.openai_like.base import OpenAILike

logger = get_logger(__name__)

# Load environment variables before any tests run
load_dotenv()

@pytest.fixture(scope="session")
def sample_audio_path(tmp_path_factory):
    """Create a sample audio file for testing"""
    path = tmp_path_factory.mktemp("audio") / "sample.wav"
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    sf.write(str(path), audio, sample_rate)
    
    logger.debug("Created test audio file: {}", path)
    assert path.exists(), "Test audio file was not created"
    assert path.stat().st_size > 0, "Test audio file is empty"
    
    return path

@pytest.fixture(scope="session")
def corrupted_audio_path(tmp_path_factory):
    """Create a corrupted audio file for testing"""
    path = tmp_path_factory.mktemp("audio") / "corrupted.wav"
    path.write_bytes(b"not a valid wav file")
    return path

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment."""
    # Set environment variables for testing
    os.environ["AUDIOKIT_TEST"] = "true"
    os.environ["AUDIOKIT_LOG_LEVEL"] = "DEBUG"  # Ensure DEBUG level
    
    # Initialize logging
    get_logger()

@pytest.fixture(autouse=True)
def change_to_temp_dir(tmp_path, monkeypatch):
    """
    Automatically change the current working directory to a temporary subdirectory
    within the test's tmp_path. This ensures that any files (e.g. .wav files) generated
    by the tests using relative paths are created in this folder rather than in the project root.
    """
    generated_dir = tmp_path / "generated_audio"
    generated_dir.mkdir()
    monkeypatch.chdir(generated_dir)
    print("Current working directory changed to:", os.getcwd())

@pytest.fixture(autouse=True)
def mock_http_calls(request):
    """
    Automatically mock external HTTP calls using respx unless the test is marked as integration.
    To run a live HTTP call (e.g. for integration tests), mark the test with @pytest.mark.integration.
    """
    if request.node.get_closest_marker("integration"):
        # For integration tests, do not mock HTTP calls.
        yield
    else:
        with respx.mock(assert_all_called=False) as respx_mock:
            # Example: Default mock for OpenRouter API endpoint.
            respx_mock.post("https://openrouter.ai/api/v1/completions").mock(
                return_value=httpx.Response(200, json={"dummy": "response"})
            )
            yield respx_mock 

# Define dummy classes to simulate a valid LLM response structure
class DummyNodeInner:
    def get_content(self):
        return "dummy indexed content"
    metadata = {"label": "test", "info": "dummy metadata"}

class DummyNode:
    node = DummyNodeInner()
    score = 1.0

class DummyResponse:
    # Although the choice isn't used in search_audio, we include it for completeness
    class DummyChoice:
        text = "dummy response"
    choices = [DummyChoice()]
    # This attribute is used by search_audio to extract search results
    source_nodes = [DummyNode()]

def dummy_complete(self, prompt, **kwargs):
    return DummyResponse()

@pytest.fixture(autouse=True)
def patch_llm(monkeypatch):
    """
    Automatically patch the 'complete' method of OpenAILike to return a dummy
    response. This bypasses the external API call during tests.
    """
    monkeypatch.setattr(OpenAILike, "complete", dummy_complete) 