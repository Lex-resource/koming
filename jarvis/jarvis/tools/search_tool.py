from langchain.tools import tool
from playwright.sync_api import sync_playwright
from jarvis.core.decorators import audit_and_store
from jarvis.core.audit_logger import OperationType
from jarvis.core.data_store import DataCategory
from jarvis.config.settings import Settings
import urllib.parse
import re
import html
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

    @staticmethod
    def _escape_html(text: str) -> str:
        """HTML转义，防止XSS攻击"""
        if not text:
            return ""
        return html.escape(text)

    @staticmethod
    def _sanitize_filename(text: str) -> str:
        """安全的文件名"""
        text = re.sub(r'[^\w\s\-]', '', text)
        return text.strip()[:50]

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
        if search_engine not in SearchTool.SEARCH_ENGINES:
            search_engine = "baidu"
        
        engine_config = SearchTool.SEARCH_ENGINES[search_engine]
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                page = browser.new_page()
                page.set_extra_http_headers({
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
                })

                url = f"{engine_config['url']}?{engine_config['query_param']}={encoded_query}"
                page.goto(url, wait_until="networkidle", timeout=30000)

                results = []
                for i in range(min(max_results, 10)):
                    try:
                        title_selector = engine_config["result_selector"].format(i=i)
                        desc_selector = engine_config["desc_selector"].format(i=i)
                        title = page.locator(title_selector).first.inner_text()
                        desc = page.locator(desc_selector).first.inner_text()
                        
                        safe_title = SearchTool._escape_html(title)
                        safe_desc = SearchTool._escape_html(desc)
                        
                        results.append(f"{i+1}. {safe_title}\n{safe_desc}\n")
                    except Exception as e:
                        continue

                browser.close()

                if results:
                    return "\n".join(results)
                else:
                    return "未找到相关信息"

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
        allowed_domains = [d.strip() for d in allowed_domains if d.strip()]
        
        if allowed_domains:
            domain = parsed_url.netloc
            if not any(domain.endswith(allowed_domain.strip()) for allowed_domain in allowed_domains):
                return f"不允许访问该域名，允许的域名: {', '.join(allowed_domains)}"
        
        safe_selector = re.sub(r'[^a-zA-Z0-9\s\-_:#.\[\]=>]', '', selector)
        if len(safe_selector) > 100:
            safe_selector = "body"
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                page = browser.new_page()

                page.goto(url, wait_until="networkidle", timeout=30000)

                content = page.locator(safe_selector).first.inner_text()

                browser.close()

                return content[:2000] if len(content) > 2000 else content

        except Exception as e:
            return f"网页抓取失败: {str(e)}"
