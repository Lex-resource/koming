# 装饰器使用指南

## 概述

本项目提供三个装饰器，用于自动记录审计日志和数据存储，确保未来的所有新增功能都能被完整记录。

## 装饰器列表

| 装饰器 | 功能 | 适用场景 |
|--------|------|----------|
| `@audit` | 只记录审计日志 | 需要追踪操作历史但不需要存数据 |
| `@store_data` | 只存储数据 | 需要保存数据但不需要审计追踪 |
| `@audit_and_store` | 同时记录审计日志和存储数据（推荐） | 大多数场景，功能最完整 |

---

## 快速开始

### 1. 导入装饰器

```python
from jarvis.core.decorators import audit, store_data, audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory
```

### 2. 使用 `@audit_and_store`（推荐）

```python
@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.WEATHER,
    agent_name="执行者",
    tags=["天气", "查询"],
    capture_args=True,
    capture_result=True
)
def get_weather(city: str) -> str:
    # 业务逻辑
    return f"{city}的天气信息"
```

---

## 装饰器参数详解

### `@audit` - 审计日志装饰器

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `operation_type` | OperationType | OperationType.TOOL_USE | 操作类型 |
| `agent_name` | str | None | 智能体名称 |
| `user_id` | str | None | 用户ID |
| `capture_args` | bool | True | 是否捕获参数 |
| `capture_result` | bool | True | 是否捕获结果 |
| `capture_duration` | bool | True | 是否记录执行时间 |

### `@store_data` - 数据存储装饰器

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `category` | DataCategory | DataCategory.SYSTEM | 数据分类 |
| `source` | str | None | 数据来源（默认使用函数名） |
| `tags` | list | None | 标签列表 |
| `metadata` | dict | None | 额外元数据 |
| `auto_store_args` | bool | True | 是否自动存储参数 |
| `auto_store_result` | bool | True | 是否自动存储结果 |

### `@audit_and_store` - 组合装饰器（推荐）

包含上述所有参数。

---

## 操作类型枚举 (OperationType)

| 值 | 说明 |
|----|------|
| `USER_INPUT` | 用户输入 |
| `AGENT_CALL` | 智能体调用 |
| `TOOL_USE` | 工具使用 |
| `DATA_QUERY` | 数据查询 |
| `MEMORY_ACCESS` | 记忆访问 |
| `SYSTEM_ACTION` | 系统动作 |

## 数据分类枚举 (DataCategory)

| 值 | 说明 |
|----|------|
| `WEATHER` | 天气数据 |
| `SEARCH` | 搜索数据 |
| `DEVICE` | 设备数据 |
| `KNOWLEDGE` | 知识数据 |
| `ANALYSIS` | 分析数据 |
| `USER_INPUT` | 用户输入数据 |
| `SYSTEM` | 系统数据 |

---

## 实际例子

### 示例1：工具函数

```python
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory

@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.SEARCH,
    agent_name="执行者",
    tags=["搜索", "网络"],
    capture_args=True,
    capture_result=True
)
def web_search(query: str) -> str:
    """网络搜索"""
    # 你的搜索逻辑
    return f"关于 {query} 的搜索结果"
```

### 示例2：分析函数

```python
@audit_and_store(
    operation_type=OperationType.ANALYSIS_RUN,  # 新增类型
    category=DataCategory.ANALYSIS,
    agent_name="分析师",
    tags=["分析", "报告"]
)
def analyze_data(data: list) -> dict:
    """数据分析"""
    result = {
        "count": len(data),
        "sum": sum(data),
        "average": sum(data) / len(data) if data else 0
    }
    return result
```

### 示例3：设备控制

```python
@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.DEVICE,
    agent_name="执行者",
    tags=["设备控制", "智能家居"]
)
def control_device(device: str, action: str) -> str:
    """控制设备"""
    return f"已{action}{device}"
```

---

## 新增操作类型或数据分类

如果需要添加新的操作类型或数据分类：

### 新增操作类型

编辑 `jarvis/core/audit_logger.py`：

```python
class OperationType(Enum):
    # 现有类型...
    YOUR_NEW_TYPE = "your_new_type"  # 新增
```

### 新增数据分类

编辑 `jarvis/core/data_store.py`：

```python
class DataCategory(Enum):
    # 现有分类...
    YOUR_NEW_CATEGORY = "your_new_category"  # 新增
```

---

## 如何查看记录

### 系统命令

| 命令 | 功能 |
|------|------|
| `审计日志` / `audit` | 查看审计日志摘要 |
| `审计导出` | 导出审计日志到文件 |
| `数据统计` / `data stats` | 查看数据统计信息 |
| `数据导出` | 导出数据记录到文件 |

### 程序查询

```python
from jarvis.core.audit_logger import audit_logger, OperationType

# 按智能体查询
logs = audit_logger.get_logs_by_agent("执行者")

# 按操作类型查询
logs = audit_logger.get_logs_by_type(OperationType.TOOL_USE)

# 获取统计
summary = audit_logger.get_agent_activity_summary()
```

---

## 最佳实践

1. **优先使用 `@audit_and_store`** - 它提供最完整的记录能力
2. **合理设置标签** - 方便后续查询和统计
3. **明确操作类型** - 选择合适的 OperationType
4. **注意数据大小** - 超大结果可以设置 `capture_result=False`
5. **保持装饰器在最上层** - 确保被正确应用

---

## 示例文件

查看 `examples/decorator_example.py` 获取更多示例。
