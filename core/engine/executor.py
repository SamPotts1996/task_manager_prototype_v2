import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class TaskExecutor:
    """
    The logic that knows how to 'execute' a single task.
    This typically calls the Llama model, memory, tools, etc.
    """

    def __init__(self, llm, memory, resource_manager, tool_marketplace, broker):
        self.llm = llm
        self.memory = memory
        self.resource_manager = resource_manager
        self.tool_marketplace = tool_marketplace
        self.broker = broker

    def execute_task(self, task: Dict) -> str:
        """
        Given a task dict, e.g. { description: "...", ... }, run it using the LLM.
        Return the result (string).
        """
        logger.debug("[TaskExecutor] Fetched context: (currently none/placeholder)")

        prompt = (
            "Objective: \n"
            f"Task: {task['description']}\n"
            "Context: \n"
            "Execute this task and provide the result.\n"
        )

        logger.info(f"[ExecutorAgent] Generating with prompt:\n{prompt}")
        result = self.llm.generate(prompt=prompt)
        logger.info(f"[ExecutorAgent] LLM responded with:\n{result}\n")

        # Optionally store result or relevant text in memory (embedding in separate model)
        # E.g. self.memory.store(task['id'], prompt + "\n" + result)  # if you want

        return result
