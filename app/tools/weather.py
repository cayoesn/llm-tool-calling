from app.runtime.registry import BaseTool, registry
from app.schemas.tool import ToolMetadata
import logging
import random

logger = logging.getLogger(__name__)

class WeatherTool(BaseTool):
    def __init__(self):
        metadata = ToolMetadata(
            name="get_weather",
            description="Mocks getting the current weather for a location.",
            category="information",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "temperature": {"type": "number"},
                    "unit": {"type": "string"},
                    "condition": {"type": "string"}
                }
            }
        )
        super().__init__(metadata)

    async def execute(self, location: str, unit: str = "celsius") -> dict:
        conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
        temp = random.randint(-10, 40) if unit == "celsius" else random.randint(14, 104)
        
        return {
            "location": location,
            "temperature": temp,
            "unit": unit,
            "condition": random.choice(conditions)
        }
