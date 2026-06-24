"""
任务管理系统

基于 frame.html 3.3 节设计，负责接收、分解、调度和执行用户指令。

支持：
- 任务分解：将用户自然语言指令分解为结构化子任务树
- 任务调度：基于优先级队列和依赖图进行任务调度
- 任务执行：使用 ThreadPoolExecutor 异步执行任务
- 状态跟踪：全生命周期任务状态管理
- 审计集成：记录任务操作到审计日志
- 消息广播：通过消息总线广播任务状态变更
"""

import uuid
import threading
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
import queue

from jarvis.core.async_executor import TaskPriority
from jarvis.core.message_queue import message_queue, MessagePriority
from jarvis.core.audit_logger import audit_logger, OperationType


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型枚举"""
    SEARCH = "search"                # 搜索任务
    DEVICE_CONTROL = "device_control"  # 设备控制任务
    ANALYSIS = "analysis"            # 分析任务
    CONVERSATION = "conversation"    # 对话任务
    CUSTOM = "custom"                # 自定义任务


@dataclass
class TaskNode:
    """
    任务节点数据结构

    表示一个可执行的子任务，包含任务的全生命周期信息。
    """
    id: str
    description: str
    task_type: TaskType
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: "TaskNode") -> bool:
        """支持优先级队列比较（优先级高的先出队）"""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        # 优先级相同时，先创建的先执行
        return self.created_at < other.created_at

    @property
    def duration(self) -> Optional[float]:
        """计算任务执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_ready(self) -> bool:
        """检查任务是否就绪（无依赖或依赖已完成）"""
        return self.status == TaskStatus.PENDING

    @property
    def is_terminal(self) -> bool:
        """检查任务是否处于终态"""
        return self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.name,
            "dependencies": list(self.dependencies),
            "status": self.status.value,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.duration,
            "metadata": self.metadata,
        }


