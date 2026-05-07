import redis
import json
import hashlib
import asyncio
from typing import Optional, Any, List, Callable
from cachetools import TTLCache
import os


class Cache:
    """Redis缓存管理器"""

    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )

        self.default_ttl = int(os.getenv("REDIS_TTL", 3600))

    def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if ttl is None:
            ttl = self.default_ttl
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        return self.redis.setex(key, ttl, value)

    def delete(self, key: str) -> bool:
        return bool(self.redis.delete(key))

    def exists(self, key: str) -> bool:
        return bool(self.redis.exists(key))

    def expire(self, key: str, ttl: int) -> bool:
        return bool(self.redis.expire(key, ttl))

    def keys(self, pattern: str = "*") -> List[str]:
        return self.redis.keys(pattern)

    def flush_pattern(self, pattern: str = "*") -> int:
        keys = self.keys(pattern)
        if keys:
            return self.redis.delete(*keys)
        return 0

    def incr(self, key: str, amount: int = 1) -> int:
        return self.redis.incrby(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        return self.redis.decrby(key, amount)

    def hset(self, name: str, key: str, value: Any) -> int:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self.redis.hset(name, key, value)

    def hget(self, name: str, key: str) -> Optional[Any]:
        value = self.redis.hget(name, key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def hgetall(self, name: str) -> dict:
        return self.redis.hgetall(name)

    def hdel(self, name: str, *keys) -> int:
        return self.redis.hdel(name, *keys)

    def publish(self, channel: str, message: Any) -> int:
        if isinstance(message, (dict, list)):
            message = json.dumps(message, ensure_ascii=False)
        return self.redis.publish(channel, message)

    def get_pubsub(self):
        return self.redis.pubsub()

    def get_statistics(self) -> dict:
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

    def flush_all(self):
        self.redis.flushall()

    def ping(self) -> bool:
        try:
            return self.redis.ping()
        except redis.RedisError:
            return False

    def close(self):
        self.redis.close()


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
