#!/usr/bin/env python3
"""
贾维斯AI助手 - 主入口文件

一个基于LangChain + CrewAI构建的全场景AI智能体系统
支持全局状态记录、审计日志和数据分类存储
"""

import os
import sys
from datetime import datetime
from jarvis.config.settings import Settings
from jarvis.core.crew_manager import CrewManager
from jarvis.core.global_state import global_state
from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.data_store import data_store, DataCategory


def handle_system_command(user_input: str) -> bool:
    """处理系统命令"""
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
    
    # 审计日志命令
    elif user_input.lower() in ["审计日志", "audit"]:
        summary = audit_logger.get_agent_activity_summary()
        print("\n🔍 审计日志摘要:")
        print(f"  - 总操作数: {summary['total_operations']}")
        print(f"  - 操作类型分布: {summary['operations_by_type']}")
        print(f"  - 智能体分布: {summary['operations_by_agent']}")
        return True
    
    elif user_input.lower() == "审计导出":
        filepath = audit_logger.export_logs()
        print(f"\n📥 审计日志已导出到: {filepath}")
        return True
    
    # 数据存储命令
    elif user_input.lower() in ["数据统计", "data stats"]:
        stats = data_store.get_statistics()
        print("\n📈 数据统计:")
        print(f"  - 总记录数: {stats['total_records']}")
        print(f"  - 分类分布: {stats['categories']}")
        print(f"  - 来源分布: {stats['sources']}")
        print(f"  - 标签分布: {stats['tags']}")
        return True
    
    elif user_input.lower() == "数据导出":
        filepath = data_store.export_records()
        print(f"\n📥 数据记录已导出到: {filepath}")
        return True
    
    return False


def main():
    try:
        Settings.validate()
    except EnvironmentError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)

    print("🚀 贾维斯AI助手启动中...")
    print("=" * 70)
    print("欢迎使用贾维斯助手！")
    print("我可以帮您查询信息、控制设备、分析问题等。")
    print("系统命令: 状态 / 历史 / 导出 / 清空历史 / 摘要")
    print("审计命令: 审计日志 / 审计导出")
    print("数据命令: 数据统计 / 数据导出")
    print("输入 '退出' 或 'quit' 结束对话。")
    print("=" * 70)

    global_state.load_history()
    audit_logger.load_logs()
    data_store.load_store()
    
    crew_manager = CrewManager()
    current_user = "user_001"

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

            start_time = datetime.now()
            audit_logger.log_operation(
                operation_type=OperationType.USER_INPUT,
                user_id=current_user,
                action="用户输入",
                details={"input": user_input}
            )

            print("🤖 贾维斯: 正在处理您的请求...")
            result = crew_manager.execute_task(user_input)
            print(f"\n🤖 贾维斯: {result}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            audit_logger.log_operation(
                operation_type=OperationType.AGENT_CALL,
                user_id=current_user,
                agent_name="贾维斯指挥官",
                action="任务执行",
                details={"input": user_input},
                result=result[:200] if len(result) > 200 else result,
                duration=duration
            )

            data_store.add_record(
                category=DataCategory.USER_INPUT,
                source="用户输入",
                content={"input": user_input, "response": result},
                metadata={"user_id": current_user, "duration": duration},
                tags=["对话", "用户交互"]
            )
            
            global_state.add_conversation(user_input, result)

        except KeyboardInterrupt:
            print("\n👋 再见！期待下次为您服务。")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()