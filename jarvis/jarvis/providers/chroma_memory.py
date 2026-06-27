"""ChromaDB 向量记忆实现 - 真实向量检索

依赖 chromadb 和 ILLM.get_embedding()
安装: pip install chromadb
"""

import os
import uuid
from typing import Dict, List, Optional

from jarvis.core.interfaces import ILLM, IMemory
from jarvis.config.settings import MemoryConfig


class ChromaMemory(IMemory):
    """ChromaDB 向量记忆 - 真实 embedding + 向量相似度检索"""

    def __init__(self, config: MemoryConfig, llm: ILLM):
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError as e:
            raise ImportError(
                "chromadb 未安装。请运行: pip install chromadb\n"
                f"原始错误: {e}"
            ) from e

        self.config = config
        self.llm = llm
        self._embedding_dim = config.embedding_dim

        # 持久化目录
        persist_path = config.persist_path or "./data/vector_store"
        os.makedirs(persist_path, exist_ok=True)

        # 初始化 Chroma 客户端
        self._client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False),
        )

        # 获取或创建 collection
        collection_name = config.collection_name or "jarvis_experience"
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, content: str, metadata: Optional[Dict] = None, memory_id: Optional[str] = None) -> str:
        """添加记忆 - 自动生成 embedding"""
        mid = memory_id or f"mem_{uuid.uuid4().hex[:12]}"
        embedding = self.llm.get_embedding(content)

        # chromadb 要求 metadata 值为基本类型，序列化复杂结构
        clean_meta = self._clean_metadata(metadata or {})

        self._collection.add(
            ids=[mid],
            documents=[content],
            embeddings=[embedding],
            metadatas=[clean_meta],
        )
        return mid

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """向量相似度检索"""
        if self._collection.count() == 0:
            return []

        query_embedding = self.llm.get_embedding(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        # 解析结果
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # 反序列化 metadata
        out = []
        for i, doc_id in enumerate(ids):
            meta = metadatas[i] if i < len(metadatas) else {}
            meta = self._restore_metadata(meta)
            out.append({
                "memory_id": doc_id,
                "content": documents[i] if i < len(documents) else "",
                "metadata": meta,
                "distance": distances[i] if i < len(distances) else 0.0,
            })
        return out

    def delete(self, memory_id: str) -> bool:
        try:
            self._collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def get(self, memory_id: str) -> Optional[Dict]:
        try:
            results = self._collection.get(ids=[memory_id], include=["documents", "metadatas"])
            if not results.get("ids"):
                return None
            idx = 0
            return {
                "memory_id": results["ids"][idx],
                "content": results["documents"][idx] if results["documents"] else "",
                "metadata": self._restore_metadata(results["metadatas"][idx] or {}) if results["metadatas"] else {},
            }
        except Exception:
            return None

    def count(self) -> int:
        try:
            return self._collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        """清空 collection（删除后重建）"""
        name = self._collection.name
        try:
            self._client.delete_collection(name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    # ============ 内部工具 ============

    @staticmethod
    def _clean_metadata(meta: Dict) -> Dict:
        """chromadb 要求 metadata 值为 str/int/float/bool/None，复杂结构序列化"""
        import json
        clean = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                clean[k] = v
            else:
                clean[k] = json.dumps(v, ensure_ascii=False)
        return clean

    @staticmethod
    def _restore_metadata(meta: Dict) -> Dict:
        """反序列化 JSON 字符串"""
        import json
        out = {}
        for k, v in meta.items():
            if isinstance(v, str) and v.startswith(("{", "[")):
                try:
                    out[k] = json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    out[k] = v
            else:
                out[k] = v
        return out
