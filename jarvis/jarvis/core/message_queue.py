"""
消息队列系统 - Agent间解耦通信

支持：
- 主题订阅/发布
- 消息持久化
- 消息优先级
- 消息过滤
- 死信队列
"""

import json
import uuid
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import queue
from concurrent.futures import ThreadPoolExecutor
import traceback


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class MessageStatus(Enum):
    """消息状态"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"
    DEAD_LETTER = "dead_letter"


@dataclass
class Message:
    """消息定义"""
    message_id: str
    topic: str
    payload: Any
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: Optional[float] = None
    retries: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    source: str = "unknown"
    correlation_id: Optional[str] = None

    def __lt__(self, other):
        """支持优先级队列比较"""
        return self.priority.value > other.priority.value

    @property
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        if self.ttl is None:
            return False
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl


@dataclass
class Subscription:
    """订阅定义"""
    subscription_id: str
    topic: str
    callback: Callable
    filter_func: Optional[Callable] = None
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    error_count: int = 0
    last_message_at: Optional[datetime] = None
    active: bool = True

    def can_receive(self, message: Message) -> bool:
        """检查订阅是否可以接收消息"""
        if not self.active:
            return False

        if message.topic != self.topic:
            return False

        if self.tags:
            message_tags = set(message.metadata.get('tags', []))
            if not message_tags.intersection(self.tags):
                return False

        if self.filter_func:
            try:
                return self.filter_func(message)
            except Exception:
                return False

        return True


class MessageQueue:
    """消息队列 - 单例模式"""

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

        self._initialized = True
        self._topics: Dict[str, queue.PriorityQueue] = defaultdict(
            lambda: queue.PriorityQueue(maxsize=10000)
        )
        self._subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self._subscription_map: Dict[str, Subscription] = {}
        self._dead_letter_queue: queue.Queue = queue.Queue()
        self._message_store: Dict[str, Message] = {}
        self._executor = ThreadPoolExecutor(max_workers=20)
        self._running = False
        self._delivery_threads: Dict[str, threading.Thread] = {}
        self._stats = {
            'total_messages': 0,
            'delivered_messages': 0,
            'failed_messages': 0,
            'dead_letter_messages': 0
        }

    def start(self):
        """启动消息队列"""
        if self._running:
            return

        self._running = True
        print("✓ 消息队列已启动")

    def stop(self):
        """停止消息队列"""
        self._running = False

        for thread in self._delivery_threads.values():
            thread.join(timeout=1.0)

        self._executor.shutdown(wait=False)
        print("✓ 消息队列已停止")

    def publish(
        self,
        topic: str,
        payload: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        source: str = "unknown",
        correlation_id: Optional[str] = None
    ) -> str:
        """
        发布消息到主题

        Args:
            topic: 主题名称
            payload: 消息内容
            priority: 优先级
            ttl: 生存时间（秒）
            metadata: 元数据
            headers: 消息头
            source: 消息来源
            correlation_id: 关联ID

        Returns:
            消息ID
        """
        message_id = f"msg_{uuid.uuid4().hex[:12]}"

        message = Message(
            message_id=message_id,
            topic=topic,
            payload=payload,
            priority=priority,
            ttl=ttl,
            metadata=metadata or {},
            headers=headers or {},
            source=source,
            correlation_id=correlation_id
        )

        with self._instance_lock:
            self._topics[topic].put(message)
            self._message_store[message_id] = message
            self._stats['total_messages'] += 1

        print(f"📤 消息已发布 [{message_id}] -> 主题: {topic} (优先级: {priority.name})")

        self._deliver_message(message)

        return message_id

    def subscribe(
        self,
        topic: str,
        callback: Callable[[Message], None],
        filter_func: Optional[Callable] = None,
        tags: Optional[Set[str]] = None,
        subscription_id: Optional[str] = None
    ) -> str:
        """
        订阅主题

        Args:
            topic: 主题名称
            callback: 回调函数
            filter_func: 过滤函数
            tags: 标签集合
            subscription_id: 订阅ID

        Returns:
            订阅ID
        """
        if subscription_id is None:
            subscription_id = f"sub_{uuid.uuid4().hex[:8]}"

        subscription = Subscription(
            subscription_id=subscription_id,
            topic=topic,
            callback=callback,
            filter_func=filter_func,
            tags=tags or set()
        )

        with self._lock:
            self._subscriptions[topic].append(subscription)
            self._subscription_map[subscription_id] = subscription

        print(f"✓ 订阅成功 [{subscription_id}] -> 主题: {topic}")
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        取消订阅

        Args:
            subscription_id: 订阅ID

        Returns:
            是否成功取消
        """
        with self._instance_lock:
            subscription = self._subscription_map.pop(subscription_id, None)
            if subscription:
                self._subscriptions[subscription.topic].remove(subscription)
                subscription.active = False
                print(f"✓ 订阅已取消 [{subscription_id}]")
                return True
            return False

    def _deliver_message(self, message: Message):
        """投递消息到订阅者"""
        if not self._running:
            return

        with self._instance_lock:
            subscriptions = [
                sub for sub in self._subscriptions.get(message.topic, [])
                if sub.can_receive(message)
            ]

        if not subscriptions:
            return

        for subscription in subscriptions:
            self._executor.submit(
                self._deliver_to_subscription,
                message,
                subscription
            )

    def _deliver_to_subscription(self, message: Message, subscription: Subscription):
        """投递消息到单个订阅者"""
        try:
            if message.is_expired:
                message.status = MessageStatus.EXPIRED
                self._handle_dead_letter(message, "Message expired")
                return

            subscription.callback(message)
            message.status = MessageStatus.DELIVERED
            subscription.message_count += 1
            subscription.last_message_at = datetime.now()

            self._stats['delivered_messages'] += 1

            print(f"📥 消息 [{message.message_id}] 已投递给 [{subscription.subscription_id}]")

        except Exception as e:
            subscription.error_count += 1
            message.retries += 1

            if message.retries >= message.max_retries:
                message.status = MessageStatus.FAILED
                self._handle_dead_letter(message, str(e))
                self._stats['failed_messages'] += 1
                print(f"✗ 消息 [{message.message_id}] 投递失败: {e}")
            else:
                time.sleep(0.1 * message.retries)
                self._deliver_to_subscription(message, subscription)

    def _handle_dead_letter(self, message: Message, reason: str):
        """处理死信消息"""
        message.status = MessageStatus.DEAD_LETTER
        message.metadata['dead_letter_reason'] = reason
        message.metadata['dead_letter_time'] = datetime.now().isoformat()

        self._dead_letter_queue.put(message)
        self._stats['dead_letter_messages'] += 1

        print(f"⚠️ 消息 [{message.message_id}] 进入死信队列: {reason}")

    def get_dead_letter_messages(self, limit: int = 100) -> List[Message]:
        """获取死信消息"""
        messages = []
        while not self._dead_letter_queue.empty() and len(messages) < limit:
            try:
                messages.append(self._dead_letter_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def republish_dead_letter(self, message_id: str, topic: str = None) -> Optional[str]:
        """
        重新发布死信消息

        Args:
            message_id: 消息ID
            topic: 新主题（可选）

        Returns:
            新消息ID
        """
        message = self._message_store.get(message_id)
        if not message or message.status != MessageStatus.DEAD_LETTER:
            return None

        message.status = MessageStatus.PENDING
        message.retries = 0

        new_topic = topic or message.topic

        return self.publish(
            topic=new_topic,
            payload=message.payload,
            priority=message.priority,
            metadata=message.metadata,
            source=f"dlq_republish:{message.source}",
            correlation_id=message.correlation_id
        )

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """获取订阅信息"""
        return self._subscription_map.get(subscription_id)

    def list_topics(self) -> List[str]:
        """列出所有主题"""
        return list(self._topics.keys())

    def list_subscriptions(self, topic: Optional[str] = None) -> List[Subscription]:
        """列出订阅"""
        if topic:
            return [
                sub for sub in self._subscriptions.get(topic, [])
                if sub.active
            ]
        return [
            sub for sub in self._subscription_map.values()
            if sub.active
        ]

    def get_queue_size(self, topic: str) -> int:
        """获取队列大小"""
        return self._topics.get(topic, queue.Queue()).qsize()

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            '总消息数': self._stats['total_messages'],
            '已投递消息': self._stats['delivered_messages'],
            '失败消息': self._stats['failed_messages'],
            '死信消息': self._stats['dead_letter_messages'],
            '主题数': len(self._topics),
            '订阅数': len(self._subscription_map),
            '运行状态': '运行中' if self._running else '已停止'
        }

    def clear_topic(self, topic: str) -> int:
        """
        清空主题队列

        Args:
            topic: 主题名称

        Returns:
            清空的消息数
        """
        count = 0
        while not self._topics[topic].empty():
            try:
                self._topics[topic].get_nowait()
                count += 1
            except queue.Empty:
                break
        print(f"✓ 主题 {topic} 已清空 ({count} 条消息)")
        return count


