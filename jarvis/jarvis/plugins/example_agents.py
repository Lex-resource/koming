"""
示例插件：安全审计Agent

这个插件展示了如何创建一个新的Agent并注册到插件系统
"""

from jarvis.agents.base_agent import BaseAgent
from jarvis.core.plugin_registry import agent_plugin, PluginRegistry, PluginMetadata


@agent_plugin(
    name="SecurityAgent",
    version="1.0.0",
    description="安全审计Agent - 审查操作安全性，识别潜在风险",
    author="JARVIS Team",
    tags=["security", "audit", "compliance"],
    priority=60
)
class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="安全审计员",
            goal="审查操作安全性，识别潜在风险，确保系统安全合规",
            backstory="""
你是贾维斯的安全审计模块，负责审查所有操作的安全性。
你具备识别潜在风险、检测异常行为、确保合规性的能力。
你会对每个操作进行风险评估，并提供改进建议。
""",
            allow_delegation=False
        )


@agent_plugin(
    name="CodeReviewAgent",
    version="1.0.0",
    description="代码审查Agent - 自动审查代码质量和安全性",
    author="JARVIS Team",
    tags=["code", "review", "quality"],
    priority=55
)
class CodeReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="代码审查员",
            goal="审查代码质量，发现潜在bug和安全漏洞",
            backstory="""
你是贾维斯的代码审查专家，精通多种编程语言和最佳实践。
你能够快速理解代码逻辑，识别代码异味，发现潜在的安全问题。
你提供的审查意见专业、具体、可操作。
""",
            allow_delegation=False
        )


@agent_plugin(
    name="DataAnalyticsAgent",
    version="1.0.0",
    description="数据分析Agent - 执行数据分析和可视化",
    author="JARVIS Team",
    tags=["data", "analytics", "visualization"],
    priority=50
)
class DataAnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="数据分析师",
            goal="分析数据，生成洞察，提供数据驱动的决策支持",
            backstory="""
你是贾维斯的数据分析专家，擅长处理各种类型的数据。
你能够进行统计分析、趋势预测、异常检测等操作。
你会用清晰易懂的方式呈现复杂的分析结果。
""",
            allow_delegation=False
        )


@agent_plugin(
    name="NotificationAgent",
    version="1.0.0",
    description="通知Agent - 管理告警和通知",
    author="JARVIS Team",
    tags=["notification", "alert", "communication"],
    priority=40
)
class NotificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="通知管理员",
            goal="管理告警规则，发送通知，跟踪告警状态",
            backstory="""
你是贾维斯的通知管理专家，负责协调各种告警和通知。
你能够根据告警级别和类型，智能地路由通知到合适的接收人。
你确保重要信息不会被遗漏。
""",
            allow_delegation=False
        )


def register_extra_plugins(registry: PluginRegistry):
    """
    注册额外插件的函数

    Args:
        registry: 插件注册中心实例
    """
    # 注册SecurityAgent
    registry.register(
        "SecurityAgent",
        SecurityAgent,
        PluginMetadata(
            name="SecurityAgent",
            version="1.0.0",
            description="安全审计Agent",
            tags=["security"]
        )
    )

    # 注册CodeReviewAgent
    registry.register(
        "CodeReviewAgent",
        CodeReviewAgent,
        PluginMetadata(
            name="CodeReviewAgent",
            version="1.0.0",
            description="代码审查Agent",
            tags=["code", "review"]
        )
    )


# 如果直接运行此文件，展示所有注册的插件
if __name__ == "__main__":
    print("=" * 80)
    print("示例插件列表")
    print("=" * 80)

    print("\n本文件包含以下示例插件:\n")

    plugins = [
        {
            "name": "SecurityAgent",
            "description": "安全审计Agent",
            "features": [
                "审查操作安全性",
                "识别潜在风险",
                "确保系统合规"
            ],
            "tags": ["security", "audit"]
        },
        {
            "name": "CodeReviewAgent",
            "description": "代码审查Agent",
            "features": [
                "审查代码质量",
                "发现潜在bug",
                "安全漏洞检测"
            ],
            "tags": ["code", "review"]
        },
        {
            "name": "DataAnalyticsAgent",
            "description": "数据分析Agent",
            "features": [
                "统计分析",
                "趋势预测",
                "数据可视化"
            ],
            "tags": ["data", "analytics"]
        },
        {
            "name": "NotificationAgent",
            "description": "通知Agent",
            "features": [
                "告警管理",
                "通知路由",
                "状态跟踪"
            ],
            "tags": ["notification", "alert"]
        }
    ]

    for plugin in plugins:
        print(f"\n🔌 {plugin['name']}")
        print(f"   描述: {plugin['description']}")
        print(f"   功能:")
        for feature in plugin['features']:
            print(f"     • {feature}")
        print(f"   标签: {', '.join(plugin['tags'])}")

    print("\n" + "=" * 80)
    print("\n使用方法:")
    print("1. 将此文件复制到 jarvis/plugins/ 目录")
    print("2. 使用装饰器 @agent_plugin 注册插件")
    print("3. 在 main_enhanced.py 中加载插件")
    print("\n示例代码:")
    print("""
    from jarvis.core.plugin_registry import agent_plugin

    @agent_plugin(
        name="MyAgent",
        version="1.0.0",
        description="我的自定义Agent",
        tags=["custom"]
    )
    class MyAgent(BaseAgent):
        def __init__(self):
            super().__init__(
                role="我的角色",
                goal="我的目标",
                backstory="我的背景故事"
            )
    """)
    print("=" * 80)
