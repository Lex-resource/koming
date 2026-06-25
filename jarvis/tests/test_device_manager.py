"""设备控制系统测试

参考 frame.html 5.2 节核心测试用例表中的"设备控制"场景：
- 输入："把空调调到 26 度"
- 预期输出：空调温度设为 26
- 验证点：DeviceTool 调用、状态更新

覆盖 frame.html 3.4 节设备控制系统：
- 3.4.1 设备抽象层：BaseDevice / ConcreteDevice
- 3.4.2 远程管理系统：DeviceRegistry 设备注册表
- 3.4.3 自动化执行系统：SceneMode 场景模式
"""
import pytest

from jarvis.core.device_manager import (
    device_manager,
    DeviceManager,
    DeviceRegistry,
    DeviceType,
    DeviceStatus,
    ConcreteDevice,
    SceneMode,
)


# =============================================================================
# pytest fixtures
# =============================================================================

@pytest.fixture
def dm():
    """设备管理器单例（全局共享）"""
    return device_manager


@pytest.fixture
def clean_registry(dm):
    """设备注册表，测试后清理新增的设备"""
    yield dm.registry
    # 清理测试中可能注册的临时设备
    for dev_id in ["test_camera", "test_sensor", "test_custom"]:
        dm.registry.unregister(dev_id)


# =============================================================================
# 测试类
# =============================================================================

class TestDeviceRegistry:
    """设备注册表测试 - 验证设备注册/注销/查找/列表功能"""

    def test_register_device(self, clean_registry):
        """测试注册新设备并验证"""
        # 创建一个新设备（摄像头）
        new_device = ConcreteDevice(
            device_id="test_camera",
            name="测试摄像头",
            device_type=DeviceType.CAMERA,
            status=DeviceStatus.ONLINE,
            properties={"power": "off", "resolution": "1080p"},
            capabilities=["turn_on", "turn_off", "record"],
        )
        # 注册设备
        result = clean_registry.register(new_device)
        assert result is True

        # 验证设备已注册
        device = clean_registry.get_device("test_camera")
        assert device is not None
        assert device.name == "测试摄像头"
        assert device.device_type == DeviceType.CAMERA

    def test_register_duplicate_device(self, clean_registry):
        """测试重复注册设备返回失败"""
        device = ConcreteDevice(
            device_id="test_sensor",
            name="测试传感器",
            device_type=DeviceType.SENSOR,
        )
        # 第一次注册成功
        assert clean_registry.register(device) is True
        # 重复注册应失败
        assert clean_registry.register(device) is False

    def test_unregister_device(self, clean_registry):
        """测试注销设备"""
        device = ConcreteDevice(
            device_id="test_custom",
            name="自定义设备",
            device_type=DeviceType.CUSTOM,
        )
        clean_registry.register(device)
        # 注销设备
        result = clean_registry.unregister("test_custom")
        assert result is True
        # 验证设备已注销
        assert clean_registry.get_device("test_custom") is None

    def test_unregister_nonexistent_device(self, clean_registry):
        """测试注销不存在的设备返回失败"""
        result = clean_registry.unregister("nonexistent_device_id")
        assert result is False

    def test_find_by_name(self, dm):
        """测试按名称查找设备"""
        # 查找默认注册的空调
        device = dm.registry.find_by_name("空调")
        assert device is not None
        assert device.name == "空调"
        assert device.device_type == DeviceType.AIR_CONDITIONER

    def test_list_devices_by_type(self, dm):
        """测试按类型列出设备"""
        # 列出所有灯光类型设备
        lights = dm.registry.list_by_type(DeviceType.LIGHT)
        assert len(lights) >= 1
        assert all(d.device_type == DeviceType.LIGHT for d in lights)

        # 列出所有空调类型设备
        acs = dm.registry.list_by_type(DeviceType.AIR_CONDITIONER)
        assert len(acs) >= 1
        assert all(d.device_type == DeviceType.AIR_CONDITIONER for d in acs)

        # 列出所有窗帘类型设备
        curtains = dm.registry.list_by_type(DeviceType.CURTAIN)
        assert len(curtains) >= 1
        assert all(d.device_type == DeviceType.CURTAIN for d in curtains)

    def test_list_all_devices(self, dm):
        """测试列出所有设备"""
        all_devices = dm.registry.list_devices()
        # 默认注册了4个设备：空调/灯光/窗帘/音响
        assert len(all_devices) >= 4

    def test_get_statistics(self, dm):
        """测试获取设备统计信息"""
        stats = dm.registry.get_statistics()
        assert "total_devices" in stats
        assert "devices_by_type" in stats
        assert "devices_by_status" in stats
        assert stats["total_devices"] >= 4


