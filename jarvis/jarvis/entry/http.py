"""HTTP 入口 - FastAPI，与 CLI 共享同一套业务逻辑"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from jarvis.app import Application, get_app
from jarvis.entry.handler import handle_command


class ChatRequest(BaseModel):
    message: str
    config_file: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


def create_app(config_file: Optional[str] = None) -> FastAPI:
    """创建 FastAPI 应用"""
    app_instance = get_app(config_file)
    api = FastAPI(title="贾维斯多智能体框架", version="2.0")

    @api.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        try:
            result = handle_command(req.message, app_instance)
            if result == "QUIT":
                return ChatResponse(response="再见！")
            return ChatResponse(response=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api.get("/models")
    async def list_models():
        return {"models": app_instance.llm.list_models()}

    @api.get("/devices")
    async def list_devices():
        return {"devices": app_instance.device.list_devices()}

    @api.get("/scenes")
    async def list_scenes():
        return {"scenes": app_instance.device.list_scenes()}

    @api.get("/sessions")
    async def list_sessions():
        return {"sessions": app_instance.storage.list_sessions()}

    @api.get("/skills")
    async def list_skills():
        skills = app_instance.database.list_skills()
        return {"skills": [s.to_dict() for s in skills]}

    @api.get("/status")
    async def status():
        return {
            "models": app_instance.llm.list_models(),
            "devices": len(app_instance.device.list_devices()),
            "scenes": len(app_instance.device.list_scenes()),
            "memories": app_instance.memory.count(),
            "cache": app_instance.cache.get_stats(),
        }

    return api


# 直接运行：uvicorn jarvis.entry.http:app
app = create_app()
