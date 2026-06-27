"""CLI 入口 - 交互式命令行，支持文本+多模态+语音"""

import os
import sys
from typing import Optional

from jarvis.app import Application, get_app
from jarvis.entry.handler import (
    handle_command, handle_image_command, handle_video_command,
    handle_voice_command, handle_tts_command,
)


def main(config_file: Optional[str] = None) -> None:
    app = get_app(config_file)

    print("=" * 60)
    print("贾维斯多智能体框架 v2.1 - CLI")
    print("=" * 60)
    print(f"可用模型: {app.llm.list_models()}")
    print(f"可用设备: {len(app.device.list_devices())} 个")
    print(f"可用场景: {len(app.device.list_scenes())} 个")
    print(f"视觉模型: {app.config.multimodal.default_vision_model}")
    print(f"视频模型: {app.config.multimodal.default_video_model}")
    print(f"语音模块: {app.config.voice.provider}")
    print("输入 '帮助' 查看命令，'退出' 结束")
    print("多模态: /image <prompt> <url...> / /video <prompt> <url...>")
    print("语音:   /voice <audio_path> / /tts <text>")
    print("=" * 60)

    try:
        while True:
            try:
                user_input = input("\n您: ").strip()
            except EOFError:
                break
            if not user_input:
                continue
            result = _dispatch(user_input, app)
            if result == "QUIT":
                print("\n再见！")
                break
            print(f"\n贾维斯: {result}")
    except KeyboardInterrupt:
        print("\n\n中断，退出中...")
    finally:
        app.shutdown()


def _dispatch(user_input: str, app: Application) -> str:
    """分发多模态/语音/普通命令"""
    if user_input.startswith("/image "):
        parts = user_input[len("/image "):].split()
        if len(parts) < 2:
            return "用法: /image <prompt> <image_url_or_path...>"
        prompt, images = parts[0], parts[1:]
        images = [_resolve_path_or_url(p) for p in images]
        return handle_image_command(prompt=prompt, images=images, app=app)

    if user_input.startswith("/video "):
        parts = user_input[len("/video "):].split()
        if len(parts) < 2:
            return "用法: /video <prompt> <video_url_or_path...>"
        prompt, videos = parts[0], parts[1:]
        videos = [_resolve_path_or_url(p) for p in videos]
        return handle_video_command(prompt=prompt, videos=videos, app=app)

    if user_input.startswith("/voice "):
        path = user_input[len("/voice "):].strip()
        if not path:
            return "用法: /voice <audio_path>"
        return handle_voice_command(audio_path=path, app=app)

    if user_input.startswith("/tts "):
        text = user_input[len("/tts "):].strip()
        if not text:
            return "用法: /tts <text>"
        return handle_tts_command(text=text, app=app)

    return handle_command(user_input, app)


def _resolve_path_or_url(source: str) -> str:
    """本地路径转 base64；URL 原样返回"""
    if source.startswith(("http://", "https://", "data:")):
        return source
    if not os.path.exists(source):
        return source  # 让适配器自己报错
    import base64
    with open(source, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


if __name__ == "__main__":
    config = sys.argv[1] if len(sys.argv) > 1 else None
    main(config)
