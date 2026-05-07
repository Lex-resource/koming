# 贾维斯AI助手 (JARVIS)

一个基于 LangChain + CrewAI 构建的全场景AI智能体系统，目标是实现类似《钢铁侠》中贾维斯的功能。

## 功能特性

- 🤖 **自然语言交互** - 支持文本输入输出，多轮对话
- 🔍 **智能搜索** - 集成网络搜索功能
- 🌤️ **天气查询** - 获取实时天气信息
- 🏠 **设备控制** - 模拟智能家居控制（空调、灯光、窗帘、音乐）
- 🧠 **记忆系统** - 基于Chroma的知识库存储
- 👥 **多智能体协作** - 指挥官、分析师、执行者、学习官分工协作
- 🔒 **审计日志** - 记录所有用户和智能体操作，支持审查追踪
- 📊 **数据分类存储** - 分门别类存储所有查询数据，支持统计分析
- 🔧 **装饰器自动记录** - 新增功能自动被审计和存储系统记录

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入您的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
GLM_API_KEY=your_glm_api_key_here
```

### 3. 运行

```bash
python main.py
```

## 项目结构

```
ceshi/
├── jarvis/                    # 核心包
│   ├── __init__.py            # 包导出模块
│   ├── agents/                # 智能体模块
│   │   ├── base_agent.py      # 基础智能体类
│   │   ├── commander.py       # 指挥官智能体
│   │   ├── analyst.py         # 分析师智能体
│   │   ├── executor.py        # 执行者智能体
│   │   └── learner.py         # 学习官智能体
│   ├── tools/                 # 工具模块
│   │   ├── search_tool.py     # 搜索工具
│   │   ├── weather_tool.py   # 天气工具
│   │   └── device_tool.py     # 设备控制工具
│   ├── memory/                # 记忆模块
│   │   └── memory_manager.py  # 记忆管理器
│   ├── core/                  # 核心模块
│   │   ├── audit_logger.py    # 审计日志系统
│   │   ├── data_store.py      # 数据分类存储
│   │   ├── decorators.py      # 装饰器（自动记录）
│   │   ├── global_state.py    # 全局状态管理
│   │   ├── crew_manager.py    # 团队协作管理
│   │   └── logger.py          # 日志工具
│   └── config/                # 配置模块
│       └── settings.py        # 设置类
├── examples/                  # 示例代码
│   └── decorator_example.py   # 装饰器使用示例
├── docs/                      # 文档目录
│   ├── TECH_STACK.md          # 技术栈说明
│   └── DECORATOR_GUIDE.md    # 装饰器使用指南
├── scripts/                   # 脚本工具目录
├── archive/                   # 归档（旧文件）
├── data/                      # 数据存储目录
├── main.py                    # 主程序入口
├── requirements.txt           # 依赖列表
└── README.md                  # 项目文档
```

## 系统命令

### 基础命令
| 命令 | 功能 |
|------|------|
| `状态` / `status` | 查看系统状态 |
| `历史` / `history` | 查看最近对话历史 |
| `导出` | 导出对话历史 |
| `清空历史` | 清空对话历史 |
| `摘要` / `summary` | 查看系统摘要 |
| `退出` / `quit` | 退出系统 |

### 审计日志命令
| 命令 | 功能 |
|------|------|
| `审计日志` / `audit` | 查看审计日志摘要 |
| `审计导出` | 导出审计日志 |

### 数据存储命令
| 命令 | 功能 |
|------|------|
| `数据统计` / `data stats` | 查看数据统计信息 |
| `数据导出` | 导出所有数据记录 |

## 使用示例

```
您: 帮我查询北京今天的天气
🤖 贾维斯: 正在处理您的请求...
北京: 🌡️ 25°C ☀️ 晴天

您: 打开空调，温度调到24度
🤖 贾维斯: 正在处理您的请求...
已开启空调
空调温度已调节至 24°C

您: 数据统计
📈 数据统计:
  - 总记录数: 2
  - 分类分布: {'user_input': 1, 'weather': 1, 'device': 1}
  - 来源分布: {'用户输入': 1, 'get_weather': 1, 'control_device': 1}
  - 标签分布: {'对话': 1, '用户交互': 1, '天气': 1, '北京': 1, '设备控制': 1, '空调': 1}

您: 审计日志
🔍 审计日志摘要:
  - 总操作数: 4
  - 操作类型分布: {'user_input': 2, 'agent_call': 2, 'data_query': 1, 'tool_use': 1}
  - 智能体分布: {'贾维斯指挥官': 2, '执行者': 2}

您: 退出
👋 再见！期待下次为您服务。
```

## 核心模块说明

### 1. 审计日志系统 (`core/audit_logger.py`)
- 记录所有用户输入、智能体调用、工具使用、数据查询等操作
- 支持按用户ID、智能体名称、操作类型、时间范围查询
- 自动保存到文件，支持导出功能

### 2. 数据分类存储 (`core/data_store.py`)
- 按类别存储数据：天气、搜索、设备、知识、分析、用户输入
- 支持标签系统，方便分类检索
- 提供统计功能，支持按分类、来源、标签统计

### 3. 装饰器系统 (`core/decorators.py`)
- `@audit` - 只记录审计日志
- `@store_data` - 只存储数据
- `@audit_and_store` - **推荐** - 同时记录审计日志和存储数据
- 装饰器自动捕获参数、结果、执行时间，错误也会被记录

**新增功能只需要添加装饰器即可被自动记录：**
```python
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory

@audit_and_store(
    operation_type=OperationType.TOOL_USE,
    category=DataCategory.ANALYSIS,
    agent_name="执行者",
    tags=["新功能标签"]
)
def your_new_function():
    # 业务逻辑...
    return result
```

## 技术栈

项目使用的主要技术：

| 类别 | 技术 | 版本 |
|------|------|------|
| **AI框架** | LangChain | 0.2.14 |
| **AI框架** | CrewAI | 0.38.0 |
| **数据存储** | Chroma | 0.5.3 |
| **HTTP请求** | requests | 2.32.3 |
| **环境变量** | python-dotenv | 1.0.1 |

详细说明请参考：[docs/TECH_STACK.md](docs/TECH_STACK.md)

## 开发计划

- [x] 基础架构搭建
- [x] 核心功能开发
- [x] 审计日志系统
- [x] 数据分类存储
- [x] 装饰器自动记录
- [ ] 多模态交互（语音识别/合成）
- [ ] 高级功能开发
- [ ] 系统优化完善

## 文档目录

| 文档 | 路径 | 说明 |
|------|------|------|
| 技术栈说明 | [docs/TECH_STACK.md](docs/TECH_STACK.md) | 详细的技术选型和框架说明 |
| 装饰器指南 | [docs/DECORATOR_GUIDE.md](docs/DECORATOR_GUIDE.md) | 装饰器使用方法和示例 |

## 相关资源

- [LangChain文档](https://python.langchain.com/)
- [CrewAI文档](https://docs.crewai.com/)
- [Chroma文档](https://docs.trychroma.com/)
- [智谱AI开放平台](https://open.bigmodel.cn/)
