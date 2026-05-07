"""缓存模块测试"""
import pytest
from jarvis.core.cache import Cache, MultiLevelCache


class TestCache:
    """缓存测试类"""

    def test_cache_set_get(self):
        """测试缓存设置和获取"""
        cache = Cache()
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        assert result == "test_value"

    def test_cache_delete(self):
        """测试缓存删除"""
        cache = Cache()
        cache.set("test_key", "test_value")
        cache.delete("test_key")
        result = cache.get("test_key")
        assert result is None

    def test_cache_exists(self):
        """测试缓存存在检查"""
        cache = Cache()
        cache.set("test_key", "test_value")
        assert cache.exists("test_key") is True
        cache.delete("test_key")
        assert cache.exists("test_key") is False

    def test_cache_json_data(self):
        """测试JSON数据存储"""
        cache = Cache()
        test_data = {"key": "value", "number": 123}
        cache.set("json_key", test_data)
        result = cache.get("json_key")
        assert result == test_data


class TestMultiLevelCache:
    """多级缓存测试类"""

    def test_multi_level_get_set(self):
        """测试多级缓存设置和获取"""
        cache = MultiLevelCache()
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        assert result == "test_value"

    def test_multi_level_delete(self):
        """测试多级缓存删除"""
        cache = MultiLevelCache()
        cache.set("test_key", "test_value")
        cache.delete("test_key")
        result = cache.get("test_key")
        assert result is None

    def test_get_or_set(self):
        """测试get_or_set方法"""
        cache = MultiLevelCache()
        result = cache.get_or_set("lazy_key", lambda: "lazy_value")
        assert result == "lazy_value"
        result = cache.get_or_set("lazy_key", lambda: "other_value")
        assert result == "lazy_value"