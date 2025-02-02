"""
AudioKit Indexing
===============

Intelligent indexing and search using LlamaIndex.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
    ServiceContext,
    StorageContext
)
from llama_index.vector_stores import PineconeVectorStore
from llama_index.embeddings import OpenAIEmbedding

from .logging import get_logger
from .config import config
from .exceptions import IndexingError

logger = get_logger(__name__)

class AudioIndex:
    """Manages intelligent indexing and search for audio data."""
    
    def __init__(self):
        """Initialize the audio indexing system."""
        logger.debug("Initializing AudioIndex")
        self._setup_index()
        self._version_tracker = defaultdict(int)  # Track document versions
    
    def _setup_index(self):
        """Setup the indexing infrastructure."""
        try:
            # Initialize embedding model
            embed_model = OpenAIEmbedding()
            service_context = ServiceContext.from_defaults(
                embed_model=embed_model
            )
            
            # Initialize vector store
            vector_store = PineconeVectorStore(
                index_name="audiokit-index"
            )
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store
            )
            
            # Create or load index
            self.index = VectorStoreIndex(
                [],
                service_context=service_context,
                storage_context=storage_context
            )
            
            logger.info("Index setup complete")
            
        except Exception as e:
            logger.exception("Failed to setup index")
            raise IndexingError("Failed to initialize indexing") from e
    
    def _get_version(self, audio_path: str, operation: str) -> int:
        """Get current version for a document."""
        key = f"{audio_path}-{operation}"
        self._version_tracker[key] += 1
        return self._version_tracker[key]
    
    def index_data(
        self,
        audio_path: str,
        data: Dict[str, Any],
        operation: str
    ) -> None:
        """
        Index audio data with versioning and enhanced metadata.
        
        Args:
            audio_path: Path to the audio file
            data: Data to index
            operation: Type of operation (analysis/processing/generation)
        """
        try:
            logger.info("Indexing {} results for: {}", operation, audio_path)
            
            # Create enhanced metadata
            metadata = {
                "audio_path": audio_path,
                "file_name": Path(audio_path).name,
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "version": self._get_version(audio_path, operation)
            }
            
            # Create document with versioning
            document = Document(
                text=json.dumps(data, indent=2),
                metadata=metadata,
                id=f"{audio_path}-{operation}-{metadata['version']}"
            )
            
            # Insert document
            self.index.insert(document)
            logger.success("Successfully indexed {} results", operation)
            
        except Exception as e:
            logger.exception("Failed to index data")
            raise IndexingError("Data indexing failed") from e
    
    def index_analysis(
        self,
        audio_path: str,
        analysis_results: Dict[str, Any]
    ) -> None:
        """
        Index audio analysis results.
        
        Args:
            audio_path: Path to the analyzed audio file
            analysis_results: Analysis results to index
        """
        try:
            logger.info("Indexing analysis results for: {}", audio_path)
            
            # Create document from analysis results
            doc_text = json.dumps(analysis_results, indent=2)
            metadata = {
                "audio_path": audio_path,
                "file_name": Path(audio_path).name,
                "analysis_type": list(analysis_results.keys())
            }
            
            document = Document(
                text=doc_text,
                metadata=metadata
            )
            
            # Index the document
            self.index.insert(document)
            logger.success("Successfully indexed analysis results")
            
        except Exception as e:
            logger.exception("Failed to index analysis results")
            raise IndexingError("Failed to index analysis") from e
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search indexed audio analyses.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of matching results with scores
        """
        try:
            logger.info("Searching with query: {}", query)
            
            # Create query engine
            query_engine = self.index.as_query_engine(
                similarity_top_k=n_results
            )
            
            # Execute search
            response = query_engine.query(query)
            
            # Format results
            results = []
            for node in response.source_nodes:
                result = {
                    "score": node.score,
                    "metadata": node.metadata,
                    "content": json.loads(node.text)
                }
                results.append(result)
            
            logger.debug("Found {} results", len(results))
            return results
            
        except Exception as e:
            logger.exception("Search failed")
            raise IndexingError("Failed to execute search") from e
    
    def similar_audio(
        self,
        audio_path: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar audio files based on analysis.
        
        Args:
            audio_path: Path to reference audio file
            n_results: Number of results to return
            
        Returns:
            List of similar audio files with similarity scores
        """
        try:
            logger.info("Finding similar audio to: {}", audio_path)
            
            # Get reference audio metadata
            query = f"file_name:{Path(audio_path).name}"
            ref_results = self.search(query, n_results=1)
            
            if not ref_results:
                raise IndexingError("Reference audio not found in index")
            
            ref_analysis = ref_results[0]["content"]
            
            # Search for similar audio
            query = json.dumps(ref_analysis)
            results = self.search(query, n_results=n_results + 1)
            
            # Remove reference audio from results
            results = [r for r in results if r["metadata"]["audio_path"] != audio_path]
            
            logger.debug("Found {} similar audio files", len(results))
            return results[:n_results]
            
        except Exception as e:
            logger.exception("Similar audio search failed")
            raise IndexingError("Failed to find similar audio") from e

# Global index instance
audio_index = AudioIndex() 