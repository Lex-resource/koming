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
    if cmd in ("quit", "exit", "退出"):
        return "QUIT"

    # 默认走决策智能体
    return a.chat(user_input)


def _help_text() -> str:
    return (
        "可用命令：\n"
        "  help/帮助       - 显示帮助\n"
        "  status/状态     - 系统状态\n"
        "  models/模型     - 可用模型列表\n"
        "  devices/设备     - 设备列表\n"
        "  scenes/场景     - 场景列表\n"
        "  skills/技能      - 已积累技能\n"
        "  sessions/会话    - 历史会话\n"
        "  quit/退出       - 退出\n\n"
        "其他输入将交给决策智能体处理。"
    )


def _status_text(app: Application) -> str:
    cache_stats = app.cache.get_stats()
    mem_count = app.memory.count()
    return (
        f"系统状态:\n"
        f"  可用模型: {app.llm.list_models()}\n"
        f"  设备数: {len(app.device.list_devices())}\n"
        f"  场景数: {len(app.device.list_scenes())}\n"
        f"  记忆条数: {mem_count}\n"
        f"  缓存: {cache_stats}\n"
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
