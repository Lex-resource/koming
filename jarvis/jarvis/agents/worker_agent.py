"""子智能体 - 按需创建，独立上下文，干完销毁"""

import time
import uuid
from datetime import datetime
from typing import List, Optional

from jarvis.core.models import (
    AgentResult,
    TaskStatus,
    ToolCall,
    ToolDefinition,
)
from jarvis.core.interfaces import ICache, ILLM, IStorage
from jarvis.core.blackboard import Blackboard


class WorkerAgent:
    """子智能体 - 隔离上下文，调 LLM + 工具，写产物到 storage，更新黑板"""

    def __init__(
        self,
        role: str,
        prompt: str,
        tools: List[ToolDefinition],
        llm: ILLM,
        model: str,
        storage: IStorage,
        blackboard: Blackboard,
        cache: Optional[ICache] = None,
        timeout: float = 120.0,
        max_retries: int = 2,
    ):
        self.agent_id = f"{role.lower().replace(' ', '-')}_{uuid.uuid4().hex[:8]}"
        self.role = role
        self.prompt = prompt
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.model = model
        self.storage = storage
        self.blackboard = blackboard
        self.cache = cache
        self.timeout = timeout
        self.max_retries = max_retries
        self._cancelled = False
        self._md_log: List[str] = []

    def execute(self, task: str, context: str = "") -> AgentResult:
        """执行子任务，ReAct 循环：LLM→工具调用→LLM→...→完成"""
        start = time.time()
        self._log(f"# {self.role} ({self.agent_id}) 执行记录\n")
        self._log(f"- 任务: {task}")
        self._log(f"- 模型: {self.model}")
        self._log(f"- 工具: {list(self.tools.keys())}")
        self._log("")

        self.blackboard.write_status(self.agent_id, self.role, TaskStatus.RUNNING, "执行中")

        # 读黑板拿其他 Agent 的产物摘要
        if context:
            self._log(f"## 上下文\n{context}\n")

        messages = [{"role": "system", "content": self.prompt},
                    {"role": "user", "content": f"任务: {task}\n\n已有上下文:\n{context}"}]

        tool_list = list(self.tools.values())
        try:
            result_text = self._react_loop(messages, tool_list, task)
            duration = time.time() - start

            # 写产物
            artifact_path = self.storage.write_artifact(
                self._session_id(),
                f"{self.agent_id}-result.md",
                result_text,
            )

            # 写执行记录 md
            self._log(f"\n## 最终产物\n{result_text}\n")
            self._log(f"\n## 耗时\n{duration:.2f}s\n")
            self._flush_md()

            self.blackboard.write_artifact(self.agent_id, artifact_path, result_text[:200])
            self.blackboard.write_status(self.agent_id, self.role, TaskStatus.COMPLETED, "完成")

            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                status=TaskStatus.COMPLETED,
                summary=result_text[:500],
                artifact_path=artifact_path,
                duration=duration,
                md_file=self._md_path(),
            )
        except Exception as e:
            duration = time.time() - start
            self._log(f"\n## 执行失败\n{e}\n")
            self._flush_md()
            self.blackboard.write_status(self.agent_id, self.role, TaskStatus.FAILED, str(e)[:200])
            return AgentResult(
                agent_id=self.agent_id,
                role=self.role,
                status=TaskStatus.FAILED,
                error=str(e),
                duration=duration,
                md_file=self._md_path(),
            )

    def _react_loop(self, messages: List[dict], tools: List[ToolDefinition], task: str) -> str:
        """ReAct 循环：LLM 输出→若调用工具则执行→再给 LLM→...→无工具调用则结束"""
        rounds = 0
        max_tool_rounds = 8
        while rounds < max_tool_rounds and not self._cancelled:
            rounds += 1
            self._log(f"## 第 {rounds} 轮\n")
            response = self.llm.chat(self.model, messages, tools=tools or None)
            self._log(f"- LLM 响应: {response.content[:200] if response.content else '(空)'}")
            if response.tool_calls:
                messages.append({"role": "assistant", "content": response.content or "",
                                 "tool_calls": [self._tool_call_to_dict(tc) for tc in response.tool_calls]})
                for tc in response.tool_calls:
                    self._log(f"- 调用工具: {tc.name}({tc.arguments})")
                    tool_result = self._invoke_tool(tc)
                    self._log(f"  结果: {str(tool_result)[:200]}")
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(tool_result)})
            else:
                return response.content or ""
        return response.content if 'response' in dir() else ""

    def _invoke_tool(self, tool_call: ToolCall) -> str:
        """执行工具调用"""
        tool = self.tools.get(tool_call.name)
        if not tool:
            return f"工具 {tool_call.name} 不存在"
        if tool.handler is None:
            return f"工具 {tool_call.name} 未提供 handler"
        try:
            result = tool.handler(**tool_call.arguments)
            return str(result)
        except Exception as e:
            return f"工具执行失败: {e}"

    def cancel(self) -> None:
        """取消执行（用户改口时决策智能体调用）"""
        self._cancelled = True

    # ============ 内部辅助 ============

    def _session_id(self) -> str:
        return self.blackboard.session_id

    def _log(self, line: str) -> None:
        self._md_log.append(line)

    def _md_path(self) -> str:
        return self.storage.get_session_dir(self._session_id()) + f"/{self.agent_id}.md"

    def _flush_md(self) -> None:
        self.storage.write_file(self._session_id(), f"{self.agent_id}.md", "\n".join(self._md_log))

    @staticmethod
    def _tool_call_to_dict(tc: ToolCall) -> dict:
        return {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
