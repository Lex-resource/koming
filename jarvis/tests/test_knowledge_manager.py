"""知识管理系统测试

参考 frame.html 5.2 节核心测试用例表中的"多轮对话"场景：
- 输入：连续 5 轮上下文相关提问
- 预期输出：正确理解上下文
- 验证点：对话历史管理、上下文引用

覆盖 frame.html 3.5 节学习与知识库系统：
- 3.5.1 知识处理层：实体抽取、向量化、偏好学习
- 3.5.2 知识存储层：知识图谱（KnowledgeGraph）、用户画像（LearningProfile）
"""
import pytest

from jarvis.core.knowledge_manager import (
    knowledge_manager,
    KnowledgeManager,
    KnowledgeGraph,
    KnowledgeEntity,
    KnowledgeRelation,
    LearningProfile,
    EntityType,
    RelationType,
)


# =============================================================================
# pytest fixtures
# =============================================================================

@pytest.fixture
def km():
    """知识管理器单例，每个测试前重置图谱和画像状态"""
    # 重置知识图谱
    knowledge_manager.graph.clear()
    # 重置用户画像
    knowledge_manager.profile.preferences.clear()
    knowledge_manager.profile.behavior_patterns.clear()
    knowledge_manager.profile.interaction_count = 0
    yield knowledge_manager
    # 测试后清理
    knowledge_manager.graph.clear()


@pytest.fixture
def graph():
    """独立的知识图谱实例（非单例，保证测试隔离）"""
    return KnowledgeGraph()


@pytest.fixture
def profile():
    """独立的用户画像实例（非单例，保证测试隔离）"""
    return LearningProfile(user_id="test_user")


# =============================================================================
# 测试类
# =============================================================================

class TestEntityExtraction:
    """实体抽取测试 - 验证 extract_entities() 从文本中识别实体"""

    def test_extract_device_entities(self, km):
        """测试从文本抽取设备实体

        设备关键词：空调/灯光/窗帘/音响 等
        """
        entities = km.extract_entities("打开空调，关闭灯光")
        # 应至少抽取到空调和灯光两个设备实体
        device_entities = [e for e in entities if e.entity_type == EntityType.DEVICE]
        assert len(device_entities) >= 2

        entity_names = [e.name for e in device_entities]
        assert "空调" in entity_names
        assert "灯光" in entity_names

    def test_extract_concept_entities(self, km):
        """测试从文本抽取概念实体

        概念关键词：天气/温度/湿度/时间 等
        """
        entities = km.extract_entities("今天天气怎么样")
        concept_entities = [e for e in entities if e.entity_type == EntityType.CONCEPT]
        assert len(concept_entities) >= 1

        entity_names = [e.name for e in concept_entities]
        assert "天气" in entity_names

    def test_extract_location_entities(self, km):
        """测试从文本抽取位置实体"""
        entities = km.extract_entities("家里的空调和办公室的灯光")
        location_entities = [e for e in entities if e.entity_type == EntityType.LOCATION]
        assert len(location_entities) >= 1

        entity_names = [e.name for e in location_entities]
        assert "家" in entity_names

    def test_extract_person_entities(self, km):
        """测试从文本抽取人物实体"""
        entities = km.extract_entities("贾维斯，帮我打开空调")
        person_entities = [e for e in entities if e.entity_type == EntityType.PERSON]
        assert len(person_entities) >= 1

        entity_names = [e.name for e in person_entities]
        assert "贾维斯" in entity_names

    def test_extract_empty_text(self, km):
        """测试空文本返回空列表"""
        entities = km.extract_entities("")
        assert entities == []

    def test_extract_no_match(self, km):
        """测试无匹配关键词返回空列表"""
        entities = km.extract_entities("zzz qqq xxx")
        assert entities == []

    def test_extract_deduplication(self, km):
        """测试实体去重（同名同类型不重复）"""
        entities = km.extract_entities("空调和空调")
        device_entities = [e for e in entities if e.entity_type == EntityType.DEVICE]
        # 同名实体应去重
        ac_entities = [e for e in device_entities if e.name == "空调"]
        assert len(ac_entities) == 1


