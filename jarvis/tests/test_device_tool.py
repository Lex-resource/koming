"""设备工具测试"""
import pytest
from jarvis.tools.device_tool import DeviceTool


class TestDeviceTool:
    """设备工具测试类"""

    def test_device_control_on(self):
        """测试设备开启"""
        device_tool = DeviceTool()
        result = device_tool.control_device("灯光", "on")
        assert "已开启" in result

    def test_device_control_off(self):
        """测试设备关闭"""
        device_tool = DeviceTool()
        result = device_tool.control_device("灯光", "off")
        assert "已关闭" in result

    def test_device_unknown_device(self):
        """测试未知设备"""
        device_tool = DeviceTool()
        result = device_tool.control_device("电视", "on")
        assert "未知设备" in result

    def test_device_adjust_temperature(self):
        """测试调节温度"""
        device_tool = DeviceTool()
        result = device_tool.control_device("空调", "调节", "26")
        assert "26°C" in result

    def test_device_adjust_invalid_param(self):
        """测试无效参数"""
        device_tool = DeviceTool()
        result = device_tool.control_device("空调", "调节", "abc")
        assert "无效" in result

    def test_get_device_status(self):
        """测试获取设备状态"""
        device_tool = DeviceTool()
        result = device_tool.get_device_status("灯光")
        assert "灯光" in result

    def test_get_all_device_status(self):
        """测试获取所有设备状态"""
        device_tool = DeviceTool()
        result = device_tool.get_device_status()
        assert "空调" in result
        assert "灯光" in result