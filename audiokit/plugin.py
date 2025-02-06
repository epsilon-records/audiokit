"""Plugin system for AudioKit."""
from typing import Dict, Any, Callable
import importlib
import logging

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages AudioKit plugins and extensions."""
    
    def __init__(self):
        """Initialize plugin manager."""
        self.plugins: Dict[str, Any] = {}
        self.processors: Dict[str, Callable] = {}
    
    def register(self, name: str, plugin: Any) -> None:
        """Register a new plugin.
        
        Args:
            name: Plugin name
            plugin: Plugin instance
        """
        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name}")
    
    def load_plugin(self, module_path: str) -> None:
        """Load plugin from Python module.
        
        Args:
            module_path: Import path to plugin module
        """
        try:
            module = importlib.import_module(module_path)
            plugin = module.setup()
            name = getattr(module, "PLUGIN_NAME", module_path)
            self.register(name, plugin)
        except Exception as e:
            logger.error(f"Failed to load plugin {module_path}: {e}")
            raise 