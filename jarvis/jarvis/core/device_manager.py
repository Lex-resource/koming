"""
设备控制系统 - 统一设备抽象与管理

参考 frame.html 3.4 节设计实现：
- 3.4.1 设备抽象层：BaseDevice 抽象基类，提供统一控制接口，屏蔽底层协议差异
- 3.4.2 远程管理系统：DeviceRegistry 设备注册表，支持设备发现/注册/查询/统计
- 3.4.3 自动化执行系统：SceneMode 场景模式，支持批量设备控制与场景联动

集成现有基础设施：
- audit_logger：记录设备操作审计日志
- message_queue：广播设备状态变更，订阅者实时感知
"""

import threading
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable

from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.message_queue import message_queue, MessagePriority


class DeviceType(Enum):
    """设备类型枚举"""
    LIGHT = "light"                    # 灯光
    AIR_CONDITIONER = "air_conditioner"  # 空调
    CURTAIN = "curtain"                # 窗帘
    SPEAKER = "speaker"                # 音响
    CAMERA = "camera"                   # 摄像头
    SENSOR = "sensor"                   # 传感器
    CUSTOM = "custom"                   # 自定义设备


class DeviceStatus(Enum):
    """设备状态枚举"""
    ONLINE = "online"            # 在线
    OFFLINE = "offline"          # 离线
    ERROR = "error"              # 错误
    MAINTENANCE = "maintenance"  # 维护中


# 设备状态变更回调类型: (device_id, old_status, new_status) -> None
StatusCallback = Callable[[str, DeviceStatus, DeviceStatus], None]


class BaseDevice(ABC):
    """设备抽象基类 - 定义统一的设备控制接口

    为不同类型的设备提供统一的控制接口，屏蔽底层协议差异，
    支持设备状态查询、指令下发和状态变更通知。

    属性：
        id: 设备唯一标识
        name: 设备名称
        device_type: 设备类型
        status: 设备在线状态
        properties: 设备属性字典（如温度、亮度、音量等）
        capabilities: 设备能力列表
    """

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: DeviceType,
        status: DeviceStatus = DeviceStatus.OFFLINE,
        properties: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None
    ):
        """
        初始化设备

        Args:
            device_id: 设备唯一标识
            name: 设备名称
            device_type: 设备类型
            status: 设备初始状态，默认为 OFFLINE
            properties: 设备属性字典，默认为空
            capabilities: 设备能力列表，默认为空
        """
        self.id = device_id
        self.name = name
        self.device_type = device_type
        self.status = status
        self.properties: Dict[str, Any] = properties if properties is not None else {}
        self.capabilities: List[str] = capabilities if capabilities is not None else []
        self._status_callbacks: List[StatusCallback] = []
        self._lock = threading.RLock()

    @abstractmethod
    def turn_on(self) -> bool:
        """开启设备

        Returns:
            是否成功开启
        """
        ...

    @abstractmethod
    def turn_off(self) -> bool:
        """关闭设备

        Returns:
            是否成功关闭
        """
        ...

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取设备完整状态

        Returns:
            设备状态字典
        """
        ...

    @abstractmethod
    def set_property(self, key: str, value: Any) -> bool:
        """设置设备属性

        Args:
            key: 属性键名
            value: 属性值

        Returns:
            是否设置成功
        """
        ...

    @abstractmethod
    def get_property(self, key: str) -> Optional[Any]:
        """获取设备属性

        Args:
            key: 属性键名

        Returns:
            属性值，不存在则返回 None
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """将设备信息序列化为字典

        Returns:
            设备信息字典
        """
        with self._lock:
            return {
                "id": self.id,
                "name": self.name,
                "device_type": self.device_type.value,
                "status": self.status.value,
                "properties": dict(self.properties),
                "capabilities": list(self.capabilities)
            }

    def update_status(self, status: DeviceStatus) -> None:
        """更新设备状态并通知回调

        Args:
            status: 新的设备状态
        """
        with self._lock:
            old_status = self.status
            self.status = status

        # 状态未变更则不通知
        if old_status != status:
            self._notify_status_change(old_status, status)

    def register_capability(self, cap_name: str) -> None:
        """注册设备能力

        Args:
            cap_name: 能力名称
        """
        with self._lock:
            if cap_name not in self.capabilities:
                self.capabilities.append(cap_name)

    def add_status_callback(self, callback: StatusCallback) -> None:
        """注册状态变更回调

        Args:
            callback: 回调函数，签名为 (device_id, old_status, new_status) -> None
        """
        with self._lock:
            self._status_callbacks.append(callback)

    def _notify_status_change(self, old_status: DeviceStatus, new_status: DeviceStatus) -> None:
        """通知所有状态变更回调

        Args:
            old_status: 旧状态
            new_status: 新状态
        """
        callbacks = list(self._status_callbacks)
        for callback in callbacks:
            try:
                callback(self.id, old_status, new_status)
            except Exception as e:
                print(f"⚠️ 设备状态回调异常 [{self.id}]: {e}")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id} name={self.name} "
            f"type={self.device_type.value} status={self.status.value}>"
        )


