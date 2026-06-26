# 贾维斯多智能体框架 (JARVIS) v2.0.0

以决策智能体为中枢、按需动态编组子智能体的多智能体编排框架。AI 自动生成提示词、审核闭环验证、执行经验持久化复用。

> 设计原则：**写抽象层，不写死实现**。所有变量可配置可管理，零硬编码；换任何底层实现只改一个文件。

---

## 一、核心理念（五条铁律）

1. **没有固定角色** — 没有预置的"搜索员/分析员"，子智能体由决策智能体按任务实时编组生成
2. **没有固定流程** — 该自干就自干，该编组就编组，编组几个、用什么模型都由决策智能体临场决定
3. **子 Agent 不互相通信** — 子智能体只读写共享黑板，不直接对话，避免上下文污染
4. **审核是闭环** — 自验 + 临时审核 Agent 双重审核，不通过打回原 Agent 重做（重做任务，不重新生成提示词）
5. **经验要沉淀复用** — 每次成功的编组方案沉淀为经验，下次同类任务优先检索复用

---

## 二、架构总览

```
┌─────────────────────────────────────────────────────────┐
│  入口层  entry/  (CLI + HTTP，功能相同)                  │
│      handler.py ── 系统命令 + chat()                     │
├─────────────────────────────────────────────────────────┤
│  依赖注入  app.py  Application                          │
│      按 config.provider 选实现 → 注入到抽象接口          │
├──────────────────────────┬──────────────────────────────┤
│  智能体层 agents/        │  实现层 providers/            │
│  (只依赖抽象接口)         │  (具体技术实现，可替换)        │
│   decision_agent.py      │   multi_provider_llm.py       │
│   worker_agent.py        │   file_storage.py             │
├──────────────────────────┤   memory_cache.py             │
│  核心层 core/            │   memory_vector.py            │
│  (只依赖抽象接口)         │   sqlite_database.py          │
│   blackboard.py          │   mock_device.py              │
│   experience_store.py    │   playwright_search.py        │
│   models.py              │                              │
│   interfaces/ (7 个抽象)  │                              │
├──────────────────────────┴──────────────────────────────┤
│  配置层  config/settings.py  (零硬编码，三层加载)         │
└─────────────────────────────────────────────────────────┘
```

**依赖方向铁律**：`agents/` 和 `core/` 只 import `core/interfaces/`，**绝不 import `providers/`**。换实现只动 `app.py`。

---

## 三、项目结构

```
jarvis/
├── main.py                          # 启动入口（--http 走 HTTP，否则 CLI）
├── requirements.txt
├── .env.example
├── jarvis/
│   ├── __init__.py                  # 顶层导出，__version__="2.0.0"
│   ├── app.py                       # 依赖注入组装 + 工具注册
│   ├── config/
│   │   └── settings.py              # 全部可配置项，零硬编码
│   ├── core/
│   │   ├── models.py                # 所有数据类（GroupPlan/AgentResult...）
│   │   ├── blackboard.py            # 共享黑板
│   │   ├── experience_store.py      # 三层经验持久化
│   │   └── interfaces/              # 7 个抽象接口
│   │       ├── llm.py  memory.py  cache.py  database.py
│   │       ├── device.py  search.py  storage.py
│   │       └── __init__.py
│   ├── agents/
│   │   ├── decision_agent.py        # 决策智能体（中枢）
│   │   └── worker_agent.py         # 子智能体（按需创建，干完销毁）
│   ├── providers/                  # 默认实现（都可替换）
│   │   ├── multi_provider_llm.py   # 多厂商 LLM 路由 + 适配器
│   │   ├── file_storage.py         # 文件存储（每 session 一目录）
│   │   ├── memory_cache.py         # 进程内 TTL 缓存
│   │   ├── memory_vector.py        # 向量记忆（关键词降级）
│   │   ├── sqlite_database.py      # SQLite（Profile/Skill/Session）
│   │   ├── mock_device.py          # 模拟设备（预留 MCP）
│   │   └── playwright_search.py    # Playwright 搜索+抓取
│   └── entry/
│       ├── handler.py              # CLI/HTTP 共享业务逻辑
│       ├── cli.py                  # CLI 交互入口
│       └── http.py                 # FastAPI HTTP 入口
├── data/                           # 运行时数据（向量库/SQLite/skills）
└── sessions/                       # 每次会话的 md 记录 + 产物
```

