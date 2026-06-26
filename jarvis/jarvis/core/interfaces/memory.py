"""向量记忆抽象接口 - 经验存储与检索"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class IMemory(ABC):
    """向量记忆 - 存'做过什么'，供相似度检索"""

    @abstractmethod
    def add(self, content: str, metadata: Optional[Dict] = None, memory_id: Optional[str] = None) -> str:
        """添加记忆，返回 memory_id"""
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """相似度检索，返回 [{memory_id, content, metadata, distance}]"""
        ...

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """删除指定记忆"""
        ...

    @abstractmethod
    def get(self, memory_id: str) -> Optional[Dict]:
        """按 ID 获取"""
        ...

    @abstractmethod
    def count(self) -> int:
        """记忆总数"""
        ...

    @abstractmethod
    def clear(self) -> None:
        """清空所有"""
        ...
