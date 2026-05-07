# 贾维斯多智能体框架 - 代码逻辑分析

## 一、项目概述

这是一个基于 **LangChain + CrewAI** 构建的多智能体协作框架，目标是为AI应用提供可扩展的智能体编排能力。框架采用模块化设计，核心亮点包括：

- **多智能体协作**：指挥官、分析师、执行者、学习官四种角色分工明确
- **插件系统**：支持动态注册和加载Agent
- **装饰器审计**：通过装饰器自动记录操作日志和数据存储
- **异步执行**：支持并发任务处理和优先级队列
- **可扩展架构**：每个模块职责单一，便于二次开发

---

## 二、核心架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (入口)                            │
│                     主循环: 用户输入 → 任务分发                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  CrewManager    │ │ GlobalState      │ │ AuditLogger      │
│  (任务编排中心)  │ │ (全局状态管理)    │ │ (审计日志系统)    │
└────────┬────────┘ └────────┬────────┘ └─────────────────┘
         │                   │
         └─────────┬─────────┘
                   │
      ┌────────────┴────────────┐
      │                         │
      ▼                         ▼
┌────────────────────┐  ┌────────────────────┐
│    Agent团队         │  │   工具集 (Tools)    │
│  ┌──────────────┐   │  │  ┌──────────────┐   │
│  │ Commander    │   │  │  │ SearchTool   │   │
│  │ (指挥官)      │   │  │  │ WeatherTool │   │
│  └──────────────┘   │  │  │ DeviceTool  │   │
│  ┌──────────────┐   │  │  └──────────────┘   │
│  │ Analyst      │   │  └────────────────────┘
│  │ (分析师)      │   │
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │ Executor    │   │
│  │ (执行者)      │   │
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │ Learner     │   │
│  │ (学习官)      │   │
│  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     增强模块 (v2.0)                               │
├─────────────────────────────────────────────────────────────────┤
│  PluginRegistry     │  AsyncTaskExecutor  │  MessageQueue        │
│  (插件注册中心)       │  (异步任务执行器)     │  (消息队列)           │
├─────────────────────────────────────────────────────────────────┤
│  Metrics            │  Microservice       │  DataStore           │
│  (监控指标)          │  (微服务架构)        │  (数据分类存储)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块详解

### 3.1 智能体层级 (Agents)

#### BaseAgent - 基类设计
```python
# jarvis/agents/base_agent.py
class BaseAgent(Agent):
    def __init__(self, role, goal, backstory, llm=None, **kwargs):
        llm = llm or self._get_default_llm()
        super().__init__(
            role=role, goal=goal, backstory=backstory,
            llm=llm, verbose=Settings.DEBUG, **kwargs
        )
```

**设计要点**：
- 继承自 `crewai.Agent`，复用 CrewAI 的Agent框架
- 统一配置 LLM（默认使用智谱GLM-4）
- 支持自定义 verbose 模式便于调试

#### 四大Agent角色

| Agent | 角色 | 职责 |
|-------|------|------|
| **CommanderAgent** | 指挥官 | 理解用户意图，制定执行计划，分配任务 |
| **AnalystAgent** | 分析师 | 分析问题，收集信息，提供专业建议 |
| **ExecutorAgent** | 执行者 | 调用工具执行具体操作 |
| **LearnerAgent** | 学习官 | 记录对话，学习新知识 |

---

### 3.2 任务编排中心 (CrewManager)

```python
# jarvis/core/crew_manager.py
class CrewManager:
    def __init__(self):
        self.commander = CommanderAgent()
        self.analyst = AnalystAgent()
        self.executor = ExecutorAgent()
        self.learner = LearnerAgent()

    def execute_task(self, user_input: str) -> str:
        task = self.create_task(user_input)
        
        crew = Crew(
            agents=[self.commander, self.analyst, self.executor, self.learner],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
```

**工作流程**：
1. 用户输入 → 创建 Task
2. Task 分配给 Commander 主导
3. CrewAI 框架自动调度 Agent 协作
4. 返回最终执行结果

---

### 3.3 装饰器系统 (Decorators)

装饰器是框架的核心特性，实现**零侵入式**的操作记录。

