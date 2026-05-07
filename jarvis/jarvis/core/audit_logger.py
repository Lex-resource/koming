import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class OperationType(Enum):
    """操作类型枚举"""
    USER_INPUT = "user_input"
    AGENT_CALL = "agent_call"
    TOOL_USE = "tool_use"
    DATA_QUERY = "data_query"
    MEMORY_ACCESS = "memory_access"
    SYSTEM_ACTION = "system_action"


class AuditLogger:
    """全局审计日志系统 - 记录所有用户和智能体的操作"""
    
    def __init__(self):
        self.audit_records: List[Dict[str, Any]] = []
        self._log_file = "./data/audit_logs.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        os.makedirs("./data", exist_ok=True)
    
    def log_operation(
        self,
        operation_type: OperationType,
        user_id: str = "anonymous",
        agent_name: str = None,
        action: str = None,
        details: Dict = None,
        result: Any = None,
        duration: float = None
    ):
        """
        记录操作日志
        
        Args:
            operation_type: 操作类型
            user_id: 用户ID
            agent_name: 智能体名称
            action: 执行的动作
            details: 详细信息
            result: 操作结果
            duration: 操作耗时（秒）
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type.value,
            "user_id": user_id,
            "agent_name": agent_name,
            "action": action,
            "details": details or {},
            "result": result,
            "duration": duration,
            "trace_id": self._generate_trace_id()
        }
        self.audit_records.append(record)
        self._save_logs()
    
    def _generate_trace_id(self) -> str:
        """生成唯一追踪ID"""
        return f"{int(datetime.now().timestamp())}_{len(self.audit_records):04d}"
    
    def get_logs_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """按用户查询日志"""
        return [r for r in self.audit_records if r["user_id"] == user_id]
    
    def get_logs_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """按智能体查询日志"""
        return [r for r in self.audit_records if r["agent_name"] == agent_name]
    
    def get_logs_by_type(self, operation_type: OperationType) -> List[Dict[str, Any]]:
        """按操作类型查询日志"""
        return [r for r in self.audit_records if r["operation_type"] == operation_type.value]
    
    def get_logs_by_time_range(self, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """按时间范围查询日志"""
        filtered = self.audit_records
        if start_time:
            filtered = [r for r in filtered if r["timestamp"] >= start_time]
        if end_time:
            filtered = [r for r in filtered if r["timestamp"] <= end_time]
        return filtered
    
    def get_agent_activity_summary(self, agent_name: str = None) -> Dict[str, Any]:
        """获取智能体活动摘要"""
        records = self.audit_records
        if agent_name:
            records = [r for r in records if r["agent_name"] == agent_name]
        
        summary = {
            "total_operations": len(records),
            "operations_by_type": {},
            "operations_by_agent": {}
        }
        
        for record in records:
            op_type = record["operation_type"]
            agent = record["agent_name"] or "system"
            
            summary["operations_by_type"][op_type] = summary["operations_by_type"].get(op_type, 0) + 1
            summary["operations_by_agent"][agent] = summary["operations_by_agent"].get(agent, 0) + 1
        
        return summary
    
    def get_user_activity_summary(self, user_id: str = None) -> Dict[str, Any]:
        """获取用户活动摘要"""
        records = self.audit_records
        if user_id:
            records = [r for r in records if r["user_id"] == user_id]
        
        summary = {
            "total_interactions": len(records),
            "users": set(),
            "operations_by_type": {}
        }
        
        for record in records:
            summary["users"].add(record["user_id"])
            op_type = record["operation_type"]
            summary["operations_by_type"][op_type] = summary["operations_by_type"].get(op_type, 0) + 1
        
        summary["users"] = list(summary["users"])
        return summary
    
    def _save_logs(self):
        """保存日志到文件"""
        try:
            with open(self._log_file, "w", encoding="utf-8") as f:
                json.dump(self.audit_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存审计日志失败: {e}")
    
    def load_logs(self):
        """从文件加载日志"""
        if os.path.exists(self._log_file):
            try:
                with open(self._log_file, "r", encoding="utf-8") as f:
                    self.audit_records = json.load(f)
            except Exception as e:
                print(f"加载审计日志失败: {e}")
    
    def export_logs(self, file_path: str = None) -> str:
        """导出日志到文件"""
        if file_path is None:
            file_path = f"./data/audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(self.audit_records)
            },
            "logs": self.audit_records
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def clear_logs(self):
        """清空日志"""
        self.audit_records = []
        if os.path.exists(self._log_file):
            os.remove(self._log_file)


audit_logger = AuditLogger()