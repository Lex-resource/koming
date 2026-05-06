#!/usr/bin/env python3
"""
贾维斯AI助手 - 主入口文件

一个基于LangChain + CrewAI构建的全场景AI智能体系统
支持全局状态记录和对话历史管理
"""

import os
import sys
from jarvis.config.settings import Settings
from jarvis.core.crew_manager import CrewManager
from jarvis.core.global_state import global_state


def handle_system_command(user_input: str) -> bool:
    """
    处理系统命令
    
    Args:
        user_input: 用户输入
    
    Returns:
        True表示已处理系统命令，False表示需要继续处理
    """
    if user_input.lower() in ["状态", "系统状态", "status"]:
        status = global_state.get_system_status()
        print("\n📊 系统状态:")
        print(f"  - 启动时间: {status.get('start_time', '未知')}")
        print(f"  - 交互次数: {status.get('total_interactions', 0)}")
        print(f"  - 激活工具: {', '.join(status.get('active_tools', ['无']))}")
        print(f"  - 记忆数量: {status.get('memory_count', 0)}")
        return True
    
    elif user_input.lower() in ["历史", "对话历史", "history"]:
        history = global_state.get_conversation_history(limit=5)
        print("\n📜 最近对话历史:")
        for i, record in enumerate(reversed(history), 1):
            time = record["timestamp"].split("T")[1][:8]
            print(f"\n  [{i}] {time}")
            print(f"    您: {record['user_input']}")
            response = record["response"]
            if len(response) > 100:
                response = response[:100] + "..."
            print(f"    贾维斯: {response}")
        return True
    
    elif user_input.lower().startswith("导出"):
        filepath = global_state.export_history()
        print(f"\n📥 对话历史已导出到: {filepath}")
        return True
    
    elif user_input.lower() in ["清空历史", "clear history"]:
        global_state.clear_history()
        print("\n🗑️ 对话历史已清空")
        return True
    
    elif user_input.lower() in ["摘要", "summary"]:
        summary = global_state.get_summary()
        print("\n📋 系统摘要:")
        print(f"  - 总对话数: {summary['total_conversations']}")
        print(f"  - 启动时间: {summary['start_time']}")
        print(f"  - 当前时间: {summary['current_time']}")
        return True
    
    return False


def main():
    try:
        Settings.validate()
    except EnvironmentError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)

    print("🚀 贾维斯AI助手启动中...")
    print("=" * 60)
    print("欢迎使用贾维斯助手！")
    print("我可以帮您查询信息、控制设备、分析问题等。")
    print("系统命令: 状态 / 历史 / 导出 / 清空历史 / 摘要")
    print("输入 '退出' 或 'quit' 结束对话。")
    print("=" * 60)

    global_state.load_history()
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

            if handle_system_command(user_input):
                continue

            print("🤖 贾维斯: 正在处理您的请求...")
            result = crew_manager.execute_task(user_input)
            print(f"\n🤖 贾维斯: {result}")
            
            global_state.add_conversation(user_input, result)

        except KeyboardInterrupt:
            print("\n👋 再见！期待下次为您服务。")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()