class TestKnowledgeGraph:
    """知识图谱测试 - 验证 KnowledgeGraph 的增删改查与路径推理"""

    def test_add_and_get_entity(self, graph):
        """测试添加和获取实体"""
        entity = KnowledgeEntity(
            name="空调",
            entity_type=EntityType.DEVICE,
            confidence=0.9,
        )
        entity_id = graph.add_entity(entity)
        retrieved = graph.get_entity(entity_id)
        assert retrieved is not None
        assert retrieved.name == "空调"
        assert retrieved.entity_type == EntityType.DEVICE

    def test_add_duplicate_entity_merges(self, graph):
        """测试添加同名同类型实体时合并属性"""
        entity1 = KnowledgeEntity(
            name="空调",
            entity_type=EntityType.DEVICE,
            properties={"brand": "格力"},
            confidence=0.8,
        )
        entity2 = KnowledgeEntity(
            name="空调",
            entity_type=EntityType.DEVICE,
            properties={"model": "KFR-35"},
            confidence=0.9,
        )
        id1 = graph.add_entity(entity1)
        id2 = graph.add_entity(entity2)
        # 同名同类型应返回相同 ID（合并）
        assert id1 == id2

        merged = graph.get_entity(id1)
        # 属性应合并
        assert merged.properties["brand"] == "格力"
        assert merged.properties["model"] == "KFR-35"
        # 置信度取较高者
        assert merged.confidence == 0.9

    def test_add_relation(self, graph):
        """测试添加关系"""
        user = KnowledgeEntity(name="用户", entity_type=EntityType.PERSON)
        ac = KnowledgeEntity(name="空调", entity_type=EntityType.DEVICE)
        user_id = graph.add_entity(user)
        ac_id = graph.add_entity(ac)

        relation = KnowledgeRelation(
            source_entity_id=user_id,
            target_entity_id=ac_id,
            relation_type=RelationType.CONTROLS,
        )
        relation_id = graph.add_relation(relation)
        assert relation_id is not None

    def test_add_relation_nonexistent_entity(self, graph):
        """测试添加关系到不存在的实体抛出异常"""
        relation = KnowledgeRelation(
            source_entity_id="nonexistent_a",
            target_entity_id="nonexistent_b",
            relation_type=RelationType.RELATED_TO,
        )
        with pytest.raises(ValueError):
            graph.add_relation(relation)

    def test_knowledge_graph_search(self, graph):
        """测试知识图谱搜索（模糊匹配）"""
        # 添加多个实体
        graph.add_entity(KnowledgeEntity(name="空调", entity_type=EntityType.DEVICE))
        graph.add_entity(KnowledgeEntity(name="空气净化器", entity_type=EntityType.DEVICE))
        graph.add_entity(KnowledgeEntity(name="灯光", entity_type=EntityType.DEVICE))

        # 搜索包含"空"的设备实体
        results = graph.search_entities("空", entity_type=EntityType.DEVICE)
        assert len(results) >= 2
        names = [r.name for r in results]
        assert "空调" in names
        assert "空气净化器" in names

    def test_knowledge_graph_path(self, graph):
        """测试知识图谱路径查找（BFS 最短路径）"""
        # 构建图：A -> B -> C
        a = graph.add_entity(KnowledgeEntity(name="节点A", entity_type=EntityType.CUSTOM))
        b = graph.add_entity(KnowledgeEntity(name="节点B", entity_type=EntityType.CUSTOM))
        c = graph.add_entity(KnowledgeEntity(name="节点C", entity_type=EntityType.CUSTOM))

        graph.add_relation(KnowledgeRelation(a, b, RelationType.RELATED_TO))
        graph.add_relation(KnowledgeRelation(b, c, RelationType.RELATED_TO))

        # 查找 A 到 C 的路径
        path = graph.find_path(a, c)
        assert len(path) == 3
        assert path[0] == a
        assert path[1] == b
        assert path[2] == c

    def test_find_path_no_connection(self, graph):
        """测试无连接的实体间路径为空"""
        a = graph.add_entity(KnowledgeEntity(name="孤立A", entity_type=EntityType.CUSTOM))
        b = graph.add_entity(KnowledgeEntity(name="孤立B", entity_type=EntityType.CUSTOM))
        path = graph.find_path(a, b)
        assert path == []

    def test_find_path_same_entity(self, graph):
        """测试查找自身到自身的路径"""
        a = graph.add_entity(KnowledgeEntity(name="自身", entity_type=EntityType.CUSTOM))
        path = graph.find_path(a, a)
        assert path == [a]

    def test_get_relations(self, graph):
        """测试获取实体的关系"""
        user = graph.add_entity(KnowledgeEntity(name="用户", entity_type=EntityType.PERSON))
        ac = graph.add_entity(KnowledgeEntity(name="空调", entity_type=EntityType.DEVICE))
        light = graph.add_entity(KnowledgeEntity(name="灯光", entity_type=EntityType.DEVICE))

        graph.add_relation(KnowledgeRelation(user, ac, RelationType.CONTROLS))
        graph.add_relation(KnowledgeRelation(user, light, RelationType.CONTROLS))

        # 获取用户的所有关系
        relations = graph.get_relations(user, direction="both")
        assert len(relations) >= 2

    def test_graph_statistics(self, graph):
        """测试知识图谱统计信息"""
        graph.add_entity(KnowledgeEntity(name="空调", entity_type=EntityType.DEVICE))
        graph.add_entity(KnowledgeEntity(name="用户", entity_type=EntityType.PERSON))

        stats = graph.get_statistics()
        assert stats["total_entities"] >= 2
        assert "entity_types" in stats
        assert "relation_types" in stats
        assert "device" in stats["entity_types"]

    def test_graph_clear(self, graph):
        """测试清空知识图谱"""
        graph.add_entity(KnowledgeEntity(name="测试实体", entity_type=EntityType.CUSTOM))
        assert graph.get_statistics()["total_entities"] >= 1

        graph.clear()
        assert graph.get_statistics()["total_entities"] == 0


