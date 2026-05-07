from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from langchain.embeddings import OpenAIEmbeddings
from typing import List, Dict, Optional
import numpy as np
import os
from jarvis.config.settings import Settings


class MemoryManager:
    """Milvus向量数据库记忆管理器 - HNSW极速版，支持降级到内存存储"""

    def __init__(self, collection_name: str = "jarvis_memory"):
        self.collection_name = collection_name
        self.embedding_dim = 1536
        self.collection = None
        self._connected = False
        self._fallback_memories: List[Dict] = []
        self._memory_id_counter = 0

        self.connections = connections

        try:
            self.connections.connect(
                alias="default",
                host=os.getenv("MILVUS_HOST", "localhost"),
                port=os.getenv("MILVUS_PORT", "19530")
            )
            self._init_collection()
            self._connected = True
            print("✓ Milvus向量数据库连接成功")
        except Exception as e:
            print(f"⚠️ Milvus连接失败，使用内存存储: {e}")
            self._connected = False

        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        except Exception as e:
            print(f"⚠️ 嵌入服务初始化失败: {e}")
            self.embeddings = None

    def _init_collection(self):
        """初始化Milvus集合 - HNSW索引"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            self.collection.load()
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="memory_id", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
                FieldSchema(name="metadata", dtype=DataType.JSON)
            ]
            
            schema = CollectionSchema(fields=fields, description="JARVIS Memory Collection - HNSW Optimized")
            self.collection = Collection(name=self.collection_name, schema=schema)
            
            # HNSW索引 - 搜索速度提升100倍
            index_params = {
                "metric_type": "L2",
                "index_type": "HNSW",  # 极速索引
                "params": {
                    "M": 16,              # 邻居数，平衡精度和速度
                    "efConstruction": 200  # 构建深度，精度
                }
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
            self.collection.load()

    def add_memory(self, content: str, memory_id: str = None, metadata: Dict = None) -> str:
        """添加记忆到向量数据库（支持降级到内存存储）"""
        if memory_id is None:
            self._memory_id_counter += 1
            memory_id = f"memory_{self._memory_id_counter}"

        if metadata is None:
            metadata = {}

        if self._connected and self.collection:
            try:
                embedding = self._get_embedding(content)

                entities = [
                    [memory_id],
                    [content],
                    [embedding],
                    [metadata]
                ]

                self.collection.insert(entities)
                self.collection.flush()

                return memory_id
            except Exception as e:
                print(f"⚠️ Milvus写入失败，降级到内存存储: {e}")
                self._connected = False

        self._fallback_memories.append({
            "memory_id": memory_id,
            "content": content,
            "metadata": metadata
        })
        return memory_id

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        if self.embeddings:
            return self.embeddings.embed_query(text)
        else:
            raise RuntimeError("嵌入服务未初始化，请检查OPENAI_API_KEY配置")

    def search_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """极速搜索记忆 - HNSW优化，支持降级"""
        if self._connected and self.collection:
            try:
                query_embedding = self._get_embedding(query)

                search_params = {
                    "metric_type": "L2",
                    "params": {"ef": 100}
                }

                results = self.collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    output_fields=["memory_id", "content", "metadata"]
                )

                memories = []
                for hits in results:
                    for hit in hits:
                        memories.append({
                            "id": hit.id,
                            "memory_id": hit.entity.get("memory_id"),
                            "content": hit.entity.get("content"),
                            "metadata": hit.entity.get("metadata"),
                            "distance": hit.distance
                        })

                return memories
            except Exception as e:
                print(f"⚠️ Milvus搜索失败，降级到内存搜索: {e}")
                self._connected = False

        return self._fallback_search(query, top_k)

    def _fallback_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """内存降级搜索"""
        if not self._fallback_memories:
            return []

        query_lower = query.lower()
        results = []

        for memory in self._fallback_memories:
            content_lower = memory.get("content", "").lower()
            distance = 1.0 - (sum(1 for word in query_lower.split() if word in content_lower) / max(len(query_lower.split()), 1))
            results.append({
                "memory_id": memory.get("memory_id"),
                "content": memory.get("content"),
                "metadata": memory.get("metadata"),
                "distance": distance
            })

        results.sort(key=lambda x: x["distance"])
        return results[:top_k]

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict]:
        """根据ID获取记忆"""
        if self._connected and self.collection:
            try:
                results = self.collection.query(
                    expr=f'memory_id == "{memory_id}"',
                    output_fields=["memory_id", "content", "metadata"]
                )

                if results:
                    result = results[0]
                    return {
                        "memory_id": result.get("memory_id"),
                        "content": result.get("content"),
                        "metadata": result.get("metadata")
                    }
            except Exception as e:
                print(f"⚠️ Milvus查询失败: {e}")
                self._connected = False

        for memory in self._fallback_memories:
            if memory.get("memory_id") == memory_id:
                return memory
        return None

    def get_all_memories(self, limit: int = 1000) -> List[Dict]:
        """获取所有记忆"""
        if self._connected and self.collection:
            try:
                results = self.collection.query(
                    expr="id > 0",
                    limit=limit,
                    output_fields=["memory_id", "content", "metadata"]
                )

                memories = []
                for result in results:
                    memories.append({
                        "memory_id": result.get("memory_id"),
                        "content": result.get("content"),
                        "metadata": result.get("metadata")
                    })

                return memories
            except Exception as e:
                print(f"⚠️ Milvus查询失败: {e}")
                self._connected = False

        return self._fallback_memories[:limit]

    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        for i, memory in enumerate(self._fallback_memories):
            if memory.get("memory_id") == memory_id:
                del self._fallback_memories[i]
                return True

        if self._connected and self.collection:
            try:
                expr = f'memory_id == "{memory_id}"'
                self.collection.delete(expr)
                self.collection.flush()
                return True
            except Exception as e:
                print(f"⚠️ Milvus删除失败: {e}")
                return False

        return False

    def clear_all_memories(self):
        """清空所有记忆"""
        self._fallback_memories.clear()

        if self._connected and self.collection:
            try:
                expr = "id > 0"
                self.collection.delete(expr)
                self.collection.flush()
            except Exception as e:
                print(f"⚠️ Milvus清空失败: {e}")

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        if self._connected and self.collection:
            try:
                return self.collection.num_entities
            except Exception:
                pass

        return len(self._fallback_memories)

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            "collection_name": self.collection_name,
            "total_memories": self.get_memory_count(),
            "embedding_dim": self.embedding_dim,
            "storage_mode": "memory" if not self._connected else "milvus",
            "fallback_count": len(self._fallback_memories)
        }

        if self._connected and self.collection:
            stats["index_type"] = "HNSW"
            stats["index_params"] = {
                "M": 16,
                "efConstruction": 200,
                "efSearch": 100
            }

        return stats

    def close(self):
        """关闭连接"""
        if self._connected:
            try:
                self.connections.disconnect("default")
            except Exception:
                pass
        self._connected = False


memory_manager = MemoryManager()