---

## 四、核心组件

### 1. 决策智能体（Orchestrator）

系统中枢，一个 ReAct 大脑。职责：**判断、自干、编组、验收、沉淀**。

完整编组流程（`decision_agent.py::_orchestrate`）：

```
用户输入
  │
  ├─ 0. 缓存命中？ → 直接返回
  ├─ 1. 决策：_decide()  LLM 判断 self_handle / orchestrate
  │     ├─ 简单任务 → _self_handle()  自己调 LLM+工具直接答
  │     └─ 复杂任务 → 进入编组
  │
  ├─ 2. 经验检索  从 memory 找类似成功案例
  ├─ 3. 编组方案  LLM 输出 GroupPlan JSON（角色/任务/工具/模型/提示词 + 完成判据）
  │     └─ 解析失败 → 降级为单通用 Agent
  ├─ 4. 执行  _execute_group()  顺序跑子 Agent，每个能读黑板拿前序产物
  ├─ 5. 审核  _review()  自验（产物存在性）+ 临时审核 Agent（逐条对照判据）
  │     └─ 不通过 → _redo_failed()  原任务+审核反馈打回原 Agent 重做（最多 max_review_rounds 轮）
  ├─ 6. 通过 → _summarize_results() 汇总
  └─ 7. 存档  _archive()  memory 存经验 / skills 存提示词 / profile 更新能力档案
```

用户改口：`handle_interruption(new_input, action)` — 决策智能体重新评估，决定保留谁、关掉谁、修改任务目标。

### 2. 子智能体（Worker Agent）

按需创建，独立上下文，干完销毁。`worker_agent.py::WorkerAgent`。

- **ReAct 循环**：`LLM → 若调用工具则执行 → 再给 LLM → 无工具调用则结束`（最多 8 轮工具调用）
- **写产物**：执行结果写 `sessions/<session>/<agent_id>-result.md`
- **写记录**：完整执行流程写 `<agent_id>.md`
- **更新黑板**：状态 + 产物路径 + 摘要写回 blackboard.md
- **可取消**：`cancel()` 供决策智能体在用户改口时调用

### 3. 共享黑板（Blackboard）

`core/blackboard.py`。所有 Agent 的共享状态区，持久化为 `blackboard.md`。

- 子 Agent **不互相通信**，只读写黑板
- 写入：任务定义 + 编组方案 + 完成判据 + 各 Agent 状态/产物摘要
- 读取：`read_artifact_summaries()` 让后续 Agent 拿到前序产出
- 借鉴 Hermes Kanban 思路：谁需要谁读

### 4. 三层经验持久化（ExperienceStore）

`core/experience_store.py`。不存上下文，存"能力"。

| 层   | 存什么        | 用途                         |
|------|--------------|------------------------------|
| Memory | 向量记忆，存"做过什么" | `search_similar(task)` 找相似成功案例 |
| Skills | 提示词模板，存"怎么干"  | `get_skill_by_trigger()` 复用提示词，含 `render()` |
| Profiles | Agent 能力档案，存"擅长什么" | `update_profile()` 记录成功率/平均耗时/用过的技能 |

**复用逻辑**：决策智能体编组前先检索 memory；命中则把历史 GroupPlan 作为参考喂给 LLM；从零写的提示词在审核通过后自动沉淀为新 skill。

---

## 五、多厂商多模型 LLM

`providers/multi_provider_llm.py`。每个模型独立配置厂商、认证、参数，决策智能体可在编组时为每个子 Agent 指定模型。

