"""
智能决策与推理系统 - 实现 frame.html 4.3 节描述的智能决策与推理能力

本模块为贾维斯提供基于规则推理的自主决策能力，包含以下核心组件：
- DecisionType：决策类型枚举，覆盖设备控制、信息查询、任务规划等场景
- Decision：决策结果数据结构，描述一个完整的决策及其推理过程
- Rule：规则定义，包含条件判断与决策生成的可调用对象
- RuleEngine：规则引擎，按优先级评估规则并生成决策
- ContextManager：上下文管理器，整合对话历史、设备状态、用户偏好等上下文
- DecisionEngine：决策引擎（单例），编排完整决策流程并集成审计日志

架构对应 frame.html 4.3 节：
    上下文理解（4.3.2） -> 决策推理引擎（4.3.1） -> 规则评估 -> 决策输出

决策流程：
    1. 收集环境信息与用户意图（ContextManager.build_context）
    2. 检索相关知识库与历史案例（knowledge_manager 集成）
    3. 评估可选方案与风险（RuleEngine.evaluate）
    4. 选择最优决策并生成执行计划（Decision 输出）
    5. 执行后评估结果并反馈学习（审计日志记录）
"""

import re
import uuid
import threading
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable

from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.knowledge_manager import knowledge_manager
from jarvis.core.device_manager import device_manager
from jarvis.core.global_state import global_state
from jarvis.core.cache import MultiLevelCache

# 任务管理器可选导入（避免强依赖，初始化失败时不影响决策引擎）
try:
    from jarvis.core.task_manager import task_manager
except Exception as e:  # pragma: no cover
    print(f"⚠️ 决策引擎：任务管理器加载失败: {e}")
    task_manager = None


# =============================================================================
# 枚举定义
# =============================================================================

class DecisionType(Enum):
    """决策类型枚举

    对应 frame.html 4.3 节中决策推理引擎输出的不同决策类别。
    """
    DEVICE_CONTROL = "device_control"            # 设备控制决策
    INFORMATION_QUERY = "information_query"      # 信息查询决策
    TASK_PLANNING = "task_planning"              # 任务规划决策
    SCENE_SELECTION = "scene_selection"          # 场景选择决策
    RECOMMENDATION = "recommendation"            # 推荐决策
    FALLBACK = "fallback"                        # 兜底决策（交给 LLM 处理）


# =============================================================================
# 决策结果数据结构
# =============================================================================

class Decision:
    """决策结果数据结构

    描述一次完整的决策，包含动作、目标、参数、置信度及推理过程。

    Attributes:
        id: 决策唯一标识
        decision_type: 决策类型（DecisionType）
        action: 具体动作描述（如 "set_property"、"search"、"execute_scene"）
        target: 动作目标（如设备名、场景名、查询关键词）
        parameters: 动作参数字典
        confidence: 置信度（0.0 ~ 1.0）
        reasoning: 决策推理过程说明
        alternatives: 备选方案列表
        created_at: 创建时间（ISO 格式字符串）
    """

    def __init__(
        self,
        decision_type: DecisionType,
        action: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        confidence: float = 0.5,
        reasoning: str = "",
        alternatives: Optional[List[Any]] = None,
        decision_id: str = None,
        created_at: str = None
    ):
        self.id = decision_id or f"decision_{uuid.uuid4().hex[:12]}"
        self.decision_type = decision_type
        self.action = action
        self.target = target
        self.parameters = parameters if parameters is not None else {}
        self.confidence = max(0.0, min(1.0, confidence))
        self.reasoning = reasoning
        self.alternatives = alternatives if alternatives is not None else []
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """将决策序列化为字典

        Returns:
            决策信息字典
        """
        return {
            "id": self.id,
            "decision_type": self.decision_type.value,
            "action": self.action,
            "target": self.target,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "alternatives": self.alternatives,
            "created_at": self.created_at
        }

    def __repr__(self) -> str:
        return (
            f"Decision(id={self.id}, type={self.decision_type.value}, "
            f"action={self.action}, target={self.target}, "
            f"confidence={self.confidence:.2f})"
        )