class ConcreteDevice(BaseDevice):
    """具体设备实现

    继承 BaseDevice，实现所有抽象方法。
    properties 字典存储设备属性（如温度、亮度、音量等），
    状态变更时记录日志。
    """

    def turn_on(self) -> bool:
        """开启设备

        将 power 属性设为 "on"，若设备处于离线状态则自动转为在线。

        Returns:
            是否成功开启
        """
        with self._lock:
            self.properties["power"] = "on"
            # 设备离线时自动转为在线
            if self.status == DeviceStatus.OFFLINE:
                old_status = self.status
                self.status = DeviceStatus.ONLINE

        print(f"✓ 设备已开启: {self.name} ({self.id})")
        return True

    def turn_off(self) -> bool:
        """关闭设备

        将 power 属性设为 "off"。

        Returns:
            是否成功关闭
        """
        with self._lock:
            self.properties["power"] = "off"

        print(f"✓ 设备已关闭: {self.name} ({self.id})")
        return True

    def get_status(self) -> Dict[str, Any]:
        """获取设备完整状态

        Returns:
            设备状态字典，包含 id、名称、类型、状态、属性、能力
        """
        return self.to_dict()

    def set_property(self, key: str, value: Any) -> bool:
        """设置设备属性

        Args:
            key: 属性键名（如 temperature、brightness、volume）
            value: 属性值

        Returns:
            是否设置成功
        """
        with self._lock:
            self.properties[key] = value

        print(f"✓ 设备属性已设置: {self.name} ({self.id}) -> {key}={value}")
        return True

    def get_property(self, key: str) -> Optional[Any]:
        """获取设备属性

        Args:
            key: 属性键名

        Returns:
            属性值，不存在则返回 None
        """
        with self._lock:
            return self.properties.get(key)


class DeviceRegistry:
    """设备注册表 - 单例模式（线程安全）

    管理所有已注册的设备，支持设备的注册、注销、查询和统计。
    对应 frame.html 3.4.2 远程管理系统中的设备发现与注册功能。
    """

    _instance = None
    _lock = threading.Lock()

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
            self._instance_lock = threading.RLock()
            self._devices: Dict[str, BaseDevice] = {}

    def register(self, device: BaseDevice) -> bool:
        """注册设备

        Args:
            device: 设备实例

        Returns:
            是否成功注册（设备ID已存在则返回 False）
        """
        with self._instance_lock:
            if device.id in self._devices:
                print(f"⚠️ 设备已存在，无法重复注册: {device.id}")
                return False
            self._devices[device.id] = device
            print(f"✓ 设备已注册: {device.name} ({device.id})")
            return True

    def unregister(self, device_id: str) -> bool:
        """注销设备

        Args:
            device_id: 设备ID

        Returns:
            是否成功注销
        """
        with self._instance_lock:
            if device_id not in self._devices:
                print(f"⚠️ 设备不存在，无法注销: {device_id}")
                return False
            device = self._devices.pop(device_id)
            print(f"✓ 设备已注销: {device.name} ({device_id})")
            return True

    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """获取设备

        Args:
            device_id: 设备ID

        Returns:
            设备实例或 None
        """
        with self._instance_lock:
            return self._devices.get(device_id)

    def list_devices(self, device_type: Optional[DeviceType] = None) -> List[BaseDevice]:
        """列出设备

        Args:
            device_type: 可选的设备类型过滤，为 None 则列出全部

        Returns:
            设备列表
        """
        with self._instance_lock:
            if device_type is None:
                return list(self._devices.values())
            return [
                dev for dev in self._devices.values()
                if dev.device_type == device_type
            ]

    def list_by_type(self, device_type: DeviceType) -> List[BaseDevice]:
        """按类型列出设备

        Args:
            device_type: 设备类型

        Returns:
            指定类型的设备列表
        """
        return self.list_devices(device_type)

    def find_by_name(self, name: str) -> Optional[BaseDevice]:
        """按名称查找设备

        Args:
            name: 设备名称

        Returns:
            设备实例或 None
        """
        with self._instance_lock:
            for device in self._devices.values():
                if device.name == name:
                    return device
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """获取设备统计信息

        Returns:
            统计信息字典，包含设备总数、按类型/状态分布
        """
        with self._instance_lock:
            devices = list(self._devices.values())

            by_type: Dict[str, int] = {}
            by_status: Dict[str, int] = {}
            for dev in devices:
                type_key = dev.device_type.value
                status_key = dev.status.value
                by_type[type_key] = by_type.get(type_key, 0) + 1
                by_status[status_key] = by_status.get(status_key, 0) + 1

            return {
                "total_devices": len(devices),
                "devices_by_type": by_type,
                "devices_by_status": by_status
            }


