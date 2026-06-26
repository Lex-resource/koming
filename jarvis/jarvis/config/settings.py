"""
贾维斯多智能体框架 - 配置层

所有可配置项集中管理，零硬编码。
优先级：环境变量 > 配置文件 > 默认值
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class LLMConfig:
    """LLM 调用配置"""
    model: str = "glm-4.5"
    temperature: float = 0.3
    max_tokens: int = 4096
    api_key: str = ""
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    timeout: float = 60.0
    stream: bool = False


@dataclass
class OrchestratorConfig:
    """决策智能体配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    max_rounds: int = 10
    enable_self_handle: bool = True
    enable_experience_reuse: bool = True
    enable_streaming: bool = False


@dataclass
class WorkerConfig:
    """子智能体配置"""
    llm: LLMConfig = field(default_factory=lambda: LLMConfig(model="glm-4.5-flash", temperature=0.2))
    timeout: float = 120.0
    max_retries: int = 2


@dataclass
class ReviewConfig:
    """审核配置"""
    enable_self_verify: bool = True
    enable_agent_review: bool = True
    max_review_rounds: int = 2
    reviewer_llm: LLMConfig = field(default_factory=lambda: LLMConfig(model="glm-4.5", temperature=0.1))


@dataclass
class MemoryConfig:
    """向量记忆配置"""
    provider: str = "chromadb"
    collection_name: str = "jarvis_experience"
    embedding_model: str = "embedding-3"
    embedding_dim: int = 1536
    embedding_api_key: str = ""
    embedding_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
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
    """设备控制配置"""
    provider: str = "mock"
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
    orchestrator: OrchestratorConfig = field(default_factory=OrchestratorConfig)
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    device: DeviceConfig = field(default_factory=DeviceConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
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

        # LLM 通用配置
        if env("LLM_API_KEY"):
            config.orchestrator.llm.api_key = env("LLM_API_KEY")
            config.worker.llm.api_key = env("LLM_API_KEY")
            config.review.reviewer_llm.api_key = env("LLM_API_KEY")
            config.memory.embedding_api_key = env("LLM_API_KEY")

        if env("LLM_BASE_URL"):
            config.orchestrator.llm.base_url = env("LLM_BASE_URL")
            config.worker.llm.base_url = env("LLM_BASE_URL")
            config.review.reviewer_llm.base_url = env("LLM_BASE_URL")
            config.memory.embedding_base_url = env("LLM_BASE_URL")

        # 决策智能体模型
        if env("ORCHESTRATOR_MODEL"):
            config.orchestrator.llm.model = env("ORCHESTRATOR_MODEL")
        if env("ORCHESTRATOR_MAX_ROUNDS"):
            config.orchestrator.max_rounds = int(env("ORCHESTRATOR_MAX_ROUNDS"))

        # 子智能体模型
        if env("WORKER_MODEL"):
            config.worker.llm.model = env("WORKER_MODEL")
        if env("WORKER_TIMEOUT"):
            config.worker.timeout = float(env("WORKER_TIMEOUT"))

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

                if isinstance(env_val, LLMConfig) and isinstance(default_val, LLMConfig):
                    for k in env_val.__dataclass_fields__:
                        env_k = getattr(env_val, k)
                        default_k = getattr(default_val, k)
                        if env_k != default_k:
                            setattr(file_section, key, env_val)
                            break
                else:
                    if env_val != default_val:
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
