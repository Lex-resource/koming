import sqlite3
import json
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class PersistentStore:
    """SQLite持久化存储 - 优化版"""
    
    def __init__(self, db_path: str = "./data/jarvis.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._stmt_cache = {}
        self._init_optimizations()
        self._init_db()

    def _init_optimizations(self):
        """初始化数据库优化设置"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-64000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=268435456")
            conn.commit()
        finally:
            conn.close()

    def _get_connection(self):
        """获取数据库连接的上下文管理器 - 线程本地连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        return self._local.conn
    
    @contextmanager
    def _transaction(self):
        """事务上下文管理器"""
        conn = self._get_connection()
        try:
            yield conn.cursor()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    response TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    user_id TEXT,
                    agent_name TEXT,
                    action TEXT,
                    details TEXT,
                    result TEXT,
                    duration REAL,
                    trace_id TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    source TEXT,
                    content TEXT,
                    metadata TEXT,
                    tags TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user
                ON conversations(user_id, timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp
                ON audit_logs(timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_data_category
                ON data_records(category, timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_operation
                ON audit_logs(operation_type, timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_agent
                ON audit_logs(agent_name, timestamp)
            """)

            conn.commit()

    def _get_connection(self):
        """获取数据库连接的上下文管理器 - 线程本地连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        yield self._local.conn

    def save_conversation(self, user_id: str, user_input: str, response: str,
                        metadata: Dict = None) -> int:
        """保存对话记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (user_id, user_input, response, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, user_input, response, datetime.now().isoformat(),
                  json.dumps(metadata, ensure_ascii=False) if metadata else None))
            conn.commit()
            return cursor.lastrowid

    def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """获取用户对话记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def save_audit_log(self, operation_type: str, user_id: str = None,
                       agent_name: str = None, action: str = None,
                       details: Dict = None, result: Any = None,
                       duration: float = None, trace_id: str = None) -> int:
        """保存审计日志"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs
                (operation_type, user_id, agent_name, action, details, result, duration, trace_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (operation_type, user_id, agent_name, action,
                  json.dumps(details, ensure_ascii=False) if details else None,
                  str(result)[:500] if result else None,
                  duration, trace_id, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_audit_logs(self, operation_type: str = None, agent_name: str = None,
                       user_id: str = None, limit: int = 100) -> List[Dict]:
        """查询审计日志"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []

            if operation_type:
                query += " AND operation_type = ?"
                params.append(operation_type)
            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def save_data_record(self, record_id: str, category: str, source: str,
                         content: Any, metadata: Dict = None,
                         tags: List[str] = None) -> int:
        """保存数据记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO data_records
                (record_id, category, source, content, metadata, tags, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (record_id, category, source,
                  json.dumps(content, ensure_ascii=False),
                  json.dumps(metadata, ensure_ascii=False) if metadata else None,
                  json.dumps(tags, ensure_ascii=False) if tags else None,
                  datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_data_records(self, category: str = None, source: str = None,
                         limit: int = 100) -> List[Dict]:
        """查询数据记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM data_records WHERE 1=1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)
            if source:
                query += " AND source = ?"
                params.append(source)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def save_system_state(self, key: str, value: Any) -> None:
        """保存系统状态"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_state (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value, ensure_ascii=False), datetime.now().isoformat()))
            conn.commit()

    def get_system_state(self, key: str) -> Optional[Any]:
        """获取系统状态"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
            row = cursor.fetchone()
            return json.loads(row['value']) if row else None

    def get_statistics(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM conversations")
            stats['total_conversations'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM audit_logs")
            stats['total_audit_logs'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM data_records")
            stats['total_data_records'] = cursor.fetchone()['count']

            return stats

    def clear_old_records(self, days: int = 30) -> int:
        """清理指定天数之前的记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cutoff = datetime.now().isoformat()

            cursor.execute("""
                DELETE FROM conversations
                WHERE timestamp < datetime(?, '-' || ? || ' days')
            """, (cutoff, days))

            cursor.execute("""
                DELETE FROM audit_logs
                WHERE timestamp < datetime(?, '-' || ? || ' days')
            """, (cutoff, days))

            cursor.execute("""
                DELETE FROM data_records
                WHERE timestamp < datetime(?, '-' || ? || ' days')
            """, (cutoff, days))

            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def vacuum(self):
        """压缩数据库"""
        with self._get_connection() as conn:
            conn.execute("VACUUM")


persistent_store = PersistentStore()
