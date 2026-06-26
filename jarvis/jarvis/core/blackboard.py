"""共享黑板 - 所有 Agent 的共享状态区，子 Agent 不互相通信，读写黑板"""

from datetime import datetime
from typing import Dict, List, Optional

from jarvis.core.models import BlackboardEntry, GroupPlan, TaskStatus
from jarvis.core.interfaces import IStorage
from jarvis.config.settings import BlackboardConfig


class Blackboard:
    """共享黑板 - 写 blackboard.md，所有 Agent 可读"""

    def __init__(self, session_id: str, storage: IStorage, config: BlackboardConfig):
        self.session_id = session_id
        self.storage = storage
        self.config = config
        self._entries: Dict[str, BlackboardEntry] = {}
        self._task: str = ""
        self._plan: Optional[GroupPlan] = None
        self._init_file()

    def _init_file(self) -> None:
        self.storage.write_file(
            self.session_id,
            self.config.blackboard_filename if hasattr(self.config, "blackboard_filename") else "blackboard.md",
            f"# 共享黑板 - {self.session_id}\n\n创建时间: {datetime.now().isoformat()}\n",
        )

    def write_task(self, task: str, plan: GroupPlan) -> None:
        """写入任务定义+编组方案+完成判据"""
        self._task = task
        self._plan = plan
        self._flush()

    def read_task(self) -> str:
        return self._task

    def read_plan(self) -> Optional[GroupPlan]:
        return self._plan

    def write_status(
        self,
        agent_id: str,
        role: str,
        status: TaskStatus,
        summary: str = "",
    ) -> None:
        """Agent 更新自己的执行状态"""
        self._entries[agent_id] = BlackboardEntry(
            agent_id=agent_id,
            role=role,
            status=status,
            summary=summary,
        )
        if self.config.auto_flush:
            self._flush()

    def read_status(self, agent_id: Optional[str] = None) -> Dict:
        """读取状态：指定 agent 读一个，None 读全部"""
        if agent_id:
            entry = self._entries.get(agent_id)
            return entry.to_dict() if entry else {}
        return {aid: e.to_dict() for aid, e in self._entries.items()}

    def read_artifact_summaries(self) -> List[Dict]:
        """读取所有 Agent 的产物摘要（供其他 Agent 读）"""
        return [
            {"agent_id": e.agent_id, "role": e.role, "summary": e.summary, "artifact_path": e.artifact_path}
            for e in self._entries.values()
            if e.artifact_path
        ]

    def write_artifact(self, agent_id: str, artifact_path: str, summary: str) -> None:
        """Agent 写入产物路径+摘要"""
        if agent_id in self._entries:
            self._entries[agent_id].artifact_path = artifact_path
            self._entries[agent_id].summary = summary
        else:
            self._entries[agent_id] = BlackboardEntry(
                agent_id=agent_id,
                role="",
                status=TaskStatus.COMPLETED,
                summary=summary,
                artifact_path=artifact_path,
            )
        if self.config.auto_flush:
            self._flush()

    def is_all_done(self) -> bool:
        """所有 Agent 是否都完成"""
        if not self._entries:
            return False
        return all(e.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
                    for e in self._entries.values())

    def _flush(self) -> None:
        """持久化到 blackboard.md"""
        lines = [f"# 共享黑板 - {self.session_id}", ""]

        if self._task:
            lines.append(f"## 任务\n{self._task}\n")

        if self._plan:
            lines.append("## 编组方案")
            lines.append(f"任务: {self._plan.task}")
            for a in self._plan.agents:
                lines.append(f"- {a.role} (model={a.model or 'default'}): {a.task}")
            lines.append("完成判据:")
            for c in self._plan.completion_criteria:
                lines.append(f"- [ ] {c}")
            lines.append("")

        lines.append("## Agent 执行状态")
        for entry in self._entries.values():
            lines.append(f"### {entry.role} ({entry.agent_id})")
            lines.append(f"- 状态: {entry.status.value}")
            lines.append(f"- 时间: {entry.timestamp}")
            if entry.summary:
                lines.append(f"- 摘要: {entry.summary}")
            if entry.artifact_path:
                lines.append(f"- 产物: {entry.artifact_path}")
            lines.append("")

        self.storage.write_file(
            self.session_id,
            self.config.blackboard_filename if hasattr(self.config, "blackboard_filename") else "blackboard.md",
            "\n".join(lines),
        )
