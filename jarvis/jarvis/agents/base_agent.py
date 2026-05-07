from crewai import Agent
from langchain_openai import ChatOpenAI
from jarvis.config.settings import Settings


class BaseAgent(Agent):
    def __init__(self, role, goal, backstory, **kwargs):
        llm = ChatOpenAI(
            model=Settings.DEFAULT_MODEL,
            temperature=Settings.DEFAULT_TEMPERATURE,
            max_tokens=Settings.DEFAULT_MAX_TOKENS,
            api_key=Settings.GLM_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=Settings.DEBUG,
            **kwargs
        )