"""
贾维斯多智能体框架 - 依赖注入组装

把所有实现注入到抽象接口，构成可运行的应用。
换任何实现（数据库/缓存/设备/搜索/记忆/LLM）只改这里。
"""

from typing import Dict, Optional

from jarvis.config.settings import Config, get_config, init_config
from jarvis.core.interfaces import ICache, IDatabase, IDevice, ILLM, IMemory, ISearch, IStorage
from jarvis.core.models import ToolDefinition
from jarvis.core.experience_store import ExperienceStore
from jarvis.agents.decision_agent import DecisionAgent


class Application:
    """应用容器 - 依赖注入组装 + 工具注册"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self._build_instances()
        self._init_db()
        self._tool_registry: Dict[str, ToolDefinition] = {}
        self._register_default_tools()
        self._decision_agent: Optional[DecisionAgent] = None

    def _build_instances(self) -> None:
        """根据 config.provider 选择实现，组装到接口"""
        # LLM
        if self.config.llm.models:
            from jarvis.providers.multi_provider_llm import MultiProviderLLM
            self.llm: ILLM = MultiProviderLLM(self.config.llm)
        else:
            raise RuntimeError("未配置任何 LLM 模型")

        # 存储
        from jarvis.providers.file_storage import FileStorage
        self.storage: IStorage = FileStorage(self.config.storage)

        # 缓存
        if self.config.cache.provider == "redis":
            from jarvis.providers.redis_cache import RedisCache  # 预留
            self.cache: ICache = RedisCache(self.config.cache)
        else:
            from jarvis.providers.memory_cache import MemoryCache
            self.cache: ICache = MemoryCache(self.config.cache)

        # 记忆
        if self.config.memory.provider == "chromadb":
            try:
                from jarvis.providers.chroma_memory import ChromaMemory  # 预留
                self.memory: IMemory = ChromaMemory(self.config.memory, self.llm)
            except ImportError:
                from jarvis.providers.memory_vector import InMemoryVectorStore
                self.memory: IMemory = InMemoryVectorStore()
        else:
            from jarvis.providers.memory_vector import InMemoryVectorStore
            self.memory: IMemory = InMemoryVectorStore()

        # 数据库
        if self.config.database.provider == "sqlite":
            from jarvis.providers.sqlite_database import SQLiteDatabase
            self.database: IDatabase = SQLiteDatabase(self.config.database)
        else:
            from jarvis.providers.sqlite_database import SQLiteDatabase
            self.database: IDatabase = SQLiteDatabase(self.config.database)

        # 设备
        if self.config.device.provider == "mcp":
            from jarvis.providers.mcp_device import MCPDevice  # 预留
            self.device: IDevice = MCPDevice(self.config.device)
        else:
            from jarvis.providers.mock_device import MockDevice
            self.device: IDevice = MockDevice()

        # 搜索
        if self.config.search.provider == "playwright":
            try:
                from jarvis.providers.playwright_search import PlaywrightSearch
                self.search: ISearch = PlaywrightSearch(self.config.search)
            except ImportError:
                self.search = None
        else:
            self.search = None

    def _init_db(self) -> None:
        """初始化数据库表"""
        self.database.init_db()

    def _register_default_tools(self) -> None:
        """注册默认工具集（封装子系统为 LLM 可调用工具）"""
        # 设备控制
        self.register_tool(ToolDefinition(
            name="control_device",
            description="控制设备。command: turn_on/turn_off/set_property/get_status",
            parameters={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "设备 ID"},
                    "command": {"type": "string", "enum": ["turn_on", "turn_off", "set_property", "get_status"]},
                    "property": {"type": "string", "description": "属性名（set_property 时必填）"},
                    "value": {"description": "属性值（set_property 时必填）"},
                },
                "required": ["device_id", "command"],
            },
            handler=self.device.control,
        ))
        self.register_tool(ToolDefinition(
            name="get_device_status",
            description="查询设备当前状态",
            parameters={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]},
            handler=self.device.get_status,
        ))
        self.register_tool(ToolDefinition(
            name="list_devices",
            description="列出所有可用设备",
            parameters={"type": "object", "properties": {}},
            handler=self.device.list_devices,
        ))
        self.register_tool(ToolDefinition(
            name="execute_scene",
            description="执行场景模式（如：回家/离家/睡眠/观影）",
            parameters={"type": "object", "properties": {"scene_name": {"type": "string"}}, "required": ["scene_name"]},
            handler=self.device.execute_scene,
        ))
        self.register_tool(ToolDefinition(
            name="list_scenes",
            description="列出所有可用场景",
            parameters={"type": "object", "properties": {}},
            handler=self.device.list_scenes,
        ))

        # 搜索
        if self.search is not None:
            self.register_tool(ToolDefinition(
                name="web_search",
                description="网页搜索，返回 [{title, url, snippet}]",
                parameters={"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]},
                handler=self.search.search,
            ))
            self.register_tool(ToolDefinition(
                name="scrape_page",
                description="抓取网页内容",
                parameters={"type": "object", "properties": {"url": {"type": "string"}, "selector": {"type": "string"}}, "required": ["url"]},
                handler=self.search.scrape,
            ))

    # ============ 公共 API ============

    def register_tool(self, tool: ToolDefinition) -> None:
        """注册自定义工具"""
        self._tool_registry[tool.name] = tool

    def register_llm_adapter(self, provider: str, adapter) -> None:
        """注册新的 LLM 厂商适配器"""
        from jarvis.providers.multi_provider_llm import MultiProviderLLM
        if isinstance(self.llm, MultiProviderLLM):
            self.llm.register_adapter(provider, adapter)

    def register_device(self, device: IDevice) -> None:
        """替换设备实现"""
        self.device = device

    def register_search(self, search: ISearch) -> None:
        """替换搜索实现"""
        self.search = search

    def get_decision_agent(self) -> DecisionAgent:
        """获取决策智能体（单例）"""
        if self._decision_agent is None:
            experience_store = ExperienceStore(
                memory=self.memory,
                database=self.database,
                config=self.config.experience,
            )
            self._decision_agent = DecisionAgent(
                llm=self.llm,
                storage=self.storage,
                experience_store=experience_store,
                config=self.config,
                cache=self.cache,
                tool_registry=self._tool_registry,
            )
        return self._decision_agent

    def chat(self, user_input: str) -> str:
        """主入口：处理用户输入"""
        return self.get_decision_agent().execute(user_input)

    def shutdown(self) -> None:
        """清理资源"""
        if self.search is not None:
            try:
                self.search.close()
            except Exception:
                pass


_global_app: Optional[Application] = None


def get_app(config_file: Optional[str] = None) -> Application:
    """获取全局应用单例"""
    global _global_app
    if _global_app is None:
        init_config(config_file)
        _global_app = Application()
    return _global_app
