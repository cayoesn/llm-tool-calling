import pytest
from app.runtime.registry import ToolRegistry, BaseTool
from app.schemas.tool import ToolMetadata

class MockTool(BaseTool):
    def __init__(self, name="mock_tool"):
        metadata = ToolMetadata(
            name=name,
            description="Mock tool",
            input_schema={},
            output_schema={}
        )
        super().__init__(metadata)

    async def execute(self, **kwargs):
        return "success"

def test_register_tool():
    registry = ToolRegistry()
    tool = MockTool()
    registry.register_tool(tool)
    
    assert len(registry.list_tools()) == 1
    assert registry.get_tool("mock_tool") == tool

def test_list_tools():
    registry = ToolRegistry()
    registry.register_tool(MockTool("tool1"))
    registry.register_tool(MockTool("tool2"))
    
    tools = registry.list_tools()
    assert len(tools) == 2
    assert any(t.name == "tool1" for t in tools)
    assert any(t.name == "tool2" for t in tools)

def test_get_tool_metadata():
    registry = ToolRegistry()
    tool = MockTool()
    registry.register_tool(tool)
    
    metadata = registry.get_tool_metadata("mock_tool")
    assert metadata.name == "mock_tool"
    assert metadata.description == "Mock tool"
