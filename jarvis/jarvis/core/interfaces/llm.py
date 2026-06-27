"""LLM 抽象接口 - 支持多模型选择 + 多模态输入"""

from abc import ABC, abstractmethod
from typing import Dict, List, Iterator, Optional, Union

from jarvis.core.models import LLMResponse, ToolDefinition


class ILLM(ABC):
    """LLM 调用抽象 - 持有多模型池，按名选择，支持文本+图片+视频"""

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
    def chat_multimodal(
        self,
        model: str,
        prompt: str,
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """多模态对话 - 支持图片和视频输入

        Args:
            model: 模型名（需支持视觉/视频理解，如 GLM-4V、glm-4.5）
            prompt: 文本提示词
            images: 图片 URL 或 base64 编码字符串列表
            videos: 视频 URL 或 base64 编码字符串列表（需模型支持视频理解）
        """
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