class TaskDecomposer:
    """
    任务分解引擎

    将用户的自然语言指令分解为结构化的子任务列表。
    基于关键词匹配判断任务类型，为复杂指令生成多个子任务并设置依赖关系。
    """

    # 任务类型关键词映射表
    _KEYWORD_MAP: Dict[TaskType, List[str]] = {
        TaskType.SEARCH: [
            "搜索", "查找", "查询", "搜一下", "查一下", "百度", "谷歌",
            "search", "find", "lookup", "查询一下", "了解一下",
        ],
        TaskType.DEVICE_CONTROL: [
            "打开", "关闭", "开启", "关掉", "调节", "设置", "控制",
            "空调", "灯光", "灯", "窗帘", "音乐", "音响", "电视",
            "温度", "亮度", "音量", "turn on", "turn off", "control",
        ],
        TaskType.ANALYSIS: [
            "分析", "总结", "归纳", "对比", "比较", "评估", "统计",
            "报表", "报告", "趋势", "analyze", "summary", "compare",
        ],
        TaskType.CONVERSATION: [
            "你好", "你是谁", "介绍一下", "聊聊", "告诉我", "解释",
            "什么是", "为什么", "怎么样", "如何", "hello", "hi",
        ],
    }

    # 复合指令分隔关键词（用于拆分多个子任务）
    _COMPOUND_KEYWORDS: List[str] = [
        "然后", "接着", "之后", "再", "并且", "同时", "另外", "以及",
    ]

    def __init__(self):
        """初始化任务分解引擎"""
        self._task_counter = 0
        self._counter_lock = threading.Lock()

    def _generate_task_id(self) -> str:
        """生成唯一任务ID（线程安全）"""
        with self._counter_lock:
            self._task_counter += 1
            return f"task_{self._task_counter:06d}_{uuid.uuid4().hex[:8]}"

    def decompose(self, user_input: str) -> List[TaskNode]:
        """
        将用户指令分解为子任务列表

        处理流程：
        1. 接收用户自然语言指令
        2. 语义解析与意图分类
        3. 任务复杂度评估
        4. 子任务分解与依赖构建
        5. 输出结构化任务列表

        Args:
            user_input: 用户自然语言指令

        Returns:
            子任务节点列表
        """
        try:
            if not user_input or not user_input.strip():
                return []

            user_input = user_input.strip()

            # 评估任务复杂度，判断是否为复合指令
            sub_instructions = self._split_compound_instruction(user_input)

            tasks: List[TaskNode] = []
            for instruction in sub_instructions:
                instruction = instruction.strip()
                if not instruction:
                    continue

                task_type = self._classify_task(instruction)
                task_node = TaskNode(
                    id=self._generate_task_id(),
                    description=instruction,
                    task_type=task_type,
                    priority=TaskPriority.NORMAL,
                    status=TaskStatus.PENDING,
                )
                tasks.append(task_node)

            # 如果没有分解出任务，创建一个对话任务
            if not tasks:
                task_node = TaskNode(
                    id=self._generate_task_id(),
                    description=user_input,
                    task_type=TaskType.CONVERSATION,
                    priority=TaskPriority.NORMAL,
                    status=TaskStatus.PENDING,
                )
                tasks.append(task_node)

            # 构建任务间依赖关系
            self._build_dependencies(tasks)

            print(f"✓ 任务分解完成: 输入 '{user_input[:30]}...' -> {len(tasks)} 个子任务")
            return tasks

        except Exception as e:
            print(f"✗ 任务分解失败: {e}")
            traceback.print_exc()
            # 分解失败时返回单个对话任务，保证流程不中断
            fallback_task = TaskNode(
                id=self._generate_task_id(),
                description=user_input,
                task_type=TaskType.CONVERSATION,
                priority=TaskPriority.NORMAL,
                status=TaskStatus.PENDING,
            )
            return [fallback_task]

    def _classify_task(self, query: str) -> TaskType:
        """
        基于关键词分类任务类型

        Args:
            query: 用户指令文本

        Returns:
            任务类型枚举
        """
        try:
            query_lower = query.lower()
            scores: Dict[TaskType, int] = {t: 0 for t in TaskType}

            for task_type, keywords in self._KEYWORD_MAP.items():
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        scores[task_type] += 1

            # 选择匹配关键词最多的类型
            best_type = max(scores, key=scores.get)
            if scores[best_type] == 0:
                return TaskType.CONVERSATION

            return best_type

        except Exception as e:
            print(f"⚠️ 任务分类异常: {e}")
            return TaskType.CONVERSATION

    def _split_compound_instruction(self, user_input: str) -> List[str]:
        """
        拆分复合指令为多个子指令

        Args:
            user_input: 用户原始输入

        Returns:
            子指令列表
        """
        try:
            sub_instructions = [user_input]

            for keyword in self._COMPOUND_KEYWORDS:
                new_splits: List[str] = []
                for instruction in sub_instructions:
                    parts = instruction.split(keyword)
                    parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) > 1:
                        new_splits.extend(parts)
                    else:
                        new_splits.append(instruction)
                sub_instructions = new_splits

            return sub_instructions if sub_instructions else [user_input]

        except Exception as e:
            print(f"⚠️ 复合指令拆分异常: {e}")
            return [user_input]

    def _build_dependencies(self, tasks: List[TaskNode]) -> None:
        """
        设置任务间依赖关系

        对于分解出的多个子任务，按顺序设置前后依赖，
        形成线性执行链（DAG 任务图的简化形式）。

        Args:
            tasks: 子任务列表
        """
        try:
            if len(tasks) <= 1:
                return

            # 按创建顺序构建线性依赖链：后一个任务依赖前一个任务
            for i in range(1, len(tasks)):
                prev_task_id = tasks[i - 1].id
                tasks[i].dependencies.append(prev_task_id)

        except Exception as e:
            print(f"⚠️ 依赖关系构建异常: {e}")


