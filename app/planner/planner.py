import json
import logging
from typing import List, Optional
import ollama
from app.core.config import settings
from app.schemas.tool import ToolCall, ToolMetadata, ToolResult
from app.runtime.registry import registry

logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, model: str = settings.LLM_MODEL):
        self.model = model
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)

    async def plan(self, user_prompt: str, available_tools: List[ToolMetadata], history: Optional[List[ToolResult]] = None) -> List[ToolCall]:
        tools_desc = "\n".join([
            f"- {t.name}: {t.description}. Input schema: {json.dumps(t.input_schema)}"
            for t in available_tools
        ])

        history_context = ""
        if history:
            history_context = "\nPrevious tool execution results:\n" + "\n".join([
                f"Tool: {r.tool_name}, Status: {r.status}, Output: {r.output if r.status == 'success' else r.error}"
                for r in history
            ])

        system_prompt = f"""
You are an AI planner for a tool-calling system.
Your task is to analyze the user prompt and decide which tools to call.
You MUST output ONLY a JSON list of tool calls.
Each tool call must have "tool_name" and "arguments" (a dictionary).

Available tools:
{tools_desc}
{history_context}

If the previous tool results are sufficient to answer the user prompt, return an empty list: [].
If you need more information or need to perform more actions, select the appropriate tools.

Example output:
[
  {{"tool_name": "calculator", "arguments": {{"expression": "2+2"}}}}
]

Do NOT include any explanation or other text.
"""

        try:
            response = await self.client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                format='json'
            )

            content = response['message']['content']
            logger.debug(f"Planner response: {content}")

            tool_calls_data = json.loads(content)
            if not isinstance(tool_calls_data, list):
                logger.error(f"Planner returned non-list output: {content}")
                return []

            tool_calls = []
            for item in tool_calls_data:
                try:
                    tool_calls.append(ToolCall(**item))
                except Exception as e:
                    logger.error(f"Error parsing tool call: {item}. Error: {str(e)}")

            return tool_calls

        except Exception as e:
            logger.error(f"Error in planner: {str(e)}")
            return []
