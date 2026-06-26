"""Playwright 搜索实现"""

from typing import List

from jarvis.core.interfaces import ISearch
from jarvis.config.settings import SearchConfig


class PlaywrightSearch(ISearch):
    """Playwright 搜索 - 百度/Bing"""

    def __init__(self, config: SearchConfig):
        self.config = config
        self._browser = None
        self._page = None

    def _ensure_browser(self):
        if self._page is None:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=self.config.browser_headless)
            self._page = self._browser.new_page()

    def search(self, query: str, max_results: int = 5) -> List[dict]:
        self._ensure_browser()
        engine = self.config.default_engine
        if engine == "baidu":
            url = f"https://www.baidu.com/s?wd={query}"
        else:
            url = f"https://www.bing.com/search?q={query}"
        self._page.goto(url, timeout=self.config.timeout * 1000)
        results = []
        items = self._page.query_selector_all(".result, .b_algo")[:max_results]
        for item in items:
            title_el = item.query_selector("h3 a, h2 a")
            if title_el:
                results.append({
                    "title": title_el.inner_text(),
                    "url": title_el.get_attribute("href") or "",
                    "snippet": item.inner_text()[:200],
                })
        return results

    def scrape(self, url: str, selector: str = "body") -> str:
        self._ensure_browser()
        self._page.goto(url, timeout=self.config.timeout * 1000)
        el = self._page.query_selector(selector)
        return el.inner_text()[:2000] if el else ""

    def close(self) -> None:
        if self._page:
            self._page.close()
        if self._browser:
            self._browser.close()
        if hasattr(self, "_pw"):
            self._pw.stop()
        self._page = None
        self._browser = None