```
MultiProviderLLM  ──按 ModelConfig.provider 路由──▶  ILLMAdapter
   ├─ OpenAICompatibleAdapter  (GLM / Qwen / DeepSeek 等 OpenAI 兼容接口)
   └─ register_adapter(provider, YourAdapter)  扩展新厂商
```

- 新厂商接入：实现 `ILLMAdapter`，调用 `app.register_llm_adapter(provider, adapter)`
- 模型选择：决策智能体在 `GroupPlan.agents[].model` 指定，简单活用 flash，复杂活用强模型

---

## 六、七个抽象接口

`core/interfaces/` — 把关抽象层，agents/core 只依赖这些。

| 接口 | 方法 | 默认实现 | 可替换为 |
|------|------|---------|---------|
| `ILLM` | chat / chat_stream / get_embedding / list_models | MultiProviderLLM | 任意厂商适配器 |
| `IMemory` | add / search / delete / get / count / clear | InMemoryVectorStore | ChromaMemory |
| `ICache` | get / set / delete / exists / clear / get_stats | MemoryCache | RedisCache |
| `IDatabase` | Profile/Skill/Session CRUD + init_db | SQLiteDatabase | 任意 ORM |
| `IDevice` | control / get_status / list_devices / execute_scene / list_scenes | MockDevice | MCPDevice |
| `ISearch` | search / scrape / close | PlaywrightSearch | 任意搜索后端 |
| `IStorage` | create_session / write_file / read_artifact / list_sessions... | FileStorage | 对象存储 |

---

## 七、配置系统

`config/settings.py`，三层加载优先级：**环境变量 > 配置文件 > 默认值**。

```python
Config.load(config_file)   # 入口：文件打底 + env 覆盖
get_config()               # 全局单例
init_config(file)          # 手动初始化
```

### 关键配置项

- **ModelConfig**：单模型配置（provider/model/api_key/base_url/temperature/extra_headers/extra_params），每个模型独立认证
- **LLMConfig**：多厂商多模型池 `Dict[str, ModelConfig]`，`get_model(name)` / `add_model()` / `list_models()`
- **OrchestratorConfig**：model / max_rounds / enable_self_handle / enable_experience_reuse
- **WorkerConfig**：default_model / timeout / max_retries
- **ReviewConfig**：enable_self_verify / enable_agent_review / max_review_rounds / reviewer_model
- 其余：MemoryConfig / CacheConfig / DatabaseConfig / DeviceConfig / SearchConfig / StorageConfig / ExperienceConfig / BlackboardConfig

### 环境变量

通用密钥（向后兼容，仅应用到未单独配置的模型）：

```
LLM_API_KEY=xxx
LLM_BASE_URL=https://...
LLM_DEFAULT_MODEL=glm-4.5-flash
```

按模型独立配置（前缀 `MODEL_<NAME>_`，模型名大写并替换 `.`/`-` 为 `_`）：

```
MODEL_GLM_4_5_API_KEY=xxx
MODEL_GLM_4_5_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
MODEL_GLM_4_5_PROVIDER=openai_compatible
MODEL_GLM_4_5_MODEL=glm-4.5
MODEL_GLM_4_5_TEMPERATURE=0.3

# 可加别的厂商
MODEL_QWEN_MAX_API_KEY=xxx
MODEL_QWEN_MAX_BASE_URL=https://dashscope.aliyuncs.com/...
MODEL_QWEN_MAX_PROVIDER=openai_compatible
```

Embedding 与其他组件：

```
EMBEDDING_API_KEY=xxx
EMBEDDING_BASE_URL=...
EMBEDDING_MODEL=embedding-3

ORCHESTRATOR_MODEL=glm-4.5
WORKER_MODEL=glm-4.5-flash
REVIEWER_MODEL=glm-4.5

MEMORY_PROVIDER=chromadb
CACHE_PROVIDER=memory           # 或 redis
REDIS_HOST=localhost
DATABASE_PROVIDER=sqlite
DATABASE_URL=sqlite:///./data/jarvis.db
DEVICE_PROVIDER=mock            # 或 mcp
MCP_SERVER_URL=...
SESSION_DIR=./sessions
```