# =============================================================================
# 规则定义
# =============================================================================

class Rule:
    """规则定义

    一条规则由条件判断函数和决策生成函数组成，附带优先级与描述。
    规则引擎按优先级从高到低依次评估规则，返回第一个匹配的决策。

    Attributes:
        name: 规则名称
        condition: 条件判断函数，签名为 condition(context: dict) -> bool
        action_generator: 决策生成函数，签名为 action_generator(context: dict) -> Decision
        priority: 优先级（数值越大优先级越高）
        description: 规则描述
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        action_generator: Callable[[Dict[str, Any]], Decision],
        priority: int = 0,
        description: str = ""
    ):
        self.name = name
        self.condition = condition
        self.action_generator = action_generator
        self.priority = priority
        self.description = description

    def matches(self, context: Dict[str, Any]) -> bool:
        """判断规则是否匹配当前上下文

        Args:
            context: 决策上下文字典

        Returns:
            是否匹配
        """
        try:
            return self.condition(context)
        except Exception as e:
            print(f"⚠️ 规则 [{self.name}] 条件判断异常: {e}")
            return False

    def generate(self, context: Dict[str, Any]) -> Optional[Decision]:
        """根据上下文生成决策

        Args:
            context: 决策上下文字典

        Returns:
            决策实例，生成失败则返回 None
        """
        try:
            return self.action_generator(context)
        except Exception as e:
            print(f"⚠️ 规则 [{self.name}] 决策生成异常: {e}")
            return None

    def __repr__(self) -> str:
        return f"Rule(name={self.name}, priority={self.priority})"


# =============================================================================
# 设备控制指令解析辅助函数
# =============================================================================

# 设备关键词到标准名称的映射（按优先级排列，长词优先避免误匹配）
_DEVICE_KEYWORD_MAP: List[tuple] = [
    ("空调", "空调"),
    ("灯光", "灯光"),
    ("窗帘", "窗帘"),
    ("音响", "音响"),
    ("电视", "电视"),
    ("灯", "灯光"),       # 短词放后面
    ("音乐", "音响"),     # 音乐关联到音响
]

# 设备属性关键词映射
_DEVICE_PROPERTY_MAP: List[tuple] = [
    (r"调[到成至]?\s*(\d+)\s*度", "temperature"),   # 温度：调到26度
    (r"亮度.*?(\d+)", "brightness"),                  # 亮度
    (r"音量.*?(\d+)", "volume"),                      # 音量
    (r"位置.*?(打开|开启|open)", "position"),          # 窗帘位置
    (r"位置.*?(关闭|合上|closed)", "position"),        # 窗帘位置
]


def _parse_device_command(user_input: str) -> Optional[Dict[str, Any]]:
    """解析设备控制指令

    从用户输入中识别设备名称、控制命令和参数。

    Args:
        user_input: 用户输入文本

    Returns:
        解析结果字典，包含 device_id/device_name/command/property/value；
        无法解析时返回 None
    """
    try:
        if not user_input:
            return None

        # 1. 识别设备名称
        device_name: Optional[str] = None
        for keyword, standard_name in _DEVICE_KEYWORD_MAP:
            if keyword in user_input:
                device_name = standard_name
                break

        if device_name is None:
            return None

        # 2. 从设备管理器查找设备 ID
        device_id = device_name
        try:
            device = device_manager.registry.find_by_name(device_name)
            if device is not None:
                device_id = device.id
        except Exception:
            pass

        # 3. 解析控制命令与参数
        command: Optional[str] = None
        property_name: Optional[str] = None
        value: Any = None

        # 3.1 检查属性设置（温度/亮度/音量/位置）
        for pattern, prop_name in _DEVICE_PROPERTY_MAP:
            match = re.search(pattern, user_input)
            if match:
                command = "set_property"
                property_name = prop_name
                raw_value = match.group(1)
                # 数值型属性转换为 int
                if raw_value.isdigit():
                    value = int(raw_value)
                else:
                    value = raw_value
                break

        # 3.2 检查开关命令
        if command is None:
            if any(kw in user_input for kw in ["打开", "开启", "开一下", "开开"]):
                command = "turn_on"
            elif any(kw in user_input for kw in ["关闭", "关掉", "关了", "关一下", "关关"]):
                command = "turn_off"

        # 3.3 默认查询状态
        if command is None:
            command = "get_status"

        return {
            "device_id": device_id,
            "device_name": device_name,
            "command": command,
            "property": property_name,
            "value": value,
        }

    except Exception as e:
        print(f"⚠️ 设备控制指令解析异常: {e}")
        return None


# =============================================================================
# 规则引擎
# =============================================================================

class RuleEngine:
    """规则引擎 - 按优先级评估规则并生成决策

    维护一组规则列表，支持动态注册。评估时按优先级从高到低依次匹配，
    返回第一个匹配规则生成的决策。

    对应 frame.html 4.3.1 决策推理引擎中的规则推理模式。
    """

    def __init__(self):
        """初始化规则引擎"""
        self._rules: List[Rule] = []
        self._lock = threading.RLock()
        self._init_default_rules()

    def register_rule(self, rule: Rule) -> None:
        """注册规则

        Args:
            rule: 规则实例
        """
        try:
            with self._lock:
                self._rules.append(rule)
                # 按优先级降序排列，保证高优先级规则先评估
                self._rules.sort(key=lambda r: r.priority, reverse=True)
        except Exception as e:
            print(f"⚠️ 注册规则失败: {e}")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Decision]:
        """按优先级评估所有规则，返回第一个匹配的决策

        Args:
            context: 决策上下文字典

        Returns:
            第一个匹配规则生成的决策；无匹配则返回 None
        """
        try:
            with self._lock:
                rules = list(self._rules)

            for rule in rules:
                try:
                    if rule.matches(context):
                        decision = rule.generate(context)
                        if decision is not None:
                            return decision
                except Exception as e:
                    print(f"⚠️ 规则 [{rule.name}] 评估异常: {e}")
                    continue

            return None
        except Exception as e:
            print(f"⚠️ 规则引擎评估异常: {e}")
            return None

    def evaluate_all(self, context: Dict[str, Any]) -> List[Decision]:
        """评估所有匹配的规则

        Args:
            context: 决策上下文字典

        Returns:
            所有匹配规则生成的决策列表
        """
        decisions: List[Decision] = []
        try:
            with self._lock:
                rules = list(self._rules)

            for rule in rules:
                try:
                    if rule.matches(context):
                        decision = rule.generate(context)
                        if decision is not None:
                            decisions.append(decision)
                except Exception as e:
                    print(f"⚠️ 规则 [{rule.name}] 评估异常: {e}")
                    continue
        except Exception as e:
            print(f"⚠️ 规则引擎批量评估异常: {e}")

        return decisions

    def get_rules(self) -> List[Rule]:
        """获取所有已注册规则"""
        with self._lock:
            return list(self._rules)

    def _init_default_rules(self) -> None:
        """初始化默认规则集

        包含设备控制、场景选择、信息查询、天气查询、时间推荐和兜底六条规则。
        """
        try:
            # -----------------------------------------------------------------
            # 1. 设备控制规则（优先级 100）
            #    识别"打开/关闭/设置 + 设备名"模式
            # -----------------------------------------------------------------
            _device_keywords = ["空调", "灯光", "窗帘", "音响", "电视", "灯", "音乐"]
            _control_keywords = [
                "打开", "关闭", "开启", "关掉", "调节", "设置",
                "调到", "调成", "调至", "调亮", "调暗", "调高", "调低",
            ]

            def device_control_condition(context: Dict[str, Any]) -> bool:
                user_input = context.get("user_input", "")
                has_device = any(kw in user_input for kw in _device_keywords)
                has_control = any(kw in user_input for kw in _control_keywords)
                return has_device and has_control

            def device_control_action(context: Dict[str, Any]) -> Decision:
                user_input = context.get("user_input", "")
                result = _parse_device_command(user_input)

                if result is None:
                    return Decision(
                        decision_type=DecisionType.DEVICE_CONTROL,
                        action="unknown",
                        target=user_input,
                        confidence=0.3,
                        reasoning="识别到设备控制意图但无法解析具体指令",
                    )

                device_name = result["device_name"]
                device_id = result["device_id"]
                command = result["command"]

                parameters: Dict[str, Any] = {"device_id": device_id}
                if result.get("property"):
                    parameters["property"] = result["property"]
                    parameters["value"] = result["value"]

                # 构建备选方案：列出其他可用设备
                alternatives: List[Any] = []
                devices = context.get("devices", [])
                for dev in devices:
                    if isinstance(dev, dict) and dev.get("id") != device_id:
                        alternatives.append({
                            "device_id": dev.get("id"),
                            "device_name": dev.get("name"),
                            "action": command,
                        })

                # 推理说明
                reasoning_parts = [f"识别到设备控制指令：{command} {device_name}"]
                if result.get("property"):
                    reasoning_parts.append(
                        f"设置 {result['property']} 为 {result['value']}"
                    )
                reasoning = "，".join(reasoning_parts)

                return Decision(
                    decision_type=DecisionType.DEVICE_CONTROL,
                    action=command,
                    target=device_name,
                    parameters=parameters,
                    confidence=0.9,
                    reasoning=reasoning,
                    alternatives=alternatives,
                )

            self.register_rule(Rule(
                name="device_control",
                condition=device_control_condition,
                action_generator=device_control_action,
                priority=100,
                description="识别设备控制指令（打开/关闭/设置设备属性）",
            ))

            # -----------------------------------------------------------------
            # 2. 场景选择规则（优先级 90）
            #    识别"场景名 + 模式"（如"回家模式"）
            # -----------------------------------------------------------------
            _scene_names = ["回家模式", "离家模式", "睡眠模式", "观影模式"]
            _scene_trigger_keywords = [
                "回家", "离家", "睡眠", "观影", "起床", "工作", "阅读", "娱乐",
            ]

            def scene_selection_condition(context: Dict[str, Any]) -> bool:
                user_input = context.get("user_input", "")
                # 直接匹配已知场景名
                if any(name in user_input for name in _scene_names):
                    return True
                # 匹配"XX模式"模式
                if "模式" in user_input and any(
                    kw in user_input for kw in _scene_trigger_keywords
                ):
                    return True
                # 匹配"执行场景"
                if "场景" in user_input and any(
                    kw in user_input for kw in ["执行", "切换", "启动", "进入"]
                ):
                    return True
                return False

            def scene_selection_action(context: Dict[str, Any]) -> Decision:
                user_input = context.get("user_input", "")

                # 匹配场景名
                matched_scene: Optional[str] = None
                for name in _scene_names:
                    if name in user_input:
                        matched_scene = name
                        break

                # 如果未直接匹配，尝试从关键词推断
                if matched_scene is None:
                    keyword_to_scene = {
                        "回家": "回家模式",
                        "睡眠": "睡眠模式",
                        "观影": "观影模式",
                        "离家": "离家模式",
                    }
                    for keyword, scene_name in keyword_to_scene.items():
                        if keyword in user_input and "模式" in user_input:
                            matched_scene = scene_name
                            break

                # 从设备管理器获取可用场景列表作为备选
                alternatives: List[Any] = []
                try:
                    stats = device_manager.get_statistics()
                    available_scenes = stats.get("scene_names", [])
                    for scene in available_scenes:
                        if scene != matched_scene:
                            alternatives.append({"scene_name": scene})
                except Exception:
                    pass

                target = matched_scene if matched_scene else user_input

                return Decision(
                    decision_type=DecisionType.SCENE_SELECTION,
                    action="execute_scene",
                    target=target,
                    parameters={"scene_name": target},
                    confidence=0.85 if matched_scene else 0.5,
                    reasoning=f"识别到场景选择指令：{target}" if matched_scene
                    else "识别到场景相关意图但未匹配到具体场景",
                    alternatives=alternatives,
                )

            self.register_rule(Rule(
                name="scene_selection",
                condition=scene_selection_condition,
                action_generator=scene_selection_action,
                priority=90,
                description="识别场景选择指令（如回家模式、睡眠模式）",
            ))

            # -----------------------------------------------------------------
            # 3. 天气查询规则（优先级 85）
            #    识别"天气"关键词
            # -----------------------------------------------------------------
            def weather_condition(context: Dict[str, Any]) -> bool:
                user_input = context.get("user_input", "")
                return "天气" in user_input

            def weather_action(context: Dict[str, Any]) -> Decision:
                user_input = context.get("user_input", "")
                return Decision(
                    decision_type=DecisionType.INFORMATION_QUERY,
                    action="weather_query",
                    target="天气",
                    parameters={"query": user_input},
                    confidence=0.85,
                    reasoning="识别到天气查询意图",
                    alternatives=[
                        {"action": "search", "target": user_input},
                    ],
                )

            self.register_rule(Rule(
                name="weather_query",
                condition=weather_condition,
                action_generator=weather_action,
                priority=85,
                description="识别天气查询指令",
            ))

            # -----------------------------------------------------------------
            # 4. 信息搜索规则（优先级 80）
            #    识别"搜索/查询/查找"关键词
            # -----------------------------------------------------------------
            _search_keywords = [
                "搜索", "查询", "查找", "搜一下", "查一下",
                "百度", "谷歌", "search", "find", "lookup",
            ]

            def search_condition(context: Dict[str, Any]) -> bool:
                user_input = context.get("user_input", "")
                user_input_lower = user_input.lower()
                return any(kw in user_input_lower for kw in _search_keywords)

            def search_action(context: Dict[str, Any]) -> Decision:
                user_input = context.get("user_input", "")

                # 提取搜索关键词（去除搜索动词及常见助词）
                query = user_input
                for kw in _search_keywords:
                    query = query.replace(kw, "")
                # 去除残留的常见助词
                for particle in ["一下", "下", "帮", "帮我", "请"]:
                    query = query.replace(particle, "")
                query = query.strip()

                return Decision(
                    decision_type=DecisionType.INFORMATION_QUERY,
                    action="search",
                    target=query if query else user_input,
                    parameters={"query": query if query else user_input},
                    confidence=0.8,
                    reasoning="识别到信息搜索意图",
                    alternatives=[
                        {"action": "weather_query", "target": "天气"},
                    ],
                )

            self.register_rule(Rule(
                name="information_search",
                condition=search_condition,
                action_generator=search_action,
                priority=80,
                description="识别信息搜索/查询指令",
            ))

            # -----------------------------------------------------------------
            # 5. 时间推荐规则（优先级 70）
            #    根据时间上下文主动推荐（如夜晚推荐睡眠模式）
            # -----------------------------------------------------------------
            _greeting_keywords = [
                "你好", "嗨", "hello", "hi", "在吗", "晚安", "早安",
            ]

            def time_recommendation_condition(context: Dict[str, Any]) -> bool:
                time_context = context.get("time_context", {})
                user_input = context.get("user_input", "")
                is_night = time_context.get("is_night", False)
                is_morning = (
                    time_context.get("current_hour", -1) in range(6, 10)
                )
                is_greeting = any(
                    kw in user_input.lower() for kw in _greeting_keywords
                )
                is_very_short = len(user_input.strip()) <= 5
                return (is_night or is_morning) and (is_greeting or is_very_short)

            def time_recommendation_action(context: Dict[str, Any]) -> Decision:
                time_context = context.get("time_context", {})
                is_night = time_context.get("is_night", False)
                current_hour = time_context.get("current_hour", 12)

                if is_night:
                    return Decision(
                        decision_type=DecisionType.RECOMMENDATION,
                        action="execute_scene",
                        target="睡眠模式",
                        parameters={"scene_name": "睡眠模式"},
                        confidence=0.6,
                        reasoning=(
                            f"当前为夜间（{current_hour}时），"
                            f"主动推荐执行睡眠模式以营造舒适睡眠环境"
                        ),
                        alternatives=[
                            {"action": "turn_off", "target": "灯光"},
                            {"action": "turn_off", "target": "音响"},
                        ],
                    )
                else:
                    return Decision(
                        decision_type=DecisionType.RECOMMENDATION,
                        action="execute_scene",
                        target="回家模式",
                        parameters={"scene_name": "回家模式"},
                        confidence=0.55,
                        reasoning=(
                            f"当前为早晨（{current_hour}时），"
                            f"主动推荐执行回家模式以开启日常环境"
                        ),
                        alternatives=[
                            {"action": "turn_on", "target": "灯光"},
                            {"action": "turn_on", "target": "空调"},
                        ],
                    )

            self.register_rule(Rule(
                name="time_recommendation",
                condition=time_recommendation_condition,
                action_generator=time_recommendation_action,
                priority=70,
                description="根据时间上下文主动推荐场景",
            ))

            # -----------------------------------------------------------------
            # 6. 兜底规则（优先级 0）
            #    始终匹配，生成 FALLBACK 决策（交给 LLM 处理）
            # -----------------------------------------------------------------
            def fallback_condition(context: Dict[str, Any]) -> bool:
                return True

            def fallback_action(context: Dict[str, Any]) -> Decision:
                user_input = context.get("user_input", "")
                return Decision(
                    decision_type=DecisionType.FALLBACK,
                    action="llm_process",
                    target=user_input,
                    parameters={"user_input": user_input},
                    confidence=0.3,
                    reasoning="无规则匹配，交给 LLM 进行自然语言处理",
                    alternatives=[],
                )

            self.register_rule(Rule(
                name="fallback",
                condition=fallback_condition,
                action_generator=fallback_action,
                priority=0,
                description="兜底规则，始终匹配，交给 LLM 处理",
            ))

        except Exception as e:
            print(f"⚠️ 默认规则集初始化失败: {e}")


# =============================================================================
# 上下文管理器
# =============================================================================

class ContextManager:
    """上下文管理器 - 构建决策上下文

    整合对话历史、设备状态、知识实体、用户偏好、系统状态和时间上下文，
    为决策引擎提供完整的背景信息。

    对应 frame.html 4.3.2 上下文理解系统：
    - 即时上下文：用户当前输入、系统当前状态、环境即时数据
    - 短期上下文：对话历史、会话中提取的实体
    - 长期上下文：用户偏好画像、知识图谱关系
    """

    def __init__(self):
        """初始化上下文管理器"""
        self._cache = MultiLevelCache()
        self._history_limit = 5

    def build_context(self, user_input: str) -> Dict[str, Any]:
        """构建决策上下文

        Args:
            user_input: 用户输入文本

        Returns:
            决策上下文字典，包含以下字段：
            - user_input: 用户输入
            - history: 最近对话历史
            - devices: 当前设备状态列表
            - entities: 从输入中抽取的实体
            - user_preferences: 用户偏好
            - system_status: 系统状态
            - time_context: 时间上下文
        """
        context: Dict[str, Any] = {"user_input": user_input}

        try:
            # 1. 对话历史（短期上下文）
            try:
                history = global_state.get_conversation_history(
                    limit=self._history_limit
                )
                context["history"] = history if history else []
            except Exception as e:
                print(f"⚠️ 获取对话历史失败: {e}")
                context["history"] = []

            # 2. 设备状态列表（即时上下文）
            try:
                context["devices"] = device_manager.list_all_devices()
            except Exception as e:
                print(f"⚠️ 获取设备状态失败: {e}")
                context["devices"] = []

            # 3. 知识实体抽取（短期上下文）
            try:
                entities = knowledge_manager.extract_entities(user_input)
                context["entities"] = [e.to_dict() for e in entities]
            except Exception as e:
                print(f"⚠️ 实体抽取失败: {e}")
                context["entities"] = []

            # 4. 用户偏好（长期上下文）
            try:
                top_prefs = knowledge_manager.profile.get_top_preferences(n=5)
                context["user_preferences"] = [
                    {"key": k, "value": v, "count": c}
                    for k, v, c in top_prefs
                ]
            except Exception as e:
                print(f"⚠️ 获取用户偏好失败: {e}")
                context["user_preferences"] = []

            # 5. 系统状态（即时上下文）
            try:
                context["system_status"] = global_state.get_system_status()
            except Exception as e:
                print(f"⚠️ 获取系统状态失败: {e}")
                context["system_status"] = {}

            # 6. 时间上下文（环境即时数据）
            context["time_context"] = self._build_time_context()

        except Exception as e:
            print(f"⚠️ 构建上下文失败: {e}")

        return context

    def _build_time_context(self) -> Dict[str, Any]:
        """构建时间上下文

        Returns:
            时间上下文字典，包含当前小时、是否白天/夜晚、是否工作日等
        """
        try:
            now = datetime.now()
            hour = now.hour
            return {
                "current_hour": hour,
                "is_daytime": 6 <= hour < 18,
                "is_night": hour >= 22 or hour < 6,
                "is_morning": 6 <= hour < 10,
                "is_workday": now.weekday() < 5,
                "weekday": now.weekday(),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
            }
        except Exception as e:
            print(f"⚠️ 构建时间上下文失败: {e}")
            return {
                "current_hour": 12,
                "is_daytime": True,
                "is_night": False,
                "is_morning": False,
                "is_workday": True,
                "weekday": 0,
                "date": "",
                "time": "",
            }


# =============================================================================
# 决策引擎（单例）
# =============================================================================

class DecisionEngine:
    """决策引擎 - 单例模式（线程安全）

    编排完整的决策流程，整合规则引擎与上下文管理器，
    集成审计日志记录决策过程。

    对应 frame.html 4.3.1 决策推理引擎的编排层：
    1. 构建上下文（收集环境信息与用户意图）
    2. 规则引擎评估（评估可选方案与风险）
    3. 选择最优决策（生成执行计划）
    4. 记录审计日志（执行后反馈学习）
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
            self._rule_engine = RuleEngine()
            self._context_manager = ContextManager()

            # 引用已有基础设施
            self._knowledge_manager = knowledge_manager
            self._device_manager = device_manager
            self._audit_logger = audit_logger
            self._task_manager = task_manager

            # 决策历史与统计
            self._decision_history: List[Decision] = []
            self._max_history = 1000
            self._statistics: Dict[str, Any] = {
                "total_decisions": 0,
                "by_type": {},
            }

            print("✓ 决策引擎初始化完成")

    # -------------------------------------------------------------------------
    # 核心决策接口
    # -------------------------------------------------------------------------

    def decide(self, user_input: str) -> Decision:
        """完整决策流程

        流程：
        1. 构建上下文
        2. 规则引擎评估
        3. 如果无规则匹配，使用兜底决策
        4. 记录审计日志

        Args:
            user_input: 用户输入文本

        Returns:
            决策实例
        """
        try:
            if not user_input:
                user_input = ""

            # 1. 构建上下文
            context = self._context_manager.build_context(user_input)

            # 2. 规则引擎评估
            decision = self._rule_engine.evaluate(context)

            # 3. 兜底决策
            if decision is None:
                decision = self._create_fallback_decision(user_input, context)

            # 4. 记录历史与统计
            self._record_decision(decision)

            # 5. 审计日志
            self._log_decision(decision, user_input)

            return decision

        except Exception as e:
            print(f"⚠️ 决策失败: {e}")
            return self._create_fallback_decision(user_input, {})

    def decide_with_context(self, context: Dict[str, Any]) -> Decision:
        """基于已有上下文决策

        Args:
            context: 决策上下文字典

        Returns:
            决策实例
        """
        try:
            user_input = context.get("user_input", "")

            # 规则引擎评估
            decision = self._rule_engine.evaluate(context)

            # 兜底决策
            if decision is None:
                decision = self._create_fallback_decision(user_input, context)

            # 记录历史与统计
            self._record_decision(decision)

            # 审计日志
            self._log_decision(decision, user_input)

            return decision

        except Exception as e:
            print(f"⚠️ 基于上下文决策失败: {e}")
            return self._create_fallback_decision(
                context.get("user_input", ""), context
            )

    # -------------------------------------------------------------------------
    # 查询接口
    # -------------------------------------------------------------------------

    def get_decision_history(self) -> List[Decision]:
        """获取决策历史

        Returns:
            决策历史列表（最近优先）
        """
        try:
            with self._instance_lock:
                return list(self._decision_history)
        except Exception as e:
            print(f"⚠️ 获取决策历史失败: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            统计信息字典，包含总决策数、按类型分布、历史大小、规则数等
        """
        try:
            with self._instance_lock:
                return {
                    "total_decisions": self._statistics["total_decisions"],
                    "by_type": dict(self._statistics["by_type"]),
                    "history_size": len(self._decision_history),
                    "rules_count": len(self._rule_engine.get_rules()),
                }
        except Exception as e:
            print(f"⚠️ 获取统计信息失败: {e}")
            return {
                "total_decisions": 0,
                "by_type": {},
                "history_size": 0,
                "rules_count": 0,
            }

    # -------------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------------

    def _record_decision(self, decision: Decision) -> None:
        """记录决策到历史与统计

        Args:
            decision: 决策实例
        """
        try:
            with self._instance_lock:
                self._decision_history.append(decision)
                if len(self._decision_history) > self._max_history:
                    self._decision_history = \
                        self._decision_history[-self._max_history:]

                self._statistics["total_decisions"] += 1
                type_name = decision.decision_type.value
                self._statistics["by_type"][type_name] = \
                    self._statistics["by_type"].get(type_name, 0) + 1
        except Exception as e:
            print(f"⚠️ 记录决策失败: {e}")

    def _log_decision(
        self,
        decision: Decision,
        user_input: str
    ) -> None:
        """记录决策审计日志

        Args:
            decision: 决策实例
            user_input: 用户输入
        """
        try:
            self._audit_logger.log_operation(
                operation_type=OperationType.SYSTEM_ACTION,
                agent_name="DecisionEngine",
                action="decide",
                details={
                    "user_input": user_input[:200],
                    "decision_type": decision.decision_type.value,
                    "action": decision.action,
                    "target": decision.target,
                    "confidence": decision.confidence,
                },
                result=decision.reasoning,
            )
        except Exception as e:
            print(f"⚠️ 决策审计日志记录失败: {e}")

    def _create_fallback_decision(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Decision:
        """创建兜底决策

        Args:
            user_input: 用户输入
            context: 决策上下文

        Returns:
            FALLBACK 类型的决策实例
        """
        return Decision(
            decision_type=DecisionType.FALLBACK,
            action="llm_process",
            target=user_input,
            parameters={"user_input": user_input},
            confidence=0.3,
            reasoning="无规则匹配，交给 LLM 进行自然语言处理",
            alternatives=[],
        )

    # -------------------------------------------------------------------------
    # 便捷访问
    # -------------------------------------------------------------------------

    @property
    def rule_engine(self) -> RuleEngine:
        """获取规则引擎实例"""
        return self._rule_engine

    @property
    def context_manager(self) -> ContextManager:
        """获取上下文管理器实例"""
        return self._context_manager


# 创建全局单例
decision_engine = DecisionEngine()
