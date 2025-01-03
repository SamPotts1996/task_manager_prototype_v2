import logging
import importlib
import os
from typing import Dict, List, Optional, Callable, Any

logger = logging.getLogger(__name__)

class Tool:
    def __init__(self, name: str, description: str, function: Callable, requirements: List[str] = None):
        self.name = name
        self.description = description
        self.function = function
        self.requirements = requirements or []
        self.metadata = {}

class ToolMarketplace:
    def __init__(self, tools_directory: str = "tools"):
        self.tools: Dict[str, Tool] = {}
        self.tools_directory = tools_directory
        self.load_tools()

    def load_tools(self):
        if not os.path.exists(self.tools_directory):
            logger.info(f"[ToolMarketplace] No tools directory found at {self.tools_directory}.")
            return
        for filename in os.listdir(self.tools_directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                try:
                    module_name = filename[:-3]
                    module = importlib.import_module(f"tools.{module_name}")
                    if hasattr(module, 'TOOL_CONFIG'):
                        tool_config = module.TOOL_CONFIG
                        self.register_tool(
                            name=tool_config['name'],
                            description=tool_config['description'],
                            function=getattr(module, tool_config['function']),
                            requirements=tool_config.get('requirements', [])
                        )
                except Exception as e:
                    logger.error(f"Error loading tool {filename}: {e}", exc_info=True)

    def register_tool(self, name: str, description: str, function: Callable, requirements: List[str] = None) -> bool:
        if name in self.tools:
            return False
        self.tools[name] = Tool(name, description, function, requirements)
        logger.info(f"[ToolMarketplace] Loaded tool: {name}")
        return True

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[Dict]:
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'requirements': tool.requirements
            }
            for tool in self.tools.values()
        ]

    def execute_tool(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool.function(**kwargs)
