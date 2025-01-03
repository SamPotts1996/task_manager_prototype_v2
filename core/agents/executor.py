import logging
from typing import Dict, Optional
from core.models.llm import LlamaInterface
from core.memory.vector import VectorStorage
from .base import BaseAgent
from core.models.prompts import PromptTemplates

logger = logging.getLogger(__name__)

class ExecutorAgent(BaseAgent):
    def __init__(self, llm: LlamaInterface, memory: VectorStorage):
        super().__init__(llm, memory)

    def execute(self, task: Dict, context: str) -> Optional[str]:
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.TASK_EXECUTION,
            objective=task.get('objective', ''),
            task=task.get('description', ''),
            context=context
        )
        logger.info(f"[ExecutorAgent] Generating with prompt:\n{prompt}\n")
        result = self.llm.generate(prompt, max_tokens=task.get('max_tokens', 200))
        logger.info(f"[ExecutorAgent] LLM responded with:\n{result}\n")
        return result

    def process(self, input_data: Dict) -> Dict:
        result = self.execute(input_data, input_data.get('context', ''))
        return {
            'task_id': input_data.get('id'),
            'result': result,
            'status': 'completed' if result else 'failed'
        }
