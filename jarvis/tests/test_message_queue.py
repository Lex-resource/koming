"""消息队列测试

参考 frame.html 5.2 节核心测试用例表中的"异步任务"场景：
- 输入："异步 搜索 AI 最新进展"
- 预期输出：返回任务 ID，后台执行
- 验证点：任务队列、状态跟踪

覆盖 frame.html 中消息队列系统：
- 主题订阅/发布
- 消息优先级
- 消息统计
- 队列启动/停止
"""
import time
import threading
import queue as queue_module
from concurrent.futures import ThreadPoolExecutor

import pytest

from jarvis.core.message_queue import (
    message_queue,
    MessageQueue,
    Message,
    MessagePriority,
    MessageStatus,
)


# =============================================================================
# pytest fixtures
# =============================================================================

@pytest.fixture
def mq():
    """消息队列单例，确保每个测试前队列处于运行状态"""
    # 确保队列已启动
    message_queue.start()
    yield message_queue


@pytest.fixture
def clean_mq(mq):
    """消息队列单例，测试后清理订阅"""
    yield mq
    # 清理测试中创建的订阅
    subs = list(mq._subscription_map.keys())
    for sub_id in subs:
        try:
            mq.unsubscribe(sub_id)
        except Exception:
            pass


# =============================================================================
# 测试类
# =============================================================================

