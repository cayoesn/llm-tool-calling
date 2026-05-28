from app.runtime.registry import BaseTool, registry
from app.schemas.tool import ToolMetadata
import logging

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    def __init__(self):
        metadata = ToolMetadata(
            name="web_search",
            description="Mocks a web search for a given query.",
            category="information",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "url": {"type": "string"},
                        "snippet": {"type": "string"}
                    }
                }
            }
        )
        super().__init__(metadata)

    async def execute(self, query: str) -> list:
        return [
            {
                "title": f"Result for {query}",
                "url": f"https://example.com/search?q={query}",
                "snippet": f"This is a mocked search result for the query: {query}"
            },
            {
                "title": f"Another result for {query}",
                "url": f"https://test.com/{query}",
                "snippet": f"Here is some more information about {query}."
            }
        ]
