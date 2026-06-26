"""LLM 抽象接口 - 支持多模型选择"""

from abc import ABC, abstractmethod
from typing import Dict, List, Iterator, Optional

from jarvis.core.models import LLMResponse, ToolDefinition


class ILLM(ABC):
    """LLM 调用抽象 - 持有多模型池，按名选择"""

    @abstractmethod
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """同步对话，支持 function calling"""
        ...

    @abstractmethod
    def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs
    ) -> Iterator[str]:
        """流式对话"""
        ...

    @abstractmethod
    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """获取文本向量"""
        ...

    @abstractmethod
    def list_models(self) -> List[str]:
        """列出可用模型名"""
        ...
