# 贾维斯AI助手 (JARVIS)

一个基于 LangChain + CrewAI 构建的全场景AI智能体系统，目标是实现类似《钢铁侠》中贾维斯的功能。

## 功能特性

- 🤖 **自然语言交互** - 支持文本输入输出，多轮对话
- 🔍 **智能搜索** - 集成网络搜索功能
- 🌤️ **天气查询** - 获取实时天气信息
- 🏠 **设备控制** - 模拟智能家居控制（空调、灯光、窗帘、音乐）
- 🧠 **记忆系统** - 基于Chroma的知识库存储
- 👥 **多智能体协作** - 指挥官、分析师、执行者、学习官分工协作

## 技术栈

- **框架**: LangChain + CrewAI
- **模型**: GLM-4.5-Flash
- **数据库**: Chroma (向量数据库)
- **工具**: Python 3.12+

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
jarvis/
├── __init__.py
├── agents/           # 智能体模块
│   ├── base_agent.py     # 基础智能体类
│   ├── commander.py      # 指挥官智能体
│   ├── analyst.py        # 分析师智能体
│   ├── executor.py       # 执行者智能体
│   └── learner.py        # 学习官智能体
├── tools/            # 工具模块
│   ├── search_tool.py    # 搜索工具
│   ├── weather_tool.py   # 天气工具
│   └── device_tool.py    # 设备控制工具
├── memory/           # 记忆模块
│   └── memory_manager.py # 记忆管理器
├── core/             # 核心模块
│   └── crew_manager.py   # 团队管理器
└── config/           # 配置模块
    └── settings.py       # 设置类
```

## 使用示例

```
您: 帮我查询北京今天的天气
🤖 贾维斯: 正在处理您的请求...
北京: 🌡️ 25°C ☀️ 晴天

您: 打开空调，温度调到24度
🤖 贾维斯: 正在处理您的请求...
已开启空调
空调温度已调节至 24°C

您: 退出
👋 再见！期待下次为您服务。
```

## 开发计划

- [x] 基础架构搭建
- [x] 核心功能开发
- [ ] 多模态交互（语音识别/合成）
- [ ] 高级功能开发
- [ ] 系统优化完善