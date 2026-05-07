import os
import time
import json
fromimport os
import time
import json
from datetime import datetime
from typing import Optional


classimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        ifimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries =import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self)import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%Mimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_fileimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return osimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvisimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    defimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: strimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dictimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level:import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING,import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data:import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetimeimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level":import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "sessionimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        consoleimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\0import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}]import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_fileimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path =import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utfimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.writeimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=Falseimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入:import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, responseimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agentimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(responseimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] ifimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dictimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "systemimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_errorimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(selfimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    defimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        statsimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.sessionimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(selfimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level":import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 forimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sumimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] ==import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entriesimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        forimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_byimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_sourceimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = Noneimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "w", encoding="utf-8") as fimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def clear_logs(self):
        """清空当前会话import os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def clear_logs(self):
        """清空当前会话日志（保留文件）"""
        self.logimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def clear_logs(self):
        """清空当前会话日志（保留文件）"""
        self.log_entries = []
        self.session_id = selfimport os
import time
import json
from datetime import datetime
from typing import Optional


class GlobalLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.log_dir = "./logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.session_id = self._generate_session_id()
        self.log_entries = []
    
    def _generate_session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_log_file_path(self) -> str:
        return os.path.join(self.log_dir, f"jarvis_{self.session_id}.log")
    
    def log(self, level: str, source: str, message: str, data: Optional[dict] = None):
        """
        记录日志
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            source: 日志来源 (agent, tool, system, user)
            message: 日志消息
            data: 附加数据（可选）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "data": data if data else {},
            "session_id": self.session_id
        }
        
        self.log_entries.append(log_entry)
        
        console_color = {
            "DEBUG": "\033[94m",
            "INFO": "\033[92m",
            "WARNING": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = console_color.get(level, "\033[0m")
        print(f"{color}[{level}] [{source}] {message}\033[0m")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry: dict):
        """将日志写入文件"""
        file_path = self._get_log_file_path()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_user_input(self, input_text: str):
        """记录用户输入"""
        self.log("INFO", "user", f"用户输入: {input_text}")
    
    def log_agent_response(self, agent_name: str, response: str):
        """记录智能体响应"""
        self.log("INFO", "agent", f"{agent_name} 响应: {response[:100]}..." if len(response) > 100 else f"{agent_name} 响应: {response}")
    
    def log_tool_call(self, tool_name: str, params: dict, result: str):
        """记录工具调用"""
        self.log("INFO", "tool", f"调用工具: {tool_name}", {"params": params, "result": result[:50] if result else None})
    
    def log_system(self, message: str, data: Optional[dict] = None):
        """记录系统消息"""
        self.log("INFO", "system", message, data)
    
    def log_error(self, source: str, error: Exception):
        """记录错误"""
        self.log("ERROR", source, f"错误: {str(error)}")
    
    def log_debug(self, source: str, message: str):
        """记录调试信息"""
        self.log("DEBUG", source, message)
    
    def get_session_stats(self) -> dict:
        """获取当前会话统计信息"""
        stats = {
            "session_id": self.session_id,
            "total_entries": len(self.log_entries),
            "entries_by_level": {
                "DEBUG": sum(1 for e in self.log_entries if e["level"] == "DEBUG"),
                "INFO": sum(1 for e in self.log_entries if e["level"] == "INFO"),
                "WARNING": sum(1 for e in self.log_entries if e["level"] == "WARNING"),
                "ERROR": sum(1 for e in self.log_entries if e["level"] == "ERROR")
            },
            "entries_by_source": {}
        }
        
        for entry in self.log_entries:
            source = entry["source"]
            stats["entries_by_source"][source] = stats["entries_by_source"].get(source, 0) + 1
        
        return stats
    
    def export_logs(self, output_path: Optional[str] = None) -> str:
        """导出日志到文件"""
        if output_path is None:
            output_path = os.path.join(self.log_dir, f"export_{self.session_id}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def clear_logs(self):
        """清空当前会话日志（保留文件）"""
        self.log_entries = []
        self.session_id = self._generate_session_id()


logger = GlobalLogger