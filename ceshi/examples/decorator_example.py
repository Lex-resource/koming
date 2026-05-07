#!/usr/bin/env python3
"""
装饰器使用示例

展示如何使用审计日志和数据存储装饰器
"""

from jarvis.core.decorators import audit, store_data, audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory


# 1. 只记录审计日志
@audit(
    operation_type=OperationType.SYSTEM_ACTION,
    agent_name="示例智能体",
    user_id="demo_user",
    capture_args=True,
    capture_result=True
)
def simple_calculator(a: int, b: int, operation: str) -> int:
    """简单计算器"""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a // b
    else:
        raise ValueError(f"不支持的操作: {operation}")


# 2. 只存储数据
@store_data(
    category=DataCategory.ANALYSIS,
    source="数据分析器",
    tags=["分析", "统计"],
    auto_store_args=True,
    auto_store_result=True
)
def analyze_numbers(numbers: list) -> dict:
    """分析数字列表"""
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers) if numbers else 0,
        "max": max(numbers) if numbers else None,
        "min": min(numbers) if numbers else None
    }


# 3. 同时记录审计日志和存储数据（推荐）
@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.ANALYSIS,
    agent_name="分析专家",
    user_id="demo_user",
    tags=["示例", "演示"],
    capture_args=True,
    capture_result=True
)
def combined_function(x: int, y: int) -> dict:
    """组合功能示例"""
    result = {
        "x": x,
        "y": y,
        "sum": x + y,
        "product": x * y
    }
    return result


# 4. 错误处理示例
@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.SYSTEM,
    agent_name="测试智能体"
)
def error_prone_function(should_error: bool = False) -> str:
    """可能出错的函数"""
    if should_error:
        raise RuntimeError("故意触发的错误")
    return "成功执行"


def main():
    """演示函数"""
    print("🎯 装饰器使用示例")
    print("=" * 50)
    
    # 1. 审计日志示例
    print("\n1️⃣ 审计日志示例")
    result = simple_calculator(10, 5, "add")
    print(f"   计算结果: {result}")
    
    result = simple_calculator(20, 8, "multiply")
    print(f"   计算结果: {result}")
    
    # 2. 数据存储示例
    print("\n2️⃣ 数据存储示例")
    analysis = analyze_numbers([1, 2, 3, 4, 5])
    print(f"   分析结果: {analysis}")
    
    # 3. 组合示例
    print("\n3️⃣ 组合示例（审计+存储）")
    combined = combined_function(7, 3)
    print(f"   组合结果: {combined}")
    
    # 4. 错误处理示例
    print("\n4️⃣ 错误处理示例")
    try:
        error_prone_function(should_error=False)
        print("   正常执行成功")
        
        error_prone_function(should_error=True)
    except Exception as e:
        print(f"   捕获到预期错误: {e}")
    
    print("\n✅ 示例运行完成！")
    print("\n💡 提示: 运行 '审计日志' 和 '数据统计' 命令查看记录")


if __name__ == "__main__":
    main()
