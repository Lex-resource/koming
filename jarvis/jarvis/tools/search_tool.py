from langchain.tools import tool
from playwright.sync_api import sync_playwright
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory
from jarvis.config.settings import Settings
import urllib.parse
import re
import os


class SearchTool:
    SEARCH_ENGINES = {
        "baidu": {
            "url": "https://www.baidu.com/s",
            "query_param": "wd",
            "result_selector": "h3.result-{i}",
            "desc_selector": "div.result-{i} .c-abstract"
        },
        "bing": {
            "url": "https://www.bing.com/search",
            "query_param": "q",
            "result_selector": "#b_results li.b_algo h2",
            "desc_selector": "#b_results li.b_algo p"
        }
    }

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
        if not query or len(query.strip()) == 0:
            return "搜索查询词不能为空"
        
        if len(query) > 500:
            return "搜索查询词长度不能超过500个字符"
        
        if re.search(r'[<>"\']', query):
            return "搜索查询词包含非法字符"
        
        encoded_query = urllib.parse.quote(query, safe='')
        
        search_engine = os.getenv("SEARCH_ENGINE", "baidu").lower()
        engine_config = SearchTool.SEARCH_ENGINES.get(search_engine, SearchTool.SEARCH_ENGINES["baidu"])
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                url = f"{engine_config['url']}?{engine_config['query_param']}={encoded_query}"
                page.goto(url, wait_until="networkidle", timeout=30000)

                results = []
                for i in range(min(max_results, 10)):
                    try:
                        title_selector = engine_config["result_selector"].format(i=i)
                        desc_selector = engine_config["desc_selector"].format(i=i)
                        title = page.locator(title_selector).first.inner_text()
                        desc = page.locator(desc_selector).first.inner_text()
                        results.append(f"{i+1}. {title}\n{desc}\n")
                    except Exception:
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
        if not url or len(url.strip()) == 0:
            return "URL不能为空"
        
        if len(url) > 2048:
            return "URL长度不能超过2048个字符"
        
        url_pattern = r'^https?://[a-zA-Z0-9][-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]$'
        if not re.match(url_pattern, url):
            return "无效的URL格式"
        
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme not in ('http', 'https'):
            return "只支持http和https协议"
        
        allowed_domains = os.getenv("ALLOWED_SCRAPE_DOMAINS", "").split(",")
        if allowed_domains and allowed_domains[0]:
            domain = parsed_url.netloc
            if not any(domain.endswith(allowed_domain.strip()) for allowed_domain in allowed_domains):
                return f"不允许访问该域名，允许的域名: {', '.join(allowed_domains)}"
        
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
