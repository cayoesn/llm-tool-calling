from app.runtime.registry import BaseTool, registry
from app.schemas.tool import ToolMetadata
import logging

logger = logging.getLogger(__name__)

class CalculatorTool(BaseTool):
    def __init__(self):
        metadata = ToolMetadata(
            name="calculator",
            description="Performs basic arithmetic calculations.",
            category="utility",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression to evaluate (e.g., '2 + 2')"}
                },
                "required": ["expression"]
            },
            output_schema={"type": "number"}
        )
        super().__init__(metadata)

    async def execute(self, expression: str) -> float:
        # NOTE: Using eval is generally dangerous. In a real app, use a safer math parser.
        # For this mock/prototype, we'll use a restricted environment or simple eval.
        try:
            # Strip potentially dangerous characters
            allowed_chars = "0123456789+-*/(). "
            if any(char not in allowed_chars for char in expression):
                raise ValueError("Invalid characters in expression")
            
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            logger.error(f"Calculator error: {str(e)}")
            raise

def register_tools():
    registry.register_tool(CalculatorTool())
    # Other tools will be registered here
