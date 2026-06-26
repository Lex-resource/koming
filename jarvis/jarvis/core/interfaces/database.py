"""数据库抽象接口 - 结构化数据持久化（Profile/Skill/Session）"""

from abc import ABC, abstractmethod
from typing import List, Optional

from jarvis.core.models import AgentProfile, Skill, SessionMeta


class IDatabase(ABC):
    """数据库 - 存结构化数据，支持换底层引擎"""

    @abstractmethod
    def init_db(self) -> None:
        """初始化表结构"""
        ...

    # Profile 存储
    @abstractmethod
    def save_profile(self, profile: AgentProfile) -> bool:
        ...

    @abstractmethod
    def get_profile(self, role: str) -> Optional[AgentProfile]:
        ...

    @abstractmethod
    def list_profiles(self) -> List[AgentProfile]:
        ...

    @abstractmethod
    def delete_profile(self, agent_id: str) -> bool:
        ...

    # Skill 存储
    @abstractmethod
    def save_skill(self, skill: Skill) -> bool:
        ...

    @abstractmethod
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        ...

    @abstractmethod
    def list_skills(self) -> List[Skill]:
        ...

    @abstractmethod
    def delete_skill(self, skill_id: str) -> bool:
        ...

    # Session 存储
    @abstractmethod
    def save_session(self, session: SessionMeta) -> bool:
        ...

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[SessionMeta]:
        ...

    @abstractmethod
    def list_sessions(self, limit: int = 50) -> List[SessionMeta]:
        ...
