import time
import json
from functools import wraps
from typing import Any, Callable, Optional, Union
from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.data_store import data_store, DataCategory, DataRecord


def audit(
    operation_type: OperationType = OperationType.TOOL_USE,
    agent_name: Optional[str] = None,
    user_id: Optional[str] = None,
    capture_args: bool = True,
    capture_result: bool = True,
    capture_duration: bool = True
):
    """
    审计日志装饰器 - 自动记录函数调用
    
    Args:
        operation_type: 操作类型
        agent_name: 智能体名称
        user_id: 用户ID
        capture_args: 是否捕获参数
        capture_result: 是否捕获结果
        capture_duration: 是否记录执行时间
    
    Usage:
        @audit(OperationType.TOOL_USE, agent_name="执行者")
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            function_name = func.__name__
            
            # 准备参数详情
            args_str = ""
            if capture_args:
                try:
                    args_str = json.dumps({
                        "args": [str(arg) for arg in args],
                        "kwargs": {k: str(v) for k, v in kwargs.items()}
                    }, ensure_ascii=False)
                except (TypeError, ValueError):
                    args_str = "参数无法序列化"
            
            # 记录开始日志
            audit_logger.log_operation(
                operation_type=operation_type,
                user_id=user_id,
                agent_name=agent_name,
                action=function_name,
                details={"params": args_str}
            )
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                duration = time.time() - start_time if capture_duration else None
                
                # 记录成功日志
                result_str = ""
                if capture_result:
                    try:
                        result_str = str(result)[:200] if result else None
                    except (TypeError, ValueError):
                        result_str = "结果无法序列化"
                
                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_str},
                    result=result_str,
                    duration=duration
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time if capture_duration else None
                
                # 记录错误日志
                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_str, "error": str(e)},
                    result=f"错误: {str(e)}",
                    duration=duration
                )
                
                raise
        
        return wrapper
    return decorator


def store_data(
    category: DataCategory = DataCategory.SYSTEM,
    source: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
    auto_store_args: bool = True,
    auto_store_result: bool = True
):
    """
    数据存储装饰器 - 自动存储函数输入输出
    
    Args:
        category: 数据分类
        source: 数据来源（默认使用函数名）
        tags: 标签列表
        metadata: 元数据
        auto_store_args: 是否自动存储参数
        auto_store_result: 是否自动存储结果
    
    Usage:
        @store_data(DataCategory.WEATHER, tags=["天气", "查询"])
        def get_weather(city):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = func.__name__
            actual_source = source or function_name
            actual_tags = tags or [function_name]
            
            # 执行函数
            try:
                result = func(*args, **kwargs)
                
                # 准备存储内容
                content = {}
                if auto_store_args:
                    content["args"] = str(args)
                    content["kwargs"] = {k: str(v) for k, v in kwargs.items()}
                if auto_store_result:
                    content["result"] = str(result)[:500] if result else None
                
                # 存储数据
                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content=content,
                    metadata=metadata,
                    tags=actual_tags
                )
                
                return result
                
            except Exception as e:
                # 存储错误数据
                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content={"error": str(e), "args": str(args), "kwargs": str(kwargs)},
                    metadata=metadata,
                    tags=actual_tags + ["error"]
                )
                
                raise
        
        return wrapper
    return decorator


def audit_and_store(
    operation_type: OperationType = OperationType.TOOL_USE,
    category: DataCategory = DataCategory.SYSTEM,
    agent_name: Optional[str] = None,
    user_id: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
    capture_args: bool = True,
    capture_result: bool = True
):
    """
    组合装饰器 - 同时记录审计日志和存储数据
    
    Args:
        operation_type: 操作类型
        category: 数据分类
        agent_name: 智能体名称
        user_id: 用户ID
        source: 数据来源
        tags: 标签列表
        metadata: 元数据
        capture_args: 是否捕获参数
        capture_result: 是否捕获结果
    
    Usage:
        @audit_and_store(
            operation_type=OperationType.TOOL_USE,
            category=DataCategory.WEATHER,
            agent_name="执行者",
            tags=["天气", "查询"]
        )
        def get_weather(city):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = func.__name__
            actual_source = source or function_name
            actual_tags = tags or [function_name]
            start_time = time.time()
            
            # 准备参数详情
            args_str = ""
            if capture_args:
                try:
                    args_str = json.dumps({
                        "args": [str(arg) for arg in args],
                        "kwargs": {k: str(v) for k, v in kwargs.items()}
                    }, ensure_ascii=False)
                except (TypeError, ValueError):
                    args_str = "参数无法序列化"
            
            # 记录开始审计日志
            audit_logger.log_operation(
                operation_type=operation_type,
                user_id=user_id,
                agent_name=agent_name,
                action=function_name,
                details={"params": args_str}
            )
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # 准备存储内容
                content = {}
                if capture_args:
                    content["args"] = str(args)
                    content["kwargs"] = {k: str(v) for k, v in kwargs.items()}
                if capture_result:
                    content["result"] = str(result)[:500] if result else None
                
                # 准备结果字符串
                result_str = ""
                if capture_result:
                    try:
                        result_str = str(result)[:200] if result else None
                    except (TypeError, ValueError):
                        result_str = "结果无法序列化"
                
                # 记录审计日志
                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_str},
                    result=result_str,
                    duration=duration
                )
                
                # 存储数据
                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content=content,
                    metadata=metadata,
                    tags=actual_tags
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # 记录错误审计日志
                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_str, "error": str(e)},
                    result=f"错误: {str(e)}",
                    duration=duration
                )
                
                # 存储错误数据
                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content={"error": str(e), "args": str(args), "kwargs": str(kwargs)},
                    metadata=metadata,
                    tags=actual_tags + ["error"]
                )
                
                raise
        
        return wrapper
    return decorator
