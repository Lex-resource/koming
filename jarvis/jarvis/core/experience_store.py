"""经验存储 - memory(向量检索) + skills(提示词模板) + profiles(Agent 能力档案)"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from jarvis.core.models import AgentProfile, GroupPlan, Skill
from jarvis.core.interfaces import IDatabase, IMemory
from jarvis.config.settings import ExperienceConfig


class ExperienceStore:
    """经验存储 - 三层：向量记忆 + 提示词模板库 + Agent 能力档案"""

    def __init__(
        self,
        memory: IMemory,
        database: IDatabase,
        config: ExperienceConfig,
    ):
        self.memory = memory
        self.db = database
        self.config = config

    # ============ Memory 层：存"做过什么" ============

    def add_experience(
        self,
        task: str,
        plan: GroupPlan,
        result_summary: str,
        session_id: str,
    ) -> str:
        """任务成功后存经验，供下次检索复用"""
        content = f"任务: {task}\n结果: {result_summary}"
        metadata = {
            "task": task,
            "result_summary": result_summary,
            "session_id": session_id,
            "group_plan": plan.to_dict(),
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }
        return self.memory.add(content, metadata=metadata)

    def search_similar(self, task: str, top_k: Optional[int] = None) -> List[Dict]:
        """向量检索类似成功经验"""
        k = top_k or self.config.memory_top_k
        results = self.memory.search(task, top_k=k)
        return [r for r in results if r.get("metadata", {}).get("success", False)]

    # ============ Skills 层：存"怎么干" ============

    def get_skill_by_trigger(self, trigger_desc: str) -> Optional[Skill]:
        """按触发条件找匹配 skill（简化实现：关键词匹配，可后续换向量匹配）"""
        skills = self.db.list_skills()
        for skill in skills:
            if skill.trigger and self._trigger_match(trigger_desc, skill.trigger):
                return skill
        return None

    def add_skill(
        self,
        prompt: str,
        tools: List[str],
        trigger: str,
        artifact_format: str = "",
    ) -> str:
        """任务成功后提炼新 skill 存库"""
        skill = Skill(
            skill_id=f"skill_{uuid.uuid4().hex[:12]}",
            trigger=trigger,
            prompt_template=prompt,
            tools=tools,
            artifact_format=artifact_format,
        )
        self.db.save_skill(skill)
        return skill.skill_id

    def increment_skill_usage(self, skill_id: str) -> None:
        """skill 被复用后更新使用统计"""
        skill = self.db.get_skill(skill_id)
        if skill:
            skill.success_count += 1
            skill.last_used = datetime.now().isoformat()
            self.db.save_skill(skill)

    def list_skills(self) -> List[Skill]:
        return self.db.list_skills()

    # ============ Profile 层：存"Agent 擅长什么" ============

    def get_profile_by_role(self, role: str) -> Optional[AgentProfile]:
        """按角色找 Agent 档案"""
        return self.db.get_profile(role)

    def update_profile(
        self,
        agent_id: str,
        role: str,
        success: bool,
        duration: float,
        skills_used: Optional[List[str]] = None,
    ) -> None:
        """任务执行后更新 Agent 能力档案统计"""
        profile = self.db.get_profile(role)
        if profile is None:
            profile = AgentProfile(
                agent_id=agent_id,
                role=role,
                tools=[],
                skills=skills_used or [],
            )
        profile.execution_count += 1
        if success:
            profile.success_count += 1
        # 增量平均耗时
        prev_total = profile.avg_duration * (profile.execution_count - 1)
        profile.avg_duration = (prev_total + duration) / profile.execution_count
        profile.last_used = datetime.now().isoformat()
        if skills_used:
            for sid in skills_used:
                if sid not in profile.skills:
                    profile.skills.append(sid)
        self.db.save_profile(profile)

    def list_profiles(self) -> List[AgentProfile]:
        return self.db.list_profiles()

    # ============ 内部工具 ============

    @staticmethod
    def _trigger_match(task_desc: str, trigger: str) -> bool:
        """触发条件匹配（简化：关键词包含）"""
        task_lower = task_desc.lower()
        for kw in trigger.lower().split("/"):
            kw = kw.strip()
            if kw and kw in task_lower:
                return True
        return False
