import os
from chromadb import Client
from chromadb.config import Settings as ChromaSettings
from jarvis.config.settings import Settings


class MemoryManager:
    def __init__(self):
        os.makedirs(Settings.MEMORY_CHROMA_PATH, exist_ok=True)
        self.client = Client(
            settings=ChromaSettings(
                persist_directory=Settings.MEMORY_CHROMA_PATH,
                anonymized_telemetry=False
            )
        )
        self.collection = self.client.get_or_create_collection("jarvis_memory")

    def add_memory(self, content: str, metadata: dict = None):
        """
        添加记忆到知识库
        
        Args:
            content: 记忆内容
            metadata: 元数据（可选）
        """
        if metadata is None:
            metadata = {}
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[f"memory_{len(self.collection.get()['ids']) + 1}"]
        )
        self.client.persist()

    def search_memory(self, query: str, n_results: int = 3) -> list:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            n_results: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        memories = []
        for i, doc in enumerate(results["documents"][0]):
            memories.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else None,
                "distance": results["distances"][0][i] if results["distances"] else None
            })
        
        return memories

    def get_all_memories(self) -> list:
        """
        获取所有记忆
        
        Returns:
            所有记忆列表
        """
        results = self.collection.get()
        memories = []
        for i, doc in enumerate(results["documents"]):
            memories.append({
                "id": results["ids"][i],
                "content": doc,
                "metadata": results["metadatas"][i] if results["metadatas"] else None
            })
        return memories

    def clear_all_memories(self):
        """
        清空所有记忆
        """
        self.collection.delete(ids=self.collection.get()["ids"])
        self.client.persist()