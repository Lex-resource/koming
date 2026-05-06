#!/usr/bin/env python3
"""
贾维斯AI助手 - 主入口文件

一个基于LangChain + CrewAI构建的全场景AI智能体系统
"""

import os
import sys
from jarvis.config.settings import Settings
from jarvis.core.crew_manager import CrewManager


def main():
    try:
        Settings.validate()
    except EnvironmentError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)

    print("🚀 贾维斯AI助手启动中...")
    print("=" * 50)
    print("欢迎使用贾维斯助手！")
    print("我可以帮您查询信息、控制设备、分析问题等。")
    print("输入 '退出' 或 'quit' 结束对话。")
    print("=" * 50)

    crew_manager = CrewManager()

    while True:
        try:
            user_input = input("\n您: ")
            
            if user_input.lower() in ["退出", "quit", "exit"]:
                print("👋 再见！期待下次为您服务。")
                break
            
            if not user_input.strip():
                print("请输入有效的请求。")
                continue

            print("🤖 贾维斯: 正在处理您的请求...")
            result = crew_manager.execute_task(user_input)
            print(f"\n🤖 贾维斯: {result}")

        except KeyboardInterrupt:
            print("\n👋 再见！期待下次为您服务。")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()