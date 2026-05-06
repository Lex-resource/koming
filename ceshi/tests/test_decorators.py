#!/usr/bin/env python3
"""
测试装饰器功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory
from jarvis.core.audit_logger import audit_logger
from jarvis.core.data_store import data_store


@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.SYSTEM,
    agent_name="测试智能体",
    tags=["测试", "单元测试"]
)
def test_add(a: int, b: int) -> int:
    """测试加法函数"""
    return a + b


def test_audit_and_store():
    """测试审计和存储装饰器"""
    print("🎯 测试装饰器功能...")
    
    # 清理之前的记录（可选）
    audit_logger.audit_records = []
    data_store.records = []
    
    # 执行测试函数
    result = test_add(3, 5)
    assert result == 8, "加法计算错误"
    print(f"✅ 函数执行成功: 3 + 5 = {result}")
    
    # 验证审计日志
    assert len(audit_logger.audit_records) > 0, "审计日志应该有记录"
    print(f"✅ 审计日志记录: {len(audit_logger.audit_records)} 条")
    
    # 验证数据存储
    assert len(data_store.records) > 0, "数据存储应该有记录"
    print(f"✅ 数据存储记录: {len(data_store.records)} 条")
    
    print("\n🎉 所有测试通过！")


if __name__ == "__main__":
    test_audit_and_store()
