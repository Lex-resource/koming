"""搜索抽象接口 - 保留 Playwright 实现"""

from abc import ABC, abstractmethod
from typing import List, Optional


class ISearch(ABC):
    """搜索 - 抽象层，实现可以是 Playwright/API/等"""

    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[dict]:
        """搜索，返回 [{title, url, snippet}]"""
        ...

    @abstractmethod
    def scrape(self, url: str, selector: str = "body") -> str:
        """抓取网页内容"""
        ...

    @abstractmethod
    def close(self) -> None:
        """释放资源（如浏览器实例）"""
        ...
