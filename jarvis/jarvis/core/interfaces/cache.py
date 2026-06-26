"""缓存抽象接口 - LLM 响应缓存"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ICache(ABC):
    """缓存 - 减少 LLM 重复调用"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """缓存统计（命中率等）"""
        ...
