"""决策智能体 - 系统中枢，ReAct 循环，能自干也能编组"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from jarvis.config.settings import Config, OrchestratorConfig, ReviewConfig, WorkerConfig
from jarvis.core.models import (
    AgentAssignment,
    AgentProfile,
    AgentResult,
    DecisionType,
    GroupPlan,
    LLMResponse,
    ReviewResult,
    ReviewVerdict,
    TaskStatus,
    ToolCall,
    ToolDefinition,
)
from jarvis.core.interfaces import ICache, IDatabase, ILLM, IStorage
from jarvis.core.blackboard import Blackboard
from jarvis.core.experience_store import ExperienceStore
from jarvis.agents.worker_agent import WorkerAgent


class DecisionAgent:
    """决策智能体 - 老板：能判断、能自干、能编组、能验收、能沉淀"""

    def __init__(
        self,
        llm: ILLM,
        storage: IStorage,
        experience_store: ExperienceStore,
        config: Config,
        cache: Optional[ICache] = None,
        tool_registry: Optional[Dict[str, ToolDefinition]] = None,
    ):
        self.llm = llm
        self.storage = storage
        self.exp = experience_store
        self.config = config
        self.cache = cache
        self.tool_registry = tool_registry or {}
        self.orch_cfg: OrchestratorConfig = config.orchestrator
        self.worker_cfg: WorkerConfig = config.worker
        self.review_cfg: ReviewConfig = config.review
        self._active_workers: Dict[str, WorkerAgent] = {}

    def execute(self, user_input: str) -> str:
        """主入口：处理用户输入，返回最终响应"""
        # 1. 缓存命中
        if self.cache:
            cached = self.cache.get(self._cache_key(user_input))
            if cached is not None:
                return cached

        # 2. 决策：自干 vs 编组
        decision = self._decide(user_input)

        if decision == DecisionType.SELF_HANDLE and self.orch_cfg.enable_self_handle:
            result = self._self_handle(user_input)
        else:
            result = self._orchestrate(user_input)

        if self.cache:
            self.cache.set(self._cache_key(user_input), result)
        return result

    # ============ 决策 ============

    def _decide(self, user_input: str) -> DecisionType:
        """让 LLM 判断这个任务该自干还是编组"""
        if not self.orch_cfg.enable_self_handle:
            return DecisionType.ORCHESTRATE

        messages = [
            {"role": "system", "content": self._judge_prompt()},
            {"role": "user", "content": f"用户输入: {user_input}\n\n请判断该自己处理还是编组。"},
        ]
        try:
            resp = self.llm.chat(self.orch_cfg.model, messages)
            text = (resp.content or "").strip().lower()
            if "self" in text or "自干" in text or "自己" in text:
                return DecisionType.SELF_HANDLE
        except Exception:
            pass
        return DecisionType.ORCHESTRATE

    def _judge_prompt(self) -> str:
        return (
            "你是任务分流决策器。判断用户输入适合哪种处理方式：\n\n"
            "1. self_handle（自干）：简单的、单步的、直接可回答的任务。例如：\n"
            "   - 直接问答（什么是 RAG、解释概念）\n"
            "   - 单设备控制（把空调调到26度）\n"
            "   - 单次查询（今天天气）\n\n"
            "2. orchestrate（编组）：复杂的、多步骤的、需要多个专家协作的任务。例如：\n"
            "   - 调研+分析+写报告\n"
            "   - 多设备联动+验证\n"
            "   - 需要搜索+综合多个信息源\n\n"
            "只输出一个词：self_handle 或 orchestrate"
        )

    # ============ 自干 ============

    def _self_handle(self, user_input: str) -> str:
        """简单任务自己调 LLM + 工具直接处理"""
        available = list(self.tool_registry.values())
        messages = [
            {"role": "system", "content": "你是贾维斯，能调用工具处理简单任务。回答用户问题。"},
            {"role": "user", "content": user_input},
        ]
        # ReAct 简单循环
        for _ in range(5):
            resp = self.llm.chat(self.orch_cfg.model, messages, tools=available or None)
            if not resp.has_tool_calls:
                return resp.content or ""
            messages.append({"role": "assistant", "content": resp.content or "",
                             "tool_calls": [{"id": tc.id, "type": "function",
                                             "function": {"name": tc.name, "arguments": tc.arguments}}
                                            for tc in resp.tool_calls]})
            for tc in resp.tool_calls:
                result = self._invoke_tool(tc)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
        return resp.content or "处理完成"

    # ============ 编组流程 ============

    def _orchestrate(self, user_input: str) -> str:
        """完整编组流程"""
        session_id = self.storage.create_session(user_input)
        blackboard = Blackboard(session_id, self.storage, self.config.blackboard)

        # 写决策记录
        self.storage.write_file(
            session_id, "orchestrator.md",
            f"# 决策智能体记录 - {session_id}\n\n## 用户输入\n{user_input}\n",
        )

        # 1. 经验检索
        experience = None
        if self.orch_cfg.enable_experience_reuse:
            experience = self._retrieve_experience(user_input)
            self._append_orchestrator_log(session_id, f"## 经验检索\n{experience or '无匹配'}\n")

        # 2. 编组决策（LLM 输出 GroupPlan）
        plan = self._create_group_plan(user_input, experience)
        blackboard.write_task(user_input, plan)
        self._append_orchestrator_log(session_id, f"## 编组方案\n{json.dumps(plan.to_dict(), ensure_ascii=False, indent=2)}\n")

        # 3. 执行
        results = self._execute_group(plan, blackboard, session_id)

        # 4. 审核
        review = self._review(plan, results, session_id)

        # 5. 不通过→打回重做
        rounds = 0
        while not review.is_passed and rounds < self.review_cfg.max_review_rounds:
            rounds += 1
            self._append_orchestrator_log(session_id, f"\n## 第 {rounds} 轮审核未通过\n{review.feedback}\n")
            results = self._redo_failed(plan, results, review, blackboard, session_id)
            review = self._review(plan, results, session_id)

        # 6. 存档或返回失败
        if review.is_passed:
            result_text = self._summarize_results(plan, results)
            self._archive(plan, results, session_id, result_text)
            self._append_orchestrator_log(session_id, f"\n## 最终结果\n{result_text}\n")
            return result_text
        else:
            return f"任务未能通过审核。反馈: {review.feedback}"

    def _retrieve_experience(self, task: str) -> Optional[Dict]:
        """检索 memory 找类似成功案例"""
        similar = self.exp.search_similar(task)
        return similar[0] if similar else None

    def _create_group_plan(self, task: str, experience: Optional[Dict]) -> GroupPlan:
        """LLM 决策编组方案 + 提示词 + 完成判据"""
        available_models = self.llm.list_models()
        available_tools = list(self.tool_registry.keys())

        exp_hint = ""
        if experience:
            exp_hint = f"\n\n历史相似成功案例（可参考或复用编组）:\n{json.dumps(experience.get('metadata', {}).get('group_plan', {}), ensure_ascii=False)}"

        messages = [
            {"role": "system", "content": self._orchestrator_prompt(available_models, available_tools)},
            {"role": "user", "content": f"任务: {task}{exp_hint}\n\n请输出编组方案 JSON。"},
        ]
        resp = self.llm.chat(self.orch_cfg.model, messages)
        return self._parse_group_plan(resp.content or "", task, experience)

    def _orchestrator_prompt(self, models: List[str], tools: List[str]) -> str:
        return (
            "你是多智能体编排决策器。根据任务设计编组方案。\n\n"
            f"可用模型: {models}\n"
            f"可用工具: {tools}\n\n"
            "输出 JSON 格式：\n"
            "```json\n"
            "{\n"
            '  "agents": [\n'
            '    {"role": "搜索专家", "task": "检索...", "tools": ["web_search"], "model": "glm-4.5-flash", "prompt": "你是搜索专家..."}\n'
            "  ],\n"
            '  "completion_criteria": ["至少3个来源", "包含2026年内容"]\n'
            "}\n"
            "```\n\n"
            "要求：\n"
            "1. 只在需要时编组，简单任务返回空 agents（但这里既然走到编组，至少1个 Agent）\n"
            "2. 每个 Agent 的 prompt 必须包含：角色、任务、输出格式、工具使用方式\n"
            "3. tools 必须从可用工具中选\n"
            "4. model 必须从可用模型中选；简单活用 flash，复杂活用强模型\n"
            "5. completion_criteria 必须是可检查的条件列表\n"
            "只输出 JSON，不要其他内容。"
        )

    def _parse_group_plan(self, llm_output: str, task: str, experience: Optional[Dict]) -> GroupPlan:
        """解析 LLM 输出为 GroupPlan，失败则降级为单 Agent"""
        try:
            # 提取 JSON
            text = llm_output.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            data = json.loads(text)

            agents = []
            for a in data.get("agents", []):
                agents.append(AgentAssignment(
                    role=a["role"],
                    task=a.get("task", ""),
                    tools=a.get("tools", []),
                    model=a.get("model"),
                    prompt=a.get("prompt", ""),
                ))
            return GroupPlan(
                task=task,
                agents=agents,
                completion_criteria=data.get("completion_criteria", []),
                reuse_from=experience.get("metadata", {}).get("session_id") if experience else None,
            )
        except Exception:
            # 降级：单 Agent
            return GroupPlan(
                task=task,
                agents=[AgentAssignment(
                    role="通用助手",
                    task=task,
                    tools=list(self.tool_registry.keys()),
                    model=self.worker_cfg.default_model,
                    prompt="你是通用助手，完成以下任务。",
                )],
                completion_criteria=["任务被完成"],
            )

    def _execute_group(self, plan: GroupPlan, blackboard: Blackboard, session_id: str) -> List[AgentResult]:
        """顺序执行子 Agent，每个完成后下一个可读黑板获取上下文"""
        results = []
        for assignment in plan.agents:
            if assignment.task and assignment.task not in blackboard.read_task():
                pass  # 子任务描述可能不同于主任务

            # 拼接上下文（其他 Agent 的产物摘要）
            context = self._build_context_from_blackboard(blackboard)

            # 获取工具定义
            tools = [self.tool_registry[name] for name in assignment.tools
                     if name in self.tool_registry]

            # 选模型
            model = assignment.model or self.worker_cfg.default_model

            worker = WorkerAgent(
                role=assignment.role,
                prompt=assignment.prompt,
                tools=tools,
                llm=self.llm,
                model=model,
                storage=self.storage,
                blackboard=blackboard,
                cache=self.cache,
                timeout=self.worker_cfg.timeout,
                max_retries=self.worker_cfg.max_retries,
            )
            self._active_workers[worker.agent_id] = worker

            result = worker.execute(assignment.task or plan.task, context)
            results.append(result)
            del self._active_workers[worker.agent_id]

            if not result.is_success:
                break  # 失败则停止后续
        return results

    def _build_context_from_blackboard(self, blackboard: Blackboard) -> str:
        """从黑板读其他 Agent 的产物摘要，拼接为子 Agent 上下文"""
        summaries = blackboard.read_artifact_summaries()
        if not summaries:
            return ""
        lines = ["已有其他 Agent 的产出:"]
        for s in summaries:
            lines.append(f"- {s['role']}: {s['summary']}")
        return "\n".join(lines)

    # ============ 审核 ============

    def _review(self, plan: GroupPlan, results: List[AgentResult], session_id: str) -> ReviewResult:
        """双重审核：自验 + 临时审核 Agent"""
        passed_criteria = []
        failed_criteria = []

        # 1. 自验：产物文件存在性
        if self.review_cfg.enable_self_verify:
            for r in results:
                if r.artifact_path and not self.storage.file_exists(session_id, f"{r.agent_id}-result.md"):
                    failed_criteria.append(f"产物文件缺失: {r.agent_id}")
            for r in results:
                if not r.is_success:
                    failed_criteria.append(f"Agent 执行失败: {r.role}")

        # 2. 临时审核 Agent：对照完成判据
        if self.review_cfg.enable_agent_review and plan.completion_criteria:
            agent_review = self._agent_review(plan, results)
            passed_criteria.extend(agent_review.get("passed", []))
            failed_criteria.extend(agent_review.get("failed", []))
        else:
            passed_criteria = list(plan.completion_criteria)

        verdict = ReviewVerdict.PASSED if not failed_criteria else ReviewVerdict.FAILED
        return ReviewResult(
            verdict=verdict,
            passed_criteria=passed_criteria,
            failed_criteria=failed_criteria,
            feedback="; ".join(failed_criteria) if failed_criteria else "全部通过",
            reviewer="self+agent" if self.review_cfg.enable_agent_review else "self",
        )

    def _agent_review(self, plan: GroupPlan, results: List[AgentResult]) -> Dict[str, List[str]]:
        """临时生成审核 Agent，对照判据逐条验收"""
        results_summary = "\n".join(f"- {r.role}: {r.summary[:300]}" for r in results)
        messages = [
            {"role": "system", "content": (
                "你是审核员。根据完成判据，逐条判断结果是否满足。"
                "输出 JSON: {\"passed\": [...], \"failed\": [...]}"
            )},
            {"role": "user", "content": (
                f"完成判据:\n{json.dumps(plan.completion_criteria, ensure_ascii=False)}\n\n"
                f"执行结果:\n{results_summary}\n\n请逐条判断。"
            )},
        ]
        try:
            resp = self.llm.chat(self.review_cfg.reviewer_model, messages)
            text = resp.content or ""
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except Exception:
            return {"passed": [], "failed": ["审核 Agent 解析失败"]}

    def _redo_failed(
        self, plan: GroupPlan, results: List[AgentResult],
        review: ReviewResult, blackboard: Blackboard, session_id: str,
    ) -> List[AgentResult]:
        """不通过→任务+提示词+审核意见打回原 Agent 重做"""
        new_results = []
        for r in results:
            if r.is_success:
                new_results.append(r)
                continue
            # 找到对应 assignment
            assignment = next((a for a in plan.agents if a.role == r.role), None)
            if not assignment:
                new_results.append(r)
                continue
            tools = [self.tool_registry[name] for name in assignment.tools if name in self.tool_registry]
            model = assignment.model or self.worker_cfg.default_model
            worker = WorkerAgent(
                role=assignment.role,
                prompt=assignment.prompt + f"\n\n上次审核反馈: {review.feedback}\n请据此修正。",
                tools=tools,
                llm=self.llm,
                model=model,
                storage=self.storage,
                blackboard=blackboard,
                cache=self.cache,
                timeout=self.worker_cfg.timeout,
            )
            context = self._build_context_from_blackboard(blackboard)
            new_results.append(worker.execute(assignment.task or plan.task, context))
        return new_results

    # ============ 存档 ============

    def _archive(self, plan: GroupPlan, results: List[AgentResult], session_id: str, result_text: str) -> None:
        """经验分两层存档：memory + skills + profile 更新"""
        # 1. memory 存经验
        self.exp.add_experience(
            task=plan.task,
            plan=plan,
            result_summary=result_text[:500],
            session_id=session_id,
        )

        # 2. skills 存提示词模板（如果是从零写的）
        if self.config.experience.auto_archive_skill:
            for assignment in plan.agents:
                if assignment.skill_id is None and assignment.prompt:
                    skill_id = self.exp.add_skill(
                        prompt=assignment.prompt,
                        tools=assignment.tools,
                        trigger=plan.task[:100],
                        artifact_format="md",
                    )
                    assignment.skill_id = skill_id

        # 3. profile 更新
        for r in results:
            assignment = next((a for a in plan.agents if a.role == r.role), None)
            skills_used = [assignment.skill_id] if assignment and assignment.skill_id else []
            self.exp.update_profile(
                agent_id=r.agent_id,
                role=r.role,
                success=r.is_success,
                duration=r.duration,
                skills_used=skills_used,
            )

    def _summarize_results(self, plan: GroupPlan, results: List[AgentResult]) -> str:
        """汇总所有 Agent 结果"""
        if not results:
            return "无结果"
        if len(results) == 1:
            return results[0].summary
        parts = []
        for r in results:
            parts.append(f"## {r.role}\n{r.summary}")
        return "\n\n".join(parts)

    # ============ 用户改口处理 ============

    def handle_interruption(self, new_input: str, action: str = "reassess") -> str:
        """用户改口时：重新评估当前局面"""
        # action: "cancel_all" / "reassess" / "keep_going"
        if action == "cancel_all":
            for worker in self._active_workers.values():
                worker.cancel()
            self._active_workers.clear()
            return "已取消所有子智能体"
        return f"已收到新指令: {new_input}，将在当前轮次结束后重新评估"

    # ============ 工具调用 ============

    def _invoke_tool(self, tool_call: ToolCall) -> str:
        tool = self.tool_registry.get(tool_call.name)
        if not tool or tool.handler is None:
            return f"工具 {tool_call.name} 不可用"
        try:
            return str(tool.handler(**tool_call.arguments))
        except Exception as e:
            return f"工具执行失败: {e}"

    # ============ 内部辅助 ============

    def _append_orchestrator_log(self, session_id: str, content: str) -> None:
        self.storage.append_file(session_id, "orchestrator.md", content)

    @staticmethod
    def _cache_key(text: str) -> str:
        import hashlib
        return "orchestrator:" + hashlib.sha256(text.encode()).hexdigest()[:16]
