from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "core" / "model"
DATA_DIR = BASE_DIR / "data"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

MODEL_CONFIG = {
    "model_path": str(MODEL_DIR / "Llama-3.2-3B-Instruct-Q8_0.gguf"),
    "n_ctx": 2048,
    "max_tokens": 200,
    "temperature": 0.1,
}

SYSTEM_CONFIG = {
    "max_tasks": 10,
    "batch_size": 3,
    "debug": False
}

MEMORY_CONFIG = {
    "vector_db_path": str(DATA_DIR / "chroma_db"),
    "state_db_path": str(DATA_DIR / "agent_state.db")
}

RESOURCE_LIMITS = {
    "max_memory_percent": 80.0,
    "max_cpu_percent": 90.0,
}

TOOL_CONFIG = {
    "enabled_tools": [
        "file_reader",
        "file_writer",
        "web_search",
        "system_info"
    ],
    "tool_timeout": 30,  # seconds
}
