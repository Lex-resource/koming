"""会话存储抽象接口 - 文件持久化（黑板/md记录/产物）"""

from abc import ABC, abstractmethod
from typing import List, Optional


class IStorage(ABC):
    """会话存储 - 每个 session 一个目录"""

    @abstractmethod
    def create_session(self, task: str) -> str:
        """创建会话目录，返回 session_id"""
        ...

    @abstractmethod
    def get_session_dir(self, session_id: str) -> str:
        """获取会话目录路径"""
        ...

    @abstractmethod
    def write_file(self, session_id: str, filename: str, content: str) -> str:
        """写入文件，返回完整路径"""
        ...

    @abstractmethod
    def read_file(self, session_id: str, filename: str) -> Optional[str]:
        """读取文件"""
        ...

    @abstractmethod
    def append_file(self, session_id: str, filename: str, content: str) -> str:
        """追加写入"""
        ...

    @abstractmethod
    def write_artifact(self, session_id: str, filename: str, content: str) -> str:
        """写入可验证产物到 artifacts/"""
        ...

    @abstractmethod
    def read_artifact(self, session_id: str, filename: str) -> Optional[str]:
        """读取产物"""
        ...

    @abstractmethod
    def list_artifacts(self, session_id: str) -> List[str]:
        """列出所有产物文件名"""
        ...

    @abstractmethod
    def list_sessions(self, limit: int = 50) -> List[str]:
        """列出历史会话"""
        ...

    @abstractmethod
    def file_exists(self, session_id: str, filename: str) -> bool:
        """检查文件是否存在（用于审核验证）"""
        ...
