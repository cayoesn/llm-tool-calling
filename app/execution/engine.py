import asyncio
import time
import logging
from typing import Any, Dict, Optional
from app.runtime.registry import registry, BaseTool
from app.schemas.tool import ToolExecutionStatus, ToolResult, ToolCall, RetryPolicy
from app.validation.validator import ToolValidator
from app.telemetry.metrics import TOOL_EXECUTION_COUNT, TOOL_LATENCY, ACTIVE_EXECUTIONS, TOOL_RETRY_COUNT
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

from app.security.permissions import security_manager

class ExecutionEngine:
    def __init__(self, validator: ToolValidator):
        self.validator = validator

    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        with tracer.start_as_current_span(f"execute_tool:{tool_call.tool_name}") as span:
            span.set_attribute("tool.name", tool_call.tool_name)
            ACTIVE_EXECUTIONS.inc()
            
            try:
                tool = registry.get_tool(tool_call.tool_name)
                if not tool:
                    TOOL_EXECUTION_COUNT.labels(tool_name=tool_call.tool_name, status="not_found").inc()
                    return ToolResult(
                        call_id=tool_call.call_id,
                        tool_name=tool_call.tool_name,
                        status=ToolExecutionStatus.FAILED,
                        output=None,
                        error=f"Tool {tool_call.tool_name} not found",
                        execution_time=0.0
                    )

                # Security check
                if not security_manager.is_tool_allowed(tool.metadata.name, tool.metadata.category, tool_call.session_id):
                    TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="permission_denied").inc()
                    return ToolResult(
                        call_id=tool_call.call_id,
                        tool_name=tool_call.tool_name,
                        status=ToolExecutionStatus.FAILED,
                        output=None,
                        error=f"Permission denied for tool {tool_call.tool_name}",
                        execution_time=0.0
                    )

                # Validate input
                is_valid, error = self.validator.validate_input(tool, tool_call.arguments)
                if not is_valid:
                    TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="validation_failed").inc()
                    return ToolResult(
                        call_id=tool_call.call_id,
                        tool_name=tool_call.tool_name,
                        status=ToolExecutionStatus.FAILED,
                        output=None,
                        error=f"Input validation failed: {error}",
                        execution_time=0.0
                    )

                start_time = time.time()
                retries = 0
                policy = tool.metadata.retry_policy

                while retries <= policy.max_retries:
                    try:
                        # Execution with timeout
                        output = await asyncio.wait_for(
                            tool.execute(**tool_call.arguments),
                            timeout=tool.metadata.timeout
                        )

                        # Validate output
                        is_valid_output, output_error = self.validator.validate_output(tool, output)
                        if not is_valid_output:
                            TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="output_validation_failed").inc()
                            return ToolResult(
                                call_id=tool_call.call_id,
                                tool_name=tool_call.tool_name,
                                status=ToolExecutionStatus.FAILED,
                                output=output,
                                error=f"Output validation failed: {output_error}",
                                execution_time=time.time() - start_time,
                                retries=retries
                            )

                        execution_time = time.time() - start_time
                        TOOL_LATENCY.labels(tool_name=tool.metadata.name).observe(execution_time)
                        TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="success").inc()
                        
                        return ToolResult(
                            call_id=tool_call.call_id,
                            tool_name=tool_call.tool_name,
                            status=ToolExecutionStatus.SUCCESS,
                            output=output,
                            execution_time=execution_time,
                            retries=retries
                        )

                    except asyncio.TimeoutError:
                        logger.error(f"Tool {tool.metadata.name} timed out")
                        if retries >= policy.max_retries:
                            TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="timeout").inc()
                            return ToolResult(
                                call_id=tool_call.call_id,
                                tool_name=tool_call.tool_name,
                                status=ToolExecutionStatus.TIMEOUT,
                                output=None,
                                error="Execution timed out",
                                execution_time=time.time() - start_time,
                                retries=retries
                            )
                    except Exception as e:
                        logger.error(f"Error executing tool {tool.metadata.name}: {str(e)}")
                        if retries >= policy.max_retries:
                            TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="failed").inc()
                            return ToolResult(
                                call_id=tool_call.call_id,
                                tool_name=tool_call.tool_name,
                                status=ToolExecutionStatus.FAILED,
                                output=None,
                                error=str(e),
                                execution_time=time.time() - start_time,
                                retries=retries
                            )

                    # Retry logic
                    retries += 1
                    TOOL_RETRY_COUNT.labels(tool_name=tool.metadata.name).inc()
                    delay = policy.initial_delay * (policy.backoff_factor ** (retries - 1))
                    logger.info(f"Retrying tool {tool.metadata.name} in {delay}s (Attempt {retries}/{policy.max_retries})")
                    await asyncio.sleep(delay)

                TOOL_EXECUTION_COUNT.labels(tool_name=tool.metadata.name, status="max_retries_reached").inc()
                return ToolResult(
                    call_id=tool_call.call_id,
                    tool_name=tool_call.tool_name,
                    status=ToolExecutionStatus.FAILED,
                    output=None,
                    error="Max retries reached",
                    execution_time=time.time() - start_time,
                    retries=retries
                )
            finally:
                ACTIVE_EXECUTIONS.dec()
