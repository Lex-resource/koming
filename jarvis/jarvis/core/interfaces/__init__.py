"""抽象接口层 - 所有实现的契约，把好关"""

from jarvis.core.interfaces.llm import ILLM
from jarvis.core.interfaces.memory import IMemory
from jarvis.core.interfaces.cache import ICache
from jarvis.core.interfaces.database import IDatabase
from jarvis.core.interfaces.device import IDevice
from jarvis.core.interfaces.search import ISearch
from jarvis.core.interfaces.storage import IStorage
from jarvis.core.interfaces.voice import ISpeech

__all__ = [
    "ILLM", "IMemory", "ICache", "IDatabase",
    "IDevice", "ISearch", "IStorage", "ISpeech",
]
