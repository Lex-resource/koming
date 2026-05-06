from langchain.tools import tool
import requests
from bs4 import BeautifulSoup


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
            
            return "\n".join(results) if results else "未找到相关信息"
        
        except Exception as e:
            return f"搜索失败: {str(e)}"