#### 三种装饰器对比

| 装饰器 | 功能 | 使用场景 |
|--------|------|----------|
| `@audit` | 仅记录审计日志 | 只需追踪操作 |
| `@store_data` | 仅存储数据 | 只需数据统计 |
| `@audit_and_store` | 同时记录+存储 | **推荐** 完整记录 |

#### 使用示例

```python
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory

@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.WEATHER,
    agent_name="执行者",
    tags=["天气", "查询"]
)
def get_weather(city: str):
    # 业务逻辑...
    return weather_data
```

#### 装饰器执行流程

```
┌─────────────┐
│ 调用函数     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ 1. 记录开始审计日志       │
│ 2. 记录开始时间           │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ 执行原始函数              │
│ - 成功: 记录结果+存储数据  │
│ - 失败: 记录错误日志      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ 返回结果 / 抛出异常       │
└─────────────────────────┘
```

---

### 3.4 审计日志系统 (AuditLogger)

```python
# jarvis/core/audit_logger.py
class AuditLogger:
    def log_operation(
        self,
        operation_type: OperationType,
        user_id: str = "anonymous",
        agent_name: str = None,
        action: str = None,
        details: Dict = None,
        result: Any = None,
        duration: float = None
    ):
```

**核心能力**：
- **异步写入**：后台线程写入文件，不阻塞主流程
- **多维度查询**：按用户/Agent/操作类型/时间范围查询
- **trace_id追踪**：每个操作生成唯一ID，便于关联分析

---

### 3.5 数据分类存储 (DataStore)

```python
# jarvis/core/data_store.py
class DataCategory(Enum):
    WEATHER = "weather"
    SEARCH = "search"
    DEVICE = "device"
    KNOWLEDGE = "knowledge"
    ANALYSIS = "analysis"
    USER_INPUT = "user_input"
```

**存储结构**：
```python
{
    "id": "uuid",
    "category": "weather",
    "source": "get_weather",
    "content": {"city": "北京", "result": "25°C"},
    "tags": ["天气", "查询"],
    "metadata": {"user_id": "001"},
    "timestamp": "2026-05-07T10:30:00"
}
```

---

## 四、增强模块 (v2.0)

### 4.1 插件系统 (PluginRegistry)

```python
@agent_plugin(
    name="MyAgent",
    version="1.0.0",
    tags=["custom", "vip"]
)
class MyAgent(BaseAgent):
    pass
```

**核心功能**：
- **装饰器注册**：通过 `@agent_plugin` 自动注册
- **目录扫描**：自动发现 `plugins/` 目录下的Agent
- **钩子系统**：支持 on_register/on_unregister/on_execute/on_error 钩子

### 4.2 异步执行器 (AsyncTaskExecutor)

```python
# 创建异步任务
task_id = executor.create_task(
    task_type="agent_execution",
    description="查询天气",
    func=get_weather,
    kwargs={"city": "北京"},
    priority=TaskPriority.HIGH
)

# 批量并行执行
results = await executor.execute_parallel([
    {"func": func1, "kwargs": {}},
    {"func": func2, "kwargs": {}},
])
```

**特性**：
- 优先级队列：高优先级任务优先执行
- 自动重试：失败任务最多重试3次
- 超时控制：可设置单任务超时时间

---

## 五、主程序流程 (main.py)

```
启动程序
    │
    ▼
┌─────────────────────┐
│ 验证配置 (Settings) │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 加载历史数据         │
│ - 对话历史           │
│ - 审计日志           │
│ - 数据存储           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 初始化 CrewManager  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐     ┌─────────────────┐
│ 主循环              │     │ 系统命令处理     │
│ while True:         │────▶│ - 状态查询       │
│   获取用户输入       │     │ - 历史导出       │
│   处理系统命令       │     │ - 数据统计       │
└──────┬──────────────┘     └─────────────────┘
       │
       ▼
┌─────────────────────┐
│ 任务执行            │
│ 1. 记录用户输入日志  │
│ 2. 调用 CrewManager  │
│ 3. 记录Agent执行日志 │
│ 4. 存储对话数据      │
│ 5. 更新全局状态      │
└─────────────────────┘
```

