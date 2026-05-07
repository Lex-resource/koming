"""pytest配置文件"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def test_settings():
    """测试环境设置"""
    os.environ["TEST_MODE"] = "true"
    yield
    del os.environ["TEST_MODE"]


@pytest.fixture(scope="function")
def mock_env():
    """模拟环境变量"""
    original_env = os.environ.copy()
    os.environ["GLM_API_KEY"] = "test_key"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    yield
    os.environ.clear()
    os.environ.update(original_env)
