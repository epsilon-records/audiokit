from typing import Protocol, Optional
from pathlib import Path
import typer
from pydantic import BaseModel
import importlib.util
import ast
from .security import PluginVerifier, PluginVerificationError

class PluginSecurityError(Exception):
    """Base class for plugin security violations"""

class PluginConfig(BaseModel):
    """Base configuration for CLI plugins"""
    enabled: bool = True
    cli_group: Optional[str] = None

SAFE_IMPORTS = {'typer', 'pathlib', 'datetime', 'json', 'yaml', 'csv'}

class CLIPlugin(Protocol):
    @classmethod
    def config_schema(cls) -> type[PluginConfig]:
        return PluginConfig
        
    def register_commands(self, app: typer.Typer):
        pass

class PluginManager:
    def __init__(self, plugin_dir: Path = Path("~/.audiokit/plugins").expanduser()):
        self.plugin_dir = plugin_dir.resolve()
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins = {}
        self.verifier = PluginVerifier()

    def load_plugins(self):
        for plugin_file in self.plugin_dir.glob("*.py"):
            try:
                self._load_plugin(plugin_file)
            except PluginSecurityError as e:
                print(f"Blocked plugin {plugin_file.name}: {str(e)}")

    def _load_plugin(self, path: Path):
        # Verify plugin before loading
        if not self.verifier.verify_plugin(path):
            raise PluginSecurityError(f"Plugin verification failed: {path.name}")

        # Validate before loading
        self._validate_imports(path)
        
        spec = importlib.util.spec_from_file_location(f"audiokit.plugin.{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in vars(module).items():
            if isinstance(obj, type) and issubclass(obj, CLIPlugin):
                plugin = obj()
                plugin.register_commands(typer.Typer())
                self.plugins[name] = plugin

    def _validate_imports(self, path: Path):
        """Check for disallowed imports using AST"""
        with open(path) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] not in SAFE_IMPORTS:
                        raise PluginSecurityError(f"Forbidden import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module.split('.')[0] not in SAFE_IMPORTS:
                    raise PluginSecurityError(f"Forbidden import: {node.module}")

# Initialize with security
manager = PluginManager()
manager.load_plugins() 