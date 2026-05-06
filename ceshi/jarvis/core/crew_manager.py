from crewai import Crew, Task
from jarvis.agents.commander import CommanderAgent
from jarvis.agents.analyst import AnalystAgent
from jarvis.agents.executor import ExecutorAgent
from jarvis.agents.learner import LearnerAgent


class CrewManager:
    def __init__(self):
        self.commander = CommanderAgent()
        self.analyst = AnalystAgent()
        self.executor = ExecutorAgent()
        self.learner = LearnerAgent()

    def create_task(self, user_input: str) -> Task:
        return Task(
            description=f"""
用户请求：{user_input}

请根据用户的请求，分析需求并执行相应的操作。
如果需要调用工具，请使用executor agent执行。
如果需要分析问题，请使用analyst agent分析。
如果需要学习新知识，请使用learner agent记录。

请以自然、友好的语言回复用户。
""",
            agent=self.commander,
            expected_output="详细的任务执行结果和回复"
        )

    def execute_task(self, user_input: str) -> str:
        task = self.create_task(user_input)
        
        crew = Crew(
            agents=[self.commander, self.analyst, self.executor, self.learner],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)