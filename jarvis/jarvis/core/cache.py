import json
import hashlib
import asyncio
from typing import Optional, Any, List, Callable
from cachetools import TTLCache
import os

try:
    import redis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False
    redis = None


class Cache:
    """Redis缓存管理器"""

    def __init__(self):
        self._connected = False
        self.redis = None
        self.default_ttl = int(os.getenv("REDIS_TTL", 3600))

        if not _REDIS_AVAILABLE:
            print("⚠️ redis模块未安装，使用空缓存")
            self._connected = False
            return

        try:
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis.ping()
            self._connected = True
            print("✓ Redis缓存连接成功")
        except Exception as e:
            print(f"⚠️ Redis连接失败，使用空缓存: {e}")
            self._connected = False

    def _ensure_connected(self) -> bool:
        if not self._connected or self.redis is None:
            return False
        try:
            self.redis.ping()
            return True
        except Exception:
            self._connected = False
            return False

    def get(self, key: str) -> Optional[Any]:
        if not self._ensure_connected():
            return None
        try:
            value = self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception:
            self._connected = False
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if not self._ensure_connected():
            return False
        if ttl is None:
            ttl = self.default_ttl

        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)

        try:
            return self.redis.setex(key, ttl, value)
        except Exception:
            self._connected = False
            return False

    def delete(self, key: str) -> bool:
        if not self._ensure_connected():
            return False
        try:
            return bool(self.redis.delete(key))
        except Exception:
            self._connected = False
            return False

    def exists(self, key: str) -> bool:
        if not self._ensure_connected():
            return False
        try:
            return bool(self.redis.exists(key))
        except Exception:
            self._connected = False
            return False

    def expire(self, key: str, ttl: int) -> bool:
        if not self._ensure_connected():
            return False
        try:
            return bool(self.redis.expire(key, ttl))
        except Exception:
            self._connected = False
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        if not self._ensure_connected():
            return []
        try:
            return self.redis.keys(pattern)
        except Exception:
            self._connected = False
            return []

    def flush_pattern(self, pattern: str = "*") -> int:
        if not self._ensure_connected():
            return 0
        try:
            keys = self.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception:
            self._connected = False
            return 0

    def incr(self, key: str, amount: int = 1) -> int:
        if not self._ensure_connected():
            return 0
        try:
            return self.redis.incrby(key, amount)
        except Exception:
            self._connected = False
            return 0

    def decr(self, key: str, amount: int = 1) -> int:
        if not self._ensure_connected():
            return 0
        try:
            return self.redis.decrby(key, amount)
        except Exception:
            self._connected = False
            return 0

    def hset(self, name: str, key: str, value: Any) -> int:
        if not self._ensure_connected():
            return 0
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return self.redis.hset(name, key, value)
        except Exception:
            self._connected = False
            return 0

    def hget(self, name: str, key: str) -> Optional[Any]:
        if not self._ensure_connected():
            return None
        try:
            value = self.redis.hget(name, key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception:
            self._connected = False
            return None

    def hgetall(self, name: str) -> dict:
        if not self._ensure_connected():
            return {}
        try:
            return self.redis.hgetall(name)
        except Exception:
            self._connected = False
            return {}

    def hdel(self, name: str, *keys) -> int:
        if not self._ensure_connected():
            return 0
        try:
            return self.redis.hdel(name, *keys)
        except Exception:
            self._connected = False
            return 0

    def publish(self, channel: str, message: Any) -> int:
        if not self._ensure_connected():
            return 0
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message, ensure_ascii=False)
            return self.redis.publish(channel, message)
        except Exception:
            self._connected = False
            return 0

    def get_pubsub(self):
        if not self._ensure_connected():
            return None
        try:
            return self.redis.pubsub()
        except Exception:
            self._connected = False
            return None

    def get_statistics(self) -> dict:
        if not self._ensure_connected():
            return {"connected": False, "error": "Not connected"}
        try:
            info = self.redis.info("stats")
            memory = self.redis.info("memory")
            return {
                "connected_clients": self.redis.info("clients")["connected_clients"],
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "used_memory_human": memory.get("used_memory_human", "0"),
                "db_keys": self.redis.dbsize()
            }
        except Exception:
            return {"connected": False, "error": "Failed to get stats"}

    def flush_all(self):
        if not self._ensure_connected():
            return
        try:
            self.redis.flushall()
        except Exception:
            pass

    def ping(self) -> bool:
        return self._ensure_connected()

    def close(self):
        if self.redis:
            try:
                self.redis.close()
            except Exception:
                pass
        self._connected = False


