from fastapi import APIRouter
from app.api.v1.endpoints import chat, tools

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
