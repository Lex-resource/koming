"""LLM 多厂商适配实现 - 按 provider 字段路由"""

import json
from typing import Dict, Iterator, List, Optional

from jarvis.config.settings import LLMConfig, ModelConfig
from jarvis.core.interfaces import ILLM
from jarvis.core.models import LLMResponse, ToolCall, ToolDefinition


class MultiProviderLLM(ILLM):
    """多厂商 LLM - 按 ModelConfig.provider 路由到不同适配器"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._adapters: Dict[str, "ILLMAdapter"] = {
            "openai_compatible": OpenAICompatibleAdapter(),
        }
        # 其他厂商适配器按需注册

    def register_adapter(self, provider: str, adapter: "ILLMAdapter") -> None:
        """注册新的厂商适配器"""
        self._adapters[provider] = adapter

    def _get_adapter(self, provider: str) -> "ILLMAdapter":
        adapter = self._adapters.get(provider)
        if not adapter:
            raise ValueError(
                f"厂商 '{provider}' 未注册适配器，可用: {list(self._adapters.keys())}。"
                f"通过 register_adapter() 注册自定义适配器。"
            )
        return adapter

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        cfg = self.config.get_model(model)
        adapter = self._get_adapter(cfg.provider)
        return adapter.chat(cfg, messages, tools, temperature, max_tokens, **kwargs)

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
        cfg = self.config.get_model(model)
        adapter = self._get_adapter(cfg.provider)
        return adapter.chat_multimodal(cfg, prompt, images, videos, temperature, max_tokens, **kwargs)

    def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs
    ) -> Iterator[str]:
        cfg = self.config.get_model(model)
        adapter = self._get_adapter(cfg.provider)
        yield from adapter.chat_stream(cfg, messages, tools, **kwargs)

    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        # 用 OpenAI 兼容接口
        adapter = self._adapters.get("openai_compatible")
        if not adapter:
            raise ValueError("embedding 需要 openai_compatible 适配器")
        return adapter.get_embedding(
            text=text,
            api_key=self.config.embedding_api_key,
            base_url=self.config.embedding_base_url,
            model=model or self.config.embedding_model,
        )

    def list_models(self) -> List[str]:
        return self.config.list_models()


class ILLMAdapter:
    """厂商适配器抽象 - 新厂商实现这个接口即可接入"""

    def chat(
        self,
        cfg: ModelConfig,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        raise NotImplementedError

    def chat_multimodal(
        self,
        cfg: ModelConfig,
        prompt: str,
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """多模态对话 - 厂商可按自有格式实现图片/视频输入"""
        raise NotImplementedError

    def chat_stream(
        self, cfg, messages, tools, **kwargs
    ) -> Iterator[str]:
        raise NotImplementedError

    def get_embedding(self, text: str, api_key: str, base_url: str, model: str) -> List[float]:
        raise NotImplementedError


class OpenAICompatibleAdapter(ILLMAdapter):
    """OpenAI 兼容接口适配器 - 支持 GLM/Qwen/DeepSeek 等所有兼容厂商"""

    def _client(self, cfg: ModelConfig):
        from openai import OpenAI
        return OpenAI(
            api_key=cfg.api_key or "dummy",
            base_url=cfg.base_url,
            timeout=cfg.timeout,
            default_headers=cfg.extra_headers or None,
        )

    def chat(
        self,
        cfg: ModelConfig,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        client = self._client(cfg)
        # 处理 messages 中含 tool_calls/tool 角色的消息
        clean_messages = self._clean_messages(messages)

        params = {
            "model": cfg.model,
            "messages": clean_messages,
            "temperature": temperature if temperature is not None else cfg.temperature,
            "max_tokens": max_tokens or cfg.max_tokens,
            **cfg.extra_params,
            **kwargs,
        }
        if tools:
            params["tools"] = [t.to_openai_schema() for t in tools]

        resp = client.chat.completions.create(**params)
        choice = resp.choices[0]
        content = choice.message.content or ""
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))
        usage = {}
        if resp.usage:
            usage = {"prompt_tokens": resp.usage.prompt_tokens,
                     "completion_tokens": resp.usage.completion_tokens,
                     "total_tokens": resp.usage.total_tokens}
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage=usage,
        )

    def chat_multimodal(
        self,
        cfg: ModelConfig,
        prompt: str,
        images: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """多模态对话 - OpenAI image_url 格式 + GLM video_url 扩展

        图片：走标准 OpenAI 格式 {"type": "image_url", "image_url": {"url": ...}}
        视频：走智谱 GLM-4V 扩展格式 {"type": "video_url", "video_url": {"url": ...}}
              其他厂商若不支持视频，可忽略 videos 参数（自动降级为纯文本+图片）

        Args:
            images: 图片列表，元素为 URL 或 base64 字符串（自动加 data:image 前缀）
            videos: 视频列表，元素为 URL 或 base64 字符串
        """
        client = self._client(cfg)
        content_parts: List[Dict] = [{"type": "text", "text": prompt}]

        for img in (images or []):
            url = self._normalize_media_url(img, is_image=True)
            content_parts.append({"type": "image_url", "image_url": {"url": url}})

        for vid in (videos or []):
            url = self._normalize_media_url(vid, is_image=False)
            content_parts.append({"type": "video_url", "video_url": {"url": url}})

        messages = [{"role": "user", "content": content_parts}]
        params = {
            "model": cfg.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else cfg.temperature,
            "max_tokens": max_tokens or cfg.max_tokens,
            **cfg.extra_params,
            **kwargs,
        }
        resp = client.chat.completions.create(**params)
        choice = resp.choices[0]
        content = choice.message.content or ""
        usage = {}
        if resp.usage:
            usage = {"prompt_tokens": resp.usage.prompt_tokens,
                     "completion_tokens": resp.usage.completion_tokens,
                     "total_tokens": resp.usage.total_tokens}
        return LLMResponse(content=content, finish_reason=choice.finish_reason, usage=usage)

    @staticmethod
    def _normalize_media_url(source: str, is_image: bool) -> str:
        """URL 原样返回；base64 自动补 data URI 前缀"""
        if source.startswith(("http://", "https://", "data:")):
            return source
        # base64 裸串 → 补 data URI 前缀
        if is_image:
            return f"data:image/jpeg;base64,{source}"
        return f"data:video/mp4;base64,{source}"

    def chat_stream(self, cfg, messages, tools=None, **kwargs) -> Iterator[str]:
        client = self._client(cfg)
        clean_messages = self._clean_messages(messages)
        params = {"model": cfg.model, "messages": clean_messages, "stream": True, **kwargs}
        if tools:
            params["tools"] = [t.to_openai_schema() for t in tools]
        stream = client.chat.completions.create(**params)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_embedding(self, text: str, api_key: str, base_url: str, model: str) -> List[float]:
        from openai import OpenAI
        client = OpenAI(api_key=api_key or "dummy", base_url=base_url)
        resp = client.embeddings.create(model=model, input=text)
        return resp.data[0].embedding

    @staticmethod
    def _clean_messages(messages: List[Dict]) -> List[Dict]:
        """清理消息，保留 OpenAI 格式兼容字段"""
        cleaned = []
        for m in messages:
            entry = {"role": m["role"]}
            if "content" in m and m["content"] is not None:
                entry["content"] = m["content"]
            if m.get("tool_calls"):
                entry["tool_calls"] = m["tool_calls"]
            if m.get("tool_call_id"):
                entry["tool_call_id"] = m["tool_call_id"]
            if m.get("name"):
                entry["name"] = m["name"]
            cleaned.append(entry)
        return cleaned


# 示例：如何添加新厂商适配器
#
# class AnthropicAdapter(ILLMAdapter):
#     def chat(self, cfg, messages, tools, ...):
#         from anthropic import Anthropic
#         client = Anthropic(api_key=cfg.api_key)
#         # 转换 messages 格式、调用、返回 LLMResponse
#         ...
#
# 在 app.py 注册：
# llm.register_adapter("anthropic", AnthropicAdapter())
