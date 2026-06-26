"""CLI 入口 - 交互式命令行"""

import sys
from typing import Optional

from jarvis.app import Application, get_app
from jarvis.entry.handler import handle_command


def main(config_file: Optional[str] = None) -> None:
    app = get_app(config_file)

    print("=" * 60)
    print("贾维斯多智能体框架 v2 - CLI")
    print("=" * 60)
    print(f"可用模型: {app.llm.list_models()}")
    print(f"可用设备: {len(app.device.list_devices())} 个")
    print(f"可用场景: {len(app.device.list_scenes())} 个")
    print("输入 '帮助' 查看命令，'退出' 结束")
    print("=" * 60)

    try:
        while True:
            try:
                user_input = input("\n您: ").strip()
            except EOFError:
                break
            if not user_input:
                continue
            result = handle_command(user_input, app)
            if result == "QUIT":
                print("\n再见！")
                break
            print(f"\n贾维斯: {result}")
    except KeyboardInterrupt:
        print("\n\n中断，退出中...")
    finally:
        app.shutdown()


if __name__ == "__main__":
    config = sys.argv[1] if len(sys.argv) > 1 else None
    main(config)
