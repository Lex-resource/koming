"""审计日志测试"""
import pytest
from jarvis.core.audit_logger import AuditLogger, OperationType


class TestAuditLogger:
    """审计日志测试类"""

    def test_log_operation(self):
        """测试记录操作日志"""
        logger = AuditLogger()
        logger.log_operation(
            operation_type=OperationType.USER_INPUT,
            user_id="test_user",
            action="test_action",
            details={"key": "value"}
        )
        logs = logger.get_logs_by_user("test_user")
        assert len(logs) >= 1

    def test_logs_by_type(self):
        """测试按类型查询日志"""
        logger = AuditLogger()
        logger.log_operation(
            operation_type=OperationType.TOOL_USE,
            agent_name="test_agent"
        )
        logs = logger.get_logs_by_type(OperationType.TOOL_USE)
        assert len(logs) >= 1

    def test_get_agent_summary(self):
        """测试获取智能体活动摘要"""
        logger = AuditLogger()
        summary = logger.get_agent_activity_summary()
        assert "total_operations" in summary

    def test_get_user_summary(self):
        """测试获取用户活动摘要"""
        logger = AuditLogger()
        summary = logger.get_user_activity_summary()
        assert "total_interactions" in summary