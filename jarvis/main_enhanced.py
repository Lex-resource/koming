#!/usr/bin/env python3
"""
贾维斯AI助手 - 增强版主入口

增强功能：
- 插件系统支持
- 异步任务执行
- 消息队列通信
- Prometheus监控指标
- 微服务架构
"""

import os
import sys
import json
from datetime import datetime
from jarvis.config.settings import Settings
from jarvis.core.enhanced_crew_manager import EnhancedCrewManager, PluginBasedCrewManager
from jarvis.core.global_state import global_state
from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.data_store import data_store, DataCategory
from jarvis.core.decorators import audit_and_store
from jarvis.core.plugin_registry import plugin_registry, register_builtin_agents
from jarvis.core.async_executor import async_task_executor, TaskPriority
from jarvis.core.message_queue import message_queue
from jarvis.core.metrics import metrics_collector, system_metrics, MetricsServer


def print_banner():
    """打印欢迎横幅"""
    print("=" * 80)
    print("🚀 贾维斯AI助手 v2.0 - 增强版")
    print("=" * 80)
    print("支持功能:")
    print("  • 插件系统 - 动态加载Agent")
    print("  • 异步执行 - 后台任务处理")
    print("  • 消息队列 - Agent间解耦通信")
    print("  • Prometheus监控 - 指标采集")
    print("  • 微服务架构 - 分布式部署")
    print("=" * 80)


