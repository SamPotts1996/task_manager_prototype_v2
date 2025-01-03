import logging
from typing import Dict, List
from .base import BaseAgent
from core.models.llm import LlamaInterface
from core.memory.vector import VectorStorage
from core.models.prompts import PromptTemplates
import re

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    def __init__(self, llm: LlamaInterface, memory: VectorStorage):
        super().__init__(llm, memory)

    def process(self, input_data: Dict) -> Dict:
        objective = input_data.get('objective', '')
        if not objective:
            logger.warning("PlannerAgent received no objective.")
            return {'status': 'failed', 'error': 'No objective provided'}

        tasks = self.create_plan(objective)
        return {
            'status': 'success',
            'tasks': tasks
        }

    def create_plan(self, objective: str) -> Dict:
        context = self.memory.get_context(objective)
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.TASK_PLANNING,
            objective=objective,
            context=context
        )
        logger.info(f"[PlannerAgent] Generating plan with prompt:\n{prompt}\n")
        response = self.llm.generate(prompt)
        logger.info(f"[PlannerAgent] Plan generation returned:\n{response}\n")

        tasks = self._parse_tasks(response, objective)
        return {"tasks": tasks}

    def _parse_tasks(self, response: str, objective: str) -> List[Dict]:
        tasks = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith("TASK#"):
                description = line[5:].strip()
                tasks.append({
                    'description': description,
                    'objective': objective,
                    'status': 'pending',
                    'priority': len(tasks),
                    'type': 'task'
                })
            elif line.startswith("TOOL#"):
                tool_line = line[5:].strip()
                parts = tool_line.split(None, 1)
                if len(parts) == 1:
                    tool_name = parts[0]
                    tool_args = {}
                else:
                    tool_name, args_str = parts
                    tool_args = self._parse_tool_args(args_str)
                tasks.append({
                    'description': f"Use tool {tool_name}",
                    'objective': objective,
                    'status': 'pending',
                    'priority': len(tasks),
                    'type': 'tool',
                    'tool_name': tool_name,
                    'tool_args': tool_args
                })
        return tasks

    def _parse_tool_args(self, args_str: str) -> dict:
        pattern = r'(\S+)=(".*?"|\S+)'
        matches = re.findall(pattern, args_str)
        parsed = {}
        for (key, val) in matches:
            val = val.strip('"')
            parsed[key] = val
        return parsed
