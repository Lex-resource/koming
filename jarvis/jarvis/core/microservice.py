"""
Agent微服务架构

支持：
- Agent服务化
- HTTP/gRPC通信
- 服务注册与发现
- 负载均衡
- 服务健康检查
"""

import json
import time
import uuid
import threading
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import traceback


class ServiceProtocol(Enum):
    """服务协议"""
    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"


class ServiceStatus(Enum):
    """服务状态"""
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


@dataclass
class ServiceInfo:
    """服务信息"""
    service_id: str
    service_name: str
    service_type: str
    host: str
    port: int
    protocol: ServiceProtocol = ServiceProtocol.HTTP
    status: ServiceStatus = ServiceStatus.STARTING
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    health_check_interval: float = 30.0
    load_factor: float = 1.0


@dataclass
class ServiceRequest:
    """服务请求"""
    request_id: str
    service_name: str
    method: str
    params: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    timeout: float = 30.0
    priority: int = 0
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceResponse:
    """服务响应"""
    request_id: str
    status: int
    data: Any = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0


class ServiceRegistry:
    """服务注册中心 - 单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._services: Dict[str, List[ServiceInfo]] = {}
        self._lock = threading.RLock()
        self._health_check_thread = None
        self._running = False
        self._discovery_hooks: List[Callable] = []

    def start(self):
        """启动服务注册中心"""
        if self._running:
            return

        self._running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
        print("✓ 服务注册中心已启动")

    def stop(self):
        """停止服务注册中心"""
        self._running = False
        if self._health_check_thread:
            self._health_check_thread.join(timeout=2.0)
        print("✓ 服务注册中心已停止")

    def register(self, service: ServiceInfo) -> bool:
        """
        注册服务

        Args:
            service: 服务信息

        Returns:
            是否成功
        """
        with self._lock:
            if service.service_name not in self._services:
                self._services[service.service_name] = []

            for existing in self._services[service.service_name]:
                if existing.service_id == service.service_id:
                    existing.last_heartbeat = datetime.now()
                    existing.status = ServiceStatus.HEALTHY
                    return True

            self._services[service.service_name].append(service)
            print(f"✓ 服务已注册: {service.service_name} ({service.service_id})")

            self._trigger_discovery_hooks(service)

            return True

    def unregister(self, service_id: str) -> bool:
        """
        注销服务

        Args:
            service_id: 服务ID

        Returns:
            是否成功
        """
        with self._lock:
            for service_name, services in self._services.items():
                for service in services:
                    if service.service_id == service_id:
                        services.remove(service)
                        print(f"✓ 服务已注销: {service_name} ({service_id})")
                        return True
        return False

    def discover(self, service_name: str) -> List[ServiceInfo]:
        """
        发现服务

        Args:
            service_name: 服务名称

        Returns:
            服务列表
        """
        with self._lock:
            services = self._services.get(service_name, [])
            return [
                s for s in services
                if s.status == ServiceStatus.HEALTHY
            ]

    def discover_one(self, service_name: str) -> Optional[ServiceInfo]:
        """
        发现单个服务（负载均衡）

        Args:
            service_name: 服务名称

        Returns:
            服务信息或None
        """
        services = self.discover(service_name)
        if not services:
            return None

        services = sorted(services, key=lambda s: s.load_factor)
        return services[0]

    def get_all_services(self) -> Dict[str, List[ServiceInfo]]:
        """获取所有服务"""
        with self._lock:
            return dict(self._services)

    def get_service_count(self, service_name: str = None) -> int:
        """获取服务数量"""
        with self._lock:
            if service_name:
                return len(self._services.get(service_name, []))
            return sum(len(services) for services in self._services.values())

    def update_heartbeat(self, service_id: str) -> bool:
        """更新心跳"""
        with self._lock:
            for services in self._services.values():
                for service in services:
                    if service.service_id == service_id:
                        service.last_heartbeat = datetime.now()
                        return True
        return False

    def update_load_factor(self, service_id: str, load_factor: float):
        """更新负载因子"""
        with self._lock:
            for services in self._services.values():
                for service in services:
                    if service.service_id == service_id:
                        service.load_factor = load_factor
                        return True

    def add_discovery_hook(self, hook: Callable):
        """添加服务发现钩子"""
        self._discovery_hooks.append(hook)

    def _trigger_discovery_hooks(self, service: ServiceInfo):
        """触发发现钩子"""
        for hook in self._discovery_hooks:
            try:
                hook(service)
            except Exception as e:
                print(f"Discovery hook error: {e}")

    def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            time.sleep(10)

            with self._lock:
                current_time = datetime.now()

                for service_name, services in self._services.items():
                    for service in services[:]:
                        age = (current_time - service.last_heartbeat).total_seconds()

                        if age > service.health_check_interval * 3:
                            if service.status != ServiceStatus.UNHEALTHY:
                                print(f"⚠️ 服务不可用: {service_name} ({service.service_id})")
                            service.status = ServiceStatus.UNHEALTHY

                        elif service.status == ServiceStatus.UNHEALTHY and age < service.health_check_interval:
                            service.status = ServiceStatus.HEALTHY
                            print(f"✓ 服务恢复: {service_name} ({service.service_id})")


class BaseAgentService:
    """Agent服务基类"""

    def __init__(
        self,
        service_name: str,
        service_type: str,
        host: str = "0.0.0.0",
        port: int = 8000,
        protocol: ServiceProtocol = ServiceProtocol.HTTP
    ):
        self.service_name = service_name
        self.service_type = service_type
        self.host = host
        self.port = port
        self.protocol = protocol
        self.service_id = f"{service_name}_{uuid.uuid4().hex[:8]}"
        self.service_info = ServiceInfo(
            service_id=self.service_id,
            service_name=service_name,
            service_type=service_type,
            host=host,
            port=port,
            protocol=protocol
        )

        self.registry = ServiceRegistry()
        self._running = False
        self._handlers: Dict[str, Callable] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)

    def register_handler(self, method: str, handler: Callable):
        """注册请求处理器"""
        self._handlers[method] = handler

    async def handle_request(self, request: ServiceRequest) -> ServiceResponse:
        """处理请求"""
        start_time = time.time()

        try:
            handler = self._handlers.get(request.method)

            if not handler:
                return ServiceResponse(
                    request_id=request.request_id,
                    status=404,
                    error=f"Method '{request.method}' not found",
                    duration=time.time() - start_time
                )

            if asyncio.iscoroutinefunction(handler):
                result = await handler(**request.params)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    lambda: handler(**request.params)
                )

            return ServiceResponse(
                request_id=request.request_id,
                status=200,
                data=result,
                duration=time.time() - start_time
            )

        except Exception as e:
            return ServiceResponse(
                request_id=request.request_id,
                status=500,
                error=str(e),
                traceback=traceback.format_exc(),
                duration=time.time() - start_time
            )

    async def handle_http_request(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """处理HTTP请求"""
        try:
            data = await request.json()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ JSON解析失败: {e}")
            data = {}
        except Exception as e:
            print(f"⚠️ 请求解析失败: {e}")
            data = {}

        service_request = ServiceRequest(
            request_id=str(uuid.uuid4()),
            service_name=self.service_name,
            method=request.match_info.get('method', 'default'),
            params=data
        )

        response = await self.handle_request(service_request)

        return aiohttp.web.json_response({
            'status': response.status,
            'data': response.data,
            'error': response.error,
            'duration': response.duration
        })

    async def start(self):
        """启动服务"""
        self._running = True
        self.registry.register(self.service_info)

        if self.protocol == ServiceProtocol.HTTP:
            app = aiohttp.web.Application()
            app.router.add_post('/{method}', self.handle_http_request)
            app.router.add_get('/health', self.health_check)

            self.runner = aiohttp.web.AppRunner(app)
            await self.runner.setup()

            site = aiohttp.web.TCPSite(self.runner, self.host, self.port)
            await site.start()

            print(f"✓ Agent服务已启动: {self.service_name} (http://{self.host}:{self.port})")

        else:
            print(f"⚠️ 协议 {self.protocol} 暂不支持")

    async def stop(self):
        """停止服务"""
        self._running = False
        self.registry.unregister(self.service_id)

        if hasattr(self, 'runner'):
            await self.runner.cleanup()

        print(f"✓ Agent服务已停止: {self.service_name}")

    async def health_check(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """健康检查"""
        return aiohttp.web.json_response({
            'service': self.service_name,
            'status': 'healthy',
            'service_id': self.service_id,
            'timestamp': datetime.now().isoformat()
        })


class AgentServiceClient:
    """Agent服务客户端"""

    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call(
        self,
        service_name: str,
        method: str,
        params: Dict[str, Any] = None,
        timeout: float = 30.0
    ) -> ServiceResponse:
        """
        调用服务

        Args:
            service_name: 服务名称
            method: 方法名
            params: 参数
            timeout: 超时时间

        Returns:
            服务响应
        """
        service = self.registry.discover_one(service_name)

        if not service:
            return ServiceResponse(
                request_id="",
                status=503,
                error=f"Service '{service_name}' not available"
            )

        url = f"http://{service.host}:{service.port}/{method}"

        try:
            async with self.session.request(
                'POST',
                url,
                json=params or {},
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                data = await response.json()

                return ServiceResponse(
                    request_id=data.get('request_id', ''),
                    status=data.get('status', response.status),
                    data=data.get('data'),
                    error=data.get('error'),
                    duration=data.get('duration', 0.0)
                )

        except asyncio.TimeoutError:
            return ServiceResponse(
                request_id="",
                status=408,
                error="Request timeout"
            )

        except Exception as e:
            return ServiceResponse(
                request_id="",
                status=500,
                error=str(e)
            )

    async def call_multiple(
        self,
        calls: List[Dict[str, Any]],
        timeout: float = 30.0
    ) -> List[ServiceResponse]:
        """
        批量调用服务

        Args:
            calls: 调用列表
            timeout: 超时时间

        Returns:
            响应列表
        """
        tasks = [
            self.call(
                service_name=call['service'],
                method=call['method'],
                params=call.get('params'),
                timeout=timeout
            )
            for call in calls
        ]

        return await asyncio.gather(*tasks)


class MicroserviceOrchestrator:
    """微服务编排器"""

    def __init__(self):
        self.registry = ServiceRegistry()
        self.client = AgentServiceClient(self.registry)
        self.workflows: Dict[str, Callable] = {}
        self._running = False

    def register_workflow(self, name: str, workflow: Callable):
        """注册工作流"""
        self.workflows[name] = workflow

    async def execute_workflow(
        self,
        workflow_name: str,
        initial_params: Dict[str, Any] = None
    ) -> Any:
        """执行工作流"""
        workflow = self.workflows.get(workflow_name)

        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        if asyncio.iscoroutinefunction(workflow):
            return await workflow(initial_params or {})
        else:
            return workflow(initial_params or {})

    async def orchestrate(
        self,
        tasks: List[Dict[str, Any]],
        strategy: str = "sequential"
    ) -> List[Any]:
        """
        编排任务

        Args:
            tasks: 任务列表
            strategy: 执行策略 ('sequential', 'parallel', 'fanout')

        Returns:
            结果列表
        """
        if strategy == "sequential":
            results = []
            async with self.client:
                for task in tasks:
                    result = await self.client.call(
                        service_name=task['service'],
                        method=task['method'],
                        params=task.get('params')
                    )
                    results.append(result)
            return results

        elif strategy == "parallel":
            async with self.client:
                tasks_to_execute = [
                    self.client.call(
                        service_name=task['service'],
                        method=task['method'],
                        params=task.get('params')
                    )
                    for task in tasks
                ]
                return await asyncio.gather(*tasks_to_execute)

        elif strategy == "fanout":
            async with self.client:
                service_name = tasks[0]['service']
                service = self.registry.discover(service_name)

                all_results = []
                for task in tasks:
                    results = await self.client.call(
                        service_name=service_name,
                        method=task['method'],
                        params=task.get('params')
                    )
                    all_results.append(results)

                return all_results

        else:
            raise ValueError(f"Unknown strategy: {strategy}")


# 创建全局服务注册中心
service_registry = ServiceRegistry()


# 示例：创建Agent服务
class CommanderAgentService(BaseAgentService):
    """指挥官Agent服务"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        super().__init__(
            service_name="CommanderAgent",
            service_type="agent",
            host=host,
            port=port
        )

        self.register_handler("execute_task", self.execute_task)
        self.register_handler("delegate_task", self.delegate_task)
        self.register_handler("coordinate", self.coordinate)

    async def execute_task(self, user_input: str) -> Dict[str, Any]:
        """执行任务"""
        return {
            "result": f"Commander executed: {user_input}",
            "delegations": []
        }

    async def delegate_task(self, task: str, to_agent: str) -> Dict[str, Any]:
        """委派任务"""
        return {
            "delegated_to": to_agent,
            "task": task,
            "status": "delegated"
        }

    async def coordinate(self, agents: List[str], task: str) -> Dict[str, Any]:
        """协调多Agent"""
        return {
            "coordinated_agents": agents,
            "task": task,
            "status": "coordinated"
        }


