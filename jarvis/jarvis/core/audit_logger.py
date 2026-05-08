import json
import os
import threading
import time
import asyncio
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
    """全局审计日志系统 - 直接写入数据库，无内存缓存（线程安全）
    
    特性：
    - 数据库不可用时自动降级到文件存储
    - 数据库恢复后自动从文件恢复数据
    - 文件恢复成功后自动删除临时文件
    """

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
            self._recovery_thread = None
            self._running = False
            self._write_queue: List[Dict[str, Any]] = []
            self._max_queue_size = 10000
            self._flush_interval = 1.0
            self._batch_size = 100
            self._recovery_interval = 30.0
            self._max_recovery_batch = 500
            self._log_file = "./data/audit_logs.jsonl"
            self._db_available = False
            self._last_db_check = 0
            self._db_check_interval = 5.0
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
                self._db_available = True
                print("✓ 审计日志数据库连接成功")
            except Exception as e:
                print(f"⚠️ 审计日志数据库连接失败: {e}")
                self._db = None
                self._db_available = False
                return False
        return True
    
    def _check_database_connection(self) -> bool:
        """检查数据库连接状态"""
        current_time = time.time()
        
        if current_time - self._last_db_check < self._db_check_interval:
            return self._db_available
        
        self._last_db_check = current_time
        
        if self._db is None:
            self._init_database()
        
        if self._db is None:
            self._db_available = False
            return False
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def check():
                async with self._db.get_session() as session:
                    from sqlalchemy import text
                    await session.execute(text("SELECT 1"))
                    return True
            
            loop.run_until_complete(check())
            loop.close()
            
            if not self._db_available:
                print("✓ 数据库连接已恢复，开始恢复文件数据...")
                self._db_available = True
            
            return True
            
        except Exception as e:
            if self._db_available:
                print(f"⚠️ 数据库连接丢失: {e}")
            self._db_available = False
            return False

    def _get_next_trace_id(self) -> str:
        """生成唯一追踪ID（线程安全）"""
        with self._counter_lock:
            AuditLogger._trace_counter += 1
            return f"{int(datetime.now().timestamp())}_{AuditLogger._trace_counter:06d}"

    def _start_async_writer(self):
        """启动异步写入线程"""
        if self._write_thread is None or not self._write_thread.is_alive():
            self._running = True
            self._write_thread = threading.Thread(target=self._writer_loop, daemon=True, name="audit_writer")
            self._write_thread.start()
        
        if self._recovery_thread is None or not self._recovery_thread.is_alive():
            self._recovery_thread = threading.Thread(target=self._recovery_loop, daemon=True, name="audit_recovery")
            self._recovery_thread.start()

    def _writer_loop(self):
        """后台写入循环"""
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
                time.sleep(1.0)
    
    def _recovery_loop(self):
        """数据库恢复循环 - 检查数据库连接并恢复文件数据"""
        while self._running:
            try:
                if self._check_database_connection():
                    self._recover_from_file()
                time.sleep(self._recovery_interval)
            except Exception as e:
                print(f"审计日志恢复线程异常: {e}")
                time.sleep(self._recovery_interval)
    
    def _recover_from_file(self):
        """从文件恢复数据到数据库"""
        if not os.path.exists(self._log_file):
            return
        
        file_size = os.path.getsize(self._log_file)
        if file_size == 0:
            return
        
        recovered_count = 0
        failed_count = 0
        remaining_records = []
        
        try:
            with open(self._log_file, "r", encoding="utf-8") as f:
                batch = []
                batch_size = 0
                
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        record = json.loads(line)
                        batch.append(record)
                        batch_size += 1
                        
                        if batch_size >= self._max_recovery_batch:
                            success = self._batch_insert_to_db(batch)
                            if success:
                                recovered_count += batch_size
                            else:
                                failed_count += batch_size
                                remaining_records.extend(batch)
                            batch = []
                            batch_size = 0
                            
                    except json.JSONDecodeError:
                        continue
                
                if batch:
                    success = self._batch_insert_to_db(batch)
                    if success:
                        recovered_count += batch_size
                    else:
                        failed_count += batch_size
                        remaining_records.extend(batch)
            
            if failed_count == 0 and recovered_count > 0:
                os.remove(self._log_file)
                print(f"✓ 审计日志已全部恢复 ({recovered_count} 条)，文件已删除")
            elif failed_count > 0:
                with open(self._log_file, "w", encoding="utf-8") as f:
                    for record in remaining_records:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"⚠️ 部分审计日志恢复失败 ({recovered_count} 成功, {failed_count} 失败)")
            else:
                print(f"✓ 审计日志恢复检查完成 (无待恢复数据)")
                
        except Exception as e:
            print(f"审计日志恢复过程异常: {e}")
    
    def _batch_insert_to_db(self, batch: List[Dict[str, Any]]) -> bool:
        """批量插入数据到数据库"""
        if not batch:
            return True
        
        if self._db is None:
            self._init_database()
        
        if self._db is None:
            return False
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def batch_insert():
                async with self._db.get_session() as session:
                    from jarvis.core.database import AuditLog

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
                    return True

            loop.run_until_complete(batch_insert())
            loop.close()
            return True

        except Exception as e:
            print(f"批量插入数据库失败: {e}")
            return False

    def _flush_to_database(self):
        """批量写入数据库"""
        if not self._write_queue:
            return

        if not self._check_database_connection():
            self._fallback_write_to_file()
            return

        batch = self._write_queue.copy()
        self._write_queue.clear()

        success = self._batch_insert_to_db(batch)
        
        if not success:
            self._write_queue.extend(batch)
            self._fallback_write_to_file()

    def _fallback_write_to_file(self):
        """回退到文件写入"""
        if self._write_queue:
            batch = self._write_queue.copy()
            self._write_queue.clear()
            self._write_batch_to_file(batch)

    def _write_batch_to_file(self, batch: List[Dict[str, Any]]):
        """批量写入文件"""
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
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
        if not os.path.exists(self._log_file):
            return []

        try:
            logs = []
            with open(self._log_file, "r", encoding="utf-8") as f:
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

        if os.path.exists(self._log_file):
            os.remove(self._log_file)
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
    
    def get_file_pending_count(self) -> int:
        """获取文件中待恢复的日志数量"""
        if not os.path.exists(self._log_file):
            return 0
        try:
            with open(self._log_file, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """获取审计日志系统状态"""
        return {
            "db_available": self._db_available,
            "queue_size": self.get_pending_count(),
            "file_pending_count": self.get_file_pending_count(),
            "log_file": self._log_file,
            "writer_running": self._write_thread.is_alive() if self._write_thread else False,
            "recovery_running": self._recovery_thread.is_alive() if self._recovery_thread else False
        }
    
    def force_recovery(self):
        """强制执行数据库恢复"""
        if self._check_database_connection():
            self._recover_from_file()
        else:
            print("⚠️ 数据库不可用，无法执行恢复")


audit_logger = AuditLogger()
