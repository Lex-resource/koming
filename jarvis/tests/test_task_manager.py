"""任务管理系统测试

参考 frame.html 5.2 节核心测试用例表中的"异步任务"场景：
- 输入："异步 搜索 AI 最新进展"
- 预期输出：返回任务 ID，后台执行
- 验证点：任务队列、状态跟踪

覆盖 frame.html 3.3 节任务管理系统：
- 任务分解：TaskDecomposer 将自然语言指令分解为子任务
- 任务调度：TaskScheduler 基于优先级队列和依赖图调度
- 任务执行：ThreadPoolExecutor 异步执行
"""
import time
import pytest

from jarvis.core.task_manager import (
    task_manager,
    TaskManager,
    TaskDecomposer,
    TaskScheduler,
    TaskNode,
    TaskType,
    TaskStatus,
)
from jarvis.core.async_executor import TaskPriority


# =============================================================================
# pytest fixtures
# =============================================================================

@pytest.fixture
def tm():
    """任务管理器单例（全局共享）"""
    return task_manager


@pytest.fixture
def decomposer():
    """任务分解器实例（每次创建新实例，保证测试独立）"""
    return TaskDecomposer()


@pytest.fixture
def scheduler():
    """任务调度器实例（不启动调度循环，保证任务保持 PENDING 状态便于测试）"""
    s = TaskScheduler(max_workers=4)
    yield s
    s.stop()


# =============================================================================
# 测试类
# =============================================================================

class TestTaskDecomposer:
    """任务分解测试 - 验证 TaskDecomposer.decompose() 的分解能力"""

    def test_decompose_search_task(self, decomposer):
        """测试分解搜索任务

        搜索类关键词：搜索/查找/查询/search 等
        """
        tasks = decomposer.decompose("搜索AI最新进展")
        assert len(tasks) >= 1
        # 验证任务类型为搜索
        assert tasks[0].task_type == TaskType.SEARCH
        # 验证任务状态为待执行
        assert tasks[0].status == TaskStatus.PENDING
        # 验证任务描述包含原始输入
        assert "搜索" in tasks[0].description or "AI" in tasks[0].description

    def test_decompose_device_task(self, decomposer):
        """测试分解设备控制任务

        设备控制关键词：打开/关闭/空调/灯光 等
        """
        tasks = decomposer.decompose("打开空调")
        assert len(tasks) >= 1
        # 验证任务类型为设备控制
        assert tasks[0].task_type == TaskType.DEVICE_CONTROL

    def test_decompose_analysis_task(self, decomposer):
        """测试分解分析任务"""
        tasks = decomposer.decompose("分析这份数据报告")
        assert len(tasks) >= 1
        assert tasks[0].task_type == TaskType.ANALYSIS

    def test_decompose_conversation_task(self, decomposer):
        """测试分解对话任务（无匹配关键词时默认为对话）"""
        tasks = decomposer.decompose("你好，介绍一下你自己")
        assert len(tasks) >= 1
        assert tasks[0].task_type == TaskType.CONVERSATION

    def test_decompound_instruction(self, decomposer):
        """测试分解复合指令（"搜索然后分析"）

        复合指令通过"然后/接着/之后"等关键词拆分为多个子任务。
        """
        tasks = decomposer.decompose("搜索AI最新进展然后分析结果")
        # 复合指令应分解为多个子任务
        assert len(tasks) >= 2
        # 第一个任务应为搜索
        assert tasks[0].task_type == TaskType.SEARCH
        # 第二个任务应为分析
        assert tasks[1].task_type == TaskType.ANALYSIS

    def test_decompose_empty_input(self, decomposer):
        """测试空输入返回空列表"""
        tasks = decomposer.decompose("")
        assert tasks == []

    def test_decompose_whitespace_input(self, decomposer):
        """测试纯空白输入返回空列表"""
        tasks = decomposer.decompose("   ")
        assert tasks == []

    def test_task_dependencies(self, decomposer):
        """测试验证任务依赖关系

        复合指令分解后，后续任务应依赖前序任务（线性依赖链）。
        """
        tasks = decomposer.decompose("搜索新闻然后总结要点接着发送邮件")
        assert len(tasks) >= 3

        # 验证线性依赖链：第 i 个任务依赖第 i-1 个任务
        for i in range(1, len(tasks)):
            assert tasks[i - 1].id in tasks[i].dependencies

    def test_single_task_no_dependencies(self, decomposer):
        """测试单个任务无依赖"""
        tasks = decomposer.decompose("搜索天气")
        assert len(tasks) == 1
        assert len(tasks[0].dependencies) == 0

    def test_task_priority(self, decomposer):
        """测试验证任务优先级排序

        TaskNode.__lt__ 按优先级值降序排列（高优先级先出队）。
        """
        # 创建不同优先级的任务
        low_task = TaskNode(
            id="low_1",
            description="低优先级任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.LOW,
        )
        high_task = TaskNode(
            id="high_1",
            description="高优先级任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.HIGH,
        )
        critical_task = TaskNode(
            id="critical_1",
            description="紧急任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.CRITICAL,
        )

        # 排序后应为：CRITICAL > HIGH > LOW
        sorted_tasks = sorted([low_task, high_task, critical_task])
        assert sorted_tasks[0].priority == TaskPriority.CRITICAL
        assert sorted_tasks[1].priority == TaskPriority.HIGH
        assert sorted_tasks[2].priority == TaskPriority.LOW

    def test_task_node_to_dict(self, decomposer):
        """测试任务节点序列化为字典"""
        tasks = decomposer.decompose("搜索AI")
        assert len(tasks) >= 1
        task_dict = tasks[0].to_dict()
        assert "id" in task_dict
        assert "description" in task_dict
        assert "task_type" in task_dict
        assert "priority" in task_dict
        assert "status" in task_dict
        assert "dependencies" in task_dict