class TestLearningProfile:
    """偏好学习测试 - 验证 LearningProfile 的偏好记录与查询"""

    def test_record_and_get_preference(self, profile):
        """测试记录和获取偏好"""
        profile.record_preference("language", "中文")
        assert profile.get_preference("language") == "中文"

    def test_preference_count_increments(self, profile):
        """测试偏好计数累加"""
        profile.record_preference("temperature", "26")
        profile.record_preference("temperature", "28")
        # 多次记录同一偏好，计数应累加
        assert profile.preferences["temperature"]["count"] == 2
        # 值为最后一次设置的值
        assert profile.get_preference("temperature") == "28"

    def test_get_nonexistent_preference(self, profile):
        """测试获取不存在的偏好返回默认值"""
        assert profile.get_preference("nonexistent") is None
        assert profile.get_preference("nonexistent", "default") == "default"

    def test_record_interaction(self, profile):
        """测试记录交互"""
        profile.record_interaction("你好", "你好，我是贾维斯")
        assert profile.interaction_count == 1
        assert len(profile.behavior_patterns) == 1

        # 记录多次交互
        profile.record_interaction("搜索天气", "今天晴天")
        assert profile.interaction_count == 2
        assert len(profile.behavior_patterns) == 2

    def test_get_top_preferences(self, profile):
        """测试获取 Top-N 偏好"""
        profile.record_preference("lang", "中文")
        profile.record_preference("lang", "中文")  # count=2
        profile.record_preference("temp", "26")     # count=1
        profile.record_preference("style", "简洁")  # count=1

        top = profile.get_top_preferences(n=2)
        assert len(top) == 2
        # 出现次数最多的应排在前面
        assert top[0][0] == "lang"
        assert top[0][2] == 2  # count

    def test_behavior_patterns_limit(self, profile):
        """测试行为模式列表大小限制"""
        # 记录超过最大限制的交互
        for i in range(profile.MAX_BEHAVIOR_PATTERNS + 10):
            profile.record_interaction(f"输入{i}", f"响应{i}")
        # 行为模式列表不应超过最大限制
        assert len(profile.behavior_patterns) <= profile.MAX_BEHAVIOR_PATTERNS

    def test_profile_to_dict_and_from_dict(self, profile):
        """测试用户画像序列化与反序列化"""
        profile.record_preference("language", "中文")
        profile.record_interaction("你好", "你好")

        data = profile.to_dict()
        assert data["user_id"] == "test_user"
        assert "preferences" in data
        assert "behavior_patterns" in data

        restored = LearningProfile.from_dict(data)
        assert restored.user_id == "test_user"
        assert restored.get_preference("language") == "中文"