class MultiLevelCache:
    """多级缓存管理器 - L1(进程内) + L2(Redis) + L3(数据库)"""

    def __init__(self):
        self.redis = Cache()
        
        self.l1_cache = TTLCache(maxsize=1000, ttl=60)
        
        self.l1_stats = {"hits": 0, "misses": 0}
        self.l2_stats = {"hits": 0, "misses": 0}

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        key_parts = [prefix] + [str(arg) for arg in args]
        key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
        key_str = ":".join(key_parts)
        
        if len(key_str) > 200:
            key_hash = hashlib.sha256(key_str.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_str

    def get(self, key: str, level: int = None) -> Optional[Any]:
        if level is None or level == 1:
            if key in self.l1_cache:
                self.l1_stats["hits"] += 1
                return self.l1_cache[key]
            self.l1_stats["misses"] += 1
        
        if level is None or level == 2:
            cached = self.redis.get(key)
            if cached is not None:
                self.l2_stats["hits"] += 1
                self.l1_cache[key] = cached
                return cached
            self.l2_stats["misses"] += 1
        
        return None

    def set(self, key: str, value: Any, ttl: int = 3600, level: int = None) -> bool:
        if level is None or level == 1:
            self.l1_cache[key] = value
        
        if level is None or level == 2:
            self.redis.set(key, value, ttl)
        
        return True

    def delete(self, key: str, level: int = None) -> bool:
        deleted = False
        
        if level is None or level == 1:
            if key in self.l1_cache:
                del self.l1_cache[key]
                deleted = True
        
        if level is None or level == 2:
            if self.redis.delete(key):
                deleted = True
        
        return deleted

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: int = 3600, level: int = None) -> Any:
        value = self.get(key, level)
        
        if value is not None:
            return value
        
        value = factory()
        self.set(key, value, ttl, level)
        
        return value

    async def get_or_set_async(self, key: str, factory, ttl: int = 3600, level: int = None) -> Any:
        value = self.get(key, level)
        
        if value is not None:
            return value
        
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        self.set(key, value, ttl, level)
        
        return value

    def invalidate_prefix(self, prefix: str) -> int:
        deleted = 0
        
        if prefix in self.l1_cache:
            del self.l1_cache[prefix]
            deleted += 1
        
        deleted += self.redis.flush_pattern(f"{prefix}*")
        
        return deleted

    def get_stats(self) -> dict:
        total_l1 = self.l1_stats["hits"] + self.l1_stats["misses"]
        total_l2 = self.l2_stats["hits"] + self.l2_stats["misses"]
        
        l1_hit_rate = (self.l1_stats["hits"] / total_l1 * 100) if total_l1 > 0 else 0
        l2_hit_rate = (self.l2_stats["hits"] / total_l2 * 100) if total_l2 > 0 else 0
        
        return {
            "l1_cache": {
                "size": len(self.l1_cache),
                "max_size": self.l1_cache.maxsize,
                "hits": self.l1_stats["hits"],
                "misses": self.l1_stats["misses"],
                "hit_rate": f"{l1_hit_rate:.2f}%"
            },
            "l2_cache": {
                **self.redis.get_statistics(),
                "hits": self.l2_stats["hits"],
                "misses": self.l2_stats["misses"],
                "hit_rate": f"{l2_hit_rate:.2f}%"
            }
        }

    def clear_l1(self):
        self.l1_cache.clear()
        self.l1_stats = {"hits": 0, "misses": 0}

    def clear_l2(self):
        self.redis.flush_all()
        self.l2_stats = {"hits": 0, "misses": 0}

    def clear_all(self):
        self.clear_l1()
        self.clear_l2()


cache = Cache()
multi_level_cache = MultiLevelCache()
