import os
import json
import threading
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from jarvis.core.database import AsyncDatabase


class GlobalLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            self._initialized = True

        self._initialized = True
        from jarvis.core.database import db as _db_instance
        self._db = _db_instance
        self.log_dir = "./logs"
        self.session_id = self._generate_session_id()
        self._lock = threading.Lock()
        self._pending_logs: List[Dict[str, Any]] = []
        self._write_thread: threading.Thread = None
        self._running = False
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        os.makedirs(self.log_dir, exist_ok=True)

    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")

    def _start_async_writer(self):
        if self._write_thread is None or not self._write_thread.is_alive():
            self._running = True
            self._write_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self._write_thread.start()

    def _writer_loop(self):
        import time
        last_flush_time = time.time()
        flush_interval = 1.0

        while self._running:
            try:
                current_time = time.time()
                should_flush = (
                    len(self._pending_logs) >= 100 or
                    (current_time - last_flush_time) >= flush_interval
                )

                if should_flush and self._pending_logs:
                    self._flush_to_db()
                    last_flush_time = current_time

                time.sleep(0.1)

            except Exception as e:
                print(f"日志写入线程异常: {e}")

    def _flush_to_db(self):
        if not self._pending_logs:
            return

        with self._lock:
            batch = self._pending_logs.copy()
            self._pending_logs.clear()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def batch_insert():
                async with self._db.get_session() as session:
                    from jarvis.core.database import AuditLog
                    from sqlalchemy import insert

                    records = [
                        AuditLog(
                            trace_id=log.get("trace_id", ""),
                            user_id=log.get("user_id", "system"),
                            agent_name=log.get("source"),
                            operation_type=log.get("level", "INFO"),
                            action=log.get("message"),
                            details={"data": log.get("data", {}), "session_id": log.get("session_id")},
                            result=None,
                            duration=None,
                            created_at=datetime.fromisoformat(log["timestamp"])
                        )
                        for log in batch
                    ]

                    session.add_all(records)
                    await session.commit()

            loop.run_until_complete(batch_insert())
            loop.close()

        except Exception as e:
            print(f"日志写入数据库失败: {e}, 尝试写入文件")
            self._write_batch_to_file(batch)

    def _write_batch_to_file(self, batch: List[Dict[str, Any]]):
        file_path = self._get_log_file_path()
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                for log in batch:
                    f.write(json.dumps(log, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"日志文件写入失败: {e}")

    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        self._start_async_writer()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id,
            "trace_id": f"{int(datetime.now().timestamp())}_{threading.get_ident():08d}"
        }

        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }

        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")

        with self._lock:
            self._pending_logs.append(log_entry)

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
        """获取最近的日志（从文件读取）"""
        logs = []
        file_path = self._get_log_file_path()

        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue

                return logs[-limit:]

            except Exception as e:
                print(f"读取日志文件失败: {e}")

        return logs

    def export_logs(self, file_path: str = None) -> str:
        """导出日志到文件"""
        if file_path is None:
            file_path = f"./logs/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "session_id": self.session_id,
                "total_entries": 0
            },
            "logs": self.get_logs(limit=100000)
        }

        export_data["metadata"]["total_entries"] = len(export_data["logs"])

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return file_path

    def flush(self):
        """强制刷新待写入日志"""
        self._flush_to_db()

    def stop(self):
        """停止日志写入线程"""
        self._running = False
        self._flush_to_db()

        if self._write_thread and self._write_thread.is_alive():
            self._write_thread.join(timeout=2.0)


logger = GlobalLogger()
