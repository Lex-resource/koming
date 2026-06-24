"""
增强版CrewManager - 集成插件系统、异步执行、消息队列

支持：
- 插件式Agent加载
- 异步任务执行
- 消息总线通信
- 性能指标收集
"""

from typing import Dict, List, Any, Optional, Callable
from crewai import Crew, Task
from jarvis.agents.base_agent import BaseAgent
from jarvis.core.plugin_registry import plugin_registry, register_builtin_agents, PluginRegistry
from jarvis.core.async_executor import (
    AsyncTaskExecutor,
    async_task_executor,
    AsyncAgentExecutor,
    TaskPriority
)
from jarvis.core.message_queue import message_queue, AgentMessageBus, MessagePriority
from jarvis.core.metrics import metrics_collector, system_metrics, AgentMetrics, setup_default_metrics
from jarvis.core.cache import MultiLevelCache
from jarvis.memory.memory_manager import memory_manager
from jarvis.core.knowledge_manager import knowledge_manager
from jarvis.core.task_manager import task_manager, TaskType
from jarvis.core.device_manager import device_manager
import time
import hashlib
import json


class EnhancedCrewManager:
    """增强版Crew管理器"""

    def __init__(self, enable_async: bool = True, enable_messaging: bool = True):
        self.enable_async = enable_async
        self.enable_messaging = enable_messaging

        register_builtin_agents()

        self.commander = plugin_registry.create_agent("Commander")
        self.analyst = plugin_registry.create_agent("Analyst")
        self.executor = plugin_registry.create_agent("Executor")
        self.learner = plugin_registry.create_agent("Learner")

        if enable_async:
            self.async_executor = AsyncAgentExecutor(
                crew_manager=self,
                task_executor=async_task_executor
            )

        if enable_messaging:
            self.message_bus = AgentMessageBus(message_queue)
            self.message_bus.set_agent_id("Orchestrator")

        self.metrics = {
            'commander': AgentMetrics('Commander'),
            'analyst': AgentMetrics('Analyst'),
            'executor': AgentMetrics('Executor'),
            'learner': AgentMetrics('Learner')
        }

        self.cache = MultiLevelCache()
        self.memory = memory_manager
        self.knowledge = knowledge_manager
        self.task_mgr = task_manager
        self.device_mgr = device_manager

        setup_default_metrics()

    def create_task(self, user_input: str, task_type: str = "general") -> Task:
        """创建任务"""
        return Task(
            description=f"""
用户请求：{user_input}

请根据用户的请求，分析需求并执行相应的操作。
如果需要调用工具，请使用executor agent执行。
如果需要分析问题，请使用analyst agent分析。
如果需要学习新知识，请使用learner agent记录。

请以自然、友好的语言回复用户。
""",
            agent=self.commander,
            expected_output="详细的任务执行结果和回复"
        )

    def _cache_key(self, user_input: str) -> str:
        """生成缓存键"""
        return hashlib.sha256(user_input.encode('utf-8')).hexdigest()[:32]

    def _retrieve_context(self, user_input: str) -> str:
        """从知识管理系统检索相关上下文（向量记忆 + 知识图谱）"""
        try:
            return self.knowledge.retrieve_context(user_input, top_k=3)
        except Exception:
            return ""

    def _store_memory(self, user_input: str, result: str):
        """将对话存入知识管理系统（向量记忆 + 知识图谱 + 偏好学习）"""
        try:
            self.knowledge.store_conversation(user_input, result)
        except Exception:
            pass

    def _learn_from_interaction(self, user_input: str, result: str):
        """从用户交互中学习偏好"""
        try:
            self.knowledge.learn_preference(user_input, result)
        except Exception:
            pass

    def execute_task(self, user_input: str, task_type: str = "general") -> str:
        """同步执行任务（带缓存和记忆增强）"""
        start_time = time.time()

        self.metrics['commander'].inc_active_requests(task_type)

        cache_key = self._cache_key(user_input)

        cached = self.cache.get(cache_key)
        if cached:
            duration = time.time() - start_time
            self.metrics['commander'].record_request(
                task_type=task_type, status="success", duration=duration
            )
            system_metrics.record_task(task_type, "success", duration)
            return f"[缓存命中] {cached}"

        try:
            context = self._retrieve_context(user_input)

            task = self.create_task(user_input + context if context else user_input, task_type)

            crew = Crew(
                agents=[
                    self.commander,
                    self.analyst,
                    self.executor,
                    self.learner
                ],
                tasks=[task],
                verbose=True
            )

            result = crew.kickoff()
            duration = time.time() - start_time

            self.metrics['commander'].record_request(
                task_type=task_type,
                status="success",
                duration=duration
            )

            system_metrics.record_task(task_type, "success", duration)

            self.cache.set(cache_key, str(result), ttl=3600)

            self._store_memory(user_input, str(result))
            self._learn_from_interaction(user_input, str(result))

            if self.enable_messaging:
                self.message_bus.broadcast(
                    message_type="task_completed",
                    payload={
                        "input": user_input,
                        "result": str(result),
                        "duration": duration
                    },
                    priority=MessagePriority.NORMAL
                )

            return str(result)

        except Exception as e:
            duration = time.time() - start_time

            self.metrics['commander'].record_request(
                task_type=task_type,
                status="error",
                duration=duration
            )
            self.metrics['commander'].record_error(type(e).__name__)

            system_metrics.record_task(task_type, "error", duration)
            system_metrics.record_error(type(e).__name__)

            return f"执行出错: {str(e)}"

        finally:
            self.metrics['commander'].dec_active_requests(task_type)

    def execute_task_async(
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
        if not self.enable_async:
            return self.execute_task(user_input)

        task_id = self.async_executor.execute_async(
            user_input=user_input,
            priority=priority,
            callback=callback
        )

        return task_id

    def execute_multiple(
        self,
        inputs: List[str],
        mode: str = "parallel"
    ) -> List[Dict[str, Any]]:
        """
        批量执行

        Args:
            inputs: 输入列表
            mode: 执行模式 ('parallel', 'sequential')

        Returns:
            结果列表
        """
        results = []

        if mode == "parallel" and self.enable_async:
            import asyncio

            async def run():
                return await self.async_executor.execute_multiple_async(
                    inputs=inputs,
                    priority=TaskPriority.NORMAL
                )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                task_results = loop.run_until_complete(run())

                for inp, result in zip(inputs, task_results):
                    results.append({
                        'input': inp,
                        'status': result.status.value,
                        'result': result.result if result.is_success else None,
                        'error': result.error if not result.is_success else None,
                        'duration': result.duration
                    })
            finally:
                loop.close()

        else:
            for inp in inputs:
                start_time = time.time()
                try:
                    result = self.execute_task(inp)
                    results.append({
                        'input': inp,
                        'status': 'completed',
                        'result': result,
                        'duration': time.time() - start_time
                    })
                except Exception as e:
                    results.append({
                        'input': inp,
                        'status': 'failed',
                        'error': str(e),
                        'duration': time.time() - start_time
                    })

        return results

    def get_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """获取Agent指标"""
        metric_obj = self.metrics.get(agent_name.lower())
        if not metric_obj:
            return {}

        return metric_obj.collector.get_all_metrics()

    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        return {
            'system': system_metrics.collector.get_all_metrics(),
            'plugin_stats': plugin_registry.get_statistics(),
            'task_stats': async_task_executor.get_statistics() if self.enable_async else {},
            'message_stats': message_queue.get_statistics() if self.enable_messaging else {}
        }

    def subscribe_to_events(self, callback: Callable):
        """订阅事件"""
        if self.enable_messaging:
            self.message_bus.subscribe_to_broadcast(callback=callback)

    def send_to_agent(
        self,
        agent_name: str,
        message_type: str,
        payload: Any
    ) -> str:
        """向Agent发送消息"""
        if not self.enable_messaging:
            return None

        return self.message_bus.send_message(
            to_agent=agent_name,
            message_type=message_type,
            payload=payload,
            priority=MessagePriority.NORMAL
        )


class PluginBasedCrewManager:
    """基于插件的Crew管理器 - 完全动态化"""

    def __init__(self):
        register_builtin_agents()
        plugin_registry.load_config()

        self._agents: Dict[str, Any] = {}
        self._load_agents()

        self.async_executor = AsyncAgentExecutor(
            crew_manager=self,
            task_executor=async_task_executor
        )

        self.message_bus = AgentMessageBus(message_queue)
        self.message_bus.set_agent_id("PluginOrchestrator")

    def _load_agents(self):
        """加载所有启用的Agent"""
        enabled_agents = plugin_registry.get_enabled_agents()

        for name, agent_class in enabled_agents.items():
            try:
                self._agents[name] = agent_class()
            except Exception as e:
                print(f"Failed to load agent {name}: {e}")

        print(f"✓ 已加载 {len(self._agents)} 个Agent")

    def reload_agents(self):
        """重新加载Agent"""
        self._agents.clear()
        self._load_agents()

    def get_agents(self) -> List[str]:
        """获取所有Agent名称"""
        return list(self._agents.keys())

    def get_agent(self, name: str) -> Optional[Any]:
        """获取Agent实例"""
        return self._agents.get(name)

    def create_task(self, user_input: str) -> Task:
        """创建任务"""
        orchestrator = self._agents.get("Commander")

        if not orchestrator:
            orchestrator = self._agents.get(list(self._agents.keys())[0])

        return Task(
            description=f"用户请求：{user_input}",
            agent=orchestrator,
            expected_output="任务执行结果"
        )

    def execute_task(self, user_input: str) -> str:
        """执行任务"""
        task = self.create_task(user_input)

        crew = Crew(
            agents=list(self._agents.values()),
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff()
        return str(result)

    def execute_task_async(
        self,
        user_input: str,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """异步执行"""
        return self.async_executor.execute_async(
            user_input=user_input,
            priority=priority
        )

    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        plugins = []

        for name in plugin_registry.list_agents():
            metadata = plugin_registry.get_metadata(name)

            if metadata:
                plugins.append({
                    'name': name,
                    'version': metadata.version,
                    'description': metadata.description,
                    'author': metadata.author,
                    'tags': metadata.tags,
                    'enabled': metadata.enabled,
                    'priority': metadata.priority
                })

        return plugins

    def enable_plugin(self, name: str) -> bool:
        """启用插件"""
        result = plugin_registry.enable(name)

        if result:
            self.reload_agents()

        return result

    def disable_plugin(self, name: str) -> bool:
        """禁用插件"""
        result = plugin_registry.disable(name)

        if result:
            plugin_registry.save_config()
            self.reload_agents()

        return result

    def discover_plugins(self, directory: str = None):
        """发现新插件"""
        plugin_registry.discover_from_directory(directory)

        if directory:
            print(f"✓ 已扫描插件目录: {directory}")


class CrewManagerFactory:
    """Crew管理器工厂"""

    @staticmethod
    def create_simple() -> EnhancedCrewManager:
        """创建简单版本"""
        return EnhancedCrewManager(
            enable_async=False,
            enable_messaging=False
        )

    @staticmethod
    def create_standard() -> EnhancedCrewManager:
        """创建标准版本"""
        return EnhancedCrewManager(
            enable_async=True,
            enable_messaging=False
        )

    @staticmethod
    def create_full() -> EnhancedCrewManager:
        """创建完整版本"""
        return EnhancedCrewManager(
            enable_async=True,
            enable_messaging=True
        )

    @staticmethod
    def create_plugin_based() -> PluginBasedCrewManager:
        """创建基于插件的版本"""
        return PluginBasedCrewManager()


# 兼容旧版本
class CrewManager(EnhancedCrewManager):
    """兼容旧版本的CrewManager"""

    def __init__(self):
        super().__init__(enable_async=False, enable_messaging=False)
