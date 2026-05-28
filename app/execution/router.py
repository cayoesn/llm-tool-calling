import asyncio
from typing import List, Dict, Any
from app.execution.engine import ExecutionEngine
from app.schemas.tool import ToolCall, ToolResult
import logging

logger = logging.getLogger(__name__)

class ToolRouter:
    def __init__(self, execution_engine: ExecutionEngine):
        self.execution_engine = execution_engine

    async def dispatch(self, tool_calls: List[ToolCall], parallel: bool = True) -> List[ToolResult]:
        if not tool_calls:
            return []

        if parallel:
            return await self._dispatch_parallel(tool_calls)
        else:
            return await self._dispatch_sequential(tool_calls)

    async def _dispatch_parallel(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        tasks = [self.execution_engine.execute_tool(call) for call in tool_calls]
        return list(await asyncio.gather(*tasks))

    async def _dispatch_sequential(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        results = []
        for call in tool_calls:
            result = await self.execution_engine.execute_tool(call)
            results.append(result)
        return results
