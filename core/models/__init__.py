# core/models/__init__.py
from core.models.llm import LlamaInterface
from core.models.prompts import PromptTemplates

__all__ = ['LlamaInterface', 'PromptTemplates']
