from langchain.tools import tool
import requests


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
            return response.text.strip()
        
        except Exception as e:
            return f"获取天气失败: {str(e)}"