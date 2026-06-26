"""内存向量记忆实现 - 零依赖，关键词检索降级"""

import uuid
from typing import Dict, List, Optional

from jarvis.core.interfaces import IMemory


class InMemoryVectorStore(IMemory):
    """内存向量记忆 - 关键词匹配降级（无 embedding 模型时用）"""

    def __init__(self):
        self._memories: Dict[str, Dict] = {}

    def add(self, content: str, metadata: Optional[Dict] = None, memory_id: Optional[str] = None) -> str:
        mid = memory_id or f"mem_{uuid.uuid4().hex[:12]}"
        self._memories[mid] = {
            "memory_id": mid,
            "content": content,
            "metadata": metadata or {},
        }
        return mid

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        # 降级为关键词匹配 + 字段权重
        query_lower = query.lower()
        scored = []
        for mem in self._memories.values():
            content_lower = mem["content"].lower()
            meta_str = str(mem.get("metadata", {})).lower()
            score = 0
            for kw in query_lower.split():
                if len(kw) < 2:
                    continue
                score += content_lower.count(kw) * 2
                score += meta_str.count(kw)
            if score > 0:
                scored.append({**mem, "distance": 1.0 / (1 + score)})
        scored.sort(key=lambda x: x["distance"])
        return scored[:top_k]

    def delete(self, memory_id: str) -> bool:
        return self._memories.pop(memory_id, None) is not None

    def get(self, memory_id: str) -> Optional[Dict]:
        return self._memories.get(memory_id)

    def count(self) -> int:
        return len(self._memories)

    def clear(self) -> None:
        self._memories.clear()
