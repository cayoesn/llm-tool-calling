from app.runtime.registry import BaseTool, registry
from app.schemas.tool import ToolMetadata
import logging
import os

logger = logging.getLogger(__name__)

class FileReaderTool(BaseTool):
    def __init__(self):
        metadata = ToolMetadata(
            name="read_file",
            description="Reads the content of a file from the 'docs' directory.",
            category="file_system",
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file to read"}
                },
                "required": ["filename"]
            },
            output_schema={"type": "string"}
        )
        super().__init__(metadata)

    async def execute(self, filename: str) -> str:
        # Restriction: only read from the 'docs' directory for security basics
        safe_dir = os.path.abspath("docs")
        file_path = os.path.abspath(os.path.join(safe_dir, filename))
        
        if not file_path.startswith(safe_dir):
            raise ValueError("Access denied: path is outside of docs directory")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {filename} not found")
            
        with open(file_path, "r") as f:
            return f.read()
