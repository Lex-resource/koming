import time
import threading
import html
from functools import wraps
from typing import Any, Callable, Optional
from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.data_store import data_store, DataCategory

_serialize_lock = threading.Lock()


def _safe_serialize(obj: Any, max_length: int = 500) -> str:
    """线程安全的序列化"""
    try:
        result = str(obj)
        if len(result) > max_length:
            return result[:max_length] + "..."
        return result
    except Exception:
        return "[无法序列化]"


def _escape_html(text: str) -> str:
    """HTML转义，防止XSS"""
    return html.escape(text)


def audit(
    operation_type: OperationType = OperationType.TOOL_USE,
    agent_name: Optional[str] = None,
    user_id: Optional[str] = None,
    capture_args: bool = True,
    capture_result: bool = True,
    capture_duration: bool = True
):
    """
    审计日志装饰器 - 自动记录函数调用（线程安全）

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

            args_details = ""
            if capture_args:
                args_details = f"args: {len(args)}, kwargs: {len(kwargs)}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time if capture_duration else None

                result_str = ""
                if capture_result:
                    result_str = _safe_serialize(result, 200)

                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_details},
                    result=result_str,
                    duration=duration
                )

                return result

            except Exception as e:
                duration = time.time() - start_time if capture_duration else None

                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_details, "error": str(e)},
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
    数据存储装饰器 - 自动存储函数输入输出（线程安全）

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

            try:
                result = func(*args, **kwargs)

                content = {}
                if auto_store_args:
                    content["args"] = _safe_serialize(args, 200)
                    content["kwargs"] = _safe_serialize(kwargs, 200)
                if auto_store_result:
                    content["result"] = _safe_serialize(result, 500)

                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content=content,
                    metadata=metadata,
                    tags=actual_tags
                )

                return result

            except Exception as e:
                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content={"error": str(e)},
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
    组合装饰器 - 同时记录审计日志和存储数据（线程安全，已优化）

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

            args_details = ""
            if capture_args:
                args_details = f"args: {len(args)}, kwargs: {len(kwargs)}"

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                content = {}
                if capture_args:
                    content["args"] = _safe_serialize(args, 200)
                    content["kwargs"] = _safe_serialize(kwargs, 200)
                if capture_result:
                    content["result"] = _safe_serialize(result, 500)

                result_str = _safe_serialize(result, 200)

                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_details},
                    result=result_str,
                    duration=duration
                )

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

                audit_logger.log_operation(
                    operation_type=operation_type,
                    user_id=user_id,
                    agent_name=agent_name,
                    action=function_name,
                    details={"params": args_details, "error": str(e)},
                    result=f"错误: {str(e)}",
                    duration=duration
                )

                data_store.add_record(
                    category=category,
                    source=actual_source,
                    content={"error": str(e)},
                    metadata=metadata,
                    tags=actual_tags + ["error"]
                )

                raise

        return wrapper
    return decorator