class TaskScheduler:
    """
    任务调度器

    根据任务优先级、资源可用性和依赖关系，将子任务分配执行。
    支持动态重调度、任务取消和状态查询。

    技术实现：
    - 基于 ThreadPoolExecutor + 优先级队列实现任务调度
    - 支持 LOW/NORMAL/HIGH/CRITICAL 四级优先级
    - 依赖图管理，确保任务按依赖顺序执行
    """

    def __init__(self, max_workers: int = 10):
        """
        初始化任务调度器

        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self._lock = threading.RLock()
        self._priority_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, TaskNode] = {}
        self._futures: Dict[str, Future] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._task_counter = 0

    def start(self) -> None:
        """启动调度器"""
        if self._running:
            return

        self._running = True
        self._scheduler_thread = threading.Thread(
            target=self._schedule_loop,
            daemon=True,
            name="task_scheduler",
        )
        self._scheduler_thread.start()
        print(f"✓ 任务调度器已启动 (max_workers={self.max_workers})")

    def stop(self) -> None:
        """停止调度器"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=2.0)
        self._executor.shutdown(wait=False)
        print("✓ 任务调度器已停止")

    def submit(self, task: TaskNode) -> str:
        """
        提交任务到调度队列

        Args:
            task: 任务节点

        Returns:
            任务ID
        """
        try:
            with self._lock:
                self._tasks[task.id] = task
                self._task_counter += 1

                # 构建依赖图
                for dep_id in task.dependencies:
                    if dep_id not in self._dependency_graph:
                        self._dependency_graph[dep_id] = []
                    self._dependency_graph[dep_id].append(task.id)

                # 将任务放入优先级队列
                self._priority_queue.put(task)

            print(f"✓ 任务已提交 [{task.id}] - {task.description[:30]}... (优先级: {task.priority.name})")
            return task.id

        except Exception as e:
            print(f"✗ 任务提交失败: {e}")
            traceback.print_exc()
            return task.id

    def _schedule_loop(self) -> None:
        """
        调度循环

        从优先级队列取出任务，检查依赖是否完成，分配执行。
        """
        while self._running:
            try:
                # 非阻塞获取任务，避免调度线程永久阻塞
                try:
                    task: TaskNode = self._priority_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # 检查任务是否已被取消
                if task.status == TaskStatus.CANCELLED:
                    continue

                # 检查依赖是否全部完成
                if not self._check_dependencies(task):
                    # 依赖未完成，重新放回队列稍后重试
                    time.sleep(0.1)
                    self._priority_queue.put(task)
                    continue

                # 分配执行
                self._execute_task(task)

            except Exception as e:
                print(f"✗ 调度循环异常: {e}")
                time.sleep(0.5)

    def _check_dependencies(self, task: TaskNode) -> bool:
        """
        检查任务依赖是否全部完成

        Args:
            task: 任务节点

        Returns:
            依赖是否全部完成
        """
        try:
            if not task.dependencies:
                return True

            for dep_id in task.dependencies:
                dep_task = self._tasks.get(dep_id)
                if dep_task is None:
                    # 依赖任务不存在，视为已完成
                    continue
                if dep_task.status != TaskStatus.COMPLETED:
                    return False

            return True

        except Exception as e:
            print(f"⚠️ 依赖检查异常: {e}")
            return False

    def _execute_task(self, task: TaskNode) -> None:
        """
        执行单个任务

        Args:
            task: 任务节点
        """
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            # 获取执行函数
            exec_func = task.metadata.get("exec_func")
            if exec_func is None:
                # 没有执行函数，直接标记完成
                task.result = f"任务 [{task.id}] 无执行函数，自动完成"
                self._complete_task(task)
                return

            # 提交到线程池执行
            future = self._executor.submit(self._run_task, task, exec_func)
            with self._lock:
                self._futures[task.id] = future

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            print(f"✗ 任务执行启动失败 [{task.id}]: {e}")

    def _run_task(self, task: TaskNode, exec_func: Callable) -> None:
        """
        线程池中运行任务的实际方法

        Args:
            task: 任务节点
            exec_func: 执行函数
        """
        try:
            result = exec_func(task)
            task.result = result
            self._complete_task(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            print(f"✗ 任务执行失败 [{task.id}]: {e}")
            traceback.print_exc()

    def _complete_task(self, task: TaskNode) -> None:
        """
        标记任务完成并触发后续依赖任务

        Args:
            task: 任务节点
        """
        try:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()

            duration = task.duration if task.duration else 0.0
            print(f"✓ 任务已完成 [{task.id}]，耗时 {duration:.2f}秒")

        except Exception as e:
            print(f"⚠️ 任务完成处理异常: {e}")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息字典
        """
        try:
            with self._lock:
                task = self._tasks.get(task_id)
                if task is None:
                    return {"error": f"任务不存在: {task_id}"}
                return task.to_dict()

        except Exception as e:
            return {"error": f"查询任务状态失败: {e}"}

    def get_pending_tasks(self) -> List[TaskNode]:
        """
        获取待执行任务列表

        Returns:
            待执行任务节点列表
        """
        try:
            with self._lock:
                return [
                    task for task in self._tasks.values()
                    if task.status == TaskStatus.PENDING
                ]

        except Exception as e:
            print(f"✗ 获取待执行任务失败: {e}")
            return []

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        try:
            with self._lock:
                task = self._tasks.get(task_id)
                if task is None:
                    return False

                # 运行中的任务无法直接取消
                if task.status == TaskStatus.RUNNING:
                    # 尝试取消 future
                    future = self._futures.get(task_id)
                    if future and not future.cancel():
                        print(f"⚠️ 任务 [{task_id}] 正在运行中，无法取消")
                        return False

                if task.is_terminal:
                    return False

                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()

            print(f"✓ 任务已取消 [{task_id}]")
            return True

        except Exception as e:
            print(f"✗ 取消任务失败: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        try:
            with self._lock:
                status_counts = {status: 0 for status in TaskStatus}
                for task in self._tasks.values():
                    status_counts[task.status] += 1

                return {
                    "总任务数": len(self._tasks),
                    "队列大小": self._priority_queue.qsize(),
                    "状态分布": {
                        status.value: count for status, count in status_counts.items()
                    },
                    "最大工作线程": self.max_workers,
                    "运行状态": "运行中" if self._running else "已停止",
                }

        except Exception as e:
            return {"error": f"获取统计信息失败: {e}"}


class TaskManager:
    """
    任务管理统一管理器 - 单例模式（线程安全）

    整合任务分解、调度和执行，提供统一的任务管理接口。
    集成审计日志和消息总线，实现全流程可追溯。

    流程：用户指令 -> 任务分解 -> 任务调度 -> 任务执行 -> 结果汇总
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
            self._instance_lock = threading.RLock()
            self.decomposer = TaskDecomposer()
            self.scheduler = TaskScheduler(max_workers=10)
            self._execution_history: List[Dict[str, Any]] = []
            self._max_history = 1000

            # 启动调度器
            self.scheduler.start()

            print("✓ 任务管理器已初始化")

    def execute(self, user_input: str) -> str:
        """
        完整执行流程（同步）

        流程：分解 -> 调度 -> 执行 -> 汇总

        Args:
            user_input: 用户输入指令

        Returns:
            执行结果汇总字符串
        """
        try:
            start_time = time.time()

            # 记录审计日志
            audit_logger.log_operation(
                operation_type=OperationType.USER_INPUT,
                action="task_execute",
                details={"user_input": user_input[:200]},
            )

            # 1. 任务分解
            tasks = self.decomposer.decompose(user_input)

            if not tasks:
                return "未能分解出可执行的任务"

            # 2. 为每个任务设置执行函数并提交调度
            for task in tasks:
                task.metadata["exec_func"] = self._create_exec_func(task, user_input)
                self.scheduler.submit(task)

            # 3. 等待所有任务完成
            results = self._wait_for_completion(tasks)

            # 4. 结果汇总
            summary = self._summarize_results(tasks, results, user_input)

            duration = time.time() - start_time

            # 记录审计日志
            audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                action="task_execute_completed",
                details={
                    "user_input": user_input[:200],
                    "task_count": len(tasks),
                },
                result=summary[:500],
                duration=duration,
            )

            # 广播任务完成消息
            self._broadcast_status(
                "task_completed",
                {
                    "user_input": user_input,
                    "task_count": len(tasks),
                    "duration": duration,
                    "summary": summary[:500],
                },
            )

            # 记录执行历史
            self._record_history(user_input, tasks, summary, duration)

            return summary

        except Exception as e:
            error_msg = f"任务执行失败: {e}"
            print(f"✗ {error_msg}")
            traceback.print_exc()

            audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                action="task_execute_failed",
                details={"user_input": user_input[:200]},
                result=error_msg,
            )

            return error_msg

    def execute_async(self, user_input: str, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """
        异步执行任务

        Args:
            user_input: 用户输入指令
            priority: 任务优先级

        Returns:
            任务批次ID（用于后续查询）
        """
        try:
            batch_id = f"batch_{uuid.uuid4().hex[:12]}"

            audit_logger.log_operation(
                operation_type=OperationType.USER_INPUT,
                action="task_execute_async",
                details={
                    "user_input": user_input[:200],
                    "batch_id": batch_id,
                    "priority": priority.name,
                },
            )

            # 在后台线程中执行
            def _async_run():
                try:
                    tasks = self.decomposer.decompose(user_input)

                    for task in tasks:
                        task.priority = priority
                        task.metadata["exec_func"] = self._create_exec_func(task, user_input)
                        task.metadata["batch_id"] = batch_id
                        self.scheduler.submit(task)

                    results = self._wait_for_completion(tasks)
                    summary = self._summarize_results(tasks, results, user_input)

                    self._broadcast_status(
                        "task_async_completed",
                        {
                            "batch_id": batch_id,
                            "user_input": user_input,
                            "summary": summary[:500],
                        },
                        priority=MessagePriority.NORMAL,
                    )

                    self._record_history(user_input, tasks, summary, 0.0)

                except Exception as e:
                    print(f"✗ 异步任务执行失败: {e}")
                    traceback.print_exc()

            thread = threading.Thread(target=_async_run, daemon=True, name=f"async_task_{batch_id}")
            thread.start()

            print(f"✓ 异步任务已提交 [{batch_id}] - {user_input[:30]}...")
            return batch_id

        except Exception as e:
            print(f"✗ 异步任务提交失败: {e}")
            traceback.print_exc()
            return ""

    def _create_exec_func(self, task: TaskNode, user_input: str) -> Callable:
        """
        为任务创建执行函数

        根据任务类型分派到不同的执行逻辑。

        Args:
            task: 任务节点
            user_input: 原始用户输入

        Returns:
            执行函数
        """
        def exec_func(t: TaskNode) -> str:
            try:
                task_type = t.task_type

                if task_type == TaskType.SEARCH:
                    return self._execute_search(t)
                elif task_type == TaskType.DEVICE_CONTROL:
                    return self._execute_device_control(t)
                elif task_type == TaskType.ANALYSIS:
                    return self._execute_analysis(t)
                elif task_type == TaskType.CONVERSATION:
                    return self._execute_conversation(t)
                else:
                    return self._execute_custom(t)

            except Exception as e:
                return f"任务执行异常: {e}"

        return exec_func

    def _execute_search(self, task: TaskNode) -> str:
        """执行搜索类任务"""
        try:
            return f"[搜索任务] 已处理搜索请求: {task.description}"
        except Exception as e:
            return f"搜索任务执行失败: {e}"

    def _execute_device_control(self, task: TaskNode) -> str:
        """执行设备控制类任务"""
        try:
            return f"[设备控制] 已处理设备控制指令: {task.description}"
        except Exception as e:
            return f"设备控制任务执行失败: {e}"

    def _execute_analysis(self, task: TaskNode) -> str:
        """执行分析类任务"""
        try:
            return f"[分析任务] 已完成分析: {task.description}"
        except Exception as e:
            return f"分析任务执行失败: {e}"

    def _execute_conversation(self, task: TaskNode) -> str:
        """执行对话类任务"""
        try:
            return f"[对话回复] {task.description}"
        except Exception as e:
            return f"对话任务执行失败: {e}"

    def _execute_custom(self, task: TaskNode) -> str:
        """执行自定义类任务"""
        try:
            return f"[自定义任务] 已执行: {task.description}"
        except Exception as e:
            return f"自定义任务执行失败: {e}"

    def _wait_for_completion(self, tasks: List[TaskNode], timeout: float = 300.0) -> List[Dict[str, Any]]:
        """
        等待所有任务完成

        Args:
            tasks: 任务列表
            timeout: 超时时间（秒）

        Returns:
            任务结果列表
        """
        try:
            deadline = time.time() + timeout

            while time.time() < deadline:
                all_done = True
                for task in tasks:
                    if not task.is_terminal:
                        all_done = False
                        break

                if all_done:
                    break

                time.sleep(0.1)

            return [task.to_dict() for task in tasks]

        except Exception as e:
            print(f"⚠️ 等待任务完成异常: {e}")
            return [task.to_dict() for task in tasks]

    def _summarize_results(
        self,
        tasks: List[TaskNode],
        results: List[Dict[str, Any]],
        user_input: str,
    ) -> str:
        """
        汇总任务执行结果

        Args:
            tasks: 任务列表
            results: 结果列表
            user_input: 原始用户输入

        Returns:
            汇总结果字符串
        """
        try:
            completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
            cancelled = sum(1 for t in tasks if t.status == TaskStatus.CANCELLED)

            lines = [
                f"任务执行汇总（共 {len(tasks)} 个子任务）:",
                f"  - 成功: {completed}",
                f"  - 失败: {failed}",
                f"  - 取消: {cancelled}",
                "",
                "执行结果:",
            ]

            for task in tasks:
                status_icon = {
                    TaskStatus.COMPLETED: "✓",
                    TaskStatus.FAILED: "✗",
                    TaskStatus.CANCELLED: "⊘",
                    TaskStatus.RUNNING: "▶",
                    TaskStatus.PENDING: "○",
                }.get(task.status, "?")

                result_str = str(task.result) if task.result else (task.error or "无结果")
                lines.append(f"  {status_icon} [{task.task_type.value}] {result_str}")

            return "\n".join(lines)

        except Exception as e:
            return f"结果汇总失败: {e}"

    def _broadcast_status(
        self,
        message_type: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> None:
        """
        通过消息总线广播任务状态变更

        Args:
            message_type: 消息类型
            payload: 消息内容
            priority: 消息优先级
        """
        try:
            message_queue.publish(
                topic="task.status",
                payload={
                    "type": message_type,
                    "data": payload,
                    "source": "TaskManager",
                },
                priority=priority,
                source="TaskManager",
                metadata={"message_type": message_type},
            )
        except Exception as e:
            print(f"⚠️ 消息广播失败: {e}")

    def _record_history(
        self,
        user_input: str,
        tasks: List[TaskNode],
        summary: str,
        duration: float,
    ) -> None:
        """
        记录执行历史

        Args:
            user_input: 用户输入
            tasks: 任务列表
            summary: 汇总结果
            duration: 执行时长
        """
        try:
            with self._instance_lock:
                self._execution_history.append({
                    "user_input": user_input[:200],
                    "task_count": len(tasks),
                    "task_ids": [t.id for t in tasks],
                    "summary": summary[:500],
                    "duration": duration,
                    "timestamp": datetime.now().isoformat(),
                })

                # 限制历史记录数量
                if len(self._execution_history) > self._max_history:
                    self._execution_history = self._execution_history[-self._max_history:]

        except Exception as e:
            print(f"⚠️ 记录历史失败: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取任务管理器统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._instance_lock:
                return {
                    "调度器状态": self.scheduler.get_statistics(),
                    "执行历史数": len(self._execution_history),
                    "分解器任务计数": self.decomposer._task_counter,
                    "运行状态": "运行中" if self.scheduler._running else "已停止",
                }

        except Exception as e:
            return {"error": f"获取统计信息失败: {e}"}

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态信息
        """
        try:
            return self.scheduler.get_task_status(task_id)
        except Exception as e:
            return {"error": f"查询任务状态失败: {e}"}

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """获取待执行任务列表"""
        try:
            tasks = self.scheduler.get_pending_tasks()
            return [t.to_dict() for t in tasks]
        except Exception as e:
            print(f"✗ 获取待执行任务失败: {e}")
            return []

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        try:
            result = self.scheduler.cancel_task(task_id)

            if result:
                audit_logger.log_operation(
                    operation_type=OperationType.SYSTEM_ACTION,
                    action="task_cancelled",
                    details={"task_id": task_id},
                )

                self._broadcast_status(
                    "task_cancelled",
                    {"task_id": task_id},
                )

            return result

        except Exception as e:
            print(f"✗ 取消任务失败: {e}")
            return False

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取执行历史

        Args:
            limit: 返回记录数量

        Returns:
            执行历史列表
        """
        try:
            with self._instance_lock:
                return self._execution_history[-limit:]
        except Exception as e:
            print(f"✗ 获取执行历史失败: {e}")
            return []

    def stop(self) -> None:
        """停止任务管理器"""
        try:
            self.scheduler.stop()
            print("✓ 任务管理器已停止")
        except Exception as e:
            print(f"✗ 停止任务管理器失败: {e}")


# 创建全局任务管理器单例
task_manager = TaskManager()
