from app.runtime.registry import BaseTool, registry
from app.schemas.tool import ToolMetadata
import logging

logger = logging.getLogger(__name__)

class SQLQueryTool(BaseTool):
    def __init__(self):
        metadata = ToolMetadata(
            name="sql_query",
            description="Mocks executing a SQL query on a database.",
            category="database",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SQL query to execute"}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "array",
                "items": {"type": "object"}
            }
        )
        super().__init__(metadata)

    async def execute(self, query: str) -> list:
        logger.info(f"Executing mock SQL query: {query}")
        # Very basic mock data
        if "users" in query.lower():
            return [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ]
        return [{"status": "success", "message": "Query executed (mocked)"}]
