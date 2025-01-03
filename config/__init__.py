from pathlib import Path
from .settings import (
    MODEL_CONFIG,
    SYSTEM_CONFIG,
    MEMORY_CONFIG,
    RESOURCE_LIMITS,
    TOOL_CONFIG
)

def get_config():
    return {
        "model_path": MODEL_CONFIG["model_path"],
        "n_ctx": MODEL_CONFIG["n_ctx"],
        "max_tokens": MODEL_CONFIG["max_tokens"],
        "temperature": MODEL_CONFIG["temperature"],
        **SYSTEM_CONFIG,
        **MEMORY_CONFIG,
        **RESOURCE_LIMITS,
    }

__all__ = ['get_config', 'MODEL_CONFIG', 'SYSTEM_CONFIG', 'MEMORY_CONFIG', 'RESOURCE_LIMITS', 'TOOL_CONFIG']
