from jarvis.agents.base_agent import BaseAgent


class LearnerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="贾维斯学习官",
            goal="记录对话历史，学习新知识，更新知识库",
            backstory="""
你是贾维斯的学习和记忆模块，负责记录对话历史和用户偏好。
你能够从对话中学习新知识，并将其存储到知识库中供后续使用。
你帮助贾维斯不断进化和改进。
""",
            allow_delegation=False
        )