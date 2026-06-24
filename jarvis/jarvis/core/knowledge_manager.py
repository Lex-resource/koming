"""
学习与知识库系统 - 实现 frame.html 3.5 节描述的知识管理能力

本模块为贾维斯提供持续学习和知识积累的能力，包含以下核心组件：
- KnowledgeEntity：知识实体，描述图谱中的节点
- KnowledgeRelation：知识关系，描述实体间的边
- KnowledgeGraph：内存图数据库，支持实体/关系的增删改查与路径推理
- LearningProfile：用户学习画像，记录偏好与行为模式
- KnowledgeManager：知识管理器（单例），整合向量记忆、知识图谱与用户画像

架构对应 frame.html 3.5 节：
    用户交互层 -> 知识处理层（实体抽取/向量化/偏好学习） -> 知识存储层（Milvus + 图谱）
"""

import re
import uuid
import threading
from datetime import datetime
from enum import Enum
from collections import deque
from typing import Dict, List, Any, Optional, Tuple

from jarvis.core.audit_logger import audit_logger, OperationType


# =============================================================================
# 枚举定义
# =============================================================================

class EntityType(Enum):
    """知识实体类型枚举"""
    PERSON = "person"            # 人物
    LOCATION = "location"        # 位置
    ORGANIZATION = "organization"  # 组织
    CONCEPT = "concept"          # 概念
    EVENT = "event"              # 事件
    DEVICE = "device"            # 设备
    CUSTOM = "custom"            # 自定义


class RelationType(Enum):
    """知识关系类型枚举"""
    BELONGS_TO = "belongs_to"    # 隶属于
    LOCATED_AT = "located_at"    # 位于
    CREATED_BY = "created_by"    # 由...创建
    RELATED_TO = "related_to"    # 相关于
    CONTROLS = "controls"        # 控制
    CUSTOM = "custom"            # 自定义


# =============================================================================
# 知识实体
# =============================================================================

