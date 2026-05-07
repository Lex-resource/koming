import os
import time
import json
import threading
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
        self._lock = threading.Lock()
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        with self._lock:
            self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_action(self, agent_name: str, action: str, details: Optional[dict] = None):
        """记录智能体动作"""
        self.log("INFO", "agent", f"{agent_name} 执行: {action}", details)
    
    def log_tool_use(self, tool_name: str, args: dict, result: str):
        """记录工具使用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"args": args, "result": result})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, message: str, exception: Optional[Exception] = None):
        """记录错误"""
        data = {"exception": str(exception)} if exception else None
        self.log("ERROR", source, message, data)
    
    def log_warning(self, source: str, message: str):
        """记录警告"""
        self.log("WARNING", source, message)
    
    def log_debug(self, source: str, message: str, data: Optional[dict] = None):
        """记录调试信息"""
        self.log("DEBUG", source, message, data)
    
    def get_logs(self, limit: int = 100) -> list:
        """获取最近的日志"""
        with self._lock:
            return self.log_entries[-limit:]
    
    def export_logs(self, file_path: str = None) -> str:
        """导出日志到文件"""
        if file_path is None:
            file_path = f"./logs/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with self._lock:
            export_data = {
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "total_entries": len(self.log_entries)
                },
                "logs": self.log_entries
            }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return file_path


logger = GlobalLogger()