class TestDeviceControl:
    """设备控制测试 - 验证设备控制（turn_on/turn_off/set_property/get_status）"""

    def test_control_device_by_name(self, dm):
        """测试通过名称控制设备（空调温度设置）

        对应 frame.html 5.2 核心测试用例：
        - 输入："把空调调到 26 度"
        - 预期输出：空调温度设为 26
        - 验证点：状态更新
        """
        # 通过名称控制空调（control_device 支持按名称查找）
        result = dm.control_device("空调", "set_property", property="temperature", value=26)
        assert result["success"] is True

        # 验证温度已设置为 26
        status = dm.get_device_status("air_conditioner")
        assert status["success"] is True
        assert status["device"]["properties"]["temperature"] == 26

    def test_control_device_turn_on(self, dm):
        """测试开启设备"""
        result = dm.control_device("light", "turn_on")
        assert result["success"] is True

        # 验证灯光已开启
        status = dm.get_device_status("light")
        assert status["device"]["properties"]["power"] == "on"

    def test_control_device_turn_off(self, dm):
        """测试关闭设备"""
        # 先开启再关闭
        dm.control_device("speaker", "turn_on")
        result = dm.control_device("speaker", "turn_off")
        assert result["success"] is True

        # 验证音响已关闭
        status = dm.get_device_status("speaker")
        assert status["device"]["properties"]["power"] == "off"

    def test_control_device_set_property(self, dm):
        """测试设置设备属性"""
        result = dm.control_device(
            "curtain", "set_property", property="position", value="open"
        )
        assert result["success"] is True

        # 验证窗帘位置已设置
        status = dm.get_device_status("curtain")
        assert status["device"]["properties"]["position"] == "open"

    def test_control_nonexistent_device(self, dm):
        """测试控制不存在设备返回失败"""
        result = dm.control_device("不存在的设备", "turn_on")
        assert result["success"] is False
        assert "不存在" in result["message"]

    def test_control_device_unknown_command(self, dm):
        """测试未知命令返回失败"""
        result = dm.control_device("light", "unknown_command")
        assert result["success"] is False
        assert "未知命令" in result["message"]

    def test_get_device_status(self, dm):
        """测试获取设备状态"""
        status = dm.get_device_status("air_conditioner")
        assert status["success"] is True
        assert status["device"]["name"] == "空调"
        assert status["device"]["device_type"] == "air_conditioner"

    def test_get_device_status_nonexistent(self, dm):
        """测试获取不存在设备的状态"""
        status = dm.get_device_status("nonexistent_device")
        assert status["success"] is False
        assert "不存在" in status["message"]

    def test_list_all_devices(self, dm):
        """测试列出所有设备（返回字典列表）"""
        devices = dm.list_all_devices()
        assert len(devices) >= 4
        # 验证每个设备字典包含必要字段
        for dev in devices:
            assert "id" in dev
            assert "name" in dev
            assert "device_type" in dev
            assert "status" in dev
            assert "properties" in dev


