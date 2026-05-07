import os
from typing import Optional


class GLMConfig:
    """
    GLM-4.5-Flash API 配置类
    
    所有配置项均可通过环境变量进行覆盖，环境变量优先级高于默认值。
    
    配置项说明：
    - API_KEY: 智谱AI API密钥，必需通过环境变量 GLM_API_KEY 设置
    - API_URL: API请求地址
    - MODEL_NAME: 模型名称
    - DEFAULT_TEMPERATURE: 默认温度参数
    - DEFAULT_MAX_TOKENS: 默认最大token数
    - RETRY: 重试次数
    - RETRY_DELAY: 重试延迟基数（秒）
    - TIMEOUT: 请求超时时间（秒）
    - LOG_LEVEL: 日志级别
    - LOG_FORMAT: 日志格式
    """
    
    # API配置
    API_KEY: str = os.getenv("GLM_API_KEY", "")
    
    # API端点配置
    API_URL: str = os.getenv(
        "GLM_API_URL", 
        "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    )
    
    # 模型配置
    MODEL_NAME: str = os.getenv("GLM_MODEL_NAME", "glm-4.5-flash")
    
    # 请求参数默认值
    DEFAULT_TEMPERATURE: float = float(os.getenv("GLM_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("GLM_MAX_TOKENS", "1024"))
    
    # 重试配置
    RETRY: int = int(os.getenv("GLM_RETRY", "2"))
    RETRY_DELAY: float = float(os.getenv("GLM_RETRY_DELAY", "1"))
    
    # 超时配置
    TIMEOUT: int = int(os.getenv("GLM_TIMEOUT", "30"))
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("GLM_LOG_LEVEL", "INFO")
    LOG_FORMAT: Optional[str] = os.getenv("GLM_LOG_FORMAT", None)
    
    def validate(self) -> Optional[str]:
        """
        验证配置的有效性
        
        Returns:
            Optional[str]: 如果验证失败返回错误信息，否则返回None
        """
        if not self.API_KEY or len(self.API_KEY.strip()) == 0:
            return "请设置 GLM_API_KEY 环境变量"
        
        if self.DEFAULT_TEMPERATURE < 0 or self.DEFAULT_TEMPERATURE > 1:
            return "GLM_TEMPERATURE 必须在 0-1 之间"
        
        if self.DEFAULT_MAX_TOKENS <= 0 or self.DEFAULT_MAX_TOKENS > 100000:
            return "GLM_MAX_TOKENS 必须在 1-100000 之间"
        
        if self.RETRY < 0 or self.RETRY > 10:
            return "GLM_RETRY 必须在 0-10 之间"
        
        if self.RETRY_DELAY <= 0 or self.RETRY_DELAY > 60:
            return "GLM_RETRY_DELAY 必须在 0-60 秒之间"
        
        if self.TIMEOUT <= 0 or self.TIMEOUT > 300:
            return "GLM_TIMEOUT 必须在 1-300 秒之间"
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            return f"GLM_LOG_LEVEL 必须是 {', '.join(valid_log_levels)} 之一"
        
        return None


config = GLMConfig()


if __name__ == "__main__":
    print("GLM配置信息:")
    print(f"API_KEY: {'已设置' if config.API_KEY else '未设置'}")
    print(f"API_URL: {config.API_URL}")
    print(f"MODEL_NAME: {config.MODEL_NAME}")
    print(f"DEFAULT_TEMPERATURE: {config.DEFAULT_TEMPERATURE}")
    print(f"DEFAULT_MAX_TOKENS: {config.DEFAULT_MAX_TOKENS}")
    print(f"RETRY: {config.RETRY}")
    print(f"RETRY_DELAY: {config.RETRY_DELAY}")
    print(f"TIMEOUT: {config.TIMEOUT}")
    print(f"LOG_LEVEL: {config.LOG_LEVEL}")
    
    validation_error = config.validate()
    if validation_error:
        print(f"\n❌ 配置验证失败: {validation_error}")
    else:
        print("\n✅ 配置验证通过")
