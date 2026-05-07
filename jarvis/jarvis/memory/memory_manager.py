from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from langchain.embeddings import OpenAIEmbeddings
from typing import List, Dict, Optional
import numpy as np
import os
from jarvis.config.settings import Settings


class MemoryManager:
    """Milvus向量数据库记忆管理器 - HNSW极速版"""

    def __init__(self, collection_name: str = "jarvis_memory"):
        self.collection_name = collection_name
        self.embedding_dim = 1536
        
        self.connections = connections
        self.connections.connect(
            alias="default",
            host=os.getenv("MILVUS_HOST", "localhost"),
            port=os.getenv("MILVUS_PORT", "19530")
        )
        
        self._init_collection()
        
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        except Exception as e:
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
        """添加记忆到向量数据库"""
        if memory_id is None:
            memory_id = f"memory_{int(np.random.randint(0, 1000000))}"
        
        if metadata is None:
            metadata = {}
        
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

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        if self.embeddings:
            return self.embeddings.embed_query(text)
        else:
            raise RuntimeError("嵌入服务未初始化，请检查OPENAI_API_KEY配置")

    def search_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """极速搜索记忆 - HNSW优化"""
        query_embedding = self._get_embedding(query)
        
        # HNSW搜索参数 - ef=100保证速度和精度
        search_params = {
            "metric_type": "L2",
            "params": {"ef": 100}  # 搜索深度，越大越精准但越慢
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

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict]:
        """根据ID获取记忆"""
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
        return None

    def get_all_memories(self, limit: int = 1000) -> List[Dict]:
        """获取所有记忆"""
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

    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        try:
            expr = f'memory_id == "{memory_id}"'
            self.collection.delete(expr)
            self.collection.flush()
            return True
        except Exception:
            return False

    def clear_all_memories(self):
        """清空所有记忆"""
        expr = "id > 0"
        self.collection.delete(expr)
        self.collection.flush()

    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return self.collection.num_entities

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "collection_name": self.collection_name,
            "total_memories": self.collection.num_entities,
            "embedding_dim": self.embedding_dim,
            "index_type": "HNSW",
            "index_params": {
                "M": 16,
                "efConstruction": 200,
                "efSearch": 100
            }
        }

    def close(self):
        """关闭连接"""
        self.connections.disconnect("default")


memory_manager = MemoryManager()
