"""语音默认实现 - 走智谱 GLM 兼容接口（CogVoice / Whisper ASR）

- ASR：调用智谱 audio.transcriptions 接口（OpenAI Whisper 兼容）
- TTS：调用智谱 audio.speech 接口（CogVoice 兼容）
- 其他厂商若需接入，实现 ISpeech 即可
"""

import os
import tempfile
from typing import List, Optional

from jarvis.core.interfaces import ISpeech


class GLMSpeechProvider(ISpeech):
    """智谱 GLM 语音实现 - OpenAI Whisper + CogVoice 兼容接口"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
        asr_model: str = "whisper-1",
        tts_model: str = "cogtts",
        default_voice: str = "female-tianmei",
        available_voices: Optional[List[str]] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.asr_model = asr_model
        self.tts_model = tts_model
        self.default_voice = default_voice
        self.available_voices = available_voices or [
            "female-tianmei", "female-yongjie", "female-chengshu",
            "male-qn-qingshu", "male-qn-jingying",
        ]

    def _client(self):
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key or "dummy",
            base_url=self.base_url,
        )

    def asr(
        self,
        audio_path: str,
        language: str = "zh",
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """语音识别 - 音频文件转文字"""
        if not os.path.exists(audio_path) and not audio_path.startswith(("http://", "https://")):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        client = self._client()
        # 本地文件直接打开；URL 走 OpenAI SDK 自动处理
        if audio_path.startswith(("http://", "https://")):
            resp = client.audio.transcriptions.create(
                model=model or self.asr_model,
                url=audio_path,
                language=language,
            )
        else:
            with open(audio_path, "rb") as f:
                resp = client.audio.transcriptions.create(
                    model=model or self.asr_model,
                    file=f,
                    language=language,
                )
        return getattr(resp, "text", "") or ""

    def tts(
        self,
        text: str,
        voice: str = "default",
        model: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """语音合成 - 文字转音频文件"""
        if not text:
            raise ValueError("TTS 文本不能为空")
        chosen_voice = voice if voice != "default" else self.default_voice

        client = self._client()
        resp = client.audio.speech.create(
            model=model or self.tts_model,
            voice=chosen_voice,
            input=text,
            **kwargs,
        )
        # 写入到指定文件或临时文件
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".mp3", prefix="jarvis_tts_")
            os.close(fd)
        resp.write_to_file(output_path)
        return output_path

    def list_voices(self) -> List[str]:
        return list(self.available_voices)

    def close(self) -> None:
        pass


class MockSpeechProvider(ISpeech):
    """语音模拟实现 - 无网络环境验证链路用"""

    def list_voices(self) -> List[str]:
        return ["mock-female", "mock-male"]

    def asr(
        self,
        audio_path: str,
        language: str = "zh",
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        return f"[模拟识别] 音频 {audio_path} 的内容（语言 {language}）"

    def tts(
        self,
        text: str,
        voice: str = "default",
        model: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".mp3", prefix="jarvis_mock_tts_")
            os.close(fd)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"[模拟合成] voice={voice} text={text}")
        return output_path

    def close(self) -> None:
        pass
