import json
import os
import threading
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
    """全局审计日志系统 - 直接写入数据库，无内存缓存（线程安全）"""

    _instance = None
    _init_lock = threading.Lock()
    _trace_counter = 0
    _counter_lock = threading.Lock()

    def __new__(cls):
        if not hasattr(cls, '_instance') or cls._instance is None:
            with cls._init_lock:
                if not hasattr(cls, '_instance') or cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._init_lock:
            if self._initialized:
                return
            self._initialized = True
            self._db = None
            self._instance_lock = threading.RLock()
            self._write_thread = None
            self._running = False
            self._write_queue: List[Dict[str, Any]] = []
            self._max_queue_size = 10000
            self._flush_interval = 1.0
            self._batch_size = 100
            self._ensure_data_dir()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs("./data", exist_ok=True)

    def _init_database(self):
        """延迟初始化数据库连接"""
        if self._db is None:
            try:
                from jarvis.core.database import db as _db_instance
                self._db = _db_instance
            except Exception as e:
                print(f"⚠️ 审计日志数据库连接失败: {e}")
                self._db = None

    def _get_next_trace_id(self) -> str:
        """生成唯一追踪ID（线程安全）"""
        with self._counter_lock:
            AuditLogger._trace_counter += 1
            return f"{int(datetime.now().timestamp())}_{AuditLogger._trace_counter:06d}"

    def _start_async_writer(self):
        """启动异步写入线程"""
        if self._write_thread is None or not self._write_thread.is_alive():
            self._running = True
            self._write_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self._write_thread.start()

    def _writer_loop(self):
        """后台写入循环"""
        import time
        last_flush_time = time.time()

        while self._running:
            try:
                current_time = time.time()
                should_flush = (
                    len(self._write_queue) >= self._batch_size or
                    (current_time - last_flush_time) >= self._flush_interval
                )

                if should_flush and self._write_queue:
                    self._flush_to_database()
                    last_flush_time = current_time

                time.sleep(0.1)

            except Exception as e:
                print(f"审计日志写入线程异常: {e}")

    def _flush_to_database(self):
        """批量写入数据库"""
        if not self._write_queue:
            return

        self._init_database()

        if self._db is None:
            self._fallback_write_to_file()
            return

        batch = self._write_queue.copy()
        self._write_queue.clear()

        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def batch_insert():
                async with self._db.get_session() as session:
                    from jarvis.core.database import AuditLog
                    from sqlalchemy import insert

                    records = [
                        AuditLog(
                            trace_id=record.get("trace_id", ""),
                            user_id=record.get("user_id", "anonymous"),
                            agent_name=record.get("agent_name"),
                            operation_type=record.get("operation_type", ""),
                            action=record.get("action"),
                            details=record.get("details", {}),
                            result=record.get("result", "")[:500] if record.get("result") else None,
                            duration=record.get("duration"),
                            created_at=datetime.fromisoformat(record["timestamp"])
                        )
                        for record in batch
                    ]

                    session.add_all(records)
                    await session.commit()

            loop.run_until_complete(batch_insert())
            loop.close()

        except Exception as e:
            print(f"审计日志批量写入数据库失败: {e}, 尝试写入文件")
            self._write_batch_to_file(batch)

    def _fallback_write_to_file(self):
        """回退到文件写入"""
        if self._write_queue:
            batch = self._write_queue.copy()
            self._write_queue.clear()
            self._write_batch_to_file(batch)

    def _write_batch_to_file(self, batch: List[Dict[str, Any]]):
        """批量写入文件"""
        log_file = "./data/audit_logs.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                for record in batch:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"审计日志文件写入失败: {e}")

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
        记录操作日志（同步接口，加入写入队列）

        Args:
            operation_type: 操作类型
            user_id: 用户ID
            agent_name: 智能体名称
            action: 执行的动作
            details: 详细信息
            result: 操作结果
            duration: 操作耗时（秒）
        """
        self._start_async_writer()

        record = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type.value,
            "user_id": user_id,
            "agent_name": agent_name,
            "action": action,
            "details": details or {},
            "result": str(result)[:500] if result else None,
            "duration": duration,
            "trace_id": self._generate_trace_id()
        }

        with self._instance_lock:
            self._write_queue.append(record)

    def _generate_trace_id(self) -> str:
        """生成唯一追踪ID"""
        return self._get_next_trace_id()

    def _get_logs_from_db(
        self,
        user_id: str = None,
        agent_name: str = None,
        operation_type: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """从数据库获取日志"""
        if self._db is None:
            self._init_database()

        if self._db is None:
            return self._get_logs_from_file(limit)

        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def fetch():
                return await self._db.get_audit_logs(
                    user_id=user_id,
                    agent_name=agent_name,
                    operation_type=operation_type,
                    limit=limit
                )

            result = loop.run_until_complete(fetch())
            loop.close()
            return result

        except Exception as e:
            print(f"从数据库获取审计日志失败: {e}")
            return self._get_logs_from_file(limit)

    def _get_logs_from_file(self, limit: int = 100) -> List[Dict[str, Any]]:
        """从文件获取日志（回退方案）"""
        log_file = "./data/audit_logs.jsonl"
        if not os.path.exists(log_file):
            return []

        try:
            logs = []
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            return logs[-limit:]

        except Exception as e:
            print(f"读取审计日志文件失败: {e}")
            return []

    def get_logs_by_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按用户查询日志"""
        logs = self._get_logs_from_db(user_id=user_id, limit=limit)
        return [r for r in logs if r.get("user_id") == user_id]

    def get_logs_by_agent(self, agent_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按智能体查询日志"""
        return self._get_logs_from_db(agent_name=agent_name, limit=limit)

    def get_logs_by_type(self, operation_type: OperationType, limit: int = 100) -> List[Dict[str, Any]]:
        """按操作类型查询日志"""
        return self._get_logs_from_db(operation_type=operation_type.value, limit=limit)

    def get_logs_by_time_range(
        self,
        start_time: str = None,
        end_time: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """按时间范围查询日志"""
        logs = self._get_logs_from_db(limit=limit * 10)

        filtered = logs
        if start_time:
            filtered = [r for r in filtered if r.get("created_at", "") >= start_time]
        if end_time:
            filtered = [r for r in filtered if r.get("created_at", "") <= end_time]

        return filtered[:limit]

    def get_agent_activity_summary(self, agent_name: str = None) -> Dict[str, Any]:
        """获取智能体活动摘要"""
        logs = self._get_logs_from_db(agent_name=agent_name, limit=10000)

        summary = {
            "total_operations": len(logs),
            "operations_by_type": {},
            "operations_by_agent": {}
        }

        for record in logs:
            op_type = record.get("operation_type", "unknown")
            agent = record.get("agent_name") or "system"

            summary["operations_by_type"][op_type] = summary["operations_by_type"].get(op_type, 0) + 1
            summary["operations_by_agent"][agent] = summary["operations_by_agent"].get(agent, 0) + 1

        return summary

    def get_user_activity_summary(self, user_id: str = None) -> Dict[str, Any]:
        """获取用户活动摘要"""
        logs = self._get_logs_from_db(user_id=user_id, limit=10000)

        summary = {
            "total_interactions": len(logs),
            "users": set(),
            "operations_by_type": {}
        }

        for record in logs:
            summary["users"].add(record.get("user_id", "anonymous"))
            op_type = record.get("operation_type", "unknown")
            summary["operations_by_type"][op_type] = summary["operations_by_type"].get(op_type, 0) + 1

        summary["users"] = list(summary["users"])
        return summary

    def load_logs(self):
        """加载日志（兼容旧接口，现在不需要加载到内存）"""
        self._init_database()
        self._start_async_writer()

    def export_logs(self, file_path: str = None) -> str:
        """导出日志到文件"""
        if file_path is None:
            safe_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"./data/audit_export_{safe_timestamp}.json"

        safe_path = self._sanitize_file_path(file_path)

        logs = self._get_logs_from_db(limit=100000)

        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(logs)
            },
            "logs": logs
        }

        try:
            with open(safe_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"导出审计日志失败: {e}")
            raise

        return safe_path

    def _sanitize_file_path(self, file_path: str) -> str:
        """安全的文件路径，防止路径遍历"""
        abs_data_dir = os.path.abspath("./data")
        safe_path = os.path.abspath(file_path)

        if not safe_path.startswith(abs_data_dir):
            filename = os.path.basename(file_path)
            return os.path.join(abs_data_dir, filename)

        return safe_path

    def clear_logs(self):
        """清空日志（仅清理文件，数据库需要单独处理）"""
        with self._instance_lock:
            self._write_queue.clear()

        log_file = "./data/audit_logs.jsonl"
        if os.path.exists(log_file):
            os.remove(log_file)
            print("✓ 审计日志文件已清空")

    def flush(self):
        """强制刷新所有待写入日志"""
        self._flush_to_database()

    def stop(self):
        """停止写入线程"""
        self._running = False
        self._flush_to_database()

    def get_pending_count(self) -> int:
        """获取待写入日志数量"""
        with self._instance_lock:
            return len(self._write_queue)


audit_logger = AuditLogger()
