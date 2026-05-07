import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "JARVIS")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    GLM_API_KEY = os.getenv("GLM_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    DEFAULT_MODEL = "glm-4.5-flash"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1024

    MEMORY_CHROMA_PATH = "./data/chroma"

    @classmethod
    def validate(cls):
        if not cls.GLM_API_KEY:
            raise EnvironmentError("GLM_API_KEY 环境变量未设置")
        return True
