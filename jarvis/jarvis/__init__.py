"""贾维斯多智能体框架 v2 - 顶层入口"""

from jarvis.config.settings import Config, get_config, init_config, ModelConfig, LLMConfig
from jarvis.app import Application, get_app
from jarvis.agents import DecisionAgent, WorkerAgent
from jarvis.core.interfaces import (
    ILLM, IMemory, ICache, IDatabase, IDevice, ISearch, IStorage,
)
from jarvis.core.models import (
    AgentProfile, Skill, GroupPlan, AgentAssignment, AgentResult,
    ReviewResult, ReviewVerdict, TaskStatus, ToolDefinition, ToolCall,
)

__version__ = "2.0.0"

__all__ = [
    "Config", "get_config", "init_config", "ModelConfig", "LLMConfig",
    "Application", "get_app",
    "DecisionAgent", "WorkerAgent",
    "ILLM", "IMemory", "ICache", "IDatabase", "IDevice", "ISearch", "IStorage",
    "AgentProfile", "Skill", "GroupPlan", "AgentAssignment", "AgentResult",
    "ReviewResult", "ReviewVerdict", "TaskStatus", "ToolDefinition", "ToolCall",
]
