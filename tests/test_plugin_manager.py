from fastapi import FastAPI

from audiokit.plugin_manager import load_plugins


def test_plugin_loading():
    app = FastAPI()
    plugins = load_plugins(app)
    # Check that plugins is a list
    assert isinstance(plugins, list)

    # If plugins are loaded, check that each has metadata with a 'name' key
    for plugin in plugins:
        metadata = plugin.get_metadata()
        assert isinstance(metadata, dict)
        assert "name" in metadata


if __name__ == "__main__":
    test_plugin_loading()
    print("Plugin loading test passed")
