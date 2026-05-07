from langchain.tools import tool
from playwright.sync_api import sync_playwright
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory


class SearchTool:
    @tool("web_search")
    @audit_and_store(
        operation_type=OperationType.TOOL_USE,
        category=DataCategory.SEARCH,
        agent_name="执行者",
        tags=["搜索", "网络"],
        capture_args=True,
        capture_result=True
    )
    def web_search(query: str, max_results: int = 5) -> str:
        """
        使用Playwright进行网络搜索获取最新信息

        Args:
            query: 搜索查询词
            max_results: 最大返回结果数量，默认5条

        Returns:
            搜索结果摘要
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(f"https://www.baidu.com/s?wd={query}", wait_until="networkidle", timeout=30000)

                results = []
                for i in range(min(max_results, 10)):
                    try:
                        title = page.locator(f"h3.result-{i}").first.inner_text()
                        desc = page.locator(f"div.result-{i} .c-abstract").first.inner_text()
                        results.append(f"{i+1}. {title}\n{desc}\n")
                    except:
                        break

                browser.close()

                return "\n".join(results) if results else "未找到相关信息"

        except Exception as e:
            return f"搜索失败: {str(e)}"

    @tool("scrape_page")
    @audit_and_store(
        operation_type=OperationType.TOOL_USE,
        category=DataCategory.SEARCH,
        agent_name="执行者",
        tags=["网页抓取", "解析"],
        capture_args=True,
        capture_result=True
    )
    def scrape_page(url: str, selector: str = "body") -> str:
        """
        使用Playwright抓取网页内容

        Args:
            url: 网页URL
            selector: CSS选择器，默认抓取body

        Returns:
            网页内容
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(url, wait_until="networkidle", timeout=30000)

                content = page.locator(selector).first.inner_text()

                browser.close()

                return content[:2000] if len(content) > 2000 else content

        except Exception as e:
            return f"网页抓取失败: {str(e)}"
