"""
贾维斯多智能体框架 - 依赖注入组装

把所有实现注入到抽象接口，构成可运行的应用。
换任何实现（数据库/缓存/设备/搜索/记忆/LLM）只改这里。
"""

from typing import Dict, Optional

from jarvis.config.settings import Config, get_config, init_config
from jarvis.core.interfaces import ICache, IDatabase, IDevice, ILLM, IMemory, ISearch, ISpeech, IStorage
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
        self._register_multimodal_tools()
        self._register_voice_tools()
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

        # 记忆 - 默认优先用 ChromaDB 真实向量检索，不可用降级到关键词匹配
        if self.config.memory.provider == "chromadb":
            try:
                from jarvis.providers.chroma_memory import ChromaMemory
                self.memory: IMemory = ChromaMemory(self.config.memory, self.llm)
            except ImportError:
                # chromadb 未安装，降级到关键词匹配
                from jarvis.providers.memory_vector import InMemoryVectorStore
                self.memory: IMemory = InMemoryVectorStore()
            except Exception as e:
                # chromadb 初始化失败（如 embedding 配置缺失），也降级
                print(f"[警告] ChromaDB 初始化失败，降级到关键词匹配: {e}")
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

        # 设备 - 只留接口，不实现模拟，等真实 MCP 接入
        if self.config.device.provider == "mcp":
            from jarvis.providers.mcp_device import MCPDevice  # 预留
            self.device: Optional[IDevice] = MCPDevice(self.config.device)
        else:
            self.device: Optional[IDevice] = None

        # 搜索
        if self.config.search.provider == "playwright":
            try:
                from jarvis.providers.playwright_search import PlaywrightSearch
                self.search: ISearch = PlaywrightSearch(self.config.search)
            except ImportError:
                self.search = None
        else:
            self.search = None

        # 语音
        if self.config.voice.provider == "glm":
            from jarvis.providers.glm_speech import GLMSpeechProvider
            self.speech: Optional[ISpeech] = GLMSpeechProvider(
                api_key=self.config.voice.api_key,
                base_url=self.config.voice.base_url,
                asr_model=self.config.voice.asr_model,
                tts_model=self.config.voice.tts_model,
                default_voice=self.config.voice.default_voice,
                available_voices=self.config.voice.available_voices,
            )
        elif self.config.voice.provider == "mock":
            from jarvis.providers.glm_speech import MockSpeechProvider
            self.speech: Optional[ISpeech] = MockSpeechProvider()
        else:
            self.speech: Optional[ISpeech] = None

    def _init_db(self) -> None:
        """初始化数据库表"""
        self.database.init_db()

    def _register_default_tools(self) -> None:
        """注册默认工具集（封装子系统为 LLM 可调用工具）"""
        # 设备控制 - 仅在设备已接入时注册
        if self.device is not None:
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

    def _register_multimodal_tools(self) -> None:
        """注册多模态工具 - 让智能体能看图/看视频"""
        mm_cfg = self.config.multimodal

        def understand_image(prompt: str, images: list, model: str = None) -> str:
            """图片理解工具 - 供 LLM function calling"""
            images = images[:mm_cfg.max_images]
            model = model or mm_cfg.default_vision_model
            try:
                resp = self.llm.chat_multimodal(
                    model=model, prompt=prompt, images=images,
                    temperature=mm_cfg.temperature,
                )
                return resp.content
            except Exception as e:
                return f"图片理解失败: {e}"

        def understand_video(prompt: str, videos: list, model: str = None) -> str:
            """视频理解工具 - 供 LLM function calling（需模型支持视频输入）"""
            videos = videos[:mm_cfg.max_videos]
            model = model or mm_cfg.default_video_model
            try:
                resp = self.llm.chat_multimodal(
                    model=model, prompt=prompt, videos=videos,
                    temperature=mm_cfg.temperature,
                )
                return resp.content
            except Exception as e:
                return f"视频理解失败: {e}"

        self.register_tool(ToolDefinition(
            name="understand_image",
            description="理解图片内容。images 是图片 URL 或 base64 列表，prompt 是想问的问题。",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "针对图片的问题"},
                    "images": {"type": "array", "items": {"type": "string"}, "description": "图片 URL 或 base64"},
                    "model": {"type": "string", "description": "可选，指定视觉模型"},
                },
                "required": ["prompt", "images"],
            },
            handler=understand_image,
        ))
        self.register_tool(ToolDefinition(
            name="understand_video",
            description="理解视频内容。videos 是视频 URL 或 base64 列表，prompt 是想问的问题。",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "针对视频的问题"},
                    "videos": {"type": "array", "items": {"type": "string"}, "description": "视频 URL 或 base64"},
                    "model": {"type": "string", "description": "可选，指定视频模型"},
                },
                "required": ["prompt", "videos"],
            },
            handler=understand_video,
        ))

    def _register_voice_tools(self) -> None:
        """注册语音工具 - 让智能体能听会说"""
        if self.speech is None:
            return

        def transcribe_audio(audio_path: str, language: str = "zh") -> str:
            """语音转文字工具"""
            try:
                return self.speech.asr(audio_path, language=language)
            except Exception as e:
                return f"语音识别失败: {e}"

        def synthesize_speech(text: str, voice: str = "default", output_path: str = None) -> str:
            """文字转语音工具，返回音频文件路径"""
            try:
                return self.speech.tts(text, voice=voice, output_path=output_path)
            except Exception as e:
                return f"语音合成失败: {e}"

        self.register_tool(ToolDefinition(
            name="transcribe_audio",
            description="语音转文字。audio_path 是音频文件路径或 URL。",
            parameters={
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string", "description": "音频文件路径或 URL"},
                    "language": {"type": "string", "description": "语言代码 zh/en/ja", "default": "zh"},
                },
                "required": ["audio_path"],
            },
            handler=transcribe_audio,
        ))
        self.register_tool(ToolDefinition(
            name="synthesize_speech",
            description="文字转语音，返回生成的音频文件路径。",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要合成的文本"},
                    "voice": {"type": "string", "description": "音色 ID，default 用默认音色"},
                    "output_path": {"type": "string", "description": "可选，指定输出文件路径"},
                },
                "required": ["text"],
            },
            handler=synthesize_speech,
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

    def register_speech(self, speech: ISpeech) -> None:
        """替换语音实现"""
        self.speech = speech

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

    def chat_with_images(self, prompt: str, images: list, model: str = None) -> str:
        """多模态入口：图片+文本 → 直接调多模态 LLM，模型原生看图"""
        mm_cfg = self.config.multimodal
        images = images[:mm_cfg.max_images]
        model = model or mm_cfg.default_vision_model
        resp = self.llm.chat_multimodal(
            model=model, prompt=prompt, images=images,
            temperature=mm_cfg.temperature,
        )
        return resp.content

    def chat_with_videos(self, prompt: str, videos: list, model: str = None) -> str:
        """多模态入口：视频+文本 → 直接调多模态 LLM，模型原生看视频"""
        mm_cfg = self.config.multimodal
        videos = videos[:mm_cfg.max_videos]
        model = model or mm_cfg.default_video_model
        resp = self.llm.chat_multimodal(
            model=model, prompt=prompt, videos=videos,
            temperature=mm_cfg.temperature,
        )
        return resp.content

    def chat_with_voice(self, audio_path: str, language: str = "zh") -> str:
        """语音入口：音频 → ASR → 决策智能体处理（不自动 TTS 回读）"""
        if self.speech is None:
            raise RuntimeError("未配置语音模块（config.voice.provider）")
        text = self.speech.asr(audio_path, language=language)
        return self.chat(text)

    def speak(self, text: str, voice: str = "default", output_path: str = None) -> str:
        """语音合成 - 把任意文本转成音频文件"""
        if self.speech is None:
            raise RuntimeError("未配置语音模块（config.voice.provider）")
        return self.speech.tts(text, voice=voice, output_path=output_path)

    def shutdown(self) -> None:
        """清理资源"""
        if self.search is not None:
            try:
                self.search.close()
            except Exception:
                pass
        if self.speech is not None:
            try:
                self.speech.close()
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
