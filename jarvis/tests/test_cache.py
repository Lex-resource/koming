"""缓存系统测试

参考 frame.html 5.1 节测试策略中的单元测试要求，
验证多级缓存（L1 进程内 + L2 Redis）的读写、未命中、TTL 过期和删除功能。

覆盖 frame.html 中缓存降级策略：
- Redis 不可用时降级为内存缓存（L1 TTLCache）
- 所有被测模块有优雅降级，无 Redis 环境下 L1 缓存正常工作
"""
import time
import pytest

from cachetools import TTLCache

from jarvis.core.cache import MultiLevelCache, Cache


# =============================================================================
# pytest fixtures
# =============================================================================

@pytest.fixture
def cache():
    """多级缓存实例，每个测试前清理 L1 缓存"""
    c = MultiLevelCache()
    c.clear_l1()
    yield c
    c.clear_l1()


# =============================================================================
# 测试类
# =============================================================================

class TestMultiLevelCache:
    """多级缓存测试 - 验证 L1(进程内) + L2(Redis) 缓存行为"""

    def test_cache_set_get(self, cache):
        """测试缓存读写"""
        # 写入缓存
        cache.set("test_key", "test_value")
        # 读取缓存
        result = cache.get("test_key")
        assert result == "test_value"

    def test_cache_set_get_complex_data(self, cache):
        """测试复杂数据类型的缓存读写"""
        data = {
            "name": "贾维斯",
            "devices": ["空调", "灯光", "窗帘"],
            "config": {"temperature": 26, "volume": 30},
        }
        cache.set("complex_key", data)
        result = cache.get("complex_key")
        assert result == data
        assert result["devices"] == ["空调", "灯光", "窗帘"]

    def test_cache_miss(self, cache):
        """测试缓存未命中"""
        # 读取不存在的键
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_miss_increments_stats(self, cache):
        """测试缓存未命中时统计计数递增"""
        cache.get("miss_key_1")
        stats = cache.get_stats()
        assert stats["l1_cache"]["misses"] >= 1

    def test_cache_hit_increments_stats(self, cache):
        """测试缓存命中时统计计数递增"""
        cache.set("hit_key", "hit_value")
        cache.get("hit_key")
        stats = cache.get_stats()
        assert stats["l1_cache"]["hits"] >= 1

    def test_cache_ttl(self, cache):
        """测试缓存TTL过期

        L1 缓存使用 TTLCache（默认 TTL=60s）。
        此处使用独立 TTLCache 验证 TTL 过期机制。
        """
        # 创建短 TTL 缓存验证过期机制
        short_cache = TTLCache(maxsize=100, ttl=1)
        short_cache["temp_key"] = "temp_value"

        # 写入后立即可读
        assert short_cache["temp_key"] == "temp_value"

        # 等待 TTL 过期
        time.sleep(1.1)

        # 过期后应不可读
        assert "temp_key" not in short_cache

    def test_cache_ttl_with_multilevel(self, cache):
        """测试多级缓存 L1 清空后数据丢失（L2 不可用时）"""
        # 仅写入 L1 缓存
        cache.set("l1_only_key", "l1_value", level=1)
        assert cache.get("l1_only_key", level=1) == "l1_value"

        # 清空 L1 模拟 TTL 过期
        cache.clear_l1()

        # L1 清空且 L2(Redis) 不可用，应返回 None
        assert cache.get("l1_only_key", level=1) is None

    def test_cache_delete(self, cache):
        """测试缓存删除"""
        cache.set("delete_key", "delete_value")
        assert cache.get("delete_key") == "delete_value"

        # 删除缓存
        result = cache.delete("delete_key")
        assert result is True

        # 删除后应未命中
        assert cache.get("delete_key") is None

    def test_cache_delete_nonexistent(self, cache):
        """测试删除不存在的缓存键"""
        result = cache.delete("nonexistent_delete_key")
        assert result is False

    def test_cache_delete_l1_only(self, cache):
        """测试仅删除 L1 缓存"""
        cache.set("l1_delete_key", "value", level=1)
        # 仅删除 L1
        cache.delete("l1_delete_key", level=1)
        assert cache.get("l1_delete_key", level=1) is None

    def test_get_or_set(self, cache):
        """测试 get_or_set 方法（懒加载）"""
        # 首次获取时调用 factory
        result = cache.get_or_set("lazy_key", lambda: "lazy_value")
        assert result == "lazy_value"

        # 再次获取时应命中缓存，不调用 factory
        result = cache.get_or_set("lazy_key", lambda: "other_value")
        assert result == "lazy_value"

    def test_get_or_set_complex(self, cache):
        """测试 get_or_set 方法存储复杂数据"""
        def factory():
            return {"computed": True, "data": [1, 2, 3]}

        result = cache.get_or_set("complex_lazy", factory)
        assert result["computed"] is True
        assert result["data"] == [1, 2, 3]

    def test_clear_l1(self, cache):
        """测试清空 L1 缓存"""
        cache.set("clear_key_1", "value1", level=1)
        cache.set("clear_key_2", "value2", level=1)

        cache.clear_l1()

        assert cache.get("clear_key_1", level=1) is None
        assert cache.get("clear_key_2", level=1) is None

    def test_get_stats(self, cache):
        """测试获取缓存统计信息"""
        cache.set("stats_key", "value")
        cache.get("stats_key")
        cache.get("miss_key")

        stats = cache.get_stats()
        assert "l1_cache" in stats
        assert "l2_cache" in stats
        assert "size" in stats["l1_cache"]
        assert "hits" in stats["l1_cache"]
        assert "misses" in stats["l1_cache"]
        assert "hit_rate" in stats["l1_cache"]

    def test_make_key(self, cache):
        """测试缓存键生成"""
        key = cache._make_key("prefix", "arg1", "arg2", kwarg1="val1")
        assert "prefix" in key
        assert "arg1" in key
        assert "arg2" in key
        assert "kwarg1=val1" in key

    def test_make_key_long_input(self, cache):
        """测试长输入的缓存键哈希"""
        # 生成超长键名
        long_arg = "x" * 300
        key = cache._make_key("prefix", long_arg)
        # 超长键应被哈希处理
        assert len(key) < 200
        assert key.startswith("prefix:")


class TestCacheRedis:
    """Redis 缓存测试 - 验证无 Redis 环境下的优雅降级"""

    def test_redis_graceful_degradation(self):
        """测试 Redis 不可用时的优雅降级"""
        cache = Cache()
        # Redis 不可用时，get 返回 None
        assert cache.get("any_key") is None
        # Redis 不可用时，set 返回 False
        assert cache.set("any_key", "value") is False
        # Redis 不可用时，exists 返回 False
        assert cache.exists("any_key") is False
        # Redis 不可用时，ping 返回 False
        assert cache.ping() is False

    def test_redis_get_statistics(self):
        """测试 Redis 不可用时的统计信息"""
        cache = Cache()
        stats = cache.get_statistics()
        assert stats["connected"] is False
