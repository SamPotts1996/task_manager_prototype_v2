from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.metadata: Dict = {}

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass

    def validate_inputs(self, **kwargs) -> bool:
        return True

    @property
    def requirements(self) -> List[str]:
        return []
