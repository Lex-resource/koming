from langchain.tools import tool
import requests
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory


class WeatherTool:
    @tool("get_weather")
    @audit_and_store(
        operation_type=OperationType.DATA_QUERY,
        category=DataCategory.WEATHER,
        agent_name="执行者",
        tags=["天气", "查询"],
        capture_args=True,
        capture_result=True
    )
    def get_weather(city: str) -> str:
        """
        获取指定城市的天气信息
        
        Args:
            city: 城市名称（如：北京、上海、广州）
        
        Returns:
            天气信息
        """
        try:
            url = f"http://wttr.in/{city}?format=3"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text.strip()
            
        except Exception as e:
            return f"获取天气失败: {str(e)}"