def handle_system_command(user_input: str, crew_manager: EnhancedCrewManager = None) -> bool:
    """处理系统命令"""
    cmd = user_input.lower().strip()

    if cmd in ["状态", "系统状态", "status"]:
        status = global_state.get_system_status()
        print("\n📊 系统状态:")
        print(f"  - 启动时间: {status.get('start_time', '未知')}")
        print(f"  - 交互次数: {status.get('total_interactions', 0)}")
        print(f"  - 激活工具: {', '.join(status.get('active_tools', ['无']))}")
        print(f"  - 记忆数量: {status.get('memory_count', 0)}")

        if crew_manager:
            print("\n📈 增强功能状态:")
            plugin_stats = plugin_registry.get_statistics()
            print(f"  - 已注册Agent: {plugin_stats['total_agents']}")
            print(f"  - 启用Agent: {plugin_stats['enabled_agents']}")

            if hasattr(crew_manager, 'enable_async') and crew_manager.enable_async:
                task_stats = async_task_executor.get_statistics()
                print(f"  - 运行中任务: {task_stats.get('运行状态', '未知')}")
                print(f"  - 队列大小: {task_stats.get('队列大小', 0)}")

            if hasattr(crew_manager, 'enable_messaging') and crew_manager.enable_messaging:
                msg_stats = message_queue.get_statistics()
                print(f"  - 消息队列状态: {msg_stats.get('运行状态', '未知')}")
                print(f"  - 总消息数: {msg_stats.get('总消息数', 0)}")

        return True

    elif cmd in ["历史", "对话历史", "history"]:
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

    elif cmd.startswith("导出"):
        filepath = global_state.export_history()
        print(f"\n📥 对话历史已导出到: {filepath}")
        return True

    elif cmd in ["清空历史", "clear history"]:
        global_state.clear_history()
        print("\n🗑️ 对话历史已清空")
        return True

    elif cmd in ["摘要", "summary"]:
        summary = global_state.get_summary()
        print("\n📋 系统摘要:")
        print(f"  - 总对话数: {summary['total_conversations']}")
        print(f"  - 启动时间: {summary['start_time']}")
        print(f"  - 当前时间: {summary['current_time']}")
        return True

    elif cmd in ["审计日志", "audit"]:
        summary = audit_logger.get_agent_activity_summary()
        print("\n🔍 审计日志摘要:")
        print(f"  - 总操作数: {summary['total_operations']}")
        print(f"  - 操作类型分布: {summary['operations_by_type']}")
        print(f"  - 智能体分布: {summary['operations_by_agent']}")
        return True

    elif cmd == "审计导出":
        filepath = audit_logger.export_logs()
        print(f"\n📥 审计日志已导出到: {filepath}")
        return True

    elif cmd in ["数据统计", "data stats"]:
        stats = data_store.get_statistics()
        print("\n📈 数据统计:")
        print(f"  - 总记录数: {stats['total_records']}")
        print(f"  - 分类分布: {stats['categories']}")
        print(f"  - 来源分布: {stats['sources']}")
        print(f"  - 标签分布: {stats['tags']}")
        return True

    elif cmd == "数据导出":
        filepath = data_store.export_records()
        print(f"\n📥 数据记录已导出到: {filepath}")
        return True

    elif cmd in ["插件", "plugins"]:
        print("\n🔌 已注册的Agent插件:")
        plugins = plugin_registry.list_agents()
        for name in plugins:
            metadata = plugin_registry.get_metadata(name)
            if metadata:
                status = "✓" if metadata.enabled else "✗"
                print(f"  {status} {name} (v{metadata.version}) - {metadata.description}")
        return True

    elif cmd.startswith("插件启用 "):
        plugin_name = cmd[5:].strip()
        result = plugin_registry.enable(plugin_name)
        print(f"{'✓' if result else '✗'} 插件 {'已启用' if result else '启用失败'}: {plugin_name}")
        return True

    elif cmd.startswith("插件禁用 "):
        plugin_name = cmd[5:].strip()
        result = plugin_registry.disable(plugin_name)
        if result:
            plugin_registry.save_config()
        print(f"{'✓' if result else '✗'} 插件 {'已禁用' if result else '禁用失败'}: {plugin_name}")
        return True

    elif cmd in ["异步状态", "async status"]:
        if hasattr(async_task_executor, 'get_statistics'):
            stats = async_task_executor.get_statistics()
            print("\n⚡ 异步执行器状态:")
            print(f"  - 运行状态: {stats.get('运行状态', '未知')}")
            print(f"  - 总任务数: {stats.get('总任务数', 0)}")
            print(f"  - 队列大小: {stats.get('队列大小', 0)}")
            print(f"  - 状态分布: {stats.get('状态分布', {})}")
        else:
            print("异步执行功能未启用")
        return True

    elif cmd in ["异步列表", "async list"]:
        tasks = async_task_executor.list_tasks()
        print(f"\n⚡ 异步任务列表 (共 {len(tasks)} 个):")
        for task in tasks[:10]:
            print(f"  [{task.task_id}] {task.description} - 状态: {task.status.value}")
        return True

    elif cmd in ["消息状态", "mq status"]:
        stats = message_queue.get_statistics()
        print("\n📬 消息队列状态:")
        print(f"  - 运行状态: {stats.get('运行状态', '未知')}")
        print(f"  - 总消息数: {stats.get('总消息数', 0)}")
        print(f"  - 已投递: {stats.get('已投递消息', 0)}")
        print(f"  - 主题数: {stats.get('主题数', 0)}")
        print(f"  - 订阅数: {stats.get('订阅数', 0)}")
        return True

    elif cmd in ["指标", "metrics"]:
        print("\n📊 Prometheus指标:")
        print(f"  访问 http://localhost:8000/metrics 查看完整指标")
        print("\n  系统指标预览:")
        metrics_data = system_metrics.collector.get_all_metrics()
        if 'gauges' in metrics_data:
            for key, value in list(metrics_data['gauges'].items())[:5]:
                print(f"    {key}: {value}")
        return True

    elif cmd in ["监控", "monitoring"]:
        if crew_manager:
            all_metrics = crew_manager.get_system_metrics()
            print("\n📈 系统监控概览:")
            print(f"\n  插件统计:")
            for key, value in all_metrics.get('plugin_stats', {}).items():
                print(f"    {key}: {value}")

            if all_metrics.get('task_stats'):
                print(f"\n  任务统计:")
                for key, value in all_metrics['task_stats'].items():
                    print(f"    {key}: {value}")

            if all_metrics.get('message_stats'):
                print(f"\n  消息统计:")
                for key, value in all_metrics['message_stats'].items():
                    print(f"    {key}: {value}")
        return True

    elif cmd.startswith("批量 "):
        queries = user_input[3:].strip().split('|')
        if len(queries) > 1 and crew_manager:
            print(f"\n⚡ 开始批量执行 {len(queries)} 个任务...")

            if hasattr(crew_manager, 'execute_multiple'):
                results = crew_manager.execute_multiple(queries, mode='parallel')

                print(f"\n✅ 批量执行完成:")
                for i, result in enumerate(results):
                    status_icon = "✓" if result.get('status') == 'completed' else "✗"
                    print(f"  {status_icon} 任务{i+1}: {result.get('input', '')[:30]}...")
                    if result.get('result'):
                        print(f"     结果: {result['result'][:50]}...")
            return True

    elif cmd.startswith("异步 "):
        query = user_input[3:].strip()
        if crew_manager and hasattr(crew_manager, 'execute_task_async'):
            task_id = crew_manager.execute_task_async(
                query,
                priority=TaskPriority.NORMAL
            )
            print(f"\n⚡ 任务已提交到异步队列")
            print(f"   任务ID: {task_id}")
            print(f"   使用 '异步状态' 查看进度")
        return True

    elif cmd in ["help", "帮助"]:
        print("\n📚 帮助信息:")
        print("  基础命令:")
        print("    状态 / history / 导出 / 摘要")
        print("\n  审计命令:")
        print("    审计日志 / 审计导出")
        print("\n  数据命令:")
        print("    数据统计 / 数据导出")
        print("\n  插件命令:")
        print("    插件 - 列出所有Agent")
        print("    插件启用 <name> - 启用插件")
        print("    插件禁用 <name> - 禁用插件")
        print("\n  异步命令:")
        print("    异步状态 - 查看异步执行器状态")
        print("    异步列表 - 列出异步任务")
        print("    异步 <query> - 异步执行任务")
        print("\n  监控命令:")
        print("    指标 / 监控")
        print("\n  批量命令:")
        print("    批量 query1 | query2 | query3")
        return True

    return False


