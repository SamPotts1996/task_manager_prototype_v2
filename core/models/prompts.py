import logging

logger = logging.getLogger(__name__)

class PromptTemplates:
    TASK_PLANNING = """Given an objective:
{objective}

Context from memory:
{context}

You can create normal tasks or tool tasks.

- Normal task:
  TASK# <description>

- Tool task:
  TOOL# <tool_name> <args in key=value form>

Example:
TASK# Research relevant files
TOOL# file_reader path="somefile.txt"
TASK# Summarize the contents

Now, produce the steps to accomplish the objective.
"""

    TASK_EXECUTION = """Objective: {objective}
Task: {task}
Context: {context}
Execute this task and provide the result."""

    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing key in prompt template: {e}")
            return template
