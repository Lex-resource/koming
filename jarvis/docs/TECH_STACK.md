# 技术栈文档

本文档详细记录贾维斯AI助手项目所使用的所有技术栈、框架、库和工具。

## 目录

- [核心技术栈](#核心技术栈)
- [AI框架](#ai框架)
- [数据存储](#数据存储)
- [开发工具](#开发工具)
- [Python版本要求](#python版本要求)
- [依赖管理](#依赖管理)

---

## 核心技术栈

### 1. AI模型与接口

| 技术 | 版本 | 用途 | 文档 |
|------|------|------|------|
| **GLM-4.5-Flash** | - | 主要语言模型 | [智谱AI](https://open.bigmodel.cn/) |
| **OpenAI API兼容** | 1.35.10 | 提供统一的AI调用接口 | [OpenAI](https://openai.com/) |

**说明**：项目使用智谱AI的GLM-4.5-Flash模型，该模型兼容OpenAI API格式，便于集成和切换。

---

## AI框架

### 1. LangChain

| 属性 | 值 |
|------|------|
| **版本** | 0.2.14 |
| **作用** | AI应用开发框架 |
| **用途** | 工具调用、提示词管理、链式调用 |
| **官网** | [langchain.com](https://langchain.com/) |

**核心功能**：
- 工具装饰器 `@tool`
- 提示词模板管理
- 链式调用（Chain）
- 代理（Agent）支持

**示例代码**：
```python
from langchain.tools import tool

class SearchTool:
    @tool("web_search")
    def web_search(query: str) -> str:
        """使用网络搜索获取信息"""
        ...
```

### 2. LangChain Community

| 属性 | 值 |
|------|------|
| **版本** | 0.2.12 |
| **作用** | LangChain扩展库 |
| **用途** | 第三方集成、社区工具 |

### 3. CrewAI

| 属性 | 值 |
|------|------|
| **版本** | 0.38.0 |
| **作用** | 多智能体协作框架 |
| **用途** | 角色化智能体编排、任务分工 |
| **官网** | [crewai.com](https://crewai.com/) |

**核心概念**：
- **Agent（智能体）**：具有特定角色和目标的AI实体
- **Task（任务）**：智能体需要完成的具体工作
- **Crew（团队）**：多个智能体组成的工作组
- **Process（流程）**：智能体协作的方式（顺序、层级等）

**项目中的智能体角色**：
| 角色 | 类名 | 职责 |
|------|------|------|
| 指挥官 | `CommanderAgent` | 接收指令、分配任务 |
| 分析师 | `AnalystAgent` | 分析问题、制定方案 |
| 执行者 | `ExecutorAgent` | 调用工具、执行操作 |
| 学习官 | `LearnerAgent` | 记录经验、更新知识库 |

**示例代码**：
```python
from crewai import Agent, Task, Crew

commander = Agent(
    role="指挥官",
    goal="理解用户意图，制定执行计划",
    backstory="你是贾维斯的指挥官"
)

crew = Crew(agents=[commander], tasks=[task])
result = crew.kickoff()
```

### 4. CrewAI Tools

| 属性 | 值 |
|------|------|
| **版本** | 0.2.14 |
| **作用** | CrewAI工具扩展库 |
| **用途** | 为智能体提供现成工具 |

---

## 数据存储

### 1. Chroma

| 属性 | 值 |
|------|------|
| **版本** | 0.5.3 |
| **作用** | 向量数据库 |
| **用途** | 知识库存储、语义搜索 |
| **官网** | [trychroma.com](https://trychroma.com/) |

**核心功能**：
- 向量嵌入存储
- 相似度搜索
- 元数据过滤
- 集合管理

**项目中的应用**：
- 记忆系统 (`jarvis/memory/memory_manager.py`)
- RAG（检索增强生成）支持
- 长期知识存储

**示例代码**：
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("knowledge")
collection.add(
    embeddings=[[1.0, 2.0, 3.0]],
    documents=["知识内容"],
    ids=["id1"]
)
```

---

## 开发工具

### 1. Python环境

| 项目 | 版本/要求 |
|------|----------|
| **Python** | 3.12+ |
| **包管理** | pip |

### 2. 环境变量管理

| 库 | 版本 | 用途 |
|----|------|------|
| **python-dotenv** | 1.0.1 | 管理环境变量，读取 `.env` 文件 |

**使用方式**：
```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GLM_API_KEY")
```

### 3. HTTP请求

| 库 | 版本 | 用途 |
|----|------|------|
| **requests** | 2.32.3 | 发送HTTP请求，调用外部API |

**示例代码**：
```python
import requests

response = requests.post(url, headers=headers, json=data, timeout=30)
response.raise_for_status()
result = response.json()
```

### 4. HTML解析

| 库 | 版本 | 用途 |
|----|------|------|
| **beautifulsoup4** | 4.12.3 | 解析HTML网页内容 |

**项目用途**：网络搜索结果解析

**示例代码**：
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, 'html.parser')
results = soup.find_all('div', class_='result')
```

### 5. 音频处理（预留）

| 库 | 版本 | 用途 |
|----|------|------|
| **pydub** | 0.25.1 | 音频处理，支持语音合成/识别 |

**未来用途**：
- 语音转文本（STT）
- 文本转语音（TTS）

---

## Python版本要求

```
Python >= 3.12
```

**推荐配置**：
```bash
# 使用 pyenv 管理Python版本
pyenv install 3.12.0
pyenv local 3.12.0

# 或使用 conda
conda create -n jarvis python=3.12
conda activate jarvis
```

---

## 依赖管理

### 安装依赖

```bash
# 克隆项目
git clone <project_url>
cd jarvis

# 安装依赖
pip install -r requirements.txt
```

### requirements.txt 内容

```
# 核心框架
langchain==0.2.14
langchain-community==0.2.12
crewai==0.38.0
crewai-tools==0.2.14

# 模型支持
openai==1.35.10

# 多模态
pydub==0.25.1

# 工具
python-dotenv==1.0.1
requests==2.32.3
beautifulsoup4==4.12.3

# 记忆与存储
chromadb==0.5.3
```

---

## 项目架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      贾维斯AI助手                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  用户界面    │  │  语音模块    │  │  API接口     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌──────────────────────────────────────────────────┐      │
│  │                 LangChain（核心框架）               │      │
│  │  • 工具调用 • 提示词管理 • 链式调用               │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────┐      │
│  │                 CrewAI（多智能体）                  │      │
│  │  • 指挥官 • 分析师 • 执行者 • 学习官              │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                 │
│         ┌────────────────┼────────────────┐                │
│         ▼                ▼                ▼                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐          │
│  │ Chroma     │  │ requests   │  │ 业务逻辑    │          │
│  │ (向量存储) │  │ (HTTP请求) │  │            │          │
│  └────────────┘  └────────────┘  └────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 未来扩展技术栈

### 计划中的技术

| 技术 | 用途 | 状态 |
|------|------|------|
| **FastAPI** | Web API服务 | 计划中 |
| **Streamlit/Gradio** | Web UI界面 | 计划中 |
| **Redis** | 缓存和会话管理 | 计划中 |
| **PostgreSQL** | 关系型数据存储 | 计划中 |
| **LangServe** | 模型部署服务 | 计划中 |
| **RAG Framework** | 高级检索增强 | 计划中 |

### 可选的AI模型

| 模型 | 提供商 | 特点 |
|------|--------|------|
| GPT-4 | OpenAI | 最强推理能力 |
| Claude | Anthropic | 长文本处理 |
| Llama | Meta | 开源可本地部署 |
| Gemini | Google | 多模态原生支持 |

---

## 技术选型理由

### 为什么选择 LangChain + CrewAI？

| 维度 | LangChain | CrewAI |
|------|-----------|--------|
| **市场占有率** | 30%（第一） | 20%（第三） |
| **学习曲线** | 中等 | 较低 |
| **生态成熟度** | 高 | 快速增长 |
| **多智能体支持** | 一般 | 优秀 |
| **工具集成** | 丰富 | 适中 |

**结论**：LangChain提供强大的基础能力（工具调用、提示词管理），CrewAI提供优秀的多智能体协作体验，两者结合是最佳选择。

### 为什么选择 Chroma？

| 维度 | Chroma | 其他方案 |
|------|--------|----------|
| **易用性** | ⭐⭐⭐⭐⭐ | 参差不齐 |
| **部署复杂度** | ⭐⭐⭐⭐⭐ | 有些较复杂 |
| **功能完整性** | ⭐⭐⭐⭐ | 基本够用 |
| **社区活跃度** | ⭐⭐⭐⭐ | 持续增长 |

**结论**：Chroma是最简单的向量数据库解决方案，适合快速开发和原型验证。

---

## 相关资源

### 官方文档

- [LangChain文档](https://python.langchain.com/)
- [CrewAI文档](https://docs.crewai.com/)
- [Chroma文档](https://docs.trychroma.com/)
- [智谱AI开放平台](https://open.bigmodel.cn/)

### 学习资源

- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [Chroma GitHub](https://github.com/chroma-core/chroma)

---

## 版本历史

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2024-XX-XX | 1.0.0 | 初始版本，基础框架搭建 |
| - | - | - LangChain + CrewAI 集成 |
| - | - | - 多智能体协作系统 |
| - | - | - 审计日志和数据存储系统 |
| - | - | - 装饰器自动记录功能 |

---

*本文档最后更新：2024年*
