"""
异步任务执行系统

支持：
- 异步任务创建和管理
- 后台任务处理
- 并行Agent执行
- 任务状态跟踪
"""

import asyncio
import uuid
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import threading


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    traceback: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """计算任务执行时长（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def is_success(self) -> bool:
        """判断任务是否成功"""
        return self.status == TaskStatus.COMPLETED


@dataclass
class AsyncTask:
    """异步任务定义"""
    task_id: str
    task_type: str
    description: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: Optional[float] = None
    retries: int = 0
    max_retries: int = 3
    result: Any = None
    error: Optional[str] = None
    callback: Optional[Callable] = None
    tags: List[str] = field(default_factory=list)

    def __lt__(self, other):
        """支持优先级队列比较"""
        return self.priority.value > other.priority.value


class AsyncTaskExecutor:
    """异步任务执行器 - 单例模式（线程安全）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, max_workers: int = 10, default_timeout: float = 300.0):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_workers: int = 10, default_timeout: float = 300.0):
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self._lock = threading.RLock()
            self.max_workers = max_workers
            self.default_timeout = default_timeout
            self.tasks: Dict[str, AsyncTask] = {}
            self.task_queue = asyncio.PriorityQueue()
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self.loop: Optional[asyncio.AbstractEventLoop] = None
            self.running = False
            self._task_counter = 0
            self._results: Dict[str, TaskResult] = {}
            self._pending_tasks: List[AsyncTask] = []
            self._startup_lock = threading.Lock()

    def start(self):
        """启动异步任务执行器"""
        if self.running:
            return

        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self._process_tasks())
        self.loop.create_task(self._cleanup_old_tasks())
        print(f"✓ 异步任务执行器已启动 (max_workers={self.max_workers})")

    def stop(self):
        """停止异步任务执行器"""
        if not self.running:
            return

        self.running = False
        if self.loop:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
        self.executor.shutdown(wait=False)
        print("✓ 异步任务执行器已停止")

    async def _process_tasks(self):
        """处理任务队列"""
        while self.running:
            try:
                if self.task_queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                asyncio.create_task(self._execute_task(task))

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"处理任务时出错: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task: AsyncTask):
        """执行单个任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        print(f"▶ 开始执行任务 [{task.task_id}] - {task.description}")

        start_time = task.started_at
        end_time = None

        try:
            if asyncio.iscoroutinefunction(task.payload.get('func')):
                result = await asyncio.wait_for(
                    task.payload['func'](**task.payload.get('kwargs', {})),
                    timeout=task.timeout or self.default_timeout
                )
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    lambda: task.payload['func'](**task.payload.get('kwargs', {}))
                )

            task.status = TaskStatus.COMPLETED
            task.result = result
            end_time = datetime.now()

            result_obj = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                start_time=start_time,
                end_time=end_time
            )
            self._results[task.task_id] = result_obj

            print(f"✓ 任务 [{task.task_id}] 执行完成，耗时 {result_obj.duration:.2f}秒")

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = f"任务执行超时 ({task.timeout}秒)"
            end_time = datetime.now()

            result_obj = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.TIMEOUT,
                error=task.error,
                start_time=start_time,
                end_time=end_time
            )
            self._results[task.task_id] = result_obj

            print(f"⏰ 任务 [{task.task_id}] 执行超时")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.traceback = traceback.format_exc()
            end_time = datetime.now()

            result_obj = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                traceback=traceback.format_exc(),
                start_time=start_time,
                end_time=end_time
            )
            self._results[task.task_id] = result_obj

            print(f"✗ 任务 [{task.task_id}] 执行失败: {e}")

            if task.retries < task.max_retries:
                task.retries += 1
                task.status = TaskStatus.PENDING
                await self.task_queue.put(task)
                print(f"↻ 任务 [{task.task_id}] 重新加入队列 (重试 {task.retries}/{task.max_retries})")

        task.completed_at = end_time or datetime.now()

        if task.callback:
            try:
                task.callback(task)
            except Exception as e:
                print(f"回调函数执行失败: {e}")

    async def _cleanup_old_tasks(self):
        """清理过期任务"""
        while self.running:
            await asyncio.sleep(60)
            current_time = datetime.now()
            tasks_to_remove = []

            for task_id, task in self.tasks.items():
                if task.completed_at:
                    age = (current_time - task.completed_at).total_seconds()
                    if age > 3600:
                        tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                self.tasks.pop(task_id, None)

    async def _flush_pending_tasks(self):
        """定期处理待处理任务队列"""
        while self.running:
            await asyncio.sleep(0.5)

            while self._pending_tasks and self.loop and self.loop.is_running():
                task = self._pending_tasks.pop(0)
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.task_queue.put(task),
                        self.loop
                    ).result(timeout=1.0)
                except Exception as e:
                    self._pending_tasks.insert(0, task)
                    await asyncio.sleep(0.1)
                    break

    def create_task(
        self,
        task_type: str,
        description: str,
        func: Callable,
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None,
        tags: List[str] = None
    ) -> str:
        """
        创建异步任务（同步接口）

        Args:
            task_type: 任务类型
            description: 任务描述
            func: 异步函数或普通函数
            kwargs: 函数参数
            priority: 优先级
            timeout: 超时时间
            callback: 完成后回调函数
            tags: 标签列表

        Returns:
            任务ID
        """
        with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter:06d}_{uuid.uuid4().hex[:8]}"

        task = AsyncTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            payload={'func': func, 'kwargs': kwargs or {}},
            priority=priority,
            timeout=timeout or self.default_timeout,
            callback=callback,
            tags=tags or []
        )

        self.tasks[task_id] = task

        if self.running and self.loop and self.loop.is_running():
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self.task_queue.put(task),
                    self.loop
                )
                future.result(timeout=1.0)
            except Exception as e:
                self._pending_tasks.append(task)
        else:
            self._pending_tasks.append(task)

        print(f"✓ 任务已创建 [{task_id}] - {description} (优先级: {priority.name})")
        return task_id

    async def create_task_async(
        self,
        task_type: str,
        description: str,
        func: Callable,
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None,
        tags: List[str] = None
    ) -> str:
        """
        创建异步任务（异步接口）

        Args:
            task_type: 任务类型
            description: 任务描述
            func: 异步函数或普通函数
            kwargs: 函数参数
            priority: 优先级
            timeout: 超时时间
            callback: 完成后回调函数
            tags: 标签列表

        Returns:
            任务ID
        """
        with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter:06d}_{uuid.uuid4().hex[:8]}"

        task = AsyncTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            payload={'func': func, 'kwargs': kwargs or {}},
            priority=priority,
            timeout=timeout or self.default_timeout,
            callback=callback,
            tags=tags or []
        )

        self.tasks[task_id] = task
        await self.task_queue.put(task)

        print(f"✓ 任务已创建 [{task_id}] - {description} (优先级: {priority.name})")
        return task_id

    def get_task(self, task_id: str) -> Optional[AsyncTask]:
        """获取任务信息"""
        return self.tasks.get(task_id)

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self._results.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status == TaskStatus.RUNNING:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()

        result_obj = TaskResult(
            task_id=task_id,
            status=TaskStatus.CANCELLED,
            start_time=task.started_at,
            end_time=datetime.now()
        )
        self._results[task_id] = result_obj

        print(f"✓ 任务已取消 [{task_id}]")
        return True

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[AsyncTask]:
        """列出任务"""
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]

        if tags:
            tasks = [t for t in tasks if any(tag in t.tags for tag in tags)]

        return tasks

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        status_counts = {status: 0 for status in TaskStatus}
        for task in self.tasks.values():
            status_counts[task.status] += 1

        return {
            "总任务数": len(self.tasks),
            "队列大小": self.task_queue.qsize(),
            "状态分布": {status.value: count for status, count in status_counts.items()},
            "最大工作线程": self.max_workers,
            "运行状态": "运行中" if self.running else "已停止"
        }

    async def execute_parallel(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[TaskResult]:
        """
        并行执行多个任务

        Args:
            tasks: 任务列表，每个任务包含 func, kwargs, priority 等

        Returns:
            结果列表
        """
        task_ids = []
        for task_info in tasks:
            task_id = self.create_task(
                task_type=task_info.get('task_type', 'parallel'),
                description=task_info.get('description', '并行任务'),
                func=task_info['func'],
                kwargs=task_info.get('kwargs', {}),
                priority=TaskPriority[task_info.get('priority', 'NORMAL')]
            )
            task_ids.append(task_id)

        results = []
        for task_id in task_ids:
            while self.get_task(task_id).status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                await asyncio.sleep(0.1)

            result = self.get_task_result(task_id)
            if result:
                results.append(result)

        return results


class AsyncAgentExecutor:
    """异步Agent执行器 - 集成到CrewManager"""

    def __init__(self, crew_manager, task_executor: AsyncTaskExecutor):
        """
        初始化异步Agent执行器

        Args:
            crew_manager: CrewManager实例
            task_executor: 异步任务执行器
        """
        self.crew_manager = crew_manager
        self.task_executor = task_executor
        self.execution_history: List[Dict[str, Any]] = []

    def execute_async(
        self,
        user_input: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        callback: Optional[Callable] = None
    ) -> str:
        """
        异步执行任务

        Args:
            user_input: 用户输入
            priority: 优先级
            callback: 完成回调

        Returns:
            任务ID
        """
        def execute_task():
            return self.crew_manager.execute_task(user_input)

        task_id = self.task_executor.create_task(
            task_type="agent_execution",
            description=f"执行用户请求: {user_input[:50]}...",
            func=execute_task,
            kwargs={},
            priority=priority,
            callback=callback,
            tags=["agent", "crew"]
        )

        return task_id

    async def execute_multiple_async(
        self,
        inputs: List[str],
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> List[TaskResult]:
        """
        批量异步执行多个请求

        Args:
            inputs: 输入列表
            priority: 优先级

        Returns:
            结果列表
        """
        tasks = [
            {
                'task_type': 'agent_execution',
                'description': f"并行执行: {inp[:30]}...",
                'func': lambda x=inp: self.crew_manager.execute_task(x),
                'kwargs': {},
                'priority': priority.name
            }
            for inp in inputs
        ]

        results = await self.task_executor.execute_parallel(tasks)

        self.execution_history.extend([
            {'input': inp, 'result': r}
            for inp, r in zip(inputs, results)
        ])

        return results

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history[-limit:]


# 创建全局异步任务执行器
async_task_executor = AsyncTaskExecutor(max_workers=10, default_timeout=300.0)


# 便捷函数
def create_async_task(
    task_type: str,
    description: str,
    func: Callable,
    kwargs: Dict[str, Any] = None,
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = None
) -> str:
    """
    创建异步任务的便捷函数

    Args:
        task_type: 任务类型
        description: 任务描述
        func: 函数
        kwargs: 参数
        priority: 优先级
        timeout: 超时时间

    Returns:
        任务ID
    """
    return async_task_executor.create_task(
        task_type=task_type,
        description=description,
        func=func,
        kwargs=kwargs,
        priority=priority,
        timeout=timeout
    )


def get_async_task_result(task_id: str) -> Optional[TaskResult]:
    """获取异步任务结果"""
    return async_task_executor.get_task_result(task_id)
