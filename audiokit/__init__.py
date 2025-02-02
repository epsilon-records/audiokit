"""
AudioKit SDK
============

A powerful audio processing toolkit with AI-driven features.

Basic usage:
    >>> from audiokit import ak
    >>> features = ak.analyze_audio("path/to/audio.wav")
    >>> print(features)
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from .ai.analysis import AudioAnalyzer
from .ai.processing import AudioProcessor
from .ai.generation import AudioGenerator
from .services.clients import SoundchartsClient
from .core.exceptions import AudioKitError, ValidationError
from .core.logging import setup_logging, get_logger
from .core.indexing import audio_index

# Get module logger
logger = get_logger(__name__)

class AudioKit:
    """Main AudioKit class providing access to all audio processing features."""
    
    def __init__(self):
        """Initialize AudioKit with default configuration."""
        self._setup_logging()
        self._initialize_components()
        self._initialize_services()
        logger.success("AudioKit initialized successfully")  # Note: using success level
    
    def _setup_logging(self):
        """Configure logging based on environment."""
        log_level = os.getenv("AUDIOKIT_LOG_LEVEL", "INFO")
        log_file = os.getenv("AUDIOKIT_LOG_FILE")
        
        # Add custom logging levels if needed
        logger.level("PROCESSING", no=25, color="<cyan>")
        logger.level("ANALYSIS", no=24, color="<blue>")
        
        setup_logging(log_level=log_level, log_file=log_file)
    
    @logger.catch(reraise=True)
    def _initialize_components(self):
        """Initialize core components."""
        try:
            self.analyzer = AudioAnalyzer()
            self.processor = AudioProcessor()
            self.generator = AudioGenerator()
        except Exception as e:
            logger.opt(exception=True).error("Failed to initialize components")
            raise AudioKitError("Component initialization failed") from e
    
    def _validate_audio_file(self, audio_path: str) -> Path:
        """Validate audio file path and format."""
        path = Path(audio_path)
        if not path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            raise ValidationError(f"Audio file not found: {audio_path}")
        
        if path.suffix.lower() not in ['.wav', '.mp3', '.flac']:
            logger.error(f"Unsupported audio format: {path.suffix}")
            raise ValidationError(f"Unsupported audio format: {path.suffix}")
        
        return path
    
    @logger.catch(reraise=True)
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze audio file and return comprehensive features.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict: Analysis results including BPM, key, genre, and instruments
            
        Raises:
            ValidationError: If audio file is invalid
            AudioKitError: If analysis fails
        """
        try:
            path = self._validate_audio_file(audio_path)
            logger.log("ANALYSIS", f"Analyzing audio file: {path}")
            
            with logger.contextualize(operation="analysis", file=path.name):
                results = {
                    "bpm_key": self.analyzer.detect_bpm_key(str(path)),
                    "genre": self.analyzer.classify_genre(str(path)),
                    "instruments": self.analyzer.identify_instruments(str(path))
                }
                logger.debug("Analysis results: {}", results)
                
                # Index with versioning
                audio_index.index_data(str(path), results, "analysis")
                
                return results
                
        except Exception as e:
            logger.opt(exception=True).error("Audio analysis failed")
            raise AudioKitError("Audio analysis failed") from e
    
    def _initialize_services(self):
        """Initialize external service clients."""
        self.soundcharts = SoundchartsClient(
            app_id=os.getenv("SOUNDCHARTS_APP_ID"),
            api_key=os.getenv("SOUNDCHARTS_API_KEY")
        )
    
    def process_audio(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        extract_vocals: bool = False,
        separate_stems: bool = False,
        reduce_noise: bool = False
    ) -> Dict[str, Any]:
        """
        Process audio with selected operations.
        
        Args:
            audio_path: Path to audio file
            output_dir: Directory for output files
            extract_vocals: Whether to extract vocals
            separate_stems: Whether to separate stems
            reduce_noise: Whether to reduce noise
            
        Returns:
            dict: Paths to processed audio files
        """
        try:
            results = {}
            path = self._validate_audio_file(audio_path)
            
            if extract_vocals:
                results["vocals"] = self.processor.extract_vocals(audio_path)
            
            if separate_stems:
                results["stems"] = self.processor.separate_stems(audio_path, output_dir)
            
            if reduce_noise:
                results["cleaned"] = self.processor.reduce_noise(audio_path)
            
            # Index processing results
            if results:
                audio_index.index_data(
                    str(path),
                    {
                        "processing": results,
                        "operations": {
                            "vocals": extract_vocals,
                            "stems": separate_stems,
                            "noise": reduce_noise
                        }
                    },
                    "processing"
                )
            
            return results
        except Exception as e:
            logger.exception("Audio processing failed")
            raise AudioKitError("Audio processing failed") from e

    def generate_content(
        self,
        audio_path: Optional[str] = None,
        instrument_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio-related content.
        
        Args:
            audio_path: Path to reference audio file
            instrument_description: Description for instrument generation
            
        Returns:
            dict: Generated content details
        """
        try:
            results = {}
            
            if audio_path:
                results["moodboard"] = self.generator.generate_moodboard(audio_path)
                
            if instrument_description:
                results["instrument"] = self.generator.generate_instrument(
                    instrument_description
                )
            
            # Index generation results
            if audio_path and results:
                audio_index.index_data(
                    audio_path,
                    {
                        "generated_content": results,
                        "generation_type": list(results.keys())
                    },
                    "generation"
                )
            
            return results
        except Exception as e:
            logger.exception("Content generation failed")
            raise AudioKitError("Content generation failed") from e

    @logger.catch(reraise=True)
    def find_similar(
        self,
        audio_path: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar audio files based on analysis."""
        path = self._validate_audio_file(audio_path)
        logger.info("Finding similar audio to: {}", path)
        
        return audio_index.similar_audio(str(path), n_results)
    
    @logger.catch(reraise=True)
    def search_audio(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search audio analyses with natural language."""
        logger.info("Searching audio with query: {}", query)
        
        return audio_index.search(query, n_results, filters)

# Create global instance
ak = AudioKit()

__all__ = ['ak', 'AudioKit']
