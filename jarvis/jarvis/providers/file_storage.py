"""文件存储实现 - 每个 session 一个目录"""

import os
import uuid
from datetime import datetime
from typing import List, Optional

from jarvis.core.interfaces import IStorage
from jarvis.config.settings import StorageConfig


class FileStorage(IStorage):
    """文件存储 - md 记录 + artifacts 产物"""

    def __init__(self, config: StorageConfig):
        self.config = config
        os.makedirs(config.session_dir, exist_ok=True)

    def create_session(self, task: str) -> str:
        session_id = f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        os.makedirs(self._session_path(session_id), exist_ok=True)
        os.makedirs(os.path.join(self._session_path(session_id), self.config.artifacts_dir_name), exist_ok=True)
        self.write_file(session_id, "meta.md", f"# 会话 {session_id}\n\n任务: {task}\n创建: {datetime.now().isoformat()}\n")
        return session_id

    def get_session_dir(self, session_id: str) -> str:
        return self._session_path(session_id)

    def write_file(self, session_id: str, filename: str, content: str) -> str:
        path = os.path.join(self._session_path(session_id), filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def read_file(self, session_id: str, filename: str) -> Optional[str]:
        path = os.path.join(self._session_path(session_id), filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def append_file(self, session_id: str, filename: str, content: str) -> str:
        path = os.path.join(self._session_path(session_id), filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return path

    def write_artifact(self, session_id: str, filename: str, content: str) -> str:
        return self.write_file(session_id, f"{self.config.artifacts_dir_name}/{filename}", content)

    def read_artifact(self, session_id: str, filename: str) -> Optional[str]:
        return self.read_file(session_id, f"{self.config.artifacts_dir_name}/{filename}")

    def list_artifacts(self, session_id: str) -> List[str]:
        path = os.path.join(self._session_path(session_id), self.config.artifacts_dir_name)
        if not os.path.exists(path):
            return []
        return sorted(os.listdir(path))

    def list_sessions(self, limit: int = 50) -> List[str]:
        if not os.path.exists(self.config.session_dir):
            return []
        entries = sorted(os.listdir(self.config.session_dir), reverse=True)
        return entries[:limit]

    def file_exists(self, session_id: str, filename: str) -> bool:
        return os.path.exists(os.path.join(self._session_path(session_id), filename))

    def _session_path(self, session_id: str) -> str:
        return os.path.join(self.config.session_dir, session_id)
