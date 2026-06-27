"""共享业务逻辑 - CLI 和 HTTP 共用"""

from typing import Optional

from jarvis.app import Application, get_app


def handle_command(user_input: str, app: Optional[Application] = None) -> str:
    """统一处理入口 - CLI 和 HTTP 都调这个"""
    a = app or get_app()
    cmd = user_input.lower().strip()

    # 系统命令
    if cmd in ("help", "帮助"):
        return _help_text()
    if cmd in ("status", "状态"):
        return _status_text(a)
    if cmd in ("models", "模型"):
        return _models_text(a)
    if cmd in ("devices", "设备"):
        return _devices_text(a)
    if cmd in ("scenes", "场景"):
        return _scenes_text(a)
    if cmd in ("skills", "技能"):
        return _skills_text(a)
    if cmd in ("sessions", "会话"):
        return _sessions_text(a)
    if cmd in ("voices", "音色"):
        return _voices_text(a)
    if cmd in ("multimodal", "多模态"):
        return _multimodal_text(a)
    if cmd in ("quit", "exit", "退出"):
        return "QUIT"

    # 默认走决策智能体
    return a.chat(user_input)


def handle_image_command(prompt: str, images: list, app: Optional[Application] = None) -> str:
    """图片+文本入口"""
    a = app or get_app()
    return a.chat_with_images(prompt=prompt, images=images)


def handle_video_command(prompt: str, videos: list, app: Optional[Application] = None) -> str:
    """视频+文本入口"""
    a = app or get_app()
    return a.chat_with_videos(prompt=prompt, videos=videos)


def handle_voice_command(audio_path: str, language: str = "zh", app: Optional[Application] = None) -> str:
    """语音输入入口 - ASR → 决策智能体"""
    a = app or get_app()
    if a.speech is None:
        return "未配置语音模块（config.voice.provider）"
    return a.chat_with_voice(audio_path, language=language)


def handle_tts_command(text: str, voice: str = "default", app: Optional[Application] = None) -> str:
    """TTS 入口 - 文本转语音"""
    a = app or get_app()
    if a.speech is None:
        return "未配置语音模块（config.voice.provider）"
    return f"音频已生成: {a.speak(text, voice=voice)}"


def _help_text() -> str:
    return (
        "可用命令：\n"
        "  help/帮助        - 显示帮助\n"
        "  status/状态      - 系统状态\n"
        "  models/模型      - 可用模型列表\n"
        "  devices/设备     - 设备列表\n"
        "  scenes/场景      - 场景列表\n"
        "  skills/技能       - 已积累技能\n"
        "  sessions/会话    - 历史会话\n"
        "  voices/音色       - 可用音色\n"
        "  multimodal/多模态 - 多模态配置\n"
        "  quit/退出        - 退出\n\n"
        "其他输入将交给决策智能体处理。\n"
        "多模态/语音：通过 HTTP 端点 /chat/images /chat/videos /chat/voice /tts"
    )


def _status_text(app: Application) -> str:
    cache_stats = app.cache.get_stats()
    mem_count = app.memory.count()
    voice_count = len(app.speech.list_voices()) if app.speech else 0
    return (
        f"系统状态:\n"
        f"  可用模型: {app.llm.list_models()}\n"
        f"  设备数: {len(app.device.list_devices())}\n"
        f"  场景数: {len(app.device.list_scenes())}\n"
        f"  音色数: {voice_count}\n"
        f"  记忆条数: {mem_count}\n"
        f"  缓存: {cache_stats}\n"
        f"  语音: {app.config.voice.provider}\n"
        f"  视觉模型: {app.config.multimodal.default_vision_model}\n"
        f"  视频模型: {app.config.multimodal.default_video_model}\n"
    )


def _models_text(app: Application) -> str:
    models = app.llm.list_models()
    return "可用模型:\n" + "\n".join(f"  - {m}" for m in models)


def _devices_text(app: Application) -> str:
    devices = app.device.list_devices()
    if not devices:
        return "无设备"
    lines = ["设备列表:"]
    for d in devices:
        lines.append(f"  - {d.get('id', '?')}: {d.get('name', '?')} ({d.get('type', '?')})")
    return "\n".join(lines)


def _scenes_text(app: Application) -> str:
    scenes = app.device.list_scenes()
    if not scenes:
        return "无场景"
    return "场景列表:\n" + "\n".join(f"  - {s}" for s in scenes)


def _voices_text(app: Application) -> str:
    if app.speech is None:
        return "未配置语音模块"
    voices = app.speech.list_voices()
    if not voices:
        return "无可用音色"
    return "可用音色:\n" + "\n".join(f"  - {v}" for v in voices)


def _multimodal_text(app: Application) -> str:
    mm = app.config.multimodal
    return (
        f"多模态配置:\n"
        f"  默认视觉模型: {mm.default_vision_model}\n"
        f"  默认视频模型: {mm.default_video_model}\n"
        f"  单次最大图片数: {mm.max_images}\n"
        f"  单次最大视频数: {mm.max_videos}\n"
        f"  默认温度: {mm.temperature}\n"
    )


def _skills_text(app: Application) -> str:
    skills = app.database.list_skills()
    if not skills:
        return "暂无积累技能"
    lines = ["已积累技能:"]
    for s in skills:
        lines.append(f"  - {s.skill_id}: {s.trigger[:50]} (使用 {s.success_count} 次)")
    return "\n".join(lines)


def _sessions_text(app: Application) -> str:
    sessions = app.storage.list_sessions(limit=10)
    if not sessions:
        return "暂无历史会话"
    return "最近会话:\n" + "\n".join(f"  - {s}" for s in sessions)