def main(mode: str = "standard"):
    """
    主函数

    Args:
        mode: 运行模式 ('simple', 'standard', 'full', 'plugin')
    """
    try:
        Settings.validate()
    except EnvironmentError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)

    print_banner()

    print("\n🔧 初始化系统组件...")

    register_builtin_agents()
    plugin_registry.load_config()

    message_queue.start()

    if mode in ["standard", "full"]:
        async_task_executor.start()

    system_metrics.set_up(1)

    metrics_server = None
    if mode == "full":
        try:
            metrics_server = MetricsServer(metrics_collector, host="0.0.0.0", port=8000)
            metrics_server.start()
        except Exception as e:
            print(f"⚠️ 指标服务器启动失败: {e}")

    if mode == "plugin":
        crew_manager = PluginBasedCrewManager()
        print(f"✓ 已加载 {len(crew_manager.get_agents())} 个Agent插件")
    else:
        enable_async = mode in ["standard", "full"]
        enable_messaging = mode == "full"

        crew_manager = EnhancedCrewManager(
            enable_async=enable_async,
            enable_messaging=enable_messaging
        )

    print("\n" + "=" * 80)
    print("✓ 系统初始化完成！")
    print("=" * 80)
    print("\n📌 快速开始:")
    print("  输入您的问题，开始与贾维斯对话")
    print("  输入 '帮助' 或 'help' 查看所有命令")
    print("  输入 '退出' 结束程序")
    print("=" * 80)

    global_state.load_history()
    audit_logger.load_logs()
    data_store.load_store()

    current_user = "user_001"

    while True:
        try:
            user_input = input("\n您: ")

            if user_input.lower() in ["退出", "quit", "exit"]:
                print("\n👋 正在清理系统...")

                plugin_registry.save_config()

                if mode in ["standard", "full"]:
                    async_task_executor.stop()

                message_queue.stop()

                if metrics_server:
                    metrics_server.stop()

                system_metrics.set_up(0)

                print("✓ 系统清理完成！")
                print("👋 再见！期待下次为您服务。")
                break

            if not user_input.strip():
                print("请输入有效的请求。")
                continue

            if handle_system_command(user_input, crew_manager):
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
            print("\n\n👋 检测到中断信号，正在清理系统...")
            break

        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="贾维斯AI助手")
    parser.add_argument(
        '--mode',
        choices=['simple', 'standard', 'full', 'plugin'],
        default='standard',
        help='运行模式: simple(基础), standard(标准), full(完整), plugin(插件)'
    )

    args = parser.parse_args()

    mode_descriptions = {
        'simple': '基础模式 - 仅核心功能',
        'standard': '标准模式 - 启用异步执行',
        'full': '完整模式 - 启用所有增强功能',
        'plugin': '插件模式 - 完全动态化Agent加载'
    }

    print(f"\n启动模式: {mode_descriptions.get(args.mode, 'standard')}")

    main(mode=args.mode)