class SceneMode:
    """场景模式 - 批量设备控制

    通过预定义的动作序列，实现对多个设备的批量控制，
    支持场景联动（如"观影模式"联动灯光、窗帘、音响）。
    对应 frame.html 3.4.3 自动化执行系统中的场景联动功能。

    actions 格式：
        [
            {"device_id": "light", "command": "turn_on"},
            {"device_id": "air_conditioner", "command": "set_property",
             "property": "temperature", "value": 26}
        ]
    """

    def __init__(self, name: str, description: str, actions: List[Dict[str, Any]]):
        """
        初始化场景模式

        Args:
            name: 场景名称
            description: 场景描述
            actions: 动作列表，每个动作为包含 device_id 和 command 的字典
        """
        self.name = name
        self.description = description
        self.actions: List[Dict[str, Any]] = actions if actions is not None else []

    def execute(self, registry: DeviceRegistry) -> Dict[str, Any]:
        """执行场景

        依次执行所有动作，批量控制设备。

        Args:
            registry: 设备注册表

        Returns:
            执行结果字典，包含成功/失败计数和详细结果
        """
        results: List[Dict[str, Any]] = []
        success_count = 0
        failed_count = 0

        for action in self.actions:
            device_id = action.get("device_id")
            command = action.get("command")

            device = registry.get_device(device_id)
            if device is None:
                results.append({
                    "device_id": device_id,
                    "command": command,
                    "success": False,
                    "message": f"设备不存在: {device_id}"
                })
                failed_count += 1
                continue

            try:
                success = self._execute_action(device, action)
                results.append({
                    "device_id": device_id,
                    "command": command,
                    "success": success,
                    "message": "执行成功" if success else "执行失败"
                })
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                results.append({
                    "device_id": device_id,
                    "command": command,
                    "success": False,
                    "message": f"执行异常: {e}"
                })
                failed_count += 1

        return {
            "success": failed_count == 0,
            "scene_name": self.name,
            "total_actions": len(self.actions),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }

    def _execute_action(self, device: BaseDevice, action: Dict[str, Any]) -> bool:
        """执行单个动作

        Args:
            device: 目标设备
            action: 动作字典

        Returns:
            是否执行成功
        """
        command = action.get("command")

        if command == "turn_on":
            return device.turn_on()
        elif command == "turn_off":
            return device.turn_off()
        elif command == "set_property":
            key = action.get("property") or action.get("key")
            value = action.get("value")
            if key is None:
                print(f"⚠️ set_property 缺少 property 参数: {action}")
                return False
            return device.set_property(key, value)
        elif command == "get_status":
            device.get_status()
            return True
        else:
            print(f"⚠️ 未知命令: {command}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典

        Returns:
            场景信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "actions": list(self.actions)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneMode":
        """从字典反序列化

        Args:
            data: 字典数据

        Returns:
            SceneMode 实例
        """
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            actions=data.get("actions", [])
        )


