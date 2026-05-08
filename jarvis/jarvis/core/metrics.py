"""
监控指标系统 - Prometheus集成

支持：
- Agent性能指标
- 任务执行指标
- 工具调用指标
- 自定义指标
- HTTP指标端点
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import re


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """指标值"""
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器（线程安全）"""

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
            self._counters: Dict[str, float] = defaultdict(float)
            self._gauges: Dict[str, float] = defaultdict(float)
            self._histograms: Dict[str, List[float]] = defaultdict(list)
            self._summaries: Dict[str, List[float]] = defaultdict(list)
            self._metric_descriptions: Dict[str, str] = {}
            self._metric_types: Dict[str, MetricType] = {}
            self._metric_labels: Dict[str, List[str]] = {}
            self._lock = threading.RLock()
            self._max_histogram_size = 10000
            self._max_summary_size = 10000
            self._max_unique_metrics = 5000
            self._hooks: Dict[str, List[Callable]] = defaultdict(list)
            self._export_formats = ["prometheus", "json", "text"]

    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        labels: Optional[List[str]] = None
    ):
        """
        注册指标

        Args:
            name: 指标名称
            metric_type: 指标类型
            description: 描述
            labels: 标签列表
        """
        with self._lock:
            self._metric_types[name] = metric_type
            self._metric_descriptions[name] = description
            self._metric_labels[name] = labels or []

    def counter_inc(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        增加计数器

        Args:
            name: 指标名称
            value: 增加的值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            self._cleanup_if_needed()
            self._trigger_hook(name, 'counter_inc', value, labels)

    def gauge_set(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        设置仪表值

        Args:
            name: 指标名称
            value: 值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            self._cleanup_if_needed()
            self._trigger_hook(name, 'gauge_set', value, labels)

    def gauge_inc(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """增加仪表值"""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] += value

    def gauge_dec(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """减少仪表值"""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] -= value

    def histogram_observe(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        记录直方图值

        Args:
            name: 指标名称
            value: 值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            if len(self._histograms[key]) > self._max_histogram_size:
                self._histograms[key] = self._histograms[key][-self._max_histogram_size:]

            self._trigger_hook(name, 'histogram_observe', value, labels)

    def summary_observe(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """记录摘要值"""
        with self._lock:
            key = self._make_key(name, labels)
            self._summaries[key].append(value)
            if len(self._summaries[key]) > self._max_summary_size:
                self._summaries[key] = self._summaries[key][-self._max_summary_size:]

    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """生成带标签的键"""
        if not labels:
            return name

        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _cleanup_if_needed(self):
        """内存清理 - 当指标数量过多时清理最旧的指标"""
        total_metrics = (
            len(self._counters) + 
            len(self._gauges) + 
            len(self._histograms) + 
            len(self._summaries)
        )
        
        if total_metrics <= self._max_unique_metrics:
            return
        
        cleanup_ratio = 0.2
        for _ in range(int(total_metrics * cleanup_ratio)):
            if self._counters:
                oldest_counter = next(iter(self._counters))
                del self._counters[oldest_counter]
            
            if self._gauges and len(self._gauges) > 100:
                oldest_gauge = next(iter(self._gauges))
                del self._gauges[oldest_gauge]

    def _parse_key(self, key: str) -> tuple:
        """解析键为名称和标签"""
        match = re.match(r'(\w+)(?:{(.*)})?', key)
        if not match:
            return key, {}

        name = match.group(1)
        labels = {}

        if match.group(2):
            for label in match.group(2).split(','):
                k, v = label.split('=')
                labels[k.strip()] = v.strip('"')

        return name, labels

    def add_hook(self, metric_name: str, callback: Callable):
        """添加指标钩子"""
        self._hooks[metric_name].append(callback)

    def _trigger_hook(self, name: str, operation: str, value: float, labels: Optional[Dict[str, str]]):
        """触发钩子"""
        for callback in self._hooks.get(name, []):
            try:
                callback(operation, value, labels)
            except Exception as e:
                print(f"Metric hook error: {e}")

    def get_metric(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """获取指标值"""
        key = self._make_key(name, labels)

        with self._lock:
            if name in self._metric_types:
                metric_type = self._metric_types[name]

                if metric_type == MetricType.COUNTER:
                    return self._counters.get(key, 0.0)
                elif metric_type == MetricType.GAUGE:
                    return self._gauges.get(key, 0.0)
                elif metric_type == MetricType.HISTOGRAM:
                    values = self._histograms.get(key, [])
                    return sum(values) / len(values) if values else 0.0
                elif metric_type == MetricType.SUMMARY:
                    values = self._summaries.get(key, [])
                    return sum(values) / len(values) if values else 0.0

        return None

    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {
                    k: {
                        'count': len(v),
                        'sum': sum(v),
                        'avg': sum(v) / len(v) if v else 0,
                        'min': min(v) if v else 0,
                        'max': max(v) if v else 0,
                        'p50': self._percentile(v, 50),
                        'p95': self._percentile(v, 95),
                        'p99': self._percentile(v, 99)
                    }
                    for k, v in self._histograms.items()
                },
                'summaries': {
                    k: {
                        'count': len(v),
                        'sum': sum(v),
                        'avg': sum(v) / len(v) if v else 0
                    }
                    for k, v in self._summaries.items()
                }
            }

    def _percentile(self, values: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def export_prometheus(self) -> str:
        """
        导出Prometheus格式

        Returns:
            Prometheus格式的指标文本
        """
        lines = []
        timestamp = int(time.time() * 1000)

        with self._lock:
            for name, metric_type in self._metric_types.items():
                description = self._metric_descriptions.get(name, '')

                if metric_type == MetricType.COUNTER:
                    lines.append(f"# HELP {name} {description}")
                    lines.append(f"# TYPE {name} counter")
                    for key, value in self._counters.items():
                        if key.startswith(name):
                            lines.append(f"{key} {value} {timestamp}")

                elif metric_type == MetricType.GAUGE:
                    lines.append(f"# HELP {name} {description}")
                    lines.append(f"# TYPE {name} gauge")
                    for key, value in self._gauges.items():
                        if key.startswith(name):
                            lines.append(f"{key} {value} {timestamp}")

                elif metric_type == MetricType.HISTOGRAM:
                    lines.append(f"# HELP {name} {description}")
                    lines.append(f"# TYPE {name} histogram")
                    for key, values in self._histograms.items():
                        if key.startswith(name.split('{')[0]):
                            count = len(values)
                            sum_val = sum(values)
                            lines.append(f"{key}_count {count} {timestamp}")
                            lines.append(f"{key}_sum {sum_val} {timestamp}")

                elif metric_type == MetricType.SUMMARY:
                    lines.append(f"# HELP {name} {description}")
                    lines.append(f"# TYPE {name} summary")
                    for key, values in self._summaries.items():
                        if key.startswith(name.split('{')[0]):
                            count = len(values)
                            sum_val = sum(values)
                            lines.append(f"{key}_count {count} {timestamp}")
                            lines.append(f"{key}_sum {sum_val} {timestamp}")

        return "\n".join(lines) + "\n"

    def export_json(self) -> str:
        """导出JSON格式"""
        return json.dumps(self.get_all_metrics(), indent=2, default=str)

    def reset(self):
        """重置所有指标"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._summaries.clear()


class AgentMetrics:
    """Agent指标封装"""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.collector = MetricsCollector()
        self._setup_metrics()

    def _setup_metrics(self):
        """设置指标"""
        prefix = f"jarvis_agent_{self.agent_name}"

        self.collector.register_metric(
            f"{prefix}_requests_total",
            MetricType.COUNTER,
            f"Agent {self.agent_name} total requests",
            ['status', 'task_type']
        )

        self.collector.register_metric(
            f"{prefix}_duration_seconds",
            MetricType.HISTOGRAM,
            f"Agent {self.agent_name} request duration",
            ['task_type']
        )

        self.collector.register_metric(
            f"{prefix}_active_requests",
            MetricType.GAUGE,
            f"Agent {self.agent_name} active requests",
            ['task_type']
        )

        self.collector.register_metric(
            f"{prefix}_errors_total",
            MetricType.COUNTER,
            f"Agent {self.agent_name} total errors",
            ['error_type']
        )

        self.collector.register_metric(
            f"{prefix}_delegations_total",
            MetricType.COUNTER,
            f"Agent {self.agent_name} total delegations"
        )

    def record_request(
        self,
        task_type: str,
        status: str,
        duration: float = 0.0
    ):
        """记录请求"""
        prefix = f"jarvis_agent_{self.agent_name}"

        self.collector.counter_inc(
            f"{prefix}_requests_total",
            labels={'status': status, 'task_type': task_type}
        )

        if duration > 0:
            self.collector.histogram_observe(
                f"{prefix}_duration_seconds",
                duration,
                labels={'task_type': task_type}
            )

    def record_delegation(self):
        """记录委派"""
        prefix = f"jarvis_agent_{self.agent_name}"
        self.collector.counter_inc(f"{prefix}_delegations_total")

    def record_error(self, error_type: str):
        """记录错误"""
        prefix = f"jarvis_agent_{self.agent_name}"
        self.collector.counter_inc(
            f"{prefix}_errors_total",
            labels={'error_type': error_type}
        )

    def set_active_requests(self, count: int, task_type: str = "default"):
        """设置活跃请求数"""
        prefix = f"jarvis_agent_{self.agent_name}"
        self.collector.gauge_set(
            f"{prefix}_active_requests",
            count,
            labels={'task_type': task_type}
        )

    def inc_active_requests(self, task_type: str = "default"):
        """增加活跃请求"""
        prefix = f"jarvis_agent_{self.agent_name}"
        self.collector.gauge_inc(
            f"{prefix}_active_requests",
            labels={'task_type': task_type}
        )

    def dec_active_requests(self, task_type: str = "default"):
        """减少活跃请求"""
        prefix = f"jarvis_agent_{self.agent_name}"
        self.collector.gauge_dec(
            f"{prefix}_active_requests",
            labels={'task_type': task_type}
        )


class SystemMetrics:
    """系统级指标"""

    def __init__(self):
        self.collector = MetricsCollector()
        self._setup_metrics()

    def _setup_metrics(self):
        """设置系统指标"""
        self.collector.register_metric(
            "jarvis_up",
            MetricType.GAUGE,
            "JARVIS is running"
        )

        self.collector.register_metric(
            "jarvis_tasks_total",
            MetricType.COUNTER,
            "Total tasks processed"
        )

        self.collector.register_metric(
            "jarvis_tasks_running",
            MetricType.GAUGE,
            "Currently running tasks"
        )

        self.collector.register_metric(
            "jarvis_task_duration_seconds",
            MetricType.HISTOGRAM,
            "Task execution duration"
        )

        self.collector.register_metric(
            "jarvis_tool_calls_total",
            MetricType.COUNTER,
            "Total tool calls",
            ['tool_name', 'status']
        )

        self.collector.register_metric(
            "jarvis_tool_duration_seconds",
            MetricType.HISTOGRAM,
            "Tool call duration",
            ['tool_name']
        )

        self.collector.register_metric(
            "jarvis_memory_usage_bytes",
            MetricType.GAUGE,
            "Memory usage in bytes"
        )

        self.collector.register_metric(
            "jarvis_conversations_total",
            MetricType.COUNTER,
            "Total conversations"
        )

        self.collector.register_metric(
            "jarvis_messages_total",
            MetricType.COUNTER,
            "Total messages processed",
            ['direction']
        )

        self.collector.register_metric(
            "jarvis_errors_total",
            MetricType.COUNTER,
            "Total errors",
            ['error_type']
        )

    def set_up(self, value: int = 1):
        """设置系统运行状态"""
        self.collector.gauge_set("jarvis_up", value)

    def record_task(self, task_type: str = "general", status: str = "success", duration: float = 0.0):
        """记录任务"""
        self.collector.counter_inc("jarvis_tasks_total", labels={'status': status, 'type': task_type})

        if duration > 0:
            self.collector.histogram_observe("jarvis_task_duration_seconds", duration)

    def set_running_tasks(self, count: int):
        """设置运行中的任务数"""
        self.collector.gauge_set("jarvis_tasks_running", count)

    def record_tool_call(
        self,
        tool_name: str,
        status: str = "success",
        duration: float = 0.0
    ):
        """记录工具调用"""
        self.collector.counter_inc(
            "jarvis_tool_calls_total",
            labels={'tool_name': tool_name, 'status': status}
        )

        if duration > 0:
            self.collector.histogram_observe(
                "jarvis_tool_duration_seconds",
                duration,
                labels={'tool_name': tool_name}
            )

    def record_conversation(self):
        """记录对话"""
        self.collector.counter_inc("jarvis_conversations_total")

    def record_message(self, direction: str = "input"):
        """记录消息"""
        self.collector.counter_inc("jarvis_messages_total", labels={'direction': direction})

    def record_error(self, error_type: str = "unknown"):
        """记录错误"""
        self.collector.counter_inc("jarvis_errors_total", labels={'error_type': error_type})


class MetricsServer:
    """指标HTTP服务器"""

    def __init__(self, collector: MetricsCollector, host: str = "0.0.0.0", port: int = 8000):
        self.collector = collector
        self.host = host
        self.port = port
        self._running = False
        self._server_thread = None

    def start(self):
        """启动指标服务器"""
        import http.server
        import socketserver

        if self._running:
            return

        class MetricsHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/metrics':
                    output = self.server.collector.export_prometheus()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; version=0.0.4')
                    self.end_headers()
                    self.wfile.write(output.encode('utf-8'))

                elif self.path == '/metrics/json':
                    output = self.server.collector.export_json()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(output.encode('utf-8'))

                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')

                else:
                    self.send_response(404)
                    self.end_headers()

        class ReuseAddrTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            self._server = ReuseAddrTCPServer(
                (self.host, self.port),
                MetricsHandler
            )
            self._server.collector = self.collector

            self._server_thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True
            )
            self._server_thread.start()

            self._running = True
            print(f"✓ 指标服务器已启动 (http://{self.host}:{self.port}/metrics)")

        except Exception as e:
            print(f"启动指标服务器失败: {e}")

    def stop(self):
        """停止指标服务器"""
        if self._running and hasattr(self, '_server'):
            self._server.shutdown()
            self._running = False
            print("✓ 指标服务器已停止")


# 创建全局实例
metrics_collector = MetricsCollector()
system_metrics = SystemMetrics()


# 便捷函数
def timeit(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
    时间装饰器

    Args:
        metric_name: 指标名称
        labels: 标签

    Example:
        @timeit("my_operation_seconds")
        def my_operation():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                metrics_collector.histogram_observe(metric_name, time.time() - start_time, labels)
                return result
            except Exception as e:
                metrics_collector.counter_inc(f"{metric_name}_errors", labels=labels)
                raise
        return wrapper
    return decorator


def setup_default_metrics():
    """设置默认指标"""
    system_metrics._setup_metrics()
    system_metrics.set_up(1)


if __name__ == "__main__":
    setup_default_metrics()

    metrics_collector.counter_inc("test_requests_total")
    metrics_collector.gauge_set("test_active", 10)
    metrics_collector.histogram_observe("test_duration", 0.5)
    metrics_collector.histogram_observe("test_duration", 1.5)
    metrics_collector.histogram_observe("test_duration", 2.5)

    print("Prometheus格式:")
    print(metrics_collector.export_prometheus())

    print("\nJSON格式:")
    print(metrics_collector.export_json())
