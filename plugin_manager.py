import importlib.metadata
from fastapi import FastAPI
from typing import List

from audiokit.plugin_interface import BasePlugin


def load_plugins(app: FastAPI) -> List[BasePlugin]:
    """Discover and load plugins registered under the 'audiokit.plugins' entry point group.

    Each plugin's register_routes() method will be called to integrate its endpoints into the given FastAPI app.
    """
    plugins: List[BasePlugin] = []
    entry_point_group = "audiokit.plugins"

    # Use importlib.metadata.entry_points() which returns an EntryPoints object in Python 3.10+
    eps = importlib.metadata.entry_points()

    # For compatibility with older Python versions
    if hasattr(eps, "select"):
        available_eps = eps.select(group=entry_point_group)
    else:
        available_eps = eps.get(entry_point_group, [])

    for ep in available_eps:
        try:
            plugin_class = ep.load()
            # Ensure that the class is a subclass of BasePlugin
            if issubclass(plugin_class, BasePlugin):
                plugin = plugin_class()
                plugin.register_routes(app)
                plugins.append(plugin)
                print(f"Loaded plugin: {plugin.get_metadata().get('name')}")
            else:
                print(f"Entry point {ep.name} does not implement BasePlugin")
        except Exception as e:
            print(f"Failed to load plugin {ep.name}: {e}")

    return plugins
