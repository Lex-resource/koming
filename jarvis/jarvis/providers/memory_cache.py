"""内存缓存实现 - 零依赖，开箱即用"""

import time
from typing import Any, Dict, Optional

from jarvis.core.interfaces import ICache
from jarvis.config.settings import CacheConfig


class MemoryCache(ICache):
    """进程内 TTL 缓存"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._store: Dict[str, tuple] = {}  # key -> (value, expire_at)
        self._stats = {"hits": 0, "misses": 0}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            self._stats["misses"] += 1
            return None
        value, expire_at = self._store[key]
        if expire_at and time.time() > expire_at:
            del self._store[key]
            self._stats["misses"] += 1
            return None
        self._stats["hits"] += 1
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        t = ttl if ttl is not None else self.config.ttl
        expire_at = time.time() + t if t else None
        self._store[key] = (value, expire_at)
        # LRU 简化：超过 maxsize 删除最早
        if len(self._store) > self.config.maxsize:
            oldest = next(iter(self._store))
            del self._store[oldest]
        return True

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        self._store.clear()
        self._stats = {"hits": 0, "misses": 0}

    def get_stats(self) -> Dict[str, Any]:
        total = self._stats["hits"] + self._stats["misses"]
        return {
            "size": len(self._store),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": self._stats["hits"] / total if total else 0.0,
        }
