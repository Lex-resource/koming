"""
贾维斯多智能体框架 - 核心数据结构

所有数据类的定义，供接口层和智能体层引用。
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    """任务/Agent执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DecisionType(str, Enum):
    """决策类型"""
    SELF_HANDLE = "self_handle"
    ORCHESTRATE = "orchestrate"


class ReviewVerdict(str, Enum):
    """审核结论"""
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVISION = "needs_revision"


@dataclass
class ToolDefinition:
    """工具定义 - 供 LLM function calling 使用"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Any = field(repr=False, default=None)

    def to_openai_schema(self) -> Dict[str, Any]:
        """转为 OpenAI function calling schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


@dataclass
class ToolCall:
    """LLM 发起的工具调用"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


@dataclass
class AgentProfile:
    """子智能体能力档案 - 存'这个人擅长什么'，不存上下文"""
    agent_id: str
    role: str
    capabilities: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    artifact_format: str = ""
    skills: List[str] = field(default_factory=list)

    execution_count: int = 0
    success_count: int = 0
    avg_duration: float = 0.0
    last_used: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "artifact_format": self.artifact_format,
            "skills": self.skills,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "avg_duration": self.avg_duration,
            "last_used": self.last_used,
            "created_at": self.created_at,
            "success_rate": self.success_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentProfile":
        data.pop("success_rate", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Skill:
    """提示词模板 - 存'怎么干'，可复用"""
    skill_id: str
    trigger: str
    prompt_template: str
    tools: List[str] = field(default_factory=list)
    artifact_format: str = ""

    success_count: int = 0
    last_used: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def render(self, **kwargs) -> str:
        """填充模板参数"""
        try:
            return self.prompt_template.format(**kwargs)
        except KeyError:
            return self.prompt_template

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "trigger": self.trigger,
            "prompt_template": self.prompt_template,
            "tools": self.tools,
            "artifact_format": self.artifact_format,
            "success_count": self.success_count,
            "last_used": self.last_used,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AgentAssignment:
    """编组成员定义"""
    role: str
    skill_id: Optional[str] = None
    prompt: str = ""
    tools: List[str] = field(default_factory=list)
    task: str = ""
    model: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "skill_id": self.skill_id,
            "prompt": self.prompt,
            "tools": self.tools,
            "task": self.task,
            "model": self.model,
        }


@dataclass
class GroupPlan:
    """编组方案 - 决策智能体输出的结构化指令"""
    plan_id: str = field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    task: str = ""
    agents: List[AgentAssignment] = field(default_factory=list)
    completion_criteria: List[str] = field(default_factory=list)
    reuse_from: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "task": self.task,
            "agents": [a.to_dict() for a in self.agents],
            "completion_criteria": self.completion_criteria,
            "reuse_from": self.reuse_from,
            "created_at": self.created_at,
        }


@dataclass
class AgentResult:
    """子智能体执行结果"""
    agent_id: str
    role: str
    status: TaskStatus = TaskStatus.COMPLETED
    summary: str = ""
    artifact_path: Optional[str] = None
    duration: float = 0.0
    error: Optional[str] = None
    md_file: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == TaskStatus.COMPLETED and self.error is None


@dataclass
class ReviewResult:
    """审核结果"""
    verdict: ReviewVerdict
    passed_criteria: List[str] = field(default_factory=list)
    failed_criteria: List[str] = field(default_factory=list)
    feedback: str = ""
    reviewer: str = "self"

    @property
    def is_passed(self) -> bool:
        return self.verdict == ReviewVerdict.PASSED


@dataclass
class BlackboardEntry:
    """黑板条目"""
    agent_id: str
    role: str
    status: TaskStatus = TaskStatus.PENDING
    summary: str = ""
    artifact_path: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status.value,
            "summary": self.summary,
            "artifact_path": self.artifact_path,
            "timestamp": self.timestamp,
        }


@dataclass
class SessionMeta:
    """会话元数据"""
    session_id: str
    task: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: TaskStatus = TaskStatus.PENDING
    plan: Optional[Dict[str, Any]] = None
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "task": self.task,
            "created_at": self.created_at,
            "status": self.status.value,
            "plan": self.plan,
            "result": self.result,
        }
