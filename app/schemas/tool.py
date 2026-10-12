import uuid
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Type, List
from enum import Enum

class ToolExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RETRYING = "retrying"
    SKIPPED = "skipped"

class RetryPolicy(BaseModel):
    max_retries: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0

class ToolMetadata(BaseModel):
    name: str
    description: str
    category: str = "general"
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    timeout: float = 30.0
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)

class ToolCall(BaseModel):
    call_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str
    arguments: Dict[str, Any]
    session_id: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)

class ToolResult(BaseModel):
    call_id: Optional[str] = None
    tool_name: str
    status: ToolExecutionStatus
    output: Any
    error: Optional[str] = None
    execution_time: float
    retries: int = 0
