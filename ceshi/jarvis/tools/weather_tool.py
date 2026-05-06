from langchain.tools import tool
import requests
from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.data_store import data_store, DataCategory


class WeatherTool:
    @tool("get_weather")
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
            result_text = response.text.strip()
            
            audit_logger.log_operation(
                operation_type=OperationType.DATA_QUERY,
                agent_name="执行者",
                action="get_weather",
                details={"city": city},
                result=result_text
            )
            
            data_store.add_record(
                category=DataCategory.WEATHER,
                source="get_weather",
                content={"city": city, "weather": result_text},
                tags=["天气", city]
            )
            
            return result_text
        
        except Exception as e:
            error_msg = f"获取天气失败: {str(e)}"
            
            audit_logger.log_operation(
                operation_type=OperationType.DATA_QUERY,
                agent_name="执行者",
                action="get_weather",
                details={"city": city, "error": str(e)},
                result="失败"
            )
            
            return error_msg