---

## 八、快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

```bash
cp .env.example .env
# 编辑 .env，至少填 LLM_API_KEY
```

或直接导出环境变量：

```bash
export LLM_API_KEY=你的key
```

### 3. 运行

```bash
# CLI 模式
python main.py

# HTTP 模式
python main.py --http        # 启动后访问 http://localhost:8000

# 指定配置文件
python main.py jarvis_config.json
```

---

## 九、入口与系统命令

`entry/handler.py::handle_command` 是 CLI 和 HTTP 共享的业务入口。

| 命令（中/英） | 功能 |
|--------------|------|
| `help` / `帮助` | 显示可用命令 |
| `status` / `状态` | 系统状态（模型/设备/记忆/缓存） |
| `models` / `模型` | 可用模型列表 |
| `devices` / `设备` | 设备列表 |
| `scenes` / `场景` | 场景列表 |
| `skills` / `技能` | 已积累技能 |
| `sessions` / `会话` | 最近会话 |
| `quit` / `退出` | 退出 |

其他输入 → `app.chat()` → 决策智能体处理。

HTTP 端点（`entry/http.py`）：`/chat` `/models` `/devices` `/scenes` `/sessions` `/skills` `/status`。

---

## 十、扩展指南

### 加一个新模型

```python
from jarvis.config.settings import ModelConfig
app = get_app()
app.config.llm.add_model(ModelConfig(
    name="qwen-max",
    provider="openai_compatible",
    model="qwen-max",
    api_key="...",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
))
```

或通过环境变量 `MODEL_QWEN_MAX_API_KEY` 等自动加载。

### 加一个新厂商适配器

```python
from jarvis.providers.multi_provider_llm import ILLMAdapter

class AnthropicAdapter(ILLMAdapter):
    def chat(self, config, messages, tools=None): ...
    def get_embedding(self, config, text): ...
    def list_models(self, config): ...

app.register_llm_adapter("anthropic", AnthropicAdapter())
```

### 加一个自定义工具

```python
from jarvis.core.models import ToolDefinition

def my_tool(query: str) -> str:
    return "..."

app.register_tool(ToolDefinition(
    name="my_tool",
    description="做什么的",
    parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    handler=my_tool,
))
```

注册后决策智能体和子智能体即可通过 function calling 调用。

### 替换底层实现

只改 `app.py::_build_instances` 中的 provider 分支，或运行时调用 `register_device()` / `register_search()`。已预留接入点：

- `ChromaMemory`（真实向量库）替代 InMemoryVectorStore
- `RedisCache` 替代 MemoryCache
- `MCPDevice`（真实物理设备）替代 MockDevice

---

## 十一、当前实现状态与边界

**已实现（默认实现可用）**：
- 决策智能体完整编组流程（检索→编组→执行→审核→存档→重做闭环）
- 子智能体 ReAct 循环 + 黑板读写 + 产物持久化
- 多厂商多模型 LLM 适配（OpenAI 兼容接口）
- 文件存储 / 内存缓存 / 关键词向量降级 / SQLite / Mock 设备 / Playwright 搜索
- CLI + HTTP 双入口
- 三层经验持久化

**预留接入点（接口已定义，实现待补）**：
- ChromaDB 真实向量记忆（当前降级为关键词匹配）
- Redis 缓存
- MCP 真实设备控制
- 更多厂商适配器（Anthropic 等）

**能力边界**：
- 不支持毫秒级实时对抗性交互（用户说话中突然改口需等当前轮次结束）
- 长时间任务需拆成短任务接力 + 黑板持久化 + 异常告警，框架能力范围内可实现
- 多模态（语音/视觉）依赖模型原生能力，不在框架层做

---

## 十二、后续路线

- [ ] 配真实 API Key 跑端到端验证（自干 + 编组各一次）
- [ ] 补 ChromaMemory 真实向量检索实现
- [ ] 补 MCPDevice 接入真实设备
- [ ] 加更多厂商适配器
- [ ] 补单元测试覆盖核心流程