class TestMessageQueue:
    """消息队列测试 - 验证启动停止、发布订阅、优先级和统计"""

    def test_queue_start_stop(self, mq):
        """测试启动停止"""
        # 验证队列已启动
        assert mq._running is True

        # 停止队列
        mq.stop()
        assert mq._running is False

        # 重新启动并重建执行器（stop 会关闭执行器）
        mq._executor = ThreadPoolExecutor(max_workers=20)
        mq.start()
        assert mq._running is True

    def test_start_idempotent(self, mq):
        """测试重复启动不会出错（幂等）"""
        mq.start()
        assert mq._running is True
        # 再次启动不应抛出异常
        mq.start()
        assert mq._running is True

    def test_publish_subscribe(self, clean_mq):
        """测试发布订阅

        订阅主题后发布消息，验证订阅者收到消息。
        """
        received = threading.Event()
        received_message = {}

        def callback(message):
            """订阅回调，记录收到的消息"""
            received_message["payload"] = message.payload
            received_message["topic"] = message.topic
            received_message["priority"] = message.priority
            received.set()

        # 订阅主题
        sub_id = clean_mq.subscribe("test.topic.publish", callback)
        assert sub_id is not None

        # 发布消息
        msg_id = clean_mq.publish(
            topic="test.topic.publish",
            payload={"data": "hello"},
            priority=MessagePriority.NORMAL,
            source="test",
        )
        assert msg_id is not None

        # 等待消息投递（异步，需等待回调执行）
        assert received.wait(timeout=3.0), "消息投递超时"

        # 验证收到的消息内容
        assert received_message["payload"] == {"data": "hello"}
        assert received_message["topic"] == "test.topic.publish"

    def test_subscribe_with_filter(self, clean_mq):
        """测试带过滤器的订阅"""
        received_messages = []
        received = threading.Event()

        def callback(message):
            received_messages.append(message)
            if len(received_messages) >= 1:
                received.set()

        # 订阅时设置过滤器：只接收 HIGH 优先级消息
        def filter_func(msg):
            return msg.priority == MessagePriority.HIGH

        clean_mq.subscribe("test.topic.filter", callback, filter_func=filter_func)

        # 发布 NORMAL 优先级消息（应被过滤）
        clean_mq.publish(
            topic="test.topic.filter",
            payload="normal",
            priority=MessagePriority.NORMAL,
        )
        time.sleep(0.3)

        # 发布 HIGH 优先级消息（应通过过滤）
        clean_mq.publish(
            topic="test.topic.filter",
            payload="high",
            priority=MessagePriority.HIGH,
        )
        assert received.wait(timeout=3.0)

        # 验证只收到 HIGH 优先级消息
        assert len(received_messages) == 1
        assert received_messages[0].payload == "high"
        assert received_messages[0].priority == MessagePriority.HIGH

    def test_unsubscribe(self, clean_mq):
        """测试取消订阅"""
        received = threading.Event()

        def callback(message):
            received.set()

        sub_id = clean_mq.subscribe("test.topic.unsub", callback)

        # 取消订阅
        result = clean_mq.unsubscribe(sub_id)
        assert result is True

        # 发布消息后不应收到
        clean_mq.publish(topic="test.topic.unsub", payload="test")
        time.sleep(0.3)
        assert not received.is_set()

    def test_message_priority(self, clean_mq):
        """测试消息优先级

        Message.__lt__ 按优先级值降序排列（高优先级先出队）。
        """
        # 创建不同优先级的消息
        msg_low = Message(
            message_id="msg_low",
            topic="test.priority",
            payload="low",
            priority=MessagePriority.LOW,
        )
        msg_normal = Message(
            message_id="msg_normal",
            topic="test.priority",
            payload="normal",
            priority=MessagePriority.NORMAL,
        )
        msg_high = Message(
            message_id="msg_high",
            topic="test.priority",
            payload="high",
            priority=MessagePriority.HIGH,
        )
        msg_critical = Message(
            message_id="msg_critical",
            topic="test.priority",
            payload="critical",
            priority=MessagePriority.CRITICAL,
        )

        # 验证优先级比较：高优先级 < 低优先级（在优先队列中先出队）
        assert msg_critical < msg_high
        assert msg_high < msg_normal
        assert msg_normal < msg_low

        # 验证优先级队列排序
        pq = queue_module.PriorityQueue()
        pq.put(msg_low)
        pq.put(msg_critical)
        pq.put(msg_normal)
        pq.put(msg_high)

        # 取出顺序应为：CRITICAL > HIGH > NORMAL > LOW
        first = pq.get()
        second = pq.get()
        third = pq.get()
        fourth = pq.get()

        assert first.priority == MessagePriority.CRITICAL
        assert second.priority == MessagePriority.HIGH
        assert third.priority == MessagePriority.NORMAL
        assert fourth.priority == MessagePriority.LOW

    def test_queue_statistics(self, clean_mq):
        """测试队列统计"""
        # 记录初始统计
        initial_stats = clean_mq.get_statistics()
        initial_total = initial_stats["总消息数"]

        # 发布消息
        clean_mq.publish(topic="test.topic.stats", payload="msg1")
        clean_mq.publish(topic="test.topic.stats", payload="msg2")

        # 获取统计
        stats = clean_mq.get_statistics()
        assert "总消息数" in stats
        assert "已投递消息" in stats
        assert "失败消息" in stats
        assert "死信消息" in stats
        assert "主题数" in stats
        assert "订阅数" in stats
        assert "运行状态" in stats

        # 验证消息计数增加
        assert stats["总消息数"] >= initial_total + 2

    def test_list_topics(self, clean_mq):
        """测试列出所有主题"""
        clean_mq.publish(topic="test.topic.list1", payload="msg")
        clean_mq.publish(topic="test.topic.list2", payload="msg")

        topics = clean_mq.list_topics()
        assert "test.topic.list1" in topics
        assert "test.topic.list2" in topics

    def test_get_queue_size(self, clean_mq):
        """测试获取队列大小"""
        clean_mq.clear_topic("test.topic.size")
        clean_mq.publish(topic="test.topic.size", payload="msg1")
        clean_mq.publish(topic="test.topic.size", payload="msg2")
        clean_mq.publish(topic="test.topic.size", payload="msg3")

        size = clean_mq.get_queue_size("test.topic.size")
        assert size >= 3

    def test_clear_topic(self, clean_mq):
        """测试清空主题队列"""
        clean_mq.publish(topic="test.topic.clear", payload="msg1")
        clean_mq.publish(topic="test.topic.clear", payload="msg2")

        # 清空主题
        count = clean_mq.clear_topic("test.topic.clear")
        assert count >= 2

        # 验证队列已清空
        assert clean_mq.get_queue_size("test.topic.clear") == 0

    def test_message_expired(self):
        """测试消息过期检查"""
        # 创建带 TTL 的消息
        msg = Message(
            message_id="msg_ttl",
            topic="test.ttl",
            payload="expiring",
            ttl=0.1,  # 0.1 秒后过期
        )
        # 刚创建时未过期
        assert msg.is_expired is False

        # 等待过期
        time.sleep(0.2)
        assert msg.is_expired is True

    def test_message_no_ttl_never_expires(self):
        """测试无 TTL 的消息永不过期"""
        msg = Message(
            message_id="msg_no_ttl",
            topic="test.no.ttl",
            payload="permanent",
            ttl=None,
        )
        assert msg.is_expired is False

    def test_singleton_pattern(self):
        """测试单例模式"""
        mq1 = MessageQueue()
        mq2 = MessageQueue()
        assert mq1 is mq2
        assert mq1 is message_queue

    def test_publish_returns_message_id(self, clean_mq):
        """测试发布消息返回消息ID"""
        msg_id = clean_mq.publish(topic="test.topic.id", payload="test")
        assert msg_id is not None
        assert msg_id.startswith("msg_")

    def test_get_subscription(self, clean_mq):
        """测试获取订阅信息"""
        def callback(message):
            pass

        sub_id = clean_mq.subscribe("test.topic.subinfo", callback)
        sub = clean_mq.get_subscription(sub_id)
        assert sub is not None
        assert sub.topic == "test.topic.subinfo"
        assert sub.active is True