class AgentMessageBus:
    """Agent消息总线 - 高级封装"""

    def __init__(self, message_queue: MessageQueue):
        self.mq = message_queue
        self._agent_id = "unknown"
        self._subscriptions: List[str] = []

    def set_agent_id(self, agent_id: str):
        """设置Agent ID"""
        self._agent_id = agent_id

    def send_message(
        self,
        to_agent: str,
        message_type: str,
        payload: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        向指定Agent发送消息

        Args:
            to_agent: 目标Agent名称
            message_type: 消息类型
            payload: 消息内容
            priority: 优先级
            correlation_id: 关联ID

        Returns:
            消息ID
        """
        topic = f"agent.{to_agent}"

        return self.mq.publish(
            topic=topic,
            payload={
                'type': message_type,
                'data': payload,
                'from_agent': self._agent_id
            },
            priority=priority,
            source=self._agent_id,
            correlation_id=correlation_id,
            metadata={'message_type': message_type}
        )

    def broadcast(
        self,
        message_type: str,
        payload: Any,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        广播消息到所有Agent

        Args:
            message_type: 消息类型
            payload: 消息内容
            priority: 优先级

        Returns:
            消息ID
        """
        return self.mq.publish(
            topic="agent.broadcast",
            payload={
                'type': message_type,
                'data': payload,
                'from_agent': self._agent_id
            },
            priority=priority,
            source=self._agent_id,
            metadata={'message_type': message_type, 'broadcast': True}
        )

    def subscribe_to_agent(
        self,
        from_agent: str,
        callback: Callable[[Message], None],
        message_type: Optional[str] = None
    ):
        """
        订阅来自特定Agent的消息

        Args:
            from_agent: 来源Agent
            callback: 回调函数
            message_type: 消息类型过滤
        """
        topic = f"agent.{from_agent}"

        filter_func = None
        if message_type:
            def filter_func(msg: Message) -> bool:
                return msg.payload.get('type') == message_type

        subscription_id = self.mq.subscribe(
            topic=topic,
            callback=callback,
            filter_func=filter_func
        )

        self._subscriptions.append(subscription_id)
        return subscription_id

    def subscribe_to_broadcast(
        self,
        callback: Callable[[Message], None],
        message_type: Optional[str] = None
    ):
        """
        订阅广播消息

        Args:
            callback: 回调函数
            message_type: 消息类型过滤
        """
        filter_func = None
        if message_type:
            def filter_func(msg: Message) -> bool:
                return msg.payload.get('type') == message_type

        subscription_id = self.mq.subscribe(
            topic="agent.broadcast",
            callback=callback,
            filter_func=filter_func
        )

        self._subscriptions.append(subscription_id)
        return subscription_id

    def request_response(
        self,
        to_agent: str,
        message_type: str,
        payload: Any,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        请求-响应模式

        Args:
            to_agent: 目标Agent
            message_type: 消息类型
            payload: 请求数据
            timeout: 超时时间

        Returns:
            响应数据
        """
        correlation_id = str(uuid.uuid4())
        response_received = threading.Event()
        response_data = {'error': 'Timeout'}

        def response_handler(message: Message):
            nonlocal response_data
            if message.correlation_id == correlation_id:
                response_data = message.payload.get('data', message.payload)
                response_received.set()

        self.subscribe_to_agent(
            from_agent=to_agent,
            callback=response_handler,
            message_type=f"{message_type}_response"
        )

        self.send_message(
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id
        )

        response_received.wait(timeout=timeout)

        return response_data

    def cleanup(self):
        """清理订阅"""
        for sub_id in self._subscriptions:
            self.mq.unsubscribe(sub_id)
        self._subscriptions.clear()


# 创建全局消息队列实例
message_queue = MessageQueue()


# Agent通信示例
def agent_communication_example():
    """Agent通信示例"""

    mq = message_queue

    def commander_callback(message: Message):
        print(f"Commander收到: {message.payload}")

    def executor_callback(message: Message):
        print(f"Executor收到: {message.payload}")

    mq.subscribe("agent.commander", commander_callback)
    mq.subscribe("agent.executor", executor_callback)

    mq.publish(
        topic="agent.executor",
        payload={'type': 'task', 'data': '执行搜索任务'},
        source="agent.commander",
        priority=MessagePriority.HIGH
    )


if __name__ == "__main__":
    agent_communication_example()
