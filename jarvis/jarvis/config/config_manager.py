"""
统一配置管理 - 使用Pydantic进行配置验证

这个模块提供了框架的统一配置管理，支持：
- 配置验证
- 配置继承
- 环境变量覆盖
- YAML/JSON配置文件
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class AgentConfigModel(BaseModel):
    """Agent配置模型"""
    name: str = Field(..., description="Agent名称")
    type: str = Field(default="custom", description="Agent类型")
    role: str = Field(..., description="Agent角色")
    goal: str = Field(..., description="Agent目标")
    backstory: str = Field(default="", description="Agent背景故事")
    tools: List[str] = Field(default_factory=list, description="工具列表")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=50, description="优先级")
    tags: List[str] = Field(default_factory=list, description="标签")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Agent名称不能为空")
        return v.strip()


class AsyncExecutorConfig(BaseModel):
    """异步执行器配置"""
    max_workers: int = Field(default=10, ge=1, le=100, description="最大工作线程数")
    default_timeout: float = Field(default=300.0, ge=1.0, description="默认超时时间（秒）")
    enable_retry: bool = Field(default=True, description="是否启用重试")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")
    cleanup_interval: int = Field(default=60, ge=10, description="清理间隔（秒）")


class MessageQueueConfig(BaseModel):
    """消息队列配置"""
    max_size: int = Field(default=10000, ge=100, description="队列最大大小")
    delivery_threads: int = Field(default=20, ge=1, le=100, description="投递线程数")
    max_message_store_size: int = Field(default=50000, ge=1000, description="消息存储最大大小")
    enable_dead_letter: bool = Field(default=True, description="是否启用死信队列")
    max_retries: int = Field(default=3, ge=1, le=10, description="最大重试次数")


class MetricsConfig(BaseModel):
    """指标配置"""
    enable: bool = Field(default=True, description="是否启用指标收集")
    server_host: str = Field(default="0.0.0.0", description="指标服务器主机")
    server_port: int = Field(default=8000, ge=1, le=65535, description="指标服务器端口")
    max_histogram_size: int = Field(default=10000, ge=100, description="直方图最大大小")


class StorageConfig(BaseModel):
    """存储配置"""
    data_dir: Path = Field(default=Path("./data"), description="数据目录")
    history_max_size: int = Field(default=1000, ge=100, description="历史记录最大条数")
    enable_persistence: bool = Field(default=True, description="是否启用持久化")


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="json", description="日志格式")
    file_path: Optional[Path] = Field(default=None, description="日志文件路径")
    max_file_size: int = Field(default=10485760, description="单个日志文件最大大小")
    backup_count: int = Field(default=5, description="备份文件数量")


class SecurityConfig(BaseModel):
    """安全配置"""
    api_key_required: bool = Field(default=True, description="是否需要API密钥")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"], description="允许的主机")
    rate_limit_enabled: bool = Field(default=False, description="是否启用速率限制")
    rate_limit_requests: int = Field(default=100, description="速率限制（请求/分钟）")


class FrameworkConfigModel(BaseModel):
    """框架主配置"""
    version: str = Field(default="3.0", description="配置版本")
    name: str = Field(default="JARVIS", description="框架名称")
    environment: str = Field(default="development", description="运行环境")
    
    agents: List[AgentConfigModel] = Field(default_factory=list, description="Agent配置列表")
    
    async_executor: AsyncExecutorConfig = Field(default_factory=AsyncExecutorConfig, description="异步执行器配置")
    message_queue: MessageQueueConfig = Field(default_factory=MessageQueueConfig, description="消息队列配置")
    metrics: MetricsConfig = Field(default_factory=MetricsConfig, description="指标配置")
    storage: StorageConfig = Field(default_factory=StorageConfig, description="存储配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="安全配置")
    
    plugins_dir: Path = Field(default=Path("./plugins"), description="插件目录")
    config_file: Optional[Path] = Field(default=None, description="配置文件路径")
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f"environment必须是以下之一: {allowed}")
        return v
    
    @field_validator('plugins_dir', 'storage')
    @classmethod
    def validate_paths(cls, v):
        if isinstance(v, Path):
            v.mkdir(parents=True, exist_ok=True)
        return v


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _lock = __import__('threading').Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self._config: Optional[FrameworkConfigModel] = None
            self._config_file: Optional[Path] = None
    
    def load_from_file(self, config_file: Union[str, Path]) -> FrameworkConfigModel:
        """从文件加载配置"""
        config_file = Path(config_file)
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        self._config_file = config_file
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._config = FrameworkConfigModel(**data)
        self._apply_env_overrides()
        
        return self._config
    
    def load_from_dict(self, data: Dict[str, Any]) -> FrameworkConfigModel:
        """从字典加载配置"""
        self._config = FrameworkConfigModel(**data)
        self._apply_env_overrides()
        return self._config
    
    def create_default(self) -> FrameworkConfigModel:
        """创建默认配置"""
        self._config = FrameworkConfigModel()
        self._apply_env_overrides()
        return self._config
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        if self._config is None:
            return
        
        env_mappings = {
            'JARVIS_ENV': ('environment', str),
            'JARVIS_MAX_WORKERS': ('async_executor.max_workers', int),
            'JARVIS_TIMEOUT': ('async_executor.default_timeout', float),
            'JARVIS_METRICS_PORT': ('metrics.server_port', int),
            'JARVIS_DATA_DIR': ('storage.data_dir', Path),
            'JARVIS_PLUGINS_DIR': ('plugins_dir', Path),
            'JARVIS_LOG_LEVEL': ('logging.level', str),
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value_type(value))
    
    def _set_nested_value(self, path: str, value: Any):
        """设置嵌套配置值"""
        parts = path.split('.')
        obj = self._config
        
        for part in parts[:-1]:
            obj = getattr(obj, part)
        
        setattr(obj, parts[-1], value)
    
    def get_config(self) -> FrameworkConfigModel:
        """获取当前配置"""
        if self._config is None:
            self._config = self.create_default()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> FrameworkConfigModel:
        """更新配置"""
        if self._config is None:
            return self.load_from_dict(updates)
        
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        return self._config
    
    def save_to_file(self, config_file: Optional[Union[str, Path]] = None) -> Path:
        """保存配置到文件"""
        if self._config is None:
            raise ValueError("没有可保存的配置")
        
        config_file = Path(config_file or self._config_file or "./config.json")
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config.model_dump(), f, indent=2, ensure_ascii=False, default=str)
        
        return config_file
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfigModel]:
        """获取特定Agent的配置"""
        if self._config is None:
            return None
        
        for agent in self._config.agents:
            if agent.name == agent_name:
                return agent
        
        return None
    
    def add_agent_config(self, agent_config: AgentConfigModel) -> None:
        """添加Agent配置"""
        if self._config is None:
            self._config = FrameworkConfigModel()
        
        existing = self.get_agent_config(agent_config.name)
        if existing:
            self._config.agents.remove(existing)
        
        self._config.agents.append(agent_config)
    
    def remove_agent_config(self, agent_name: str) -> bool:
        """移除Agent配置"""
        if self._config is None:
            return False
        
        agent = self.get_agent_config(agent_name)
        if agent:
            self._config.agents.remove(agent)
            return True
        
        return False


def load_config(config_file: Optional[str] = None) -> FrameworkConfigModel:
    """便捷函数：加载配置"""
    manager = ConfigManager()
    
    if config_file:
        return manager.load_from_file(config_file)
    elif os.getenv('JARVIS_CONFIG_FILE'):
        return manager.load_from_file(os.getenv('JARVIS_CONFIG_FILE'))
    else:
        return manager.create_default()


def get_config() -> FrameworkConfigModel:
    """便捷函数：获取当前配置"""
    return ConfigManager().get_config()


def save_config(config_file: Optional[str] = None) -> Path:
    """便捷函数：保存配置"""
    return ConfigManager().save_to_file(config_file)
