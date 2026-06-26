"""设备控制抽象接口 - 预留 MCP 接入"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IDevice(ABC):
    """设备控制 - 抽象层，实现可以是 Mock/MCP/真实硬件"""

    @abstractmethod
    def control(self, device_id: str, command: str, **kwargs) -> Dict[str, Any]:
        """控制设备
        Args:
            device_id: 设备标识
            command: turn_on / turn_off / set_property / get_status
        Returns:
            {"success": bool, "device_id": str, "message": str, "device": dict}
        """
        ...

    @abstractmethod
    def get_status(self, device_id: str) -> Dict[str, Any]:
        """查询设备状态"""
        ...

    @abstractmethod
    def list_devices(self) -> List[Dict[str, Any]]:
        """列出所有设备"""
        ...

    @abstractmethod
    def execute_scene(self, scene_name: str) -> Dict[str, Any]:
        """执行场景模式"""
        ...

    @abstractmethod
    def list_scenes(self) -> List[str]:
        """列出可用场景"""
        ...

    @abstractmethod
    def register_device(self, device_config: Dict[str, Any]) -> bool:
        """注册设备（运行时动态扩展）"""
        ...

    @abstractmethod
    def register_scene(self, scene_config: Dict[str, Any]) -> bool:
        """注册场景"""
        ...
