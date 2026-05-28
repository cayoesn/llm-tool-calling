from fastapi import APIRouter
from typing import List
from app.runtime.registry import registry
from app.schemas.tool import ToolMetadata

router = APIRouter()

@router.get("/", response_model=List[ToolMetadata])
async def list_tools():
    return registry.list_tools()

@router.get("/{name}", response_model=ToolMetadata)
async def get_tool(name: str):
    metadata = registry.get_tool_metadata(name)
    if not metadata:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    return metadata
