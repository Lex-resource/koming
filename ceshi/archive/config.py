"""
GLM-4.5-Flash API 配置文件

该文件包含所有可配置的参数，通过环境变量或默认值提供。
配置优先级：环境变量 > 默认值
"""

import os
from typing import Optional


class GLMConfig:
    """GLM-4.5-Flash API 配置类"""

    # API 基础配置
    API_KEY: str = os.getenv("GLM_API_KEY", "")
    API_URL: str = os.getenv("GLM_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
    MODEL_NAME: str = os.getenv("GLM_MODEL_NAME", "glm-4.5-flash")

    # 请求配置
    TIMEOUT: int = int(os.getenv("GLM_TIMEOUT", "30"))
    RETRY: int = int(os.getenv("GLM_RETRY", "2"))
    RETRY_DELAY: float = float(os.getenv("GLM_RETRY_DELAY", "1.0"))

    # 模型参数默认值
    DEFAULT_TEMPERATURE: float = float(os.getenv("GLM_DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("GLM_DEFAULT_MAX_TOKENS", "1024"))
    DEFAULT_STREAM: bool = bool(os.getenv("GLM_DEFAULT_STREAM", "false").lower() == "true")

    # 日志配置
    LOG_LEVEL: str = os.getenv("GLM_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "GLM_LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    @classmethod
    def validate(cls) -> Optional[str]:
        """
        验证配置是否完整

        Returns:
            Optional[str]: 如果配置无效，返回错误信息；否则返回 None
        """
        if not cls.API_KEY:
            return "GLM_API_KEY 环境变量未设置"
        if not cls.API_URL:
            return "GLM_API_URL 环境变量未设置"
        if not cls.MODEL_NAME:
            return "GLM_MODEL_NAME 环境变量未设置"
        
        if cls.TIMEOUT <= 0:
            return "TIMEOUT 必须大于 0"
        if cls.RETRY < 0:
            return "RETRY 不能为负数"
        if cls.RETRY_DELAY <= 0:
            return "RETRY_DELAY 必须大于 0"
        if not (0 <= cls.DEFAULT_TEMPERATURE <= 1):
            return "DEFAULT_TEMPERATURE 必须在 0-1 之间"
        if cls.DEFAULT_MAX_TOKENS <= 0:
            return "DEFAULT_MAX_TOKENS 必须大于 0"
        
        return None

    @classmethod
    def to_dict(cls) -> dict:
        """
        将配置转换为字典

        Returns:
            dict: 配置字典
        """
        return {
            "API_KEY": "***" if cls.API_KEY else None,
            "API_URL": cls.API_URL,
            "MODEL_NAME": cls.MODEL_NAME,
            "TIMEOUT": cls.TIMEOUT,
            "RETRY": cls.RETRY,
            "RETRY_DELAY": cls.RETRY_DELAY,
            "DEFAULT_TEMPERATURE": cls.DEFAULT_TEMPERATURE,
            "DEFAULT_MAX_TOKENS": cls.DEFAULT_MAX_TOKENS,
            "DEFAULT_STREAM": cls.DEFAULT_STREAM,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "LOG_FORMAT": cls.LOG_FORMAT
        }

    @classmethod
    def print_config(cls):
        """打印当前配置（不包含敏感信息）"""
        config_dict = cls.to_dict()
        print("=" * 60)
        print("GLM-4.5-Flash API 配置")
        print("=" * 60)
        for key, value in config_dict.items():
            print(f"{key:20} : {value}")
        print("=" * 60)


config = GLMConfig()
