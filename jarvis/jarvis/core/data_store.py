import json
import os
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class DataCategory(Enum):
    """数据分类枚举"""
    WEATHER = "weather"
    SEARCH = "search"
    DEVICE = "device"
    KNOWLEDGE = "knowledge"
    ANALYSIS = "analysis"
    USER_INPUT = "user_input"
    SYSTEM = "system"


class DataRecord:
    """数据记录类"""
    
    def __init__(
        self,
        category: DataCategory,
        source: str,
        content: Any,
        metadata: Dict = None,
        tags: List[str] = None
    ):
        self.id = self._generate_id()
        self.category = category.value
        self.source = source
        self.content = content
        self.metadata = metadata or {}
        self.tags = tags or []
        self.timestamp = datetime.now().isoformat()
    
    def _generate_id(self) -> str:
        return f"data_{int(datetime.now().timestamp())}_{os.urandom(4).hex()}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata,
            "tags": self.tags,
            "timestamp": self.timestamp
        }


class DataStore:
    """数据分类存储系统 - 分门别类存储所有查询数据"""
    
    def __init__(self):
        self.records: List[DataRecord] = []
        self._store_file = "./data/data_store.json"
        self._ensure_data_dir()
        self._lock = threading.Lock()
        self._write_queue = asyncio.Queue()
        self._start_async_writer()
    
    def _start_async_writer(self):
        """启动异步写入线程"""
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer_thread.start()
    
    def _writer_loop(self):
        """后台写入循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_write_loop())
    
    async def _async_write_loop(self):
        """异步写入循环"""
        while True:
            records = await self._write_queue.get()
            try:
                data = [r.to_dict() for r in records]
                with open(self._store_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存数据存储失败: {e}")
            self._write_queue.task_done()
    
    def _ensure_data_dir(self):
        os.makedirs("./data", exist_ok=True)
    
    def add_record(
        self,
        category: DataCategory,
        source: str,
        content: Any,
        metadata: Dict = None,
        tags: List[str] = None
    ) -> str:
        """
        添加数据记录
        
        Args:
            category: 数据分类
            source: 数据来源（智能体名称或工具名称）
            content: 数据内容
            metadata: 元数据
            tags: 标签列表
        
        Returns:
            记录ID
        """
        record = DataRecord(category, source, content, metadata, tags)
        with self._lock:
            self.records.append(record)
        self._schedule_save()
        return record.id
    
    def _schedule_save(self):
        """调度异步保存"""
        with self._lock:
            records_copy = list(self.records)
        self._write_queue.put_nowait(records_copy)
    
    def get_records_by_category(self, category: DataCategory) -> List[DataRecord]:
        """按分类查询数据"""
        return [r for r in self.records if r.category == category.value]
    
    def get_records_by_source(self, source: str) -> List[DataRecord]:
        """按来源查询数据"""
        return [r for r in self.records if r.source == source]
    
    def get_records_by_tag(self, tag: str) -> List[DataRecord]:
        """按标签查询数据"""
        return [r for r in self.records if tag in r.tags]
    
    def get_records_by_time_range(self, start_time: str = None, end_time: str = None) -> List[DataRecord]:
        """按时间范围查询数据"""
        filtered = self.records
        if start_time:
            filtered = [r for r in filtered if r.timestamp >= start_time]
        if end_time:
            filtered = [r for r in filtered if r.timestamp <= end_time]
        return filtered
    
    def get_statistics(self, category: DataCategory = None) -> Dict[str, Any]:
        """获取数据统计信息"""
        records = self.records
        if category:
            records = [r for r in records if r.category == category.value]
        
        stats = {
            "total_records": len(records),
            "categories": {},
            "sources": {},
            "tags": {},
            "time_range": {
                "earliest": None,
                "latest": None
            }
        }
        
        if records:
            timestamps = [r.timestamp for r in records]
            stats["time_range"]["earliest"] = min(timestamps)
            stats["time_range"]["latest"] = max(timestamps)
        
        for record in records:
            stats["categories"][record.category] = stats["categories"].get(record.category, 0) + 1
            stats["sources"][record.source] = stats["sources"].get(record.source, 0) + 1
            
            for tag in record.tags:
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1
        
        return stats
    
    def get_category_statistics(self) -> Dict[str, int]:
        """获取各分类数据统计"""
        stats = {}
        for record in self.records:
            stats[record.category] = stats.get(record.category, 0) + 1
        return stats
    
    def get_source_statistics(self) -> Dict[str, int]:
        """获取各来源数据统计"""
        stats = {}
        for record in self.records:
            stats[record.source] = stats.get(record.source, 0) + 1
        return stats
    
    def export_records(self, category: DataCategory = None, file_path: str = None) -> str:
        """导出数据记录"""
        records = self.records
        if category:
            records = [r for r in records if r.category == category.value]
        
        if file_path is None:
            category_suffix = f"_{category.value}" if category else ""
            file_path = f"./data/data_export{category_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(records),
                "category_filter": category.value if category else "all"
            },
            "records": [r.to_dict() for r in records]
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load_store(self):
        """从文件加载数据存储"""
        if os.path.exists(self._store_file):
            try:
                with open(self._store_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = []
                    for item in data:
                        record = DataRecord(
                            category=DataCategory(item["category"]),
                            source=item["source"],
                            content=item["content"],
                            metadata=item.get("metadata", {}),
                            tags=item.get("tags", [])
                        )
                        record.id = item["id"]
                        record.timestamp = item["timestamp"]
                        self.records.append(record)
            except Exception as e:
                print(f"加载数据存储失败: {e}")
    
    def clear_store(self):
        """清空数据存储"""
        self.records = []
        if os.path.exists(self._store_file):
            os.remove(self._store_file)


data_store = DataStore()