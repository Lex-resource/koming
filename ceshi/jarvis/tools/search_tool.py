from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from jarvis.core.audit_logger import audit_logger, OperationType
from jarvis.core.data_store import data_store, DataCategory


class SearchTool:
    @tool("web_search")
    def web_search(query: str) -> str:
        """
        使用网络搜索获取最新信息
        
        Args:
            query: 搜索查询词
        
        Returns:
            搜索结果摘要
        """
        try:
            url = f"https://www.baidu.com/s?wd={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for item in soup.find_all('div', class_='result-op', limit=5):
                title = item.find('h3')
                desc = item.find('span', class_='c-abstract')
                if title and desc:
                    results.append(f"{title.get_text()}\n{desc.get_text()}\n")
            
            result_text = "\n".join(results) if results else "未找到相关信息"
            
            audit_logger.log_operation(
                operation_type=OperationType.TOOL_USE,
                agent_name="执行者",
                action="web_search",
                details={"query": query},
                result=result_text[:100]
            )
            
            data_store.add_record(
                category=DataCategory.SEARCH,
                source="web_search",
                content={"query": query, "results": result_text},
                tags=["搜索", "网络"]
            )
            
            return result_text
        
        except Exception as e:
            error_msg = f"搜索失败: {str(e)}"
            
            audit_logger.log_operation(
                operation_type=OperationType.TOOL_USE,
                agent_name="执行者",
                action="web_search",
                details={"query": query, "error": str(e)},
                result="失败"
            )
            
            return error_msg