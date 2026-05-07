import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from jarvis.core.database import AsyncDatabase


class DataCategory(Enum):
    """数据分类枚举"""
    WEATHER = "weather"
    SEARCH = "search"
    DEVICE = "device"
    KNOWLEDGE = "knowledge"
    ANALYSIS = "analysis"
    USER_INPUT = "user_input"
    SYSTEM = "system"


class DataStore:
    """数据分类存储系统 - PostgreSQL增量保存版"""
    
    _instance = None
    _init_lock = __import__('threading').Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        from jarvis.core.database import db as _db_instance
        self._db = _db_instance
    
    def add_record(
        self,
        category: DataCategory,
        source: str,
        content: Any,
        metadata: Dict = None,
        tags: List[str] = None
    ) -> str:
        """添加数据记录（同步接口，内部异步执行）"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.ensure_future(
                    self._add_record_async(category, source, content, metadata, tags)
                )
                try:
                    return future.result(timeout=5.0)
                except asyncio.TimeoutError:
                    return f"data_{uuid.uuid4().hex[:12]}"
            else:
                return loop.run_until_complete(
                    self._add_record_async(category, source, content, metadata, tags)
                )
        except RuntimeError:
            return asyncio.run(
                self._add_record_async(category, source, content, metadata, tags)
            )
    
    async def _add_record_async(
        self,
        category: DataCategory,
        source: str,
        content: Any,
        metadata: Dict = None,
        tags: List[str] = None
    ) -> str:
        """异步添加数据记录"""
        record_id = f"data_{uuid.uuid4().hex[:12]}"
        
        record = await self._db.add_data_record(
            record_id=record_id,
            category=category.value,
            source=source,
            content={"content": content, "metadata": metadata} if metadata else {"content": content},
            metadata=metadata,
            tags=tags
        )
        
        return record["id"]
    
    async def get_records_by_category(self, category: DataCategory, limit: int = 100) -> List[Dict]:
        records = await self._db.get_data_records(category=category.value, limit=limit)
        return records
    
    async def get_records_by_source(self, source: str, limit: int = 100) -> List[Dict]:
        records = await self._db.get_data_records(source=source, limit=limit)
        return records
    
    async def get_records_by_tag(self, tag: str, limit: int = 100) -> List[Dict]:
        all_records = await self._db.get_data_records(limit=limit * 10)
        return [r for r in all_records if tag in (r.get("tags") or [])][:limit]
    
    async def get_records_by_time_range(
        self,
        start_time: str = None,
        end_time: str = None,
        limit: int = 100
    ) -> List[Dict]:
        all_records = await self._db.get_data_records(limit=limit)
        filtered = all_records
        
        if start_time:
            filtered = [r for r in filtered if r.get("created_at", "") >= start_time]
        if end_time:
            filtered = [r for r in filtered if r.get("created_at", "") <= end_time]
        
        return filtered[:limit]
    
    async def get_statistics(self, category: DataCategory = None) -> Dict[str, Any]:
        records = await self._db.get_data_records(
            category=category.value if category else None,
            limit=10000
        )
        
        stats = {
            "total_records": len(records),
            "categories": {},
            "sources": {},
            "tags": {},
            "time_range": {"earliest": None, "latest": None}
        }
        
        timestamps = []
        
        for record in records:
            cat = record.get("category", "unknown")
            src = record.get("source", "unknown")
            rec_tags = record.get("tags") or []
            created = record.get("created_at")
            
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
            stats["sources"][src] = stats["sources"].get(src, 0) + 1
            
            for tag in rec_tags:
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1
            
            if created:
                timestamps.append(created)
        
        if timestamps:
            stats["time_range"]["earliest"] = min(timestamps)
            stats["time_range"]["latest"] = max(timestamps)
        
        return stats
    
    async def get_category_statistics(self) -> Dict[str, int]:
        stats = await self.get_statistics()
        return stats["categories"]
    
    async def get_source_statistics(self) -> Dict[str, int]:
        stats = await self.get_statistics()
        return stats["sources"]
    
    async def clear_store(self):
        pass


data_store = DataStore()
