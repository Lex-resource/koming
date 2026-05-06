from langchain.tools import tool


class DeviceTool:
    _devices = {
        "空调": {"status": "off", "temperature": 25},
        "灯光": {"status": "off", "brightness": 50},
        "窗帘": {"status": "closed"},
        "音乐": {"status": "off", "volume": 30}
    }

    @tool("control_device")
    def control_device(device: str, action: str, parameter: str = None) -> str:
        """
        控制智能家居设备
        
        Args:
            device: 设备名称（空调、灯光、窗帘、音乐）
            action: 操作动作（on/off/打开/关闭/调节）
            parameter: 可选参数（如温度、亮度、音量等）
        
        Returns:
            操作结果
        """
        device = device.replace("灯", "灯光").replace("空调", "空调")
        
        if device not in DeviceTool._devices:
            return f"未知设备: {device}"
        
        action_map = {
            "on": "on", "打开": "on", "开启": "on",
            "off": "off", "关闭": "off", "关掉": "off"
        }
        
        normalized_action = action_map.get(action, action)
        
        if normalized_action in ["on", "off"]:
            DeviceTool._devices[device]["status"] = normalized_action
            status_text = "已开启" if normalized_action == "on" else "已关闭"
            return f"{status_text} {device}"
        
        elif normalized_action == "调节":
            if device == "空调" and parameter:
                try:
                    temp = int(parameter)
                    DeviceTool._devices[device]["temperature"] = temp
                    return f"空调温度已调节至 {temp}°C"
                except ValueError:
                    return "温度参数无效"
            
            elif device == "灯光" and parameter:
                try:
                    brightness = int(parameter)
                    DeviceTool._devices[device]["brightness"] = max(0, min(100, brightness))
                    return f"灯光亮度已调节至 {brightness}%"
                except ValueError:
                    return "亮度参数无效"
            
            elif device == "音乐" and parameter:
                try:
                    volume = int(parameter)
                    DeviceTool._devices[device]["volume"] = max(0, min(100, volume))
                    return f"音乐音量已调节至 {volume}%"
                except ValueError:
                    return "音量参数无效"
            
            else:
                return f"{device}不支持此参数调节"
        
        else:
            return f"未知操作: {action}"

    @tool("get_device_status")
    def get_device_status(device: str = None) -> str:
        """
        获取设备状态
        
        Args:
            device: 设备名称（可选，不传则获取所有设备状态）
        
        Returns:
            设备状态信息
        """
        if device:
            device = device.replace("灯", "灯光").replace("空调", "空调")
            if device in DeviceTool._devices:
                status = DeviceTool._devices[device]
                status_str = f"{device}: "
                if status["status"] == "on":
                    status_str += "已开启"
                    if "temperature" in status:
                        status_str += f"，温度: {status['temperature']}°C"
                    if "brightness" in status:
                        status_str += f"，亮度: {status['brightness']}%"
                    if "volume" in status:
                        status_str += f"，音量: {status['volume']}%"
                else:
                    status_str += "已关闭"
                return status_str
            else:
                return f"未知设备: {device}"
        
        else:
            result = "当前设备状态:\n"
            for dev, status in DeviceTool._devices.items():
                result += f"- {dev}: {'开启' if status['status'] == 'on' else '关闭'}"
                if "temperature" in status:
                    result += f" ({status['temperature']}°C)"
                elif "brightness" in status:
                    result += f" ({status['brightness']}%)"
                elif "volume" in status:
                    result += f" ({status['volume']}%)"
                result += "\n"
            return result.strip()