class KnowledgeEntity:
    """知识实体 - 知识图谱中的节点

    描述一个具体的知识对象，例如人物、位置、设备、概念等。

    Attributes:
        id: 实体唯一标识
        name: 实体名称
        entity_type: 实体类型（EntityType）
        properties: 实体属性字典
        source: 知识来源（如对话、文档等）
        confidence: 置信度（0.0 ~ 1.0）
        created_at: 创建时间（ISO 格式字符串）
    """

    def __init__(
        self,
        name: str,
        entity_type: EntityType = EntityType.CUSTOM,
        entity_id: str = None,
        properties: Dict[str, Any] = None,
        source: str = "conversation",
        confidence: float = 0.8,
        created_at: str = None
    ):
        self.id = entity_id or f"entity_{uuid.uuid4().hex[:12]}"
        self.name = name
        self.entity_type = entity_type
        self.properties = properties if properties is not None else {}
        self.source = source
        self.confidence = max(0.0, min(1.0, confidence))
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """将实体序列化为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "properties": self.properties,
            "source": self.source,
            "confidence": self.confidence,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEntity":
        """从字典反序列化实体

        Args:
            data: 包含实体字段的字典

        Returns:
            KnowledgeEntity 实例
        """
        entity_type_value = data.get("entity_type", EntityType.CUSTOM.value)
        # 兼容字符串与枚举
        if isinstance(entity_type_value, EntityType):
            entity_type = entity_type_value
        else:
            try:
                entity_type = EntityType(entity_type_value)
            except ValueError:
                entity_type = EntityType.CUSTOM

        return cls(
            name=data.get("name", ""),
            entity_type=entity_type,
            entity_id=data.get("id"),
            properties=data.get("properties", {}),
            source=data.get("source", "conversation"),
            confidence=data.get("confidence", 0.8),
            created_at=data.get("created_at")
        )

    def __repr__(self) -> str:
        return f"KnowledgeEntity(id={self.id}, name={self.name}, type={self.entity_type.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KnowledgeEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# =============================================================================
# 知识关系
# =============================================================================

class KnowledgeRelation:
    """知识关系 - 知识图谱中的边

    描述两个实体之间的关系，例如"隶属于"、"位于"、"控制"等。

    Attributes:
        id: 关系唯一标识
        source_entity_id: 起始实体 ID
        target_entity_id: 目标实体 ID
        relation_type: 关系类型（RelationType）
        properties: 关系属性字典
        confidence: 置信度（0.0 ~ 1.0）
    """

    def __init__(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relation_type: RelationType = RelationType.RELATED_TO,
        relation_id: str = None,
        properties: Dict[str, Any] = None,
        confidence: float = 0.8
    ):
        self.id = relation_id or f"relation_{uuid.uuid4().hex[:12]}"
        self.source_entity_id = source_entity_id
        self.target_entity_id = target_entity_id
        self.relation_type = relation_type
        self.properties = properties if properties is not None else {}
        self.confidence = max(0.0, min(1.0, confidence))

    def to_dict(self) -> Dict[str, Any]:
        """将关系序列化为字典"""
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relation_type": self.relation_type.value,
            "properties": self.properties,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeRelation":
        """从字典反序列化关系

        Args:
            data: 包含关系字段的字典

        Returns:
            KnowledgeRelation 实例
        """
        relation_type_value = data.get("relation_type", RelationType.RELATED_TO.value)
        if isinstance(relation_type_value, RelationType):
            relation_type = relation_type_value
        else:
            try:
                relation_type = RelationType(relation_type_value)
            except ValueError:
                relation_type = RelationType.RELATED_TO

        return cls(
            source_entity_id=data.get("source_entity_id", ""),
            target_entity_id=data.get("target_entity_id", ""),
            relation_type=relation_type,
            relation_id=data.get("id"),
            properties=data.get("properties", {}),
            confidence=data.get("confidence", 0.8)
        )

    def __repr__(self) -> str:
        return (
            f"KnowledgeRelation(id={self.id}, "
            f"{self.source_entity_id} -[{self.relation_type.value}]-> {self.target_entity_id})"
        )


# =============================================================================
# 知识图谱
# =============================================================================

class KnowledgeGraph:
    """知识图谱 - 内存图数据库（线程安全）

    维护实体与关系的存储，并通过邻接表支持快速的关系查询与路径推理。

    数据结构：
        - _entities: 实体字典 {entity_id: KnowledgeEntity}
        - _relations: 关系字典 {relation_id: KnowledgeRelation}
        - _adjacency: 邻接表 {entity_id: {neighbor_id: [relation_id, ...]}}
    """

    def __init__(self):
        self._entities: Dict[str, KnowledgeEntity] = {}
        self._relations: Dict[str, KnowledgeRelation] = {}
        # 邻接表：双向，便于按方向查询
        self._adjacency: Dict[str, Dict[str, List[str]]] = {}
        self._lock = threading.RLock()

    def add_entity(self, entity: KnowledgeEntity) -> str:
        """添加实体到知识图谱

        若已存在同名同类型的实体，则合并属性并提升置信度，避免重复创建。

        Args:
            entity: 知识实体实例

        Returns:
            实体 ID
        """
        with self._lock:
            # 实体对齐：同名同类型视为同一实体
            existing = self._find_entity_by_name(entity.name, entity.entity_type)
            if existing is not None:
                # 合并属性
                for key, value in entity.properties.items():
                    if key not in existing.properties:
                        existing.properties[key] = value
                # 置信度取较高者
                existing.confidence = max(existing.confidence, entity.confidence)
                return existing.id

            self._entities[entity.id] = entity
            self._adjacency.setdefault(entity.id, {})
            return entity.id

    def add_relation(self, relation: KnowledgeRelation) -> str:
        """添加关系到知识图谱

        Args:
            relation: 知识关系实例

        Returns:
            关系 ID
        """
        with self._lock:
            # 校验实体是否存在
            if relation.source_entity_id not in self._entities:
                raise ValueError(f"起始实体不存在: {relation.source_entity_id}")
            if relation.target_entity_id not in self._entities:
                raise ValueError(f"目标实体不存在: {relation.target_entity_id}")

            self._relations[relation.id] = relation

            # 构建双向邻接表
            self._adjacency.setdefault(relation.source_entity_id, {})
            self._adjacency[relation.source_entity_id].setdefault(
                relation.target_entity_id, []
            ).append(relation.id)

            self._adjacency.setdefault(relation.target_entity_id, {})
            self._adjacency[relation.target_entity_id].setdefault(
                relation.source_entity_id, []
            ).append(relation.id)

            return relation.id

    def get_entity(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """根据 ID 获取实体

        Args:
            entity_id: 实体 ID

        Returns:
            实体实例，不存在则返回 None
        """
        with self._lock:
            return self._entities.get(entity_id)

    def get_relations(
        self,
        entity_id: str,
        direction: str = "both"
    ) -> List[KnowledgeRelation]:
        """获取与实体相关的关系

        Args:
            entity_id: 实体 ID
            direction: 方向，可选 "outgoing"（出边）、"incoming"（入边）、"both"（双向，默认）

        Returns:
            关系列表
        """
        with self._lock:
            if direction not in ("outgoing", "incoming", "both"):
                raise ValueError(f"无效的方向参数: {direction}")

            relations: List[KnowledgeRelation] = []
            for relation in self._relations.values():
                if direction in ("outgoing", "both") and relation.source_entity_id == entity_id:
                    relations.append(relation)
                if direction in ("incoming", "both") and relation.target_entity_id == entity_id:
                    relations.append(relation)
            return relations

    def search_entities(
        self,
        name: str,
        entity_type: Optional[EntityType] = None
    ) -> List[KnowledgeEntity]:
        """按名称搜索实体（支持模糊匹配）

        Args:
            name: 实体名称关键词
            entity_type: 可选，限定实体类型

        Returns:
            匹配的实体列表
        """
        with self._lock:
            results: List[KnowledgeEntity] = []
            name_lower = name.lower()
            for entity in self._entities.values():
                if name_lower not in entity.name.lower():
                    continue
                if entity_type is not None and entity.entity_type != entity_type:
                    continue
                results.append(entity)
            return results

    def find_path(self, entity_id_a: str, entity_id_b: str) -> List[str]:
        """查找两个实体之间的最短路径（广度优先搜索）

        Args:
            entity_id_a: 起始实体 ID
            entity_id_b: 目标实体 ID

        Returns:
            路径上的实体 ID 列表；不存在路径或实体不存在时返回空列表
        """
        with self._lock:
            if entity_id_a not in self._entities or entity_id_b not in self._entities:
                return []
            if entity_id_a == entity_id_b:
                return [entity_id_a]

            # BFS 搜索最短路径
            visited = {entity_id_a}
            queue = deque([(entity_id_a, [entity_id_a])])

            while queue:
                current_id, path = queue.popleft()
                neighbors = self._adjacency.get(current_id, {})
                for neighbor_id in neighbors:
                    if neighbor_id in visited:
                        continue
                    new_path = path + [neighbor_id]
                    if neighbor_id == entity_id_b:
                        return new_path
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, new_path))

            return []

    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息

        Returns:
            包含实体数、关系数、类型分布等信息的字典
        """
        with self._lock:
            entity_type_counts: Dict[str, int] = {}
            relation_type_counts: Dict[str, int] = {}

            for entity in self._entities.values():
                type_name = entity.entity_type.value
                entity_type_counts[type_name] = entity_type_counts.get(type_name, 0) + 1

            for relation in self._relations.values():
                type_name = relation.relation_type.value
                relation_type_counts[type_name] = relation_type_counts.get(type_name, 0) + 1

            return {
                "total_entities": len(self._entities),
                "total_relations": len(self._relations),
                "entity_types": entity_type_counts,
                "relation_types": relation_type_counts
            }

    def _find_entity_by_name(
        self,
        name: str,
        entity_type: EntityType
    ) -> Optional[KnowledgeEntity]:
        """按名称与类型查找已存在的实体（内部方法，调用前需持有锁）"""
        for entity in self._entities.values():
            if entity.name == name and entity.entity_type == entity_type:
                return entity
        return None

    def get_all_entities(self) -> List[KnowledgeEntity]:
        """获取所有实体"""
        with self._lock:
            return list(self._entities.values())

    def get_all_relations(self) -> List[KnowledgeRelation]:
        """获取所有关系"""
        with self._lock:
            return list(self._relations.values())

    def clear(self):
        """清空知识图谱"""
        with self._lock:
            self._entities.clear()
            self._relations.clear()
            self._adjacency.clear()


