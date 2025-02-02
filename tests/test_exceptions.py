import pytest
from audiokit.core.exceptions import (
    AudioKitError,
    ValidationError,
    ProcessingError,
    IndexingError
)
from audiokit.core.logging import get_logger

logger = get_logger(__name__)

def test_audio_kit_error():
    """Test base AudioKitError"""
    with pytest.raises(AudioKitError):
        logger.info("Testing AudioKitError")
        raise AudioKitError("Test error")

def test_validation_error():
    """Test ValidationError"""
    with pytest.raises(ValidationError):
        logger.info("Testing ValidationError")
        raise ValidationError("Validation failed") 