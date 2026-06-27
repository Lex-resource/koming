"""语音抽象接口 - ASR 语音转文字 + TTS 文字转语音"""

from abc import ABC, abstractmethod
from typing import List, Optional


class ISpeech(ABC):
    """语音能力抽象 - 输入音频文件，输出文本；输入文本，输出音频文件"""

    @abstractmethod
    def asr(
        self,
        audio_path: str,
        language: str = "zh",
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """语音识别 - 音频转文字

        Args:
            audio_path: 音频文件路径（本地路径或 URL）
            language: 语言代码（zh/en/ja...）
            model: 指定 ASR 模型，None 用默认
        Returns:
            识别出的文本
        """
        ...

    @abstractmethod
    def tts(
        self,
        text: str,
        voice: str = "default",
        model: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """语音合成 - 文字转音频

        Args:
            text: 要合成的文本
            voice: 音色 ID（如 male/female/child）
            model: 指定 TTS 模型，None 用默认
            output_path: 输出文件路径，None 则自动生成临时文件
        Returns:
            生成的音频文件路径
        """
        ...

    @abstractmethod
    def list_voices(self) -> List[str]:
        """列出可用音色"""
        ...

    @abstractmethod
    def close(self) -> None:
        """释放资源"""
        ...
