"""全局日志测试"""
import pytest
from jarvis.core.logger import GlobalLogger


class TestGlobalLogger:
    """全局日志测试类"""

    def test_log_basic(self):
        """测试基本日志记录"""
        logger = GlobalLogger()
        logger.log("INFO", "test", "test message")
        logs = logger.get_logs()
        assert len(logs) >= 1

    def test_log_user_input(self):
        """测试用户输入日志"""
        logger = GlobalLogger()
        logger.log_user_input("Hello")
        logs = logger.get_logs()
        assert any("用户输入" in log["message"] for log in logs)

    def test_log_error(self):
        """测试错误日志"""
        logger = GlobalLogger()
        logger.log_error("test", "error message", Exception("test exception"))
        logs = logger.get_logs()
        assert any(log["level"] == "ERROR" for log in logs)

    def test_log_warning(self):
        """测试警告日志"""
        logger = GlobalLogger()
        logger.log_warning("test", "warning message")
        logs = logger.get_logs()
        assert any(log["level"] == "WARNING" for log in logs)

    def test_log_debug(self):
        """测试调试日志"""
        logger = GlobalLogger()
        logger.log_debug("test", "debug message", {"key": "value"})
        logs = logger.get_logs()
        assert any(log["level"] == "DEBUG" for log in logs)