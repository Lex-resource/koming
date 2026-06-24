"""
贾维斯 AI 助手 - 主包初始化

注意：部分模块依赖 crewai、langchain 等第三方库，
当这些库未安装时，相关导入会被跳过，不影响核心模块的使用。
"""

__all__ = []
__version__ = "1.0.0"


def _safe_import(module_path: str, names: list, all_list: list):
    """安全导入模块，失败时跳过并打印警告"""
    try:
        mod = __import__(module_path, fromlist=names)
        for name in names:
            globals()[name] = getattr(mod, name)
            all_list.append(name)
    except Exception as e:
        print(f"⚠️ 跳过导入 {module_path}: {e}")


# 配置模块（无外部依赖）
_safe_import("jarvis.config.settings", ["Settings"], __all__)

# Agent 模块（依赖 crewai）
_safe_import("jarvis.agents.commander", ["CommanderAgent"], __all__)
_safe_import("jarvis.agents.analyst", ["AnalystAgent"], __all__)
_safe_import("jarvis.agents.executor", ["ExecutorAgent"], __all__)
_safe_import("jarvis.agents.learner", ["LearnerAgent"], __all__)

# 工具模块（依赖 langchain）
_safe_import("jarvis.tools.search_tool", ["SearchTool"], __all__)
_safe_import("jarvis.tools.weather_tool", ["WeatherTool"], __all__)
_safe_import("jarvis.tools.device_tool", ["DeviceTool"], __all__)

# 记忆模块
_safe_import("jarvis.memory.memory_manager", ["MemoryManager", "memory_manager"], __all__)

# 核心模块
_safe_import("jarvis.core.audit_logger", ["audit_logger", "OperationType"], __all__)
_safe_import("jarvis.core.data_store", ["data_store", "DataCategory", "DataRecord"], __all__)
_safe_import("jarvis.core.decorators", ["audit", "store_data", "audit_and_store"], __all__)
_safe_import("jarvis.core.global_state", ["global_state"], __all__)
_safe_import(
    "jarvis.core.knowledge_manager",
    ["knowledge_manager", "KnowledgeManager", "KnowledgeGraph",
     "KnowledgeEntity", "KnowledgeRelation", "LearningProfile",
     "EntityType", "RelationType"],
    __all__,
)
_safe_import("jarvis.core.crew_manager", ["CrewManager"], __all__)
_safe_import("jarvis.core.database", ["db", "AsyncDatabase"], __all__)
_safe_import("jarvis.core.cache", ["cache", "MultiLevelCache", "multi_level_cache"], __all__)
_safe_import(
    "jarvis.core.task_manager",
    ["task_manager", "TaskManager", "TaskNode", "TaskStatus", "TaskType",
     "TaskDecomposer", "TaskScheduler"],
    __all__,
)
