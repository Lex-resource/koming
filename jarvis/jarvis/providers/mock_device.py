"""Mock 设备实现 - 预留 MCP 接入，先用内存模拟"""

from typing import Any, Dict, List

from jarvis.core.interfaces import IDevice


class MockDevice(IDevice):
    """内存模拟设备 - 验证架构链路，后续换 MCP 实现"""

    def __init__(self):
        self._devices: Dict[str, Dict[str, Any]] = {
            "ac_living": {"id": "ac_living", "name": "客厅空调", "type": "ac", "on": False, "temperature": 26, "mode": "cool"},
            "light_living": {"id": "light_living", "name": "客厅灯", "type": "light", "on": False, "brightness": 80},
            "curtain_living": {"id": "curtain_living", "name": "客厅窗帘", "type": "curtain", "open": True},
            "speaker_living": {"id": "speaker_living", "name": "客厅音响", "type": "speaker", "on": False, "volume": 30},
        }
        self._scenes: Dict[str, List[Dict]] = {
            "回家": [{"device": "light_living", "command": "turn_on"},
                    {"device": "ac_living", "command": "turn_on", "property": "temperature", "value": 26}],
            "离家": [{"device": "light_living", "command": "turn_off"},
                    {"device": "ac_living", "command": "turn_off"},
                    {"device": "curtain_living", "command": "set_property", "property": "open", "value": False}],
            "睡眠": [{"device": "light_living", "command": "turn_off"},
                    {"device": "ac_living", "command": "set_property", "property": "temperature", "value": 24}],
            "观影": [{"device": "light_living", "command": "set_property", "property": "brightness", "value": 20},
                    {"device": "curtain_living", "command": "set_property", "property": "open", "value": False},
                    {"device": "speaker_living", "command": "turn_on"}],
        }

    def control(self, device_id: str, command: str, **kwargs) -> Dict[str, Any]:
        dev = self._devices.get(device_id)
        if not dev:
            return {"success": False, "device_id": device_id, "message": "设备不存在"}
        if command == "turn_on":
            dev["on"] = True
        elif command == "turn_off":
            dev["on"] = False
        elif command == "set_property":
            prop = kwargs.get("property") or kwargs.get("key")
            if prop:
                dev[prop] = kwargs.get("value")
        elif command == "get_status":
            pass
        return {"success": True, "device_id": device_id, "command": command, "message": "OK", "device": dev}

    def get_status(self, device_id: str) -> Dict[str, Any]:
        dev = self._devices.get(device_id)
        if not dev:
            return {"success": False, "device_id": device_id, "message": "设备不存在"}
        return {"success": True, "device_id": device_id, "device": dev}

    def list_devices(self) -> List[Dict[str, Any]]:
        return list(self._devices.values())

    def execute_scene(self, scene_name: str) -> Dict[str, Any]:
        actions = self._scenes.get(scene_name)
        if not actions:
            return {"success": False, "scene_name": scene_name, "message": "场景不存在"}
        results = [self.control(a["device"], a["command"], **{k: v for k, v in a.items() if k not in ("device", "command")}) for a in actions]
        return {"success": True, "scene_name": scene_name, "total_actions": len(actions),
                "success_count": sum(1 for r in results if r["success"]), "failed_count": 0, "results": results}

    def list_scenes(self) -> List[str]:
        return list(self._scenes.keys())

    def register_device(self, device_config: Dict[str, Any]) -> bool:
        dev_id = device_config.get("id")
        if not dev_id:
            return False
        self._devices[dev_id] = device_config
        return True

    def register_scene(self, scene_config: Dict[str, Any]) -> bool:
        name = scene_config.get("name")
        if not name:
            return False
        self._scenes[name] = scene_config.get("actions", [])
        return True
