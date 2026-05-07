from jarvis.agents.base_agent import BaseAgent
from jarvis.tools.search_tool import SearchTool
from jarvis.tools.weather_tool import WeatherTool
from jarvis.tools.device_tool import DeviceTool


class ExecutorAgent(BaseAgent):
    def __init__(self):
        tools = [
            SearchTool(),
            WeatherTool(),
            DeviceTool()
        ]

        super().__init__(
            role="贾维斯执行者",
            goal="执行具体任务，调用工具完成操作",
            backstory="""
你是贾维斯的执行模块，擅长调用各种工具完成实际操作。
你可以进行网络搜索、查询天气、控制智能设备等操作。
你是实现贾维斯物理交互能力的关键模块。
""",
            tools=tools,
            allow_delegation=False
        )