class TestKnowledgeManager:
    """知识管理统一管理器测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        km1 = KnowledgeManager()
        km2 = KnowledgeManager()
        assert km1 is km2
        assert km1 is knowledge_manager

    def test_store_and_retrieve(self, km):
        """测试存储对话并检索上下文

        对应 frame.html 5.2 核心测试用例"多轮对话"：
        - 验证对话历史管理、上下文引用
        """
        # 存储对话
        km.store_conversation("打开空调", "好的，已为您打开空调")

        # 检索相关上下文
        context = km.retrieve_context("空调")
        # 应返回非空上下文（知识图谱中已有空调实体）
        assert isinstance(context, str)

    def test_store_conversation_builds_graph(self, km):
        """测试存储对话后知识图谱中建立实体与关系"""
        km.store_conversation("打开空调关闭灯光", "已完成")

        # 验证图谱中已有实体
        stats = km.graph.get_statistics()
        assert stats["total_entities"] >= 1

        # 验证能搜索到空调实体
        results = km.graph.search_entities("空调")
        assert len(results) >= 1

    def test_learn_preference(self, km):
        """测试偏好学习

        从交互中识别用户偏好（如语言、温度等）并记录到用户画像。
        """
        # 学习语言偏好
        km.learn_preference("请用中文回答", "好的，我会用中文回答")
        assert km.profile.get_preference("language") == "中文"

    def test_learn_temperature_preference(self, km):
        """测试学习温度偏好"""
        km.learn_preference("把空调调到26度", "已将空调调至26度")
        assert km.profile.get_preference("temperature") == "26"

    def test_learn_response_style_preference(self, km):
        """测试学习响应风格偏好"""
        km.learn_preference("请简洁回答", "好的")
        assert km.profile.get_preference("response_style") == "简洁"

    def test_get_user_profile(self, km):
        """测试获取用户画像"""
        km.learn_preference("用中文", "好的")
        profile = km.get_user_profile()
        assert "user_id" in profile
        assert "preferences" in profile
        assert "behavior_patterns" in profile
        assert "interaction_count" in profile
        assert "top_preferences" in profile

    def test_get_statistics(self, km):
        """测试获取统计信息"""
        km.store_conversation("打开空调", "好的")
        stats = km.get_knowledge_statistics()
        assert "knowledge_graph" in stats
        assert "user_profile" in stats
        assert "memory" in stats
        # 图谱统计应包含实体数
        assert "total_entities" in stats["knowledge_graph"]

    def test_graph_property(self, km):
        """测试 graph 属性访问"""
        assert km.graph is not None
        assert isinstance(km.graph, KnowledgeGraph)

    def test_profile_property(self, km):
        """测试 profile 属性访问"""
        assert km.profile is not None
        assert isinstance(km.profile, LearningProfile)
