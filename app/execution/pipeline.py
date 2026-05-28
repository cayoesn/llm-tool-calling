import logging
import time
import uuid
from typing import List, Dict, Any, Optional
from app.planner.planner import Planner
from app.execution.router import ToolRouter
from app.runtime.registry import registry
from app.schemas.tool import ToolCall, ToolResult
import ollama
from app.core.config import settings
from app.telemetry.mlflow_logger import mlflow_logger
from app.security.permissions import security_manager
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class ExecutionPipeline:
    def __init__(self, planner: Planner, router: ToolRouter, max_turns: int = 5):
        self.planner = planner
        self.router = router
        self.max_turns = max_turns
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)

    async def run(self, user_prompt: str) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        with tracer.start_as_current_span("execution_pipeline") as span:
            span.set_attribute("user_prompt", user_prompt)
            span.set_attribute("session_id", session_id)
            logger.info(f"Starting execution pipeline for prompt: {user_prompt} (Session: {session_id})")
            
            all_tool_calls = []
            all_results = []
            
            try:
                for turn in range(self.max_turns):
                    logger.info(f"Execution turn {turn + 1}/{self.max_turns}")
                    
                    # 1. Planning
                    available_tools = registry.list_tools()
                    tool_calls = await self.planner.plan(user_prompt, available_tools, history=all_results)
                    
                    if not tool_calls:
                        logger.info("No more tools selected by planner.")
                        break

                    # Assign session_id to each tool call
                    for tc in tool_calls:
                        tc.session_id = session_id

                    all_tool_calls.extend(tool_calls)

                    # 2. Execution
                    logger.info(f"Executing {len(tool_calls)} tool calls")
                    results = await self.router.dispatch(tool_calls)
                    all_results.extend(results)
                    
                    # Check if we should continue or if all tools failed
                    if all(r.status != 'success' for r in results):
                        logger.warning("All tools in this turn failed. Stopping.")
                        break
            finally:
                security_manager.reset_session(session_id)

            # 3. Final Response Generation
            context = "\n".join([
                f"Tool: {r.tool_name}\nArguments: {next((tc.arguments for tc in all_tool_calls if tc.tool_name == r.tool_name), 'N/A')}\nOutput: {r.output if r.status == 'success' else r.error}"
                for r in all_results
            ])
            
            final_prompt = f"""
User prompt: {user_prompt}

The following tools were executed during the process:
{context}

Please provide a final answer to the user based on the tool results above.
"""
            
            response = await self.client.chat(
                model=settings.LLM_MODEL,
                messages=[{'role': 'user', 'content': final_prompt}]
            )
            final_response = response['message']['content']
            
            # Log to MLflow
            mlflow_results = [r.dict() for r in all_results]
            mlflow_tool_calls = [tc.dict() for tc in all_tool_calls]
            mlflow_logger.log_execution(user_prompt, mlflow_tool_calls, mlflow_results, final_response)
            
            return {
                "prompt": user_prompt,
                "tool_calls": mlflow_tool_calls,
                "results": mlflow_results,
                "final_response": final_response
            }