class DeviceManager:
    """统一设备管理器 - 单例模式（线程安全）

    整合 DeviceRegistry 和 SceneMode，提供统一的设备控制入口。
    集成 audit_logger 记录设备操作审计日志，
    集成 message_queue 广播设备状态变更，订阅者实时感知。
    """

    _instance = None
    _lock = threading.Lock()

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
            self._instance_lock = threading.RLock()

            # 设备注册表（单例）
            self.registry = DeviceRegistry()

            # 场景模式注册表
            self._scenes: Dict[str, SceneMode] = {}

            # 消息队列（单例），启动以支持消息投递
            self._message_queue = message_queue
            self._message_queue.start()

            # 审计日志（单例）
            self._audit_logger = audit_logger

            # 初始化默认设备和场景
            self._init_default_devices()
            self._init_default_scenes()

            print("✓ DeviceManager 初始化完成")

    def control_device(self, device_id: str, command: str, **kwargs) -> Dict[str, Any]:
        """控制设备

        Args:
            device_id: 设备ID
            command: 控制命令（turn_on/turn_off/set_property/get_status）
            **kwargs: 命令参数（如 property, value）

        Returns:
            控制结果字典，包含 success、message 和设备状态
        """
        device = self.registry.get_device(device_id)
        if device is None:
            result = {
                "success": False,
                "device_id": device_id,
                "command": command,
                "message": f"设备不存在: {device_id}"
            }
            self._log_device_operation(device_id, command, result, success=False)
            return result

        try:
            if command == "turn_on":
                success = device.turn_on()
                message = f"设备 {device.name} 已开启" if success else f"设备 {device.name} 开启失败"
            elif command == "turn_off":
                success = device.turn_off()
                message = f"设备 {device.name} 已关闭" if success else f"设备 {device.name} 关闭失败"
            elif command == "set_property":
                key = kwargs.get("property") or kwargs.get("key")
                value = kwargs.get("value")
                if key is None:
                    success = False
                    message = "缺少参数: property 或 key"
                else:
                    success = device.set_property(key, value)
                    message = (
                        f"设备 {device.name} 属性 {key} 已设置为 {value}"
                        if success else f"设备 {device.name} 属性设置失败"
                    )
            elif command == "get_status":
                success = True
                message = "查询成功"
            else:
                success = False
                message = f"未知命令: {command}"

            result = {
                "success": success,
                "device_id": device_id,
                "command": command,
                "message": message,
                "device": device.to_dict()
            }

            self._log_device_operation(device_id, command, result, success=success)

            # 状态变更类命令广播状态（查询类命令不广播）
            if success and command in ("turn_on", "turn_off", "set_property"):
                self._broadcast_status(device)

            return result

        except Exception as e:
            result = {
                "success": False,
                "device_id": device_id,
                "command": command,
                "message": f"控制异常: {e}"
            }
            self._log_device_operation(device_id, command, result, success=False)
            return result

    def execute_scene(self, scene_name: str) -> Dict[str, Any]:
        """执行场景

        Args:
            scene_name: 场景名称

        Returns:
            执行结果字典，包含成功/失败计数和详细结果
        """
        scene = self._scenes.get(scene_name)
        if scene is None:
            result = {
                "success": False,
                "scene_name": scene_name,
                "message": f"场景不存在: {scene_name}"
            }
            self._audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                agent_name="DeviceManager",
                action="execute_scene",
                details={"scene_name": scene_name},
                result=f"场景不存在: {scene_name}"
            )
            return result

        try:
            result = scene.execute(self.registry)

            self._audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                agent_name="DeviceManager",
                action="execute_scene",
                details={
                    "scene_name": scene_name,
                    "total_actions": result["total_actions"],
                    "success_count": result["success_count"],
                    "failed_count": result["failed_count"]
                },
                result=(
                    f"场景 {scene_name} 执行完成: "
                    f"{result['success_count']}/{result['total_actions']} 成功"
                )
            )

            # 广播场景执行事件
            self._broadcast_scene_execution(scene_name, result)

            return result
        except Exception as e:
            result = {
                "success": False,
                "scene_name": scene_name,
                "message": f"场景执行异常: {e}"
            }
            self._audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                agent_name="DeviceManager",
                action="execute_scene",
                details={"scene_name": scene_name, "error": str(e)},
                result=f"场景执行异常: {e}"
            )
            return result

    def register_scene(self, scene: SceneMode) -> bool:
        """注册场景

        Args:
            scene: 场景模式实例

        Returns:
            是否成功注册（场景名称已存在则返回 False）
        """
        with self._instance_lock:
            if scene.name in self._scenes:
                print(f"⚠️ 场景已存在，无法重复注册: {scene.name}")
                return False
            self._scenes[scene.name] = scene
            print(f"✓ 场景已注册: {scene.name}")
            return True

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """查询设备状态

        Args:
            device_id: 设备ID

        Returns:
            设备状态字典
        """
        device = self.registry.get_device(device_id)
        if device is None:
            return {
                "success": False,
                "device_id": device_id,
                "message": f"设备不存在: {device_id}"
            }

        status = device.get_status()

        self._audit_logger.log_operation(
            operation_type=OperationType.DATA_QUERY,
            agent_name="DeviceManager",
            action="get_device_status",
            details={"device_id": device_id},
            result=f"查询设备状态: {device.name}"
        )

        return {
            "success": True,
            "device_id": device_id,
            "device": status
        }

    def list_all_devices(self) -> List[Dict[str, Any]]:
        """列出所有设备

        Returns:
            设备信息字典列表
        """
        devices = self.registry.list_devices()
        return [dev.to_dict() for dev in devices]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            统计信息字典，包含设备总数、类型/状态分布、场景数量
        """
        registry_stats = self.registry.get_statistics()
        return {
            "total_devices": registry_stats["total_devices"],
            "devices_by_type": registry_stats["devices_by_type"],
            "devices_by_status": registry_stats["devices_by_status"],
            "total_scenes": len(self._scenes),
            "scene_names": list(self._scenes.keys())
        }

    def _init_default_devices(self) -> None:
        """初始化默认设备

        与现有 device_tool.py 保持一致，预置空调/灯光/窗帘/音响四类设备。
        """
        devices = [
            ConcreteDevice(
                device_id="air_conditioner",
                name="空调",
                device_type=DeviceType.AIR_CONDITIONER,
                status=DeviceStatus.ONLINE,
                properties={"power": "off", "temperature": 25},
                capabilities=["turn_on", "turn_off", "set_temperature"]
            ),
            ConcreteDevice(
                device_id="light",
                name="灯光",
                device_type=DeviceType.LIGHT,
                status=DeviceStatus.ONLINE,
                properties={"power": "off", "brightness": 50},
                capabilities=["turn_on", "turn_off", "set_brightness"]
            ),
            ConcreteDevice(
                device_id="curtain",
                name="窗帘",
                device_type=DeviceType.CURTAIN,
                status=DeviceStatus.ONLINE,
                properties={"power": "off", "position": "closed"},
                capabilities=["turn_on", "turn_off", "set_position"]
            ),
            ConcreteDevice(
                device_id="speaker",
                name="音响",
                device_type=DeviceType.SPEAKER,
                status=DeviceStatus.ONLINE,
                properties={"power": "off", "volume": 30},
                capabilities=["turn_on", "turn_off", "set_volume"]
            ),
        ]

        for device in devices:
            self.registry.register(device)

    def _init_default_scenes(self) -> None:
        """初始化默认场景

        预置回家模式/离家模式/睡眠模式/观影模式四个场景。
        """
        scenes = [
            SceneMode(
                name="回家模式",
                description="回家后自动开启灯光、空调，打开窗帘",
                actions=[
                    {"device_id": "light", "command": "turn_on"},
                    {"device_id": "light", "command": "set_property",
                     "property": "brightness", "value": 80},
                    {"device_id": "air_conditioner", "command": "turn_on"},
                    {"device_id": "air_conditioner", "command": "set_property",
                     "property": "temperature", "value": 26},
                    {"device_id": "curtain", "command": "set_property",
                     "property": "position", "value": "open"},
                    {"device_id": "speaker", "command": "turn_on"},
                    {"device_id": "speaker", "command": "set_property",
                     "property": "volume", "value": 30},
                ]
            ),
            SceneMode(
                name="离家模式",
                description="离家时关闭所有设备",
                actions=[
                    {"device_id": "light", "command": "turn_off"},
                    {"device_id": "air_conditioner", "command": "turn_off"},
                    {"device_id": "curtain", "command": "set_property",
                     "property": "position", "value": "closed"},
                    {"device_id": "speaker", "command": "turn_off"},
                ]
            ),
            SceneMode(
                name="睡眠模式",
                description="睡眠时关闭灯光和音响，关闭窗帘，空调调至舒适温度",
                actions=[
                    {"device_id": "light", "command": "turn_off"},
                    {"device_id": "curtain", "command": "set_property",
                     "property": "position", "value": "closed"},
                    {"device_id": "air_conditioner", "command": "turn_on"},
                    {"device_id": "air_conditioner", "command": "set_property",
                     "property": "temperature", "value": 26},
                    {"device_id": "speaker", "command": "turn_off"},
                ]
            ),
            SceneMode(
                name="观影模式",
                description="观影时调暗灯光，关闭窗帘，开启音响",
                actions=[
                    {"device_id": "light", "command": "turn_on"},
                    {"device_id": "light", "command": "set_property",
                     "property": "brightness", "value": 20},
                    {"device_id": "curtain", "command": "set_property",
                     "property": "position", "value": "closed"},
                    {"device_id": "speaker", "command": "turn_on"},
                    {"device_id": "speaker", "command": "set_property",
                     "property": "volume", "value": 60},
                    {"device_id": "air_conditioner", "command": "turn_on"},
                    {"device_id": "air_conditioner", "command": "set_property",
                     "property": "temperature", "value": 24},
                ]
            ),
        ]

        for scene in scenes:
            self.register_scene(scene)

    def _log_device_operation(
        self,
        device_id: str,
        command: str,
        result: Dict[str, Any],
        success: bool
    ) -> None:
        """记录设备操作审计日志

        Args:
            device_id: 设备ID
            command: 控制命令
            result: 操作结果
            success: 是否成功
        """
        try:
            self._audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                agent_name="DeviceManager",
                action="control_device",
                details={
                    "device_id": device_id,
                    "command": command
                },
                result=result.get("message", "")
            )
        except Exception as e:
            print(f"⚠️ 审计日志记录失败: {e}")

    def _broadcast_status(self, device: BaseDevice) -> None:
        """广播设备状态变更

        通过消息队列发布设备状态变更事件，订阅者可实时感知。
        对应 frame.html 3.4.1 中"设备状态变更时通过消息队列广播"。

        Args:
            device: 设备实例
        """
        try:
            self._message_queue.publish(
                topic="device.status",
                payload={
                    "device_id": device.id,
                    "device_name": device.name,
                    "device_type": device.device_type.value,
                    "status": device.status.value,
                    "properties": dict(device.properties),
                    "timestamp": datetime.now().isoformat()
                },
                priority=MessagePriority.NORMAL,
                source="DeviceManager",
                metadata={"event": "status_change", "device_id": device.id}
            )
        except Exception as e:
            print(f"⚠️ 设备状态广播失败: {e}")

    def _broadcast_scene_execution(self, scene_name: str, result: Dict[str, Any]) -> None:
        """广播场景执行事件

        Args:
            scene_name: 场景名称
            result: 执行结果
        """
        try:
            self._message_queue.publish(
                topic="device.scene",
                payload={
                    "scene_name": scene_name,
                    "success": result.get("success", False),
                    "total_actions": result.get("total_actions", 0),
                    "success_count": result.get("success_count", 0),
                    "failed_count": result.get("failed_count", 0),
                    "timestamp": datetime.now().isoformat()
                },
                priority=MessagePriority.NORMAL,
                source="DeviceManager",
                metadata={"event": "scene_execution", "scene_name": scene_name}
            )
        except Exception as e:
            print(f"⚠️ 场景执行广播失败: {e}")


# 创建全局单例
device_manager = DeviceManager()