class TestSceneMode:
    """场景模式测试 - 验证场景执行（回家/离家/睡眠/观影模式）"""

    def test_execute_scene_home(self, dm):
        """测试执行回家模式场景

        回家模式：开启灯光(亮度80)、开启空调(温度26)、打开窗帘、开启音响(音量30)
        """
        result = dm.execute_scene("回家模式")
        assert result["success"] is True
        assert result["scene_name"] == "回家模式"
        assert result["total_actions"] > 0
        assert result["success_count"] == result["total_actions"]
        assert result["failed_count"] == 0

        # 验证灯光已开启且亮度为80
        light_status = dm.get_device_status("light")
        assert light_status["device"]["properties"]["power"] == "on"
        assert light_status["device"]["properties"]["brightness"] == 80

        # 验证空调已开启且温度为26
        ac_status = dm.get_device_status("air_conditioner")
        assert ac_status["device"]["properties"]["power"] == "on"
        assert ac_status["device"]["properties"]["temperature"] == 26

    def test_execute_scene_sleep(self, dm):
        """测试执行睡眠模式场景

        睡眠模式：关闭灯光、关闭窗帘、开启空调(温度26)、关闭音响
        """
        result = dm.execute_scene("睡眠模式")
        assert result["success"] is True
        assert result["scene_name"] == "睡眠模式"
        assert result["failed_count"] == 0

        # 验证灯光已关闭
        light_status = dm.get_device_status("light")
        assert light_status["device"]["properties"]["power"] == "off"

        # 验证窗帘已关闭
        curtain_status = dm.get_device_status("curtain")
        assert curtain_status["device"]["properties"]["position"] == "closed"

        # 验证音响已关闭
        speaker_status = dm.get_device_status("speaker")
        assert speaker_status["device"]["properties"]["power"] == "off"

    def test_execute_scene_away(self, dm):
        """测试执行离家模式场景

        离家模式：关闭灯光、关闭空调、关闭窗帘、关闭音响
        """
        result = dm.execute_scene("离家模式")
        assert result["success"] is True
        assert result["scene_name"] == "离家模式"
        assert result["failed_count"] == 0

        # 验证所有设备已关闭
        for device_id in ["light", "air_conditioner", "speaker"]:
            status = dm.get_device_status(device_id)
            assert status["device"]["properties"]["power"] == "off"

    def test_execute_scene_movie(self, dm):
        """测试执行观影模式场景

        观影模式：调暗灯光(亮度20)、关闭窗帘、开启音响(音量60)、开启空调(温度24)
        """
        result = dm.execute_scene("观影模式")
        assert result["success"] is True
        assert result["scene_name"] == "观影模式"
        assert result["failed_count"] == 0

        # 验证灯光亮度为20
        light_status = dm.get_device_status("light")
        assert light_status["device"]["properties"]["brightness"] == 20

        # 验证音响音量为60
        speaker_status = dm.get_device_status("speaker")
        assert speaker_status["device"]["properties"]["volume"] == 60

        # 验证空调温度为24
        ac_status = dm.get_device_status("air_conditioner")
        assert ac_status["device"]["properties"]["temperature"] == 24

    def test_execute_nonexistent_scene(self, dm):
        """测试执行不存在场景返回失败"""
        result = dm.execute_scene("不存在的场景")
        assert result["success"] is False
        assert "不存在" in result["message"]

    def test_scene_to_dict_and_from_dict(self):
        """测试场景模式序列化与反序列化"""
        scene = SceneMode(
            name="测试场景",
            description="用于测试的场景",
            actions=[
                {"device_id": "light", "command": "turn_on"},
                {"device_id": "light", "command": "set_property",
                 "property": "brightness", "value": 50},
            ],
        )
        # 序列化
        data = scene.to_dict()
        assert data["name"] == "测试场景"
        assert len(data["actions"]) == 2

        # 反序列化
        restored = SceneMode.from_dict(data)
        assert restored.name == "测试场景"
        assert len(restored.actions) == 2


class TestDeviceManagerSingleton:
    """设备管理器单例测试"""

    def test_singleton_pattern(self):
        """测试单例模式 - 多次实例化返回同一对象"""
        dm1 = DeviceManager()
        dm2 = DeviceManager()
        assert dm1 is dm2
        assert dm1 is device_manager

    def test_registry_singleton(self):
        """测试设备注册表单例"""
        r1 = DeviceRegistry()
        r2 = DeviceRegistry()
        assert r1 is r2

    def test_default_devices_initialized(self, dm):
        """测试默认设备已初始化"""
        devices = dm.list_all_devices()
        device_ids = [d["id"] for d in devices]
        # 验证默认注册的4个设备
        assert "air_conditioner" in device_ids
        assert "light" in device_ids
        assert "curtain" in device_ids
        assert "speaker" in device_ids

    def test_default_scenes_initialized(self, dm):
        """测试默认场景已初始化"""
        stats = dm.get_statistics()
        assert stats["total_scenes"] >= 4
        scene_names = stats["scene_names"]
        assert "回家模式" in scene_names
        assert "离家模式" in scene_names
        assert "睡眠模式" in scene_names
        assert "观影模式" in scene_names

    def test_get_statistics(self, dm):
        """测试获取设备管理器统计信息"""
        stats = dm.get_statistics()
        assert "total_devices" in stats
        assert "devices_by_type" in stats
        assert "devices_by_status" in stats
        assert "total_scenes" in stats
        assert "scene_names" in stats
        assert stats["total_devices"] >= 4
