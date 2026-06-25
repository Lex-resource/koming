"""全局状态测试

参考 frame.html 5.2 节核心测试用例表中的"多轮对话"场景：
- 输入：连续 5 轮上下文相关提问
- 预期输出：正确理解上下文
- 验证点：对话历史管理、上下文引用

覆盖全局状态管理器的对话历史记录、系统状态跟踪和数据导出功能。
"""
import os
import json
import pytest

from jarvis.core.global_state import global_state, GlobalState


# =============================================================================
# pytest fixtures
# =============================================================================

@pytest.fixture
def gs():
    """全局状态单例，每个测试前清空历史"""
    global_state.clear_history()
    yield global_state
    # 测试后清理
    global_state.clear_history()


# =============================================================================
# 测试类
# =============================================================================

class TestConversationHistory:
    """对话历史测试 - 验证对话记录的添加、查询和限制"""

    def test_add_and_get_history(self, gs):
        """测试添加并获取对话历史"""
        # 添加对话记录
        gs.add_conversation("你好", "你好，我是贾维斯")
        gs.add_conversation("今天天气怎么样", "今天晴天")

        # 获取全部历史
        history = gs.get_conversation_history()
        assert len(history) == 2

        # 验证第一条记录内容
        assert history[0]["user_input"] == "你好"
        assert history[0]["response"] == "你好，我是贾维斯"
        assert "timestamp" in history[0]

        # 验证第二条记录内容
        assert history[1]["user_input"] == "今天天气怎么样"
        assert history[1]["response"] == "今天晴天"

    def test_add_with_agent_info(self, gs):
        """测试带智能体信息的对话记录"""
        agent_info = {"agent": "commander", "tools": ["search"]}
        gs.add_conversation("搜索AI", "搜索结果...", agent_info=agent_info)

        history = gs.get_conversation_history()
        assert len(history) == 1
        assert history[0]["agent_info"]["agent"] == "commander"

    def test_get_history_with_limit(self, gs):
        """测试获取指定数量的历史记录"""
        for i in range(5):
            gs.add_conversation(f"问题{i}", f"回答{i}")

        # 获取最近3条
        history = gs.get_conversation_history(limit=3)
        assert len(history) == 3
        # 验证返回的是最近的记录
        assert history[0]["user_input"] == "问题2"
        assert history[2]["user_input"] == "问题4"

    def test_history_limit(self, gs):
        """测试历史记录限制（MAX_HISTORY_SIZE）

        超过最大限制时自动截断，保留最近的记录。
        """
        # 添加超过最大限制的记录
        max_size = gs.MAX_HISTORY_SIZE
        for i in range(max_size + 100):
            gs.add_conversation(f"输入{i}", f"输出{i}")

        history = gs.get_conversation_history()
        # 历史记录不应超过最大限制
        assert len(history) == max_size
        # 验证保留的是最近的记录
        assert history[-1]["user_input"] == f"输入{max_size + 99}"
        assert history[0]["user_input"] == f"输入{100}"

    def test_clear_history(self, gs):
        """测试清空历史"""
        gs.add_conversation("测试1", "回答1")
        gs.add_conversation("测试2", "回答2")
        assert len(gs.get_conversation_history()) == 2

        # 清空历史
        gs.clear_history()
        assert len(gs.get_conversation_history()) == 0
        # 交互计数也应归零
        assert gs.get_system_status()["total_interactions"] == 0

    def test_export_history(self, gs, tmp_path):
        """测试导出历史到文件"""
        gs.add_conversation("导出测试", "导出回答")

        # 导出到临时文件
        export_file = str(tmp_path / "export.json")
        result_path = gs.export_history(file_path=export_file)

        assert result_path == export_file
        assert os.path.exists(export_file)

        # 验证导出文件内容
        with open(export_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "metadata" in data
        assert "history" in data
        assert data["metadata"]["total_records"] >= 1
        assert len(data["history"]) >= 1

    def test_export_history_default_path(self, gs):
        """测试导出历史使用默认路径"""
        gs.add_conversation("默认导出", "回答")

        result_path = gs.export_history()
        assert result_path is not None
        assert os.path.exists(result_path)

        # 清理导出的文件
        if os.path.exists(result_path):
            os.remove(result_path)

    def test_get_conversation_by_time_range(self, gs):
        """测试按时间范围获取对话历史"""
        gs.add_conversation("第一条", "回答1")

        # 记录时间戳作为起始时间
        start_time = gs.get_conversation_history()[0]["timestamp"]

        gs.add_conversation("第二条", "回答2")

        # 查询从第一条之后的所有记录
        history = gs.get_conversation_by_time_range(start_time=start_time)
        assert len(history) >= 2

        # 查询第一条之前的记录（应为空）
        history_before = gs.get_conversation_by_time_range(end_time=start_time)
        assert len(history_before) <= 1


class TestSystemStatus:
    """系统状态测试 - 验证系统状态的更新和查询"""

    def test_system_status(self, gs):
        """测试获取系统状态"""
        status = gs.get_system_status()
        assert "start_time" in status
        assert "total_interactions" in status
        assert "active_tools" in status
        assert "memory_count" in status

    def test_total_interactions_increment(self, gs):
        """测试交互计数递增"""
        initial = gs.get_system_status()["total_interactions"]

        gs.add_conversation("测试", "回答")
        assert gs.get_system_status()["total_interactions"] == initial + 1

        gs.add_conversation("测试2", "回答2")
        assert gs.get_system_status()["total_interactions"] == initial + 2

    def test_update_system_status(self, gs):
        """测试更新系统状态"""
        gs.update_system_status("active_tools", ["search", "weather"])
        gs.update_system_status("memory_count", 42)

        status = gs.get_system_status()
        assert status["active_tools"] == ["search", "weather"]
        assert status["memory_count"] == 42

    def test_get_summary(self, gs):
        """测试获取系统摘要"""
        gs.add_conversation("摘要测试", "回答")
        gs.update_system_status("memory_count", 10)

        summary = gs.get_summary()
        assert summary["total_conversations"] >= 1
        assert "start_time" in summary
        assert "current_time" in summary
        assert summary["memory_count"] == 10

    def test_status_is_copy(self, gs):
        """测试返回的状态是副本（修改不影响内部状态）"""
        status = gs.get_system_status()
        status["total_interactions"] = 999

        # 内部状态不应被修改
        actual = gs.get_system_status()
        assert actual["total_interactions"] != 999
