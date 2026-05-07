from crewai import Agent
from langchain_openai import ChatOpenAI
from jarvis.config.settings import Settings
from typing import Optional, Any


class BaseAgent(Agent):
    _default_llm = None

    def __init__(self, role, goal, backstory, llm: Optional[Any] = None, **kwargs):
        if llm is None:
            llm = self._get_default_llm()
        
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            verbose=Settings.DEBUG,
            **kwargs
        )

    def _get_default_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=Settings.DEFAULT_MODEL,
            temperature=Settings.DEFAULT_TEMPERATURE,
            max_tokens=Settings.DEFAULT_MAX_TOKENS,
            api_key=Settings.GLM_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )

    @classmethod
    def set_default_llm(cls, llm: Any):
        cls._default_llm = llm