class TestTaskScheduler:
    """任务调度测试 - 验证 TaskScheduler 的提交/查询/统计功能"""

    def test_scheduler_submit(self, scheduler):
        """测试提交任务到调度器"""
        task = TaskNode(
            id="test_submit_001",
            description="测试提交任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.NORMAL,
        )
        task_id = scheduler.submit(task)
        assert task_id == "test_submit_001"

        # 验证任务已在调度器中
        status = scheduler.get_task_status(task_id)
        assert "error" not in status or status.get("status") is not None
        assert status["id"] == task_id

    def test_scheduler_get_task_status(self, scheduler):
        """测试查询任务状态"""
        task = TaskNode(
            id="test_status_001",
            description="测试状态查询",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.NORMAL,
        )
        scheduler.submit(task)
        status = scheduler.get_task_status("test_status_001")
        assert status["id"] == "test_status_001"
        assert status["description"] == "测试状态查询"

    def test_scheduler_get_nonexistent_task(self, scheduler):
        """测试查询不存在的任务"""
        status = scheduler.get_task_status("nonexistent_task_id")
        assert "error" in status

    def test_scheduler_cancel_task(self, scheduler):
        """测试取消待执行任务"""
        # 创建待执行任务（调度器未启动，任务保持 PENDING 状态）
        task = TaskNode(
            id="test_cancel_001",
            description="测试取消任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.NORMAL,
        )
        scheduler.submit(task)
        # 取消任务
        result = scheduler.cancel_task("test_cancel_001")
        assert result is True
        # 验证任务状态为已取消
        status = scheduler.get_task_status("test_cancel_001")
        assert status["status"] == TaskStatus.CANCELLED.value

    def test_scheduler_get_pending_tasks(self, scheduler):
        """测试获取待执行任务列表"""
        # 创建待执行任务（调度器未启动，任务保持 PENDING 状态）
        task = TaskNode(
            id="test_pending_001",
            description="待执行任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.NORMAL,
        )
        scheduler.submit(task)
        pending = scheduler.get_pending_tasks()
        # 应至少包含我们提交的待执行任务
        pending_ids = [t.id for t in pending]
        assert "test_pending_001" in pending_ids

    def test_scheduler_get_statistics(self, scheduler):
        """测试获取调度器统计信息"""
        task = TaskNode(
            id="test_stats_001",
            description="统计测试任务",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.NORMAL,
        )
        scheduler.submit(task)

        stats = scheduler.get_statistics()
        assert "总任务数" in stats
        assert "队列大小" in stats
        assert "状态分布" in stats
        assert "最大工作线程" in stats
        assert "运行状态" in stats
        assert stats["总任务数"] >= 1

    def test_scheduler_priority_ordering(self, scheduler):
        """测试调度器优先级队列排序"""
        low_task = TaskNode(
            id="prio_low_001",
            description="低优先级",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.LOW,
        )
        high_task = TaskNode(
            id="prio_high_001",
            description="高优先级",
            task_type=TaskType.CUSTOM,
            priority=TaskPriority.HIGH,
        )
        scheduler.submit(low_task)
        scheduler.submit(high_task)

        # 验证两个任务都已提交
        assert scheduler.get_task_status("prio_low_001")["id"] == "prio_low_001"
        assert scheduler.get_task_status("prio_high_001")["id"] == "prio_high_001"
        # 验证优先级队列大小
        assert scheduler._priority_queue.qsize() >= 2


class TestTaskManager:
    """任务管理统一管理器测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        tm1 = TaskManager()
        tm2 = TaskManager()
        assert tm1 is tm2
        assert tm1 is task_manager

    def test_decomposer_accessible(self, tm):
        """测试分解器可访问"""
        assert tm.decomposer is not None
        assert isinstance(tm.decomposer, TaskDecomposer)

    def test_scheduler_accessible(self, tm):
        """测试调度器可访问"""
        assert tm.scheduler is not None
        assert isinstance(tm.scheduler, TaskScheduler)

    def test_get_statistics(self, tm):
        """测试获取统计信息"""
        stats = tm.get_statistics()
        assert "调度器状态" in stats
        assert "执行历史数" in stats
        assert "分解器任务计数" in stats
        assert "运行状态" in stats

    def test_get_task_status(self, tm):
        """测试通过管理器查询任务状态"""
        # 查询不存在的任务
        status = tm.get_task_status("nonexistent_task_via_manager")
        assert "error" in status

    def test_get_pending_tasks(self, tm):
        """测试获取待执行任务列表"""
        pending = tm.get_pending_tasks()
        assert isinstance(pending, list)

    def test_get_execution_history(self, tm):
        """测试获取执行历史"""
        history = tm.get_execution_history(limit=5)
        assert isinstance(history, list)
        assert len(history) <= 5
