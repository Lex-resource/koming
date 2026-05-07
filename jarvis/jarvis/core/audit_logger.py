import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from enum import Enum


class OperationType(Enum):
    """操作类型枚举"""
    USER_INPUT = "user_input"
    AGENT_CALL = "agent_call"
    TOOL_USE = "tool_use"
    DATA_QUERY = "data_query"
    MEMORY_ACCESS = "memory_access"
    SYSTEM_ACTION = "system_action"


import threading

class AuditLogger:
    """全局审计日志系统 - 记录所有用户和智能体的操作"""

    def __init__(self):
        self.audit_records: List[Dict[str, Any]] = []
        self._log_file = "./data/audit_logs.json"
        self._ensure_data_dir()
        self._lock = threading.Lock()
        self._write_queue = asyncio.Queue()
        self._start_async_writer()

    def _ensure_data_dir(self):
        os.makedirs("./data", exist_ok=True)

    def _start_async_writer(self):
        """启动异步写入线程"""
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer_thread.start()

    def _writer_loop(self):
        """后台写入循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_write_loop())

    async def _async_write_loop(self):
        """异步写入循环"""
        while True:
            record = await self._write_queue.get()
            try:
                with open(self._log_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                records = []

            records.append(record)

            with open(self._log_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            self._write_queue.task_done()

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
        记录操作日志（同步接口，内部使用异步写入）

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

        with self._lock:
            self.audit_records.append(record)

        self._write_queue.put_nowait(record)

    async def async_log_operation(
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
        记录操作日志（异步接口）

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

        with self._lock:
            self.audit_records.append(record)

        await self._write_queue.put(record)

    def _generate_trace_id(self) -> str:
        """生成唯一追踪ID"""
        return f"{int(datetime.now().timestamp())}_{len(self.audit_records):04d}"

    def get_logs_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """按用户查询日志"""
        with self._lock:
            return [r for r in self.audit_records if r["user_id"] == user_id]

    def get_logs_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """按智能体查询日志"""
        with self._lock:
            return [r for r in self.audit_records if r["agent_name"] == agent_name]

    def get_logs_by_type(self, operation_type: OperationType) -> List[Dict[str, Any]]:
        """按操作类型查询日志"""
        with self._lock:
            return [r for r in self.audit_records if r["operation_type"] == operation_type.value]

    def get_logs_by_time_range(self, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """按时间范围查询日志"""
        with self._lock:
            filtered = list(self.audit_records)
        if start_time:
            filtered = [r for r in filtered if r["timestamp"] >= start_time]
        if end_time:
            filtered = [r for r in filtered if r["timestamp"] <= end_time]
        return filtered

    def get_agent_activity_summary(self, agent_name: str = None) -> Dict[str, Any]:
        """获取智能体活动摘要"""
        with self._lock:
            records = list(self.audit_records)
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
        with self._lock:
            records = list(self.audit_records)
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

    def load_logs(self):
        """从文件加载日志"""
        if os.path.exists(self._log_file):
            try:
                with open(self._log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                with self._lock:
                    self.audit_records = data
            except Exception as e:
                print(f"加载审计日志失败: {e}")

    def export_logs(self, file_path: str = None) -> str:
        """导出日志到文件"""
        if file_path is None:
            file_path = f"./data/audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with self._lock:
            records = list(self.audit_records)

        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(records)
            },
            "logs": records
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return file_path

    def clear_logs(self):
        """清空日志"""
        with self._lock:
            self.audit_records = []
        if os.path.exists(self._log_file):
            os.remove(self._log_file)


audit_logger = AuditLogger()
