# Plugin Guide for Audiokit

## Overview

The Audiokit package provides a plugin architecture that allows you to extend its functionality by creating independent modules. Plugins are discovered using entry points declared in your pyproject.toml, making it easy to integrate community contributions or proprietary features.

## Base Plugin Interface

The base interface is defined in `audiokit/plugin_interface.py`:

```python
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
```

## Creating a New Plugin

1. Create your plugin file (e.g., `my_plugin.py`) in the `audiokit/plugins/` directory.
2. Implement your plugin class inheriting from `BasePlugin`.
3. Register endpoints by implementing the `register_routes(app: FastAPI)` method.

**Example:**

```python
from fastapi import FastAPI, APIRouter
from typing import Dict
from audiokit.plugin_interface import BasePlugin

class MyPlugin(BasePlugin):
    def register_routes(self, app: FastAPI):
        router = APIRouter()

        @router.get("/hello")
        async def hello():
            return {"message": "Hello from MyPlugin!"}

        app.include_router(router, prefix="/plugins/my_plugin")

    def get_metadata(self) -> Dict[str, str]:
        return {"name": "My Plugin", "version": "1.0.0", "description": "An example plugin."}
```

## Configuring Entry Points

To have your plugin discovered, add an entry in your project's `pyproject.toml`` under the`[tool.poetry.plugins."audiokit.plugins"]` group. For example:

```toml
[tool.poetry.plugins."audiokit.plugins"]
my_plugin = "audiokit.plugins.my_plugin:MyPlugin"
```

## Plugin Manager

At application startup, the plugin manager in `audiokit/plugin_manager.py` will use Python's `importlib.metadata` to load all plugins registered under the `audiokit.plugins` entry point group and automatically register their routes.

## Testing Your Plugin

1. Run the API server and check the logs for plugin load messages.
2. Verify that the new routes (e.g., `/plugins/my_plugin/hello`) are accessible.

## Conclusion

This plugin system allows for a modular expansion of Audiokit, fostering community contributions and enabling integration of proprietary features as plugins without altering the core codebase.
