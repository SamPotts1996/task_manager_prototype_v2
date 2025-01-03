from abc import ABC, abstractmethod
from typing import Dict
from core.models.llm import LlamaInterface
from core.memory.vector import VectorStorage

class BaseAgent(ABC):
    def __init__(self, llm: LlamaInterface, memory: VectorStorage):
        self.llm = llm
        self.memory = memory
        self.state: Dict = {}

    @abstractmethod
    def process(self, input_data: Dict) -> Dict:
        pass

    def get_state(self) -> Dict:
        return self.state.copy()

    def update_state(self, new_state: Dict):
        self.state.update(new_state)
