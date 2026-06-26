"""SQLite 数据库实现 - 结构化数据持久化（Profile/Skill/Session）"""

import json
import sqlite3
import threading
from typing import List, Optional

from jarvis.core.interfaces import IDatabase
from jarvis.core.models import AgentProfile, Skill, SessionMeta, TaskStatus
from jarvis.config.settings import DatabaseConfig


class SQLiteDatabase(IDatabase):
    """SQLite 数据库 - 单文件，零配置"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._local = threading.local()
        self._init_lock = threading.Lock()
        self._initialized = False

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            # 处理 sqlite:///path → path
            url = self.config.url.replace("sqlite:///", "").replace("sqlite://", "")
            self._local.conn = sqlite3.connect(url, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def init_db(self) -> None:
        with self._init_lock:
            if self._initialized:
                return
            conn = self._conn()
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                agent_id TEXT PRIMARY KEY,
                role TEXT UNIQUE,
                data TEXT NOT NULL,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS skills (
                skill_id TEXT PRIMARY KEY,
                trigger TEXT,
                data TEXT NOT NULL,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                task TEXT,
                status TEXT,
                data TEXT NOT NULL,
                created_at TEXT
            );
            """)
            conn.commit()
            self._initialized = True

    # ===== Profile =====

    def save_profile(self, profile: AgentProfile) -> bool:
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO profiles (agent_id, role, data, updated_at) VALUES (?, ?, ?, ?)",
            (profile.agent_id, profile.role, json.dumps(profile.to_dict(), ensure_ascii=False),
             __import__("datetime").datetime.now().isoformat()),
        )
        conn.commit()
        return True

    def get_profile(self, role: str) -> Optional[AgentProfile]:
        conn = self._conn()
        row = conn.execute("SELECT data FROM profiles WHERE role = ?", (role,)).fetchone()
        return AgentProfile.from_dict(json.loads(row["data"])) if row else None

    def list_profiles(self) -> List[AgentProfile]:
        conn = self._conn()
        rows = conn.execute("SELECT data FROM profiles").fetchall()
        return [AgentProfile.from_dict(json.loads(r["data"])) for r in rows]

    def delete_profile(self, agent_id: str) -> bool:
        conn = self._conn()
        cur = conn.execute("DELETE FROM profiles WHERE agent_id = ?", (agent_id,))
        conn.commit()
        return cur.rowcount > 0

    # ===== Skill =====

    def save_skill(self, skill: Skill) -> bool:
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO skills (skill_id, trigger, data, updated_at) VALUES (?, ?, ?, ?)",
            (skill.skill_id, skill.trigger, json.dumps(skill.to_dict(), ensure_ascii=False),
             __import__("datetime").datetime.now().isoformat()),
        )
        conn.commit()
        return True

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        conn = self._conn()
        row = conn.execute("SELECT data FROM skills WHERE skill_id = ?", (skill_id,)).fetchone()
        return Skill.from_dict(json.loads(row["data"])) if row else None

    def list_skills(self) -> List[Skill]:
        conn = self._conn()
        rows = conn.execute("SELECT data FROM skills").fetchall()
        return [Skill.from_dict(json.loads(r["data"])) for r in rows]

    def delete_skill(self, skill_id: str) -> bool:
        conn = self._conn()
        cur = conn.execute("DELETE FROM skills WHERE skill_id = ?", (skill_id,))
        conn.commit()
        return cur.rowcount > 0

    # ===== Session =====

    def save_session(self, session: SessionMeta) -> bool:
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id, task, status, data, created_at) VALUES (?, ?, ?, ?, ?)",
            (session.session_id, session.task, session.status.value,
             json.dumps(session.to_dict(), ensure_ascii=False), session.created_at),
        )
        conn.commit()
        return True

    def get_session(self, session_id: str) -> Optional[SessionMeta]:
        conn = self._conn()
        row = conn.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return None
        data = json.loads(row["data"])
        data["status"] = TaskStatus(data["status"])
        return SessionMeta(**data)

    def list_sessions(self, limit: int = 50) -> List[SessionMeta]:
        conn = self._conn()
        rows = conn.execute("SELECT data FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for r in rows:
            data = json.loads(r["data"])
            data["status"] = TaskStatus(data["status"])
            result.append(SessionMeta(**data))
        return result
