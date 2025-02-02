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

import pinecone
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

from .logging import get_logger
from .exceptions import IndexingError
from .config import config

logger = get_logger(__name__)

class AudioIndex:
    """Manages indexing and searching of audio analysis results."""
    
    def __init__(self):
        """Initialize the audio index."""
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=config.get("PINECONE_API_KEY"),
                environment=config.get("PINECONE_ENV")
            )
            
            # Get or create index
            index_name = "audiokit"
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # Default for OpenAI embeddings
                    metric="cosine"
                )
            
            # Setup vector store
            pinecone_index = pinecone.Index(index_name)
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Initialize vector store index
            self.index = VectorStoreIndex.from_documents(
                [],
                storage_context=storage_context,
                show_progress=True  # Show progress in the method
            )
            
            logger.info("Audio index initialized successfully")
            
        except Exception as e:
            logger.exception("Failed to initialize audio index")
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
        """
        Search indexed audio data.
        """
        try:
            # Execute search
            response = self.index.as_query_engine().query(
                query,
                similarity_top_k=n_results,
                filters=filters
            )
            
            # Format results
            results = []
            for node in response.source_nodes:
                results.append({
                    "score": node.score,
                    "content": json.loads(node.text),
                    "metadata": node.metadata
                })
            
            return results
            
        except Exception as e:
            logger.exception("Search failed")
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