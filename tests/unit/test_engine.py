import pytest
import asyncio
from app.execution.engine import ExecutionEngine
from app.validation.validator import ToolValidator
from app.schemas.tool import ToolCall, ToolExecutionStatus
from app.runtime.registry import registry, BaseTool
from app.schemas.tool import ToolMetadata

class SuccessTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(name="success_tool", description="desc", input_schema={}, output_schema={}))
    async def execute(self, **kwargs):
        return "ok"

class FailTool(BaseTool):
    def __init__(self):
        super().__init__(ToolMetadata(name="fail_tool", description="desc", input_schema={}, output_schema={}))
    async def execute(self, **kwargs):
        raise ValueError("failed")

@pytest.mark.asyncio
async def test_execute_tool_success():
    registry.register_tool(SuccessTool())
    engine = ExecutionEngine(ToolValidator())
    call = ToolCall(tool_name="success_tool", arguments={})
    
    result = await engine.execute_tool(call)
    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.output == "ok"

@pytest.mark.asyncio
async def test_execute_tool_fail():
    registry.register_tool(FailTool())
    engine = ExecutionEngine(ToolValidator())
    call = ToolCall(tool_name="fail_tool", arguments={})
    
    result = await engine.execute_tool(call)
    assert result.status == ToolExecutionStatus.FAILED
    assert "failed" in result.error
