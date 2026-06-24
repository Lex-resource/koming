"""
JARVIS 插件包 - 动态加载入口

提供 load_plugin 公共 API，供 plugin_registry 的目录扫描机制调用。
插件通过 @agent_plugin 装饰器在模块导入时自动注册到 PluginRegistry。
"""

import importlib
import os
from typing import Optional


def load_plugin(module_name: str, directory: str = None):
    """
    加载指定名称的插件模块

    Args:
        module_name: 插件模块名（不含 .py 后缀）
        directory: 插件所在目录，默认为 jarvis/plugins

    Returns:
        加载的模块对象，失败返回 None
    """
    if directory is None:
        directory = os.path.dirname(__file__)

    filepath = os.path.join(directory, f"{module_name}.py")
    if not os.path.exists(filepath):
        print(f"插件文件不存在: {filepath}")
        return None

    try:
        spec = importlib.util.spec_from_file_location(
            f"jarvis.plugins.{module_name}",
            filepath
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception as e:
        print(f"加载插件 {module_name} 失败: {e}")

    return None


def list_available_plugins(directory: str = None):
    """
    列出目录中所有可用的插件模块名

    Args:
        directory: 插件目录，默认为 jarvis/plugins

    Returns:
        插件模块名列表
    """
    if directory is None:
        directory = os.path.dirname(__file__)

    if not os.path.exists(directory):
        return []

    return [
        f[:-3]
        for f in os.listdir(directory)
        if f.endswith('.py') and not f.startswith('_') and f != '__init__.py'
    ]