# =============================================================================
# 用户学习画像
# =============================================================================

class LearningProfile:
    """用户学习画像 - 记录偏好与行为模式

    从用户交互中持续学习，构建包含偏好、行为模式和交互统计的画像模型。

    Attributes:
        user_id: 用户 ID
        preferences: 偏好字典 {key: {"value": ..., "count": ...}}
        behavior_patterns: 行为模式列表
        interaction_count: 交互次数
        last_active: 最后活跃时间（ISO 格式字符串）
    """

    MAX_BEHAVIOR_PATTERNS = 200

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.preferences: Dict[str, Dict[str, Any]] = {}
        self.behavior_patterns: List[Dict[str, Any]] = []
        self.interaction_count: int = 0
        self.last_active: str = datetime.now().isoformat()

    def record_preference(self, key: str, value: Any) -> None:
        """记录用户偏好

        同一偏好多次记录会累加计数，用于衡量偏好强度。

        Args:
            key: 偏好键（如 "language"、"temperature"）
            value: 偏好值
        """
        if not key:
            return
        if key in self.preferences:
            self.preferences[key]["count"] += 1
            self.preferences[key]["value"] = value
            self.preferences[key]["updated_at"] = datetime.now().isoformat()
        else:
            self.preferences[key] = {
                "value": value,
                "count": 1,
                "updated_at": datetime.now().isoformat()
            }

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好值

        Args:
            key: 偏好键
            default: 默认值（偏好不存在时返回）

        Returns:
            偏好值，不存在则返回 default
        """
        pref = self.preferences.get(key)
        if pref is None:
            return default
        return pref.get("value", default)

    def record_interaction(self, input_text: str, response: str) -> None:
        """记录一次用户交互

        Args:
            input_text: 用户输入文本
            response: 系统响应文本
        """
        self.interaction_count += 1
        self.last_active = datetime.now().isoformat()

        pattern = {
            "timestamp": self.last_active,
            "input_length": len(input_text),
            "response_length": len(response),
            "input_preview": input_text[:100]
        }
        self.behavior_patterns.append(pattern)

        # 限制行为模式列表大小，保留最近的记录
        if len(self.behavior_patterns) > self.MAX_BEHAVIOR_PATTERNS:
            self.behavior_patterns = self.behavior_patterns[-self.MAX_BEHAVIOR_PATTERNS:]

    def get_top_preferences(self, n: int = 5) -> List[Tuple[str, Any, int]]:
        """获取出现次数最多的 Top-N 偏好

        Args:
            n: 返回数量

        Returns:
            偏好元组列表 (key, value, count)，按 count 降序排列
        """
        sorted_prefs = sorted(
            self.preferences.items(),
            key=lambda item: item[1].get("count", 0),
            reverse=True
        )
        return [
            (key, info.get("value"), info.get("count", 0))
            for key, info in sorted_prefs[:n]
        ]

    def to_dict(self) -> Dict[str, Any]:
        """将用户画像序列化为字典"""
        return {
            "user_id": self.user_id,
            "preferences": self.preferences,
            "behavior_patterns": self.behavior_patterns,
            "interaction_count": self.interaction_count,
            "last_active": self.last_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningProfile":
        """从字典反序列化用户画像

        Args:
            data: 包含画像字段的字典

        Returns:
            LearningProfile 实例
        """
        profile = cls(user_id=data.get("user_id", "default"))
        profile.preferences = data.get("preferences", {})
        profile.behavior_patterns = data.get("behavior_patterns", [])
        profile.interaction_count = data.get("interaction_count", 0)
        profile.last_active = data.get("last_active", datetime.now().isoformat())
        return profile


# =============================================================================
# 知识管理器（单例）
# =============================================================================

class KnowledgeManager:
    """知识管理器 - 整合向量记忆、知识图谱与用户画像（单例模式）

    对应 frame.html 3.5 节学习与知识库系统的核心编排层，负责：
    - 从文本中抽取实体与关系并写入知识图谱
    - 将对话内容写入向量记忆（Milvus + HNSW）
    - 检索相关上下文（向量召回 + 图谱关联）
    - 从交互中学习用户偏好并维护用户画像
    - 集成审计日志记录知识操作
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return
            self._initialized = True

            self._graph = KnowledgeGraph()
            self._profile = LearningProfile(user_id="default")

            # 引用全局向量记忆管理器
            try:
                from jarvis.memory.memory_manager import memory_manager
                self._memory_manager = memory_manager
            except Exception as e:
                print(f"⚠️ 知识管理器：向量记忆管理器加载失败: {e}")
                self._memory_manager = None

            # 实体抽取规则：关键词 -> (实体类型, 标准名称)
            self._entity_patterns: Dict[str, Tuple[EntityType, str]] = {
                # 人物
                "我": (EntityType.PERSON, "用户"),
                "用户": (EntityType.PERSON, "用户"),
                "贾维斯": (EntityType.PERSON, "贾维斯"),
                # 设备
                "空调": (EntityType.DEVICE, "空调"),
                "灯": (EntityType.DEVICE, "灯光"),
                "灯光": (EntityType.DEVICE, "灯光"),
                "窗帘": (EntityType.DEVICE, "窗帘"),
                "音乐": (EntityType.DEVICE, "音乐"),
                "电视": (EntityType.DEVICE, "电视"),
                "音响": (EntityType.DEVICE, "音响"),
                # 位置
                "家": (EntityType.LOCATION, "家"),
                "家里": (EntityType.LOCATION, "家"),
                "办公室": (EntityType.LOCATION, "办公室"),
                "公司": (EntityType.LOCATION, "公司"),
                "卧室": (EntityType.LOCATION, "卧室"),
                "客厅": (EntityType.LOCATION, "客厅"),
                # 概念
                "天气": (EntityType.CONCEPT, "天气"),
                "温度": (EntityType.CONCEPT, "温度"),
                "湿度": (EntityType.CONCEPT, "湿度"),
                "时间": (EntityType.CONCEPT, "时间"),
                "日程": (EntityType.CONCEPT, "日程"),
                "新闻": (EntityType.CONCEPT, "新闻"),
            }

            print("✓ 知识管理器初始化完成")

    # -------------------------------------------------------------------------
    # 实体抽取
    # -------------------------------------------------------------------------

    def extract_entities(self, text: str) -> List[KnowledgeEntity]:
        """从文本中提取知识实体（基于关键词和模式匹配）

        采用关键词字典匹配的方式识别文本中的实体，并对同一实体去重。

        Args:
            text: 待解析的文本

        Returns:
            提取到的知识实体列表
        """
        if not text:
            return []

        entities: List[KnowledgeEntity] = []
        seen_names: set = set()

        try:
            for keyword, (entity_type, standard_name) in self._entity_patterns.items():
                if keyword in text and standard_name not in seen_names:
                    entity = KnowledgeEntity(
                        name=standard_name,
                        entity_type=entity_type,
                        source="conversation",
                        confidence=0.85
                    )
                    entities.append(entity)
                    seen_names.add(standard_name)
        except Exception as e:
            print(f"⚠️ 实体抽取失败: {e}")

        return entities

    # -------------------------------------------------------------------------
    # 对话存储
    # -------------------------------------------------------------------------

    def store_conversation(self, user_input: str, response: str) -> None:
        """存储对话到向量记忆与知识图谱

        将对话内容写入向量记忆（用于语义检索），同时抽取实体写入知识图谱，
        并尝试在用户与提及的实体之间建立 RELATED_TO 关系。

        Args:
            user_input: 用户输入
            response: 系统响应
        """
        try:
            # 1. 写入向量记忆
            if self._memory_manager is not None:
                combined_text = f"用户: {user_input}\n贾维斯: {response}"
                self._memory_manager.add_memory(
                    content=combined_text,
                    metadata={
                        "type": "conversation",
                        "timestamp": datetime.now().isoformat(),
                        "user_input": user_input[:200]
                    }
                )

            # 2. 抽取实体并写入知识图谱
            entities = self.extract_entities(user_input)
            entity_ids: List[str] = []
            for entity in entities:
                try:
                    entity_id = self._graph.add_entity(entity)
                    entity_ids.append(entity_id)
                except Exception as e:
                    print(f"⚠️ 添加实体失败: {e}")

            # 3. 在用户与提及的实体间建立关联关系
            if entity_ids:
                user_entity = KnowledgeEntity(
                    name="用户",
                    entity_type=EntityType.PERSON,
                    source="conversation",
                    confidence=0.9
                )
                user_id = self._graph.add_entity(user_entity)
                for target_id in entity_ids:
                    if target_id == user_id:
                        continue
                    relation = KnowledgeRelation(
                        source_entity_id=user_id,
                        target_entity_id=target_id,
                        relation_type=RelationType.RELATED_TO,
                        confidence=0.7
                    )
                    try:
                        self._graph.add_relation(relation)
                    except Exception as e:
                        print(f"⚠️ 添加关系失败: {e}")

            # 4. 记录交互到用户画像
            self._profile.record_interaction(user_input, response)

            # 5. 审计日志
            audit_logger.log_operation(
                operation_type=OperationType.MEMORY_ACCESS,
                action="store_conversation",
                details={
                    "entity_count": len(entities),
                    "input_length": len(user_input)
                },
                result="success"
            )
        except Exception as e:
            print(f"⚠️ 存储对话失败: {e}")
            audit_logger.log_operation(
                operation_type=OperationType.MEMORY_ACCESS,
                action="store_conversation",
                details={"error": str(e)},
                result="failed"
            )

    # -------------------------------------------------------------------------
    # 上下文检索
    # -------------------------------------------------------------------------

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """检索与查询相关的上下文（向量召回 + 图谱关联）

        Args:
            query: 查询文本
            top_k: 向量召回数量

        Returns:
            拼接后的上下文字符串
        """
        context_parts: List[str] = []

        try:
            # 1. 向量记忆召回
            if self._memory_manager is not None:
                memories = self._memory_manager.search_memory(query, top_k=top_k)
                for memory in memories:
                    content = memory.get("content")
                    if content:
                        context_parts.append(f"[相关记忆] {content}")

            # 2. 知识图谱关联
            entities = self.extract_entities(query)
            for entity in entities:
                existing_list = self._graph.search_entities(entity.name, entity.entity_type)
                for existing in existing_list:
                    relations = self._graph.get_relations(existing.id, direction="both")
                    if relations:
                        rel_desc = "; ".join(
                            f"{r.relation_type.value}->{r.target_entity_id if r.source_entity_id == existing.id else r.source_entity_id}"
                            for r in relations[:3]
                        )
                        context_parts.append(
                            f"[知识图谱] {existing.name}({existing.entity_type.value}) 关系: {rel_desc}"
                        )
                    else:
                        context_parts.append(
                            f"[知识图谱] {existing.name}({existing.entity_type.value})"
                        )

            audit_logger.log_operation(
                operation_type=OperationType.MEMORY_ACCESS,
                action="retrieve_context",
                details={
                    "query_length": len(query),
                    "context_parts": len(context_parts)
                },
                result="success"
            )
        except Exception as e:
            print(f"⚠️ 检索上下文失败: {e}")
            audit_logger.log_operation(
                operation_type=OperationType.MEMORY_ACCESS,
                action="retrieve_context",
                details={"error": str(e)},
                result="failed"
            )

        return "\n".join(context_parts) if context_parts else ""

    # -------------------------------------------------------------------------
    # 偏好学习
    # -------------------------------------------------------------------------

    def learn_preference(self, user_input: str, response: str) -> None:
        """从交互中学习用户偏好

        通过模式匹配识别用户表达的偏好（如语言、温度、设备习惯等）并记录到用户画像。

        Args:
            user_input: 用户输入
            response: 系统响应
        """
        try:
            # 偏好规则：关键词 -> 偏好键
            preference_rules = [
                (r"中文|汉语", "language", "中文"),
                (r"英文|英语|English", "language", "英文"),
                (r"(\d+)\s*度", "temperature", None),
                (r"简洁|简单", "response_style", "简洁"),
                (r"详细|具体", "response_style", "详细"),
            ]

            for pattern, key, fixed_value in preference_rules:
                match = re.search(pattern, user_input)
                if match:
                    if fixed_value is not None:
                        self._profile.record_preference(key, fixed_value)
                    elif match.groups():
                        # 带捕获组的规则（如温度数值）
                        self._profile.record_preference(key, match.group(1))

            # 记录交互
            self._profile.record_interaction(user_input, response)

            audit_logger.log_operation(
                operation_type=OperationType.MEMORY_ACCESS,
                action="learn_preference",
                details={"input_length": len(user_input)},
                result="success"
            )
        except Exception as e:
            print(f"⚠️ 学习偏好失败: {e}")
            audit_logger.log_operation(
                operation_type=OperationType.MEMORY_ACCESS,
                action="learn_preference",
                details={"error": str(e)},
                result="failed"
            )

    # -------------------------------------------------------------------------
    # 查询接口
    # -------------------------------------------------------------------------

    def get_user_profile(self) -> Dict[str, Any]:
        """获取用户画像

        Returns:
            用户画像字典，包含偏好、行为模式、交互统计及 Top 偏好
        """
        profile_dict = self._profile.to_dict()
        profile_dict["top_preferences"] = self._profile.get_top_preferences(n=5)
        return profile_dict

    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息

        Returns:
            包含图谱统计、记忆统计与用户画像摘要的字典
        """
        stats: Dict[str, Any] = {
            "knowledge_graph": self._graph.get_statistics(),
            "user_profile": {
                "user_id": self._profile.user_id,
                "interaction_count": self._profile.interaction_count,
                "preference_count": len(self._profile.preferences),
                "last_active": self._profile.last_active
            }
        }

        if self._memory_manager is not None:
            try:
                stats["memory"] = self._memory_manager.get_statistics()
            except Exception as e:
                stats["memory"] = {"error": str(e)}
        else:
            stats["memory"] = {"available": False}

        return stats

    # -------------------------------------------------------------------------
    # 便捷访问
    # -------------------------------------------------------------------------

    @property
    def graph(self) -> KnowledgeGraph:
        """获取知识图谱实例"""
        return self._graph

    @property
    def profile(self) -> LearningProfile:
        """获取用户画像实例"""
        return self._profile


# 创建全局单例
knowledge_manager = KnowledgeManager()
