from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from app.schemas.tool import ToolMetadata, ToolResult, ToolCall
import logging

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        if tool.metadata.name in self._tools:
            logger.warning(f"Tool {tool.metadata.name} already registered. Overwriting.")
        self._tools[tool.metadata.name] = tool
        logger.info(f"Tool {tool.metadata.name} registered successfully.")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolMetadata]:
        return [tool.metadata for tool in self._tools.values()]

    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        tool = self.get_tool(name)
        return tool.metadata if tool else None

# Singleton instance
registry = ToolRegistry()