---

## 六、扩展性设计要点

### 6.1 新增工具 (Tool)

```python
# jarvis/tools/my_tool.py
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory

@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.KNOWLEDGE,
    agent_name="执行者",
    tags=["新工具"]
)
def my_new_tool(param):
    """新工具函数，自动被审计和存储"""
    return result
```

### 6.2 新增Agent

```python
# jarvis/agents/my_agent.py
from jarvis.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="我的Agent",
            goal="具体目标",
            backstory="背景故事",
            allow_delegation=True
        )
```

### 6.3 注册新Agent到插件系统

```python
# 在 jarvis/core/plugin_registry.py 的 register_builtin_agents() 中添加
registry.register(
    "MyAgent",
    MyAgent,
    PluginMetadata(
        name="MyAgent",
        version="1.0.0",
        description="我的自定义Agent",
        tags=["custom"]
    )
)
```

---

## 七、数据流向图

```
用户输入
    │
    ├──▶ AuditLogger.log_operation() ──▶ audit_logs.json
    │
    ▼
CrewManager.execute_task()
    │
    ├──▶ Commander (理解意图)
    │        │
    │        ├──▶ Analyst (分析问题)
    │        │        │
    │        └──▶ Executor (执行工具)
    │                 │
    │                 ├──▶ @audit_and_store 装饰的函数
    │                 │        │
    │                 │        ├──▶ AuditLogger
    │                 │        │
    │                 │        └──▶ DataStore
    │                 │
    │                 └──▶ Tools (SearchTool, WeatherTool, etc.)
    │
    └──▶ Learner (学习记录)
    
    │
    ▼
返回结果
    │
    ├──▶ AuditLogger ──▶ 记录Agent执行
    │
    ├──▶ DataStore ──▶ 存储对话数据
    │
    └──▶ GlobalState ──▶ 更新对话历史
```

---

## 八、关键设计模式

### 8.1 单例模式
```python
class PluginRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 8.2 装饰器模式
- 零侵入式增强功能
- 统一处理横切关注点（日志、存储、审计）

### 8.3 观察者模式（钩子系统）
```python
_plugin_hooks = {
    'on_register': [],
    'on_unregister': [],
    'on_execute': [],
    'on_error': []
}
```

### 8.4 生产者-消费者模式
- 异步写入线程：生产者放入队列，消费者写入文件
- 异步任务执行器：任务队列 → 工作线程池

---

## 九、文件组织结构

```
jarvis/
├── agents/                    # Agent定义
│   ├── base_agent.py         # 基类 (继承CrewAI.Agent)
│   ├── commander.py          # 指挥官
│   ├── analyst.py            # 分析师
│   ├── executor.py           # 执行者
│   └── learner.py            # 学习官
│
├── core/                     # 核心系统
│   ├── crew_manager.py       # 任务编排中心
│   ├── audit_logger.py       # 审计日志 (异步写入)
│   ├── data_store.py         # 数据分类存储
│   ├── global_state.py       # 全局状态管理
│   ├── decorators.py         # 装饰器系统 ⭐
│   ├── plugin_registry.py    # 插件注册中心
│   ├── async_executor.py     # 异步任务执行
│   ├── message_queue.py      # 消息队列
│   ├── metrics.py            # 监控指标
│   └── microservice.py       # 微服务架构
│
├── tools/                    # 工具集
│   ├── search_tool.py
│   ├── weather_tool.py
│   └── device_tool.py
│
├── memory/                   # 记忆系统
│   └── memory_manager.py
│
└── config/                   # 配置
    └── settings.py
```

---

## 十、总结

### 框架优势
1. **高可扩展性**：模块独立，支持插件动态加载
2. **零侵入审计**：装饰器实现，无需修改业务代码
3. **异步非阻塞**：后台写入，不影响主流程
4. **多维度追踪**：trace_id 贯穿整个请求生命周期
5. **开箱即用**：内置4种Agent角色，快速构建应用

### 适用场景
- 企业级AI助手
- 多Agent协作系统
- 需要完整操作审计的应用
- 需要数据分类统计的系统

---

*文档生成时间：2026-05-07*
*框架版本：v2.0*
