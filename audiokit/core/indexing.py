"""
Audio Indexing Module
===================
Handles indexing and searching of audio analysis results.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from llama_index.core import VectorStoreIndex, Document, StorageContext, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore

from .logging import get_logger
from .exceptions import IndexingError, ConfigurationError
from .config import config
from .openrouter_config import configure_openrouter

logger = get_logger(__name__)

class AudioIndex:
    """Manages indexing and searching of audio analysis results."""
    
    def __init__(self):
        """Initialize the audio index."""
        try:
            logger.debug("Initializing AudioIndex")
            
            if not config.pinecone_api_key:
                logger.error("Pinecone API key is missing in configuration")
                raise ConfigurationError("Pinecone API key is not configured")
            
            logger.debug(f"Using Pinecone index: {config.pinecone_index_name}")
            logger.debug("Initializing Pinecone vector store")
            
            # Configure OpenRouter
            llm, embed_model = configure_openrouter(config.openrouter_api_key)
            
            # Update LlamaIndex settings
            Settings.llm = llm
            Settings.embed_model = embed_model
            
            # Initialize Pinecone vector store through LlamaIndex
            vector_store = PineconeVectorStore(
                api_key=config.pinecone_api_key,
                index_name=config.pinecone_index_name,
                insert_kwargs={},
                add_sparse_vector=False,
                tokenizer=None,
                default_empty_query_vector=None,
                text_key="text"
            )
            
            logger.debug("Creating storage context")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            logger.debug("Initializing vector store index")
            self.index = VectorStoreIndex.from_documents(
                [],
                storage_context=storage_context,
                show_progress=True
            )
            
            logger.info("Audio index initialized successfully")
            
        except ConfigurationError as e:
            logger.error("Configuration error: {}", str(e))
            raise
        except Exception as e:
            logger.exception("Failed to initialize audio index. Error details: %s", str(e))
            logger.error("Pinecone API key used: %s", config.pinecone_api_key)
            logger.error("Pinecone index name: %s", config.pinecone_index_name)
            raise IndexingError("Index initialization failed") from e
    
    def index_data(
        self,
        audio_path: str,
        data: Dict[str, Any],
        operation: str
    ) -> None:
        """
        Index audio analysis or processing results.
        """
        try:
            # Create metadata
            metadata = {
                "audio_path": audio_path,
                "file_name": Path(audio_path).name,
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "version": self._get_next_version(audio_path),
                "id": f"{Path(audio_path).stem}_{operation}"
            }
            
            # Create document
            doc = Document(
                text=json.dumps(data, indent=2),
                metadata=metadata
            )
            
            # Insert document into the index
            self.index.insert(doc)
            logger.debug("Indexed %s data for: %s", operation, audio_path)
            
        except Exception as e:
            logger.exception("Failed to index data")
            raise IndexingError("Data indexing failed") from e
    
    def _get_next_version(self, audio_path: str) -> int:
        """Get next version number for audio file."""
        try:
            results = self.search_audio(f"file_name:{Path(audio_path).name}")
            if not results:
                return 1
            versions = [r["metadata"]["version"] for r in results]
            return max(versions) + 1
        except Exception:
            return 1
    
    def search_audio(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search audio analyses with natural language."""
        try:
            logger.info("Searching audio with query: {}", query)
            
            # Create query engine with proper parameters
            query_engine = self.index.as_query_engine(
                similarity_top_k=n_results,
                filters=filters
            )
            
            response = query_engine.query(query)
            
            if not response:
                logger.warning("No results found for query: {}", query)
                return []
            
            return [{
                "content": node.node.get_content(),
                "metadata": node.node.metadata,
                "score": node.score
            } for node in response.source_nodes]
            
        except Exception as e:
            logger.error("Search failed")
            logger.opt(exception=True).debug("Search error details")
            raise IndexingError("Search failed") from e
    
    def similar_audio(
        self,
        audio_path: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar audio files based on indexed data."""
        try:
            # Get document for reference audio
            results = self.search_audio(
                f"file_name:{Path(audio_path).name}",
                n_results=1
            )
            if not results:
                raise IndexingError(f"No index entry found for: {audio_path}")
            
            # Search for similar documents (excluding the reference itself)
            query = results[0]["content"]
            return self.search_audio(
                json.dumps(query),
                n_results=n_results + 1  # +1 to exclude self-match
            )[1:]
            
        except Exception as e:
            logger.exception("Similar audio search failed")
            raise IndexingError("Similar audio search failed") from e

# Create a global instance
audio_index = AudioIndex()