class ExecutorAgentService(BaseAgentService):
    """执行者Agent服务"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8002):
        super().__init__(
            service_name="ExecutorAgent",
            service_type="agent",
            host=host,
            port=port
        )

        self.register_handler("execute_tool", self.execute_tool)
        self.register_handler("search", self.search)
        self.register_handler("get_weather", self.get_weather)

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        return {
            "tool": tool_name,
            "params": params,
            "result": f"Executed {tool_name}",
            "status": "success"
        }

    async def search(self, query: str) -> Dict[str, Any]:
        """搜索"""
        return {
            "query": query,
            "results": [f"Result for {query}"],
            "count": 1
        }

    async def get_weather(self, location: str) -> Dict[str, Any]:
        """获取天气"""
        return {
            "location": location,
            "weather": "Sunny",
            "temperature": 25
        }


# 服务工厂
class AgentServiceFactory:
    """Agent服务工厂"""

    _services = {}

    @classmethod
    def register(cls, service_name: str, service_class: type):
        """注册服务类"""
        cls._services[service_name] = service_class

    @classmethod
    def create(cls, service_name: str, **kwargs) -> BaseAgentService:
        """创建服务实例"""
        service_class = cls._services.get(service_name)

        if not service_class:
            raise ValueError(f"Service class '{service_name}' not found")

        return service_class(**kwargs)

    @classmethod
    def create_all(cls) -> Dict[str, BaseAgentService]:
        """创建所有服务"""
        return {
            name: cls.create(name)
            for name in cls._services.keys()
        }


# 注册默认服务
AgentServiceFactory.register("CommanderAgent", CommanderAgentService)
AgentServiceFactory.register("ExecutorAgent", ExecutorAgentService)


async def start_all_services():
    """启动所有Agent服务"""
    registry = ServiceRegistry()
    registry.start()

    services = {}

    for name, service_class in AgentServiceFactory._services.items():
        port = 8000 + len(services)
        service = AgentServiceFactory.create(
            name,
            host="0.0.0.0",
            port=port
        )
        await service.start()
        services[name] = service

    return services


async def stop_all_services(services: Dict[str, BaseAgentService]):
    """停止所有Agent服务"""
    for service in services.values():
        await service.stop()

    service_registry.stop()


if __name__ == "__main__":
    async def main():
        services = await start_all_services()

        await asyncio.sleep(5)

        await stop_all_services(services)

    asyncio.run(main())
