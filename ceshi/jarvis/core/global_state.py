import json
import os
from datetime import datetime
from typing import Dict, List, Any


class GlobalState:
    """全局状态管理器 - 记录所有对话历史和系统状态"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_status: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "total_interactions": 0,
            "active_tools": [],
            "memory_count": 0
        }
        self._history_file = "./data/conversation_history.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        os.makedirs("./data", exist_ok=True)
    
    def add_conversation(self, user_input: str, response: str, agent_info: Dict = None):
        """
        添加对话记录
        
        Args:
            user_input: 用户输入
            response: 系统响应
            agent_info: 参与的智能体信息（可选）
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "agent_info": agent_info or {},
            "system_status": self.system_status.copy()
        }
        self.conversation_history.append(record)
        self.system_status["total_interactions"] += 1
        self._save_history()
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            limit: 返回记录数量限制
        
        Returns:
            对话历史列表
        """
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history
    
    def get_conversation_by_time_range(self, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """
        按时间范围获取对话历史
        
        Args:
            start_time: 开始时间（ISO格式）
            end_time: 结束时间（ISO格式）
        
        Returns:
            对话历史列表
        """
        filtered = self.conversation_history
        if start_time:
            filtered = [r for r in filtered if r["timestamp"] >= start_time]
        if end_time:
            filtered = [r for r in filtered if r["timestamp"] <= end_time]
        return filtered
    
    def update_system_status(self, key: str, value: Any):
        """
        更新系统状态
        
        Args:
            key: 状态键
            value: 状态值
        """
        self.system_status[key] = value
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取当前系统状态
        
        Returns:
            系统状态字典
        """
        return self.system_status.copy()
    
    def _save_history(self):
        """保存对话历史到文件"""
        try:
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败: {e}")
    
    def load_history(self):
        """从文件加载对话历史"""
        if os.path.exists(self._history_file):
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
                self.system_status["total_interactions"] = len(self.conversation_history)
            except Exception as e:
                print(f"加载对话历史失败: {e}")
    
    def export_history(self, file_path: str = None) -> str:
        """
        导出对话历史
        
        Args:
            file_path: 导出文件路径（可选）
        
        Returns:
            导出内容
        """
        if file_path is None:
            file_path = f"./data/conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(self.conversation_history),
                "system_status": self.system_status
            },
            "history": self.conversation_history
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self.system_status["total_interactions"] = 0
        if os.path.exists(self._history_file):
            os.remove(self._history_file)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取系统摘要
        
        Returns:
            系统摘要信息
        """
        return {
            "total_conversations": len(self.conversation_history),
            "start_time": self.system_status.get("start_time"),
            "current_time": datetime.now().isoformat(),
            "active_tools": self.system_status.get("active_tools", []),
            "memory_count": self.system_status.get("memory_count", 0)
        }


# 创建全局单例
global_state = GlobalState()