import os
import json
from typing import Optional
from ..base_tool import BaseTool

class FileReader(BaseTool):
    def __init__(self):
        super().__init__(
            name="file_reader",
            description="Read content from files"
        )

    def execute(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

class FileWriter(BaseTool):
    def __init__(self):
        super().__init__(
            name="file_writer",
            description="Write content to files"
        )

    def execute(self, file_path: str, content: str) -> bool:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False