TOOL_CONFIG = {
    "name": "file_writer",
    "description": "Writes content to a file",
    "function": "write_file",
}

def write_file(file_path: str, content: str) -> bool:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True
