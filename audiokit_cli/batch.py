"""Batch processing support for AudioKit client."""
from typing import List, Dict, Any, Union
from pathlib import Path
import asyncio
from dataclasses import dataclass
from .errors import BatchError

@dataclass
class BatchItem:
    """Single item in a batch request."""
    audio: Union[str, Path]
    options: Dict[str, Any]
    result: Any = None
    error: Exception = None

class BatchProcessor:
    """Handles batch processing of audio files."""
    
    def __init__(self, client, max_concurrent: int = 5):
        """Initialize batch processor.
        
        Args:
            client: AudioKit client instance
            max_concurrent: Maximum concurrent requests
        """
        self.client = client
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def _process_item(self, item: BatchItem) -> None:
        """Process single batch item.
        
        Args:
            item: Batch item to process
        """
        try:
            async with self.semaphore:
                if "analyze" in item.options:
                    item.result = await self.client.analyze(
                        item.audio,
                        **item.options.get("analyze_options", {})
                    )
                elif "process" in item.options:
                    item.result = await self.client.process(
                        item.audio,
                        **item.options.get("process_options", {})
                    )
                else:
                    raise BatchError("Invalid operation in batch item")
        except Exception as e:
            item.error = e
            
    async def process(self, items: List[BatchItem]) -> List[BatchItem]:
        """Process batch of items.
        
        Args:
            items: List of batch items to process
            
        Returns:
            Processed batch items with results/errors
            
        Raises:
            BatchError: If batch processing fails
        """
        try:
            tasks = [
                asyncio.create_task(self._process_item(item))
                for item in items
            ]
            await asyncio.gather(*tasks)
            return items
        except Exception as e:
            raise BatchError(f"Batch processing failed: {str(e)}") 