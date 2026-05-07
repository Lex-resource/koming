"""搜索工具测试"""
import pytest
from jarvis.tools.search_tool import SearchTool


class TestSearchTool:
    """搜索工具测试类"""

    def test_web_search_empty_query(self):
        """测试空查询词"""
        result = SearchTool.web_search("")
        assert "不能为空" in result

    def test_web_search_long_query(self):
        """测试超长查询词"""
        long_query = "a" * 600
        result = SearchTool.web_search(long_query)
        assert "超过500个字符" in result

    def test_web_search_invalid_chars(self):
        """测试非法字符"""
        result = SearchTool.web_search('test"<script>')
        assert "非法字符" in result

    def test_scrape_page_empty_url(self):
        """测试空URL"""
        result = SearchTool.scrape_page("")
        assert "不能为空" in result

    def test_scrape_page_invalid_url(self):
        """测试无效URL格式"""
        result = SearchTool.scrape_page("invalid-url")
        assert "无效的URL格式" in result

    def test_scrape_page_invalid_scheme(self):
        """测试无效协议"""
        result = SearchTool.scrape_page("ftp://example.com")
        assert "只支持http和https协议" in result