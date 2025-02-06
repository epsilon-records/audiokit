"""Progress tracking for AudioKit operations."""
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

class ProgressState(str, Enum):
    """Operation progress states."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    DOWNLOADING = "downloading"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class Progress:
    """Progress information."""
    state: ProgressState
    total: Optional[int] = None
    completed: int = 0
    message: Optional[str] = None
    details: Optional[dict] = None

    @property
    def percentage(self) -> Optional[float]:
        """Calculate percentage complete."""
        if self.total is None or self.total == 0:
            return None
        return (self.completed / self.total) * 100

class ProgressTracker:
    """Tracks progress of operations."""
    
    def __init__(self, callback: Optional[Callable[[Progress], Any]] = None):
        """Initialize progress tracker.
        
        Args:
            callback: Optional callback for progress updates
        """
        self.callback = callback
        self._progress = Progress(state=ProgressState.PENDING)
        self._queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start progress tracking."""
        if self._task is None:
            self._task = asyncio.create_task(self._process_updates())
            
    async def stop(self):
        """Stop progress tracking."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            
    def update(
        self,
        state: Optional[ProgressState] = None,
        completed: Optional[int] = None,
        total: Optional[int] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """Update progress state.
        
        Args:
            state: New progress state
            completed: Number of units completed
            total: Total number of units
            message: Progress message
            details: Additional details
        """
        if state is not None:
            self._progress.state = state
        if completed is not None:
            self._progress.completed = completed
        if total is not None:
            self._progress.total = total
        if message is not None:
            self._progress.message = message
        if details is not None:
            self._progress.details = details
            
        # Queue update for async processing
        self._queue.put_nowait(self._progress)
        
    async def _process_updates(self):
        """Process queued progress updates."""
        try:
            while True:
                progress = await self._queue.get()
                if self.callback:
                    await asyncio.to_thread(self.callback, progress)
                self._queue.task_done()
        except asyncio.CancelledError:
            pass 