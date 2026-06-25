"""pytest配置文件"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 忽略依赖未安装模块（langchain/sqlalchemy）的预置测试文件，
# 这些文件在无 crewai/langchain/sqlalchemy 环境下无法收集或无法通过
collect_ignore = [
    "test_device_tool.py",   # 依赖 langchain
    "test_logger.py",        # 依赖 sqlalchemy（经 database 模块）
    "test_search_tool.py",   # 依赖 langchain
    "test_audit_logger.py",   # 依赖 sqlalchemy（异步写入需数据库支持）
]


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
