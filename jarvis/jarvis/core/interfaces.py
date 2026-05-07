"""
接口抽象层 - 定义核心接口契约

这个模块定义了框架的核心接口，用于解耦具体实现，提高可扩展性。
所有具体实现都应该实现这些接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class AgentRegistryInterface(ABC):
    """Agent注册中心接口"""
    
    @abstractmethod
    def register(self, name: str, agent_class: Type, metadata: Any = None) -> None:
        """注册Agent"""
        pass
    
    @abstractmethod
    def unregister(self, name: str) -> bool:
        """注销Agent"""
        pass
    
    @abstractmethod
    def get(self, name: str) -> Optional[Type]:
        """获取Agent类"""
        pass
    
    @abstractmethod
    def list_agents(self) -> List[str]:
        """列出所有Agent名称"""
        pass
    
    @abstractmethod
    def get_enabled_agents(self) -> Dict[str, Type]:
        """获取所有启用的Agent"""
        pass
    
    @abstractmethod
    def create_agent(self, name: str, **kwargs) -> Optional[Any]:
        """创建Agent实例"""
        pass


class TaskExecutorInterface(ABC):
    """任务执行器接口"""
    
    @abstractmethod
    def start(self) -> None:
        """启动执行器"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止执行器"""
        pass
    
    @abstractmethod
    def create_task(
        self,
        task_type: str,
        description: str,
        func: Callable,
        kwargs: Dict[str, Any] = None,
        priority: Any = None,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None
    ) -> str:
        """创建任务"""
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Any]:
        """获取任务"""
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        pass


class MessageBusInterface(ABC):
    """消息总线接口"""
    
    @abstractmethod
    def start(self) -> None:
        """启动消息总线"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止消息总线"""
        pass
    
    @abstractmethod
    def publish(
        self,
        topic: str,
        payload: Any,
        priority: Any = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """发布消息"""
        pass
    
    @abstractmethod
    def subscribe(
        self,
        topic: str,
        callback: Callable,
        filter_func: Optional[Callable] = None
    ) -> str:
        """订阅主题"""
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        pass


class MetricsCollectorInterface(ABC):
    """指标收集器接口"""
    
    @abstractmethod
    def counter_inc(self, name: str, value: float = 1.0, labels: Dict[str, str] = None) -> None:
        """增加计数器"""
        pass
    
    @abstractmethod
    def gauge_set(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """设置仪表值"""
        pass
    
    @abstractmethod
    def histogram_observe(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """记录直方图值"""
        pass
    
    @abstractmethod
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        pass


class StorageInterface(ABC):
    """存储接口"""
    
    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """保存数据"""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """加载数据"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除数据"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查数据是否存在"""
        pass


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    type: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FrameworkConfig:
    """框架配置"""
    version: str = "3.0"
    agents: List[AgentConfig] = None
    enable_async: bool = True
    enable_messaging: bool = True
    enable_metrics: bool = True
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = []


class PluginContext:
    """插件上下文"""
    
    def __init__(self, config: FrameworkConfig = None):
        self.config = config or FrameworkConfig()
        self._services: Dict[str, Any] = {}
    
    def register_service(self, name: str, service: Any) -> None:
        """注册服务"""
        self._services[name] = service
    
    def get_service(self, name: str) -> Optional[Any]:
        """获取服务"""
        return self._services.get(name)
    
    def get_config(self) -> FrameworkConfig:
        """获取配置"""
        return self.config


class AgentPluginInterface(ABC):
    """Agent插件接口"""
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """插件ID"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @abstractmethod
    def get_agents(self) -> List[Type]:
        """获取插件提供的Agent列表"""
        pass
    
    @abstractmethod
    def initialize(self, context: PluginContext) -> None:
        """初始化插件"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭插件"""
        pass


def implements_interface(cls, interface_class):
    """检查类是否实现了指定接口"""
    return issubclass(cls, interface_class) or hasattr(cls, '_implements_' + interface_class.__name__)


def register_interface_implementation(interface_class, implementation_class):
    """注册接口实现"""
    setattr(interface_class, '_implementation_' + interface_class.__name__, implementation_class)


def get_interface_implementation(interface_class):
    """获取接口实现"""
    return getattr(interface_class, '_implementation_' + interface_class.__name__, None)
