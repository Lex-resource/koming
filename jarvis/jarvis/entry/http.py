"""HTTP 入口 - FastAPI，与 CLI 共享同一套业务逻辑"""

import os
import tempfile
from typing import List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from jarvis.app import Application, get_app
from jarvis.entry.handler import handle_command


class ChatRequest(BaseModel):
    message: str
    config_file: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


class MultimodalRequest(BaseModel):
    prompt: str
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    model: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    output_path: Optional[str] = None


def create_app(config_file: Optional[str] = None) -> FastAPI:
    """创建 FastAPI 应用"""
    app_instance = get_app(config_file)
    api = FastAPI(title="贾维斯多智能体框架", version="2.1.0")

    @api.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        try:
            result = handle_command(req.message, app_instance)
            if result == "QUIT":
                return ChatResponse(response="再见！")
            return ChatResponse(response=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api.post("/chat/images", response_model=ChatResponse)
    async def chat_with_images(req: MultimodalRequest):
        """图片+文本对话"""
        try:
            result = app_instance.chat_with_images(
                prompt=req.prompt, images=req.images or [], model=req.model,
            )
            return ChatResponse(response=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api.post("/chat/videos", response_model=ChatResponse)
    async def chat_with_videos(req: MultimodalRequest):
        """视频+文本对话"""
        try:
            result = app_instance.chat_with_videos(
                prompt=req.prompt, videos=req.videos or [], model=req.model,
            )
            return ChatResponse(response=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api.post("/chat/voice", response_model=ChatResponse)
    async def chat_with_voice(
        audio: UploadFile = File(...),
        language: str = Form("zh"),
    ):
        """语音对话 - 上传音频文件 → ASR → 决策智能体"""
        if app_instance.speech is None:
            raise HTTPException(status_code=400, detail="未配置语音模块")
        suffix = os.path.splitext(audio.filename)[1] or ".mp3"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="jarvis_voice_in_")
        os.close(fd)
        try:
            content = await audio.read()
            with open(tmp_path, "wb") as f:
                f.write(content)
            result = app_instance.chat_with_voice(tmp_path, language=language)
            return ChatResponse(response=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    @api.post("/tts")
    async def text_to_speech(req: TTSRequest):
        """文字转语音"""
        if app_instance.speech is None:
            raise HTTPException(status_code=400, detail="未配置语音模块")
        try:
            path = app_instance.speak(req.text, voice=req.voice, output_path=req.output_path)
            return {"audio_path": path, "voice": req.voice}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @api.get("/voices")
    async def list_voices():
        if app_instance.speech is None:
            return {"voices": []}
        return {"voices": app_instance.speech.list_voices()}

    @api.get("/models")
    async def list_models():
        return {"models": app_instance.llm.list_models()}

    @api.get("/devices")
    async def list_devices():
        if app_instance.device is None:
            return {"devices": [], "note": "设备模块未接入（仅留接口）"}
        return {"devices": app_instance.device.list_devices()}

    @api.get("/scenes")
    async def list_scenes():
        if app_instance.device is None:
            return {"scenes": [], "note": "设备模块未接入（仅留接口）"}
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
            "devices": len(app_instance.device.list_devices()) if app_instance.device else 0,
            "scenes": len(app_instance.device.list_scenes()) if app_instance.device else 0,
            "voices": len(app_instance.speech.list_voices()) if app_instance.speech else 0,
            "memories": app_instance.memory.count(),
            "cache": app_instance.cache.get_stats(),
            "voice_provider": app_instance.config.voice.provider,
            "device_provider": app_instance.config.device.provider,
            "multimodal": {
                "vision_model": app_instance.config.multimodal.default_vision_model,
                "video_model": app_instance.config.multimodal.default_video_model,
            },
        }

    return api


# 直接运行：uvicorn jarvis.entry.http:app
app = create_app()
