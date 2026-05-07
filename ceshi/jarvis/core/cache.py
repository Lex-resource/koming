import redis
import json
from typing import Optional, Any, List
from datetime import timedelta
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
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，不存在返回None
        """
        value = self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认使用配置的默认值
        
        Returns:
            是否设置成功
        """
        if ttl is None:
            ttl = self.default_ttl
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        return self.redis.setex(key, ttl, value)

    def delete(self, key: str) -> bool:
        """删除缓存"""
        return bool(self.redis.delete(key))

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return bool(self.redis.exists(key))

    def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间"""
        return bool(self.redis.expire(key, ttl))

    def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        return self.redis.ttl(key)

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键"""
        return self.redis.keys(pattern)

    def flush_pattern(self, pattern: str = "*") -> int:
        """删除匹配的键"""
        keys = self.keys(pattern)
        if keys:
            return self.redis.delete(*keys)
        return 0

    def incr(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        return self.redis.incrby(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        return self.redis.decrby(key, amount)

    def hset(self, name: str, key: str, value: Any) -> int:
        """设置哈希字段"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return self.redis.hset(name, key, value)

    def hget(self, name: str, key: str) -> Optional[Any]:
        """获取哈希字段"""
        value = self.redis.hget(name, key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None

    def hgetall(self, name: str) -> dict:
        """获取所有哈希字段"""
        return self.redis.hgetall(name)

    def hdel(self, name: str, *keys) -> int:
        """删除哈希字段"""
        return self.redis.hdel(name, *keys)

    def lpush(self, key: str, *values) -> int:
        """向左插入列表"""
        serialized = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for v in values]
        return self.redis.lpush(key, *serialized)

    def rpush(self, key: str, *values) -> int:
        """向右插入列表"""
        serialized = [json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for v in values]
        return self.redis.rpush(key, *serialized)

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表范围"""
        values = self.redis.lrange(key, start, end)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except:
                result.append(v)
        return result

    def lpop(self, key: str) -> Optional[Any]:
        """向左弹出"""
        value = self.redis.lpop(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None

    def rpop(self, key: str) -> Optional[Any]:
        """向右弹出"""
        value = self.redis.rpop(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None

    def publish(self, channel: str, message: Any) -> int:
        """发布消息"""
        if isinstance(message, (dict, list)):
            message = json.dumps(message, ensure_ascii=False)
        return self.redis.publish(channel, message)

    def get_pubsub(self):
        """获取发布订阅对象"""
        return self.redis.pubsub()

    def get_statistics(self) -> dict:
        """获取缓存统计"""
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
        """清空所有缓存"""
        self.redis.flushall()

    def ping(self) -> bool:
        """检查连接"""
        try:
            return self.redis.ping()
        except:
            return False

    def close(self):
        """关闭连接"""
        self.redis.close()


cache = Cache()
