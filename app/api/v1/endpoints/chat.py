from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
from app.execution.pipeline import ExecutionPipeline
from app.planner.planner import Planner
from app.execution.router import ToolRouter
from app.execution.engine import ExecutionEngine
from app.validation.validator import ToolValidator

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    prompt: str
    tool_calls: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    final_response: str

def get_pipeline():
    validator = ToolValidator()
    engine = ExecutionEngine(validator)
    router = ToolRouter(engine)
    planner = Planner()
    return ExecutionPipeline(planner, router)

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, pipeline: ExecutionPipeline = Depends(get_pipeline)):
    try:
        result = await pipeline.run(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
