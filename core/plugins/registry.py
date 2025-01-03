import logging
from typing import Dict, Any, Optional, Callable
import importlib

logger = logging.getLogger(__name__)

class PluginRegistry:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.commands: Dict[str, Callable] = {}

    def register_plugin(self, name: str, plugin: Any):
        if name in self.plugins:
            raise ValueError(f"Plugin {name} already registered")
        self.plugins[name] = plugin

    def register_command(self, name: str, handler: Callable):
        if name in self.commands:
            raise ValueError(f"Command {name} already registered")
        self.commands[name] = handler

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.plugins.get(name)

    def execute_command(self, command: str, *args, **kwargs) -> Any:
        handler = self.commands.get(command)
        if handler:
            return handler(*args, **kwargs)
        raise ValueError(f"Unknown command: {command}")

    def load_plugin(self, module_path: str, class_name: str):
        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            plugin = plugin_class()
            self.register_plugin(class_name, plugin)
            return plugin
        except Exception as e:
            logger.exception(f"Error loading plugin {module_path}.{class_name}: {e}")
            return None
