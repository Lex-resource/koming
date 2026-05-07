"""
Agent插件系统 - 动态注册和加载机制

支持：
- 装饰器注册
- 配置文件注册
- 目录扫描自动发现
"""

import os
import json
import importlib
import inspect
from typing import Dict, Type, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0


class PluginRegistry:
    """Agent插件注册中心 - 单例模式"""

    _instance = None
    _init_lock = threading.Lock()
    _agents: Dict[str, Type] = {}
    _metadata: Dict[str, PluginMetadata] = {}
    _plugin_hooks: Dict[str, List[Callable]] = {
        'on_register': [],
        'on_unregister': [],
        'on_execute': [],
        'on_error': []
    }

    def __new__(cls):
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config_file = "./data/plugin_config.json"
        self._plugins_dir = "./jarvis/plugins"
        self._instance_lock = threading.RLock()
        self._ensure_plugins_dir()

    def _ensure_plugins_dir(self):
        """确保插件目录存在"""
        os.makedirs(self._plugins_dir, exist_ok=True)
        os.makedirs("./data", exist_ok=True)

    def register(self, name: str, agent_class: Type, metadata: Optional[PluginMetadata] = None):
        """
        注册Agent插件

        Args:
            name: 插件名称（唯一标识）
            agent_class: Agent类
            metadata: 插件元数据
        """
        if name in self._agents:
            raise ValueError(f"Plugin '{name}' already registered")

        self._agents[name] = agent_class

        if metadata is None:
            metadata = PluginMetadata(name=name)

        self._metadata[name] = metadata

        self._trigger_hook('on_register', name, agent_class)

        print(f"✓ Plugin registered: {name} (version: {metadata.version})")

    def unregister(self, name: str) -> bool:
        """
        注销Agent插件

        Args:
            name: 插件名称

        Returns:
            是否成功注销
        """
        if name not in self._agents:
            return False

        agent_class = self._agents.pop(name)
        self._metadata.pop(name, None)

        self._trigger_hook('on_unregister', name, agent_class)

        print(f"✓ Plugin unregistered: {name}")
        return True

    def get(self, name: str) -> Optional[Type]:
        """
        获取Agent类

        Args:
            name: 插件名称

        Returns:
            Agent类或None
        """
        return self._agents.get(name)

    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """获取插件元数据"""
        return self._metadata.get(name)

    def list_agents(self) -> List[str]:
        """列出所有注册的Agent名称"""
        return list(self._agents.keys())

    def list_agents_by_tag(self, tag: str) -> List[str]:
        """根据标签筛选Agent"""
        return [
            name for name, meta in self._metadata.items()
            if tag in meta.tags and meta.enabled
        ]

    def get_enabled_agents(self) -> Dict[str, Type]:
        """获取所有启用的Agent"""
        return {
            name: agent_class
            for name, agent_class in self._agents.items()
            if self._metadata.get(name, PluginMetadata(name=name)).enabled
        }

    def enable(self, name: str) -> bool:
        """启用插件"""
        if name in self._metadata:
            self._metadata[name].enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        """禁用插件"""
        if name in self._metadata:
            self._metadata[name].enabled = False
            return True
        return False

    def add_hook(self, hook_name: str, callback: Callable):
        """
        添加插件钩子

        Args:
            hook_name: 钩子名称 ('on_register', 'on_unregister', 'on_execute', 'on_error')
            callback: 回调函数
        """
        if hook_name in self._plugin_hooks:
            self._plugin_hooks[hook_name].append(callback)

    def _trigger_hook(self, hook_name: str, *args, **kwargs):
        """触发插件钩子"""
        for callback in self._plugin_hooks.get(hook_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Hook error in {hook_name}: {e}")

    def discover_from_directory(self, directory: str = None):
        """
        从目录自动发现插件

        Args:
            directory: 插件目录路径
        """
        if directory is None:
            directory = self._plugins_dir

        if not os.path.exists(directory):
            print(f"Plugins directory not found: {directory}")
            return

        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                self._load_plugin_module(module_name, directory)

    def _load_plugin_module(self, module_name: str, directory: str):
        """加载插件模块"""
        try:
            import sys
            from jarvis.plugins import load_plugin

            spec = importlib.util.spec_from_file_location(
                module_name,
                os.path.join(directory, f"{module_name}.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                if hasattr(module, 'register_plugin'):
                    module.register_plugin(self)

        except Exception as e:
            print(f"Failed to load plugin {module_name}: {e}")

    def save_config(self):
        """保存配置到文件"""
        config = {
            "agents": {
                name: {
                    "version": meta.version,
                    "description": meta.description,
                    "author": meta.author,
                    "tags": meta.tags,
                    "enabled": meta.enabled,
                    "priority": meta.priority
                }
                for name, meta in self._metadata.items()
            }
        }

        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save plugin config: {e}")

    def load_config(self):
        """从文件加载配置"""
        if not os.path.exists(self._config_file):
            return

        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            for name, info in config.get("agents", {}).items():
                if name in self._metadata:
                    self._metadata[name].enabled = info.get("enabled", True)
                    self._metadata[name].priority = info.get("priority", 0)
                    self._metadata[name].tags = info.get("tags", [])

        except Exception as e:
            print(f"Failed to load plugin config: {e}")

    def create_agent(self, name: str, **kwargs) -> Optional[Any]:
        """
        创建Agent实例

        Args:
            name: Agent名称
            **kwargs: 传递给Agent构造函数的参数

        Returns:
            Agent实例或None
        """
        agent_class = self.get(name)
        if agent_class is None:
            return None

        metadata = self.get_metadata(name)
        if metadata and not metadata.enabled:
            print(f"Plugin '{name}' is disabled")
            return None

        self._trigger_hook('on_execute', name)

        try:
            agent = agent_class(**kwargs)
            return agent
        except Exception as e:
            self._trigger_hook('on_error', name, e)
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        enabled_count = sum(1 for m in self._metadata.values() if m.enabled)

        return {
            "total_agents": len(self._agents),
            "enabled_agents": enabled_count,
            "disabled_agents": len(self._agents) - enabled_count,
            "total_tags": len(set(tag for meta in self._metadata.values() for tag in meta.tags)),
            "plugins_directory": self._plugins_dir,
            "config_file": self._config_file
        }


def agent_plugin(name: str, version: str = "1.0.0", description: str = "",
                 author: str = "", tags: List[str] = None, priority: int = 0):
    """
    Agent插件装饰器

    Args:
        name: 插件名称
        version: 版本号
        description: 描述
        author: 作者
        tags: 标签列表
        priority: 优先级

    Returns:
        装饰器函数
    """
    def decorator(cls):
        metadata = PluginMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            tags=tags or [],
            priority=priority
        )

        registry = PluginRegistry()
        registry.register(name, cls, metadata)

        return cls

    return decorator


def register_builtin_agents():
    """注册内置Agent"""
    from jarvis.agents.commander import CommanderAgent
    from jarvis.agents.analyst import AnalystAgent
    from jarvis.agents.executor import ExecutorAgent
    from jarvis.agents.learner import LearnerAgent

    registry = PluginRegistry()

    registry.register(
        "Commander",
        CommanderAgent,
        PluginMetadata(
            name="Commander",
            version="1.0.0",
            description="指挥官Agent - 理解用户意图，制定执行计划",
            author="JARVIS Team",
            tags=["core", "coordinator"],
            priority=100
        )
    )

    registry.register(
        "Analyst",
        AnalystAgent,
        PluginMetadata(
            name="Analyst",
            version="1.0.0",
            description="分析师Agent - 分析问题，收集信息",
            author="JARVIS Team",
            tags=["core", "analysis"],
            priority=90
        )
    )

    registry.register(
        "Executor",
        ExecutorAgent,
        PluginMetadata(
            name="Executor",
            version="1.0.0",
            description="执行者Agent - 调用工具执行操作",
            author="JARVIS Team",
            tags=["core", "execution"],
            priority=80
        )
    )

    registry.register(
        "Learner",
        LearnerAgent,
        PluginMetadata(
            name="Learner",
            version="1.0.0",
            description="学习官Agent - 记录对话，学习知识",
            author="JARVIS Team",
            tags=["core", "learning"],
            priority=70
        )
    )


# 创建全局单例
plugin_registry = PluginRegistry()
