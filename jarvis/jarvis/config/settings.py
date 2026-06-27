"""
贾维斯多智能体框架 - 配置层

所有可配置项集中管理，零硬编码。
优先级：环境变量 > 配置文件 > 默认值
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List


@dataclass
class ModelConfig:
    """单个模型配置 - 每个模型独立配置厂商、认证、参数"""
    name: str = "glm-4.5"
    provider: str = "openai_compatible"
    model: str = "glm-4.5"
    api_key: str = ""
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    api_version: str = ""
    region: str = ""
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: float = 60.0
    stream: bool = False
    extra_headers: Dict[str, str] = field(default_factory=dict)
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """LLM 配置 - 多厂商多模型池，每个模型独立配置认证"""
    models: Dict[str, ModelConfig] = field(default_factory=lambda: {
        "glm-4.5": ModelConfig(
            name="glm-4.5",
            provider="openai_compatible",
            model="glm-4.5",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            temperature=0.3,
        ),
        "glm-4.5-flash": ModelConfig(
            name="glm-4.5-flash",
            provider="openai_compatible",
            model="glm-4.5-flash",
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            temperature=0.2,
        ),
    })
    default_model: str = "glm-4.5-flash"
    embedding_model: str = "embedding-3"
    embedding_api_key: str = ""
    embedding_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"

    def get_model(self, name: str = None) -> ModelConfig:
        """按名获取模型配置，None 用默认"""
        key = name or self.default_model
        if key not in self.models:
            raise ValueError(f"模型 '{key}' 未配置，可用: {list(self.models.keys())}")
        return self.models[key]

    def add_model(self, config: ModelConfig) -> None:
        """动态添加模型"""
        self.models[config.name] = config

    def list_models(self) -> List[str]:
        return list(self.models.keys())


@dataclass
class OrchestratorConfig:
    """决策智能体配置"""
    model: str = "glm-4.5"
    max_rounds: int = 10
    enable_self_handle: bool = True
    enable_experience_reuse: bool = True
    enable_streaming: bool = False


@dataclass
class WorkerConfig:
    """子智能体配置"""
    default_model: str = "glm-4.5-flash"
    timeout: float = 120.0
    max_retries: int = 2


@dataclass
class ReviewConfig:
    """审核配置"""
    enable_self_verify: bool = True
    enable_agent_review: bool = True
    max_review_rounds: int = 2
    reviewer_model: str = "glm-4.5"


@dataclass
class MemoryConfig:
    """向量记忆配置"""
    provider: str = "chromadb"
    collection_name: str = "jarvis_experience"
    embedding_model: str = "embedding-3"
    embedding_dim: int = 1536
    top_k: int = 3
    persist_path: str = "./data/vector_store"


@dataclass
class CacheConfig:
    """缓存配置"""
    provider: str = "memory"
    ttl: int = 3600
    maxsize: int = 1000
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""


@dataclass
class DatabaseConfig:
    """数据库配置"""
    provider: str = "sqlite"
    url: str = "sqlite:///./data/jarvis.db"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class DeviceConfig:
    """设备控制配置 - 默认不接入，等真实 MCP 实现"""
    provider: str = ""  # 空=未接入 / "mcp"=MCP真实设备
    mcp_server_url: str = ""
    mcp_timeout: float = 10.0


@dataclass
class SearchConfig:
    """搜索配置"""
    provider: str = "playwright"
    max_results: int = 5
    timeout: float = 30.0
    browser_headless: bool = True
    default_engine: str = "baidu"


@dataclass
class VoiceConfig:
    """语音配置 - ASR 语音识别 + TTS 语音合成"""
    provider: str = "mock"  # mock / glm / 自定义
    api_key: str = ""
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    asr_model: str = "whisper-1"
    tts_model: str = "cogtts"
    default_voice: str = "female-tianmei"
    default_language: str = "zh"
    available_voices: List[str] = field(default_factory=lambda: [
        "female-tianmei", "female-yongjie", "female-chengshu",
        "male-qn-qingshu", "male-qn-jingying",
    ])


@dataclass
class MultimodalConfig:
    """多模态配置 - 图片/视频理解"""
    # 默认用于多模态理解的模型（需支持视觉/视频输入，如 glm-4.5、glm-4v）
    default_vision_model: str = "glm-4.5"
    # 默认用于视频理解的模型（需显式支持 video 输入）
    default_video_model: str = "glm-4.5"
    # 单次最大图片数
    max_images: int = 10
    # 单次最大视频数
    max_videos: int = 1
    # 默认温度
    temperature: float = 0.3


@dataclass
class StorageConfig:
    """文件存储配置"""
    session_dir: str = "./sessions"
    file_format: str = "md"
    artifacts_dir_name: str = "artifacts"
    blackboard_filename: str = "blackboard.md"
    orchestrator_filename: str = "orchestrator.md"


@dataclass
class ExperienceConfig:
    """经验复用配置"""
    memory_top_k: int = 3
    skill_match_threshold: float = 0.7
    auto_archive_skill: bool = True
    skills_file: str = "./data/skills.json"
    profiles_file: str = "./data/profiles.json"


@dataclass
class BlackboardConfig:
    """黑板配置"""
    auto_flush: bool = True
    max_history_entries: int = 100


@dataclass
class Config:
    """全局配置 - 所有配置的根"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    device: DeviceConfig = field(default_factory=DeviceConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    multimodal: MultimodalConfig = field(default_factory=MultimodalConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    experience: ExperienceConfig = field(default_factory=ExperienceConfig)
    blackboard: BlackboardConfig = field(default_factory=BlackboardConfig)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        config = cls()
        for section_name, section_data in data.items():
            if not hasattr(config, section_name):
                continue
            section = getattr(config, section_name)
            for key, value in section_data.items():
                if hasattr(section, key):
                    if isinstance(value, dict) and hasattr(section, key):
                        sub = getattr(section, key)
                        if isinstance(sub, LLMConfig):
                            for k, v in value.items():
                                if hasattr(sub, k):
                                    setattr(sub, k, v)
                    else:
                        setattr(section, key, value)
        return config

    @classmethod
    def from_file(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量加载配置，覆盖默认值"""
        config = cls()

        def env(key: str, default=None):
            val = os.getenv(key)
            return val if val is not None else default

        # 通用密钥（向后兼容）：只应用到未单独配置的模型
        common_key = env("LLM_API_KEY")
        common_url = env("LLM_BASE_URL")

        # 按模型名独立配置：MODEL_<NAME>_API_KEY / MODEL_<NAME>_BASE_URL
        for model_name, model_cfg in config.llm.models.items():
            env_prefix = f"MODEL_{model_name.upper().replace('.', '_').replace('-', '_')}"

            specific_key = env(f"{env_prefix}_API_KEY")
            if specific_key:
                model_cfg.api_key = specific_key
            elif common_key:
                model_cfg.api_key = common_key

            specific_url = env(f"{env_prefix}_BASE_URL")
            if specific_url:
                model_cfg.base_url = specific_url
            elif common_url:
                model_cfg.base_url = common_url

            specific_provider = env(f"{env_prefix}_PROVIDER")
            if specific_provider:
                model_cfg.provider = specific_provider

            specific_model_id = env(f"{env_prefix}_MODEL")
            if specific_model_id:
                model_cfg.model = specific_model_id

            specific_temp = env(f"{env_prefix}_TEMPERATURE")
            if specific_temp:
                model_cfg.temperature = float(specific_temp)

        # Embedding 配置
        embedding_key = env("EMBEDDING_API_KEY")
        if embedding_key:
            config.llm.embedding_api_key = embedding_key
        elif common_key:
            config.llm.embedding_api_key = common_key

        embedding_url = env("EMBEDDING_BASE_URL")
        if embedding_url:
            config.llm.embedding_base_url = embedding_url
        elif common_url:
            config.llm.embedding_base_url = common_url

        if env("EMBEDDING_MODEL"):
            config.llm.embedding_model = env("EMBEDDING_MODEL")

        # 默认模型
        if env("LLM_DEFAULT_MODEL"):
            config.llm.default_model = env("LLM_DEFAULT_MODEL")

        # 决策智能体模型
        if env("ORCHESTRATOR_MODEL"):
            config.orchestrator.model = env("ORCHESTRATOR_MODEL")
        if env("ORCHESTRATOR_MAX_ROUNDS"):
            config.orchestrator.max_rounds = int(env("ORCHESTRATOR_MAX_ROUNDS"))

        # 子智能体默认模型
        if env("WORKER_MODEL"):
            config.worker.default_model = env("WORKER_MODEL")
        if env("WORKER_TIMEOUT"):
            config.worker.timeout = float(env("WORKER_TIMEOUT"))

        # 审核模型
        if env("REVIEWER_MODEL"):
            config.review.reviewer_model = env("REVIEWER_MODEL")

        # 记忆配置
        if env("MEMORY_PROVIDER"):
            config.memory.provider = env("MEMORY_PROVIDER")
        if env("MEMORY_PERSIST_PATH"):
            config.memory.persist_path = env("MEMORY_PERSIST_PATH")

        # 缓存配置
        if env("CACHE_PROVIDER"):
            config.cache.provider = env("CACHE_PROVIDER")
        if env("REDIS_HOST"):
            config.cache.redis_host = env("REDIS_HOST")

        # 数据库配置
        if env("DATABASE_URL"):
            config.database.url = env("DATABASE_URL")
        if env("DATABASE_PROVIDER"):
            config.database.provider = env("DATABASE_PROVIDER")

        # 设备配置
        if env("DEVICE_PROVIDER"):
            config.device.provider = env("DEVICE_PROVIDER")
        if env("MCP_SERVER_URL"):
            config.device.mcp_server_url = env("MCP_SERVER_URL")

        # 语音配置 - 优先用通用 LLM 密钥作后备
        if env("VOICE_PROVIDER"):
            config.voice.provider = env("VOICE_PROVIDER")
        if env("VOICE_API_KEY"):
            config.voice.api_key = env("VOICE_API_KEY")
        elif common_key:
            config.voice.api_key = common_key
        if env("VOICE_BASE_URL"):
            config.voice.base_url = env("VOICE_BASE_URL")
        elif common_url:
            config.voice.base_url = common_url
        if env("ASR_MODEL"):
            config.voice.asr_model = env("ASR_MODEL")
        if env("TTS_MODEL"):
            config.voice.tts_model = env("TTS_MODEL")
        if env("TTS_DEFAULT_VOICE"):
            config.voice.default_voice = env("TTS_DEFAULT_VOICE")

        # 多模态配置
        if env("VISION_MODEL"):
            config.multimodal.default_vision_model = env("VISION_MODEL")
        if env("VIDEO_MODEL"):
            config.multimodal.default_video_model = env("VIDEO_MODEL")
        if env("MAX_IMAGES"):
            config.multimodal.max_images = int(env("MAX_IMAGES"))
        if env("MAX_VIDEOS"):
            config.multimodal.max_videos = int(env("MAX_VIDEOS"))

        # 存储配置
        if env("SESSION_DIR"):
            config.storage.session_dir = env("SESSION_DIR")

        return config

    @classmethod
    def load(cls, config_file: Optional[str] = None) -> "Config":
        """加载配置：配置文件先打底，环境变量再覆盖"""
        if config_file and os.path.exists(config_file):
            config = cls.from_file(config_file)
        else:
            config = cls()

        defaults = cls()
        env_config = cls.from_env()

        for section_name in config.to_dict().keys():
            env_section = getattr(env_config, section_name)
            file_section = getattr(config, section_name)
            default_section = getattr(defaults, section_name)

            for key in env_section.__dataclass_fields__:
                env_val = getattr(env_section, key)
                default_val = getattr(default_section, key)

                # LLMConfig 含多厂商模型池，逐模型合并
                if isinstance(env_val, LLMConfig) and isinstance(default_val, LLMConfig):
                    if env_val.default_model != default_val.default_model:
                        file_section.default_model = env_val.default_model
                    if env_val.embedding_model != default_val.embedding_model:
                        file_section.embedding_model = env_val.embedding_model
                    if env_val.embedding_api_key != default_val.embedding_api_key:
                        file_section.embedding_api_key = env_val.embedding_api_key
                    if env_val.embedding_base_url != default_val.embedding_base_url:
                        file_section.embedding_base_url = env_val.embedding_base_url
                    for model_name, env_model in env_val.models.items():
                        default_model = default_val.models.get(model_name)
                        if default_model and env_model != default_model:
                            file_section.models[model_name] = env_model
                elif env_val != default_val:
                    setattr(file_section, key, env_val)

        return config


_global_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置单例"""
    global _global_config
    if _global_config is None:
        _global_config = Config.load(
            os.getenv("JARVIS_CONFIG_FILE")
        )
    return _global_config


def init_config(config_file: Optional[str] = None) -> Config:
    """初始化全局配置"""
    global _global_config
    _global_config = Config.load(config_file)
    return _global_config
