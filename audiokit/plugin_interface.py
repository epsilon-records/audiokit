from abc import ABC, abstractmethod
from fastapi import FastAPI
from typing import Dict


class BasePlugin(ABC):
    @abstractmethod
    def register_routes(self, app: FastAPI):
        """Register plugin routes into the FastAPI application."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata including name, version, and description."""
        pass
