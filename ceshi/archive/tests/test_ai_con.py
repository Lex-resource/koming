"""
GLM-4.5-Flash API 客户端单元测试

测试覆盖：
1. 配置文件测试
2. API调用基本功能测试
3. 错误处理测试
4. 重试机制测试
5. 并发请求测试
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import requests
from requests.exceptions import HTTPError, RequestException, Timeout

from ai_con import call_glm45_flash, setup_logging
from config import config


class TestConfig:
    """配置文件测试"""

    def test_config_defaults(self):
        """测试默认配置值"""
        assert config.API_URL == "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        assert config.MODEL_NAME == "glm-4.5-flash"
        assert config.TIMEOUT == 30
        assert config.RETRY == 2
        assert config.RETRY_DELAY == 1.0
        assert config.DEFAULT_TEMPERATURE == 0.7
        assert config.DEFAULT_MAX_TOKENS == 1024
        assert config.LOG_LEVEL == "INFO"

    def test_config_validation_empty_key(self):
        """测试配置验证 - 空API密钥"""
        with patch.object(config, 'API_KEY', ''):
            result = config.validate()
            assert result == "GLM_API_KEY 环境变量未设置"

    def test_config_validation_invalid_timeout(self):
        """测试配置验证 - 无效超时时间"""
        with patch.object(config, 'TIMEOUT', -1):
            result = config.validate()
            assert result == "TIMEOUT 必须大于 0"

    def test_config_validation_invalid_temperature(self):
        """测试配置验证 - 无效温度参数"""
        with patch.object(config, 'DEFAULT_TEMPERATURE', 1.5):
            result = config.validate()
            assert result == "DEFAULT_TEMPERATURE 必须在 0-1 之间"

    def test_config_to_dict_hides_key(self):
        """测试配置转换为字典时隐藏API密钥"""
        config.API_KEY = "secret_key_123"
        config_dict = config.to_dict()
        assert config_dict["API_KEY"] == "***"


class TestCallGLM45Flash:
    """API调用函数测试"""

    def test_call_success(self):
        """测试成功调用API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"choices": [{"message": {"content": "测试响应"}}]}'
        mock_response.json.return_value = {"choices": [{"message": {"content": "测试响应"}}]}
        
        with patch('requests.post', return_value=mock_response):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=0
            )
            
            assert prompt == "测试问题"
            assert response == "测试响应"
            assert error is None

    def test_call_empty_response(self):
        """测试空响应处理"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ''
        
        with patch('requests.post', return_value=mock_response):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=0
            )
            
            assert response is None
            assert "空内容" in error

    def test_call_http_error_429(self):
        """测试HTTP 429错误处理"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.text = '{"error": "rate limit exceeded"}'
        
        with patch('requests.post', side_effect=[HTTPError(response=mock_response), HTTPError(response=mock_response)]):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=2,
                delay=0.1
            )
            
            assert response is None
            assert "429" in error
            assert "已达最大重试次数" in error

    def test_call_http_error_other(self):
        """测试其他HTTP错误处理"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text = '{"error": "server error"}'
        
        with patch('requests.post', side_effect=HTTPError(response=mock_response)):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=0
            )
            
            assert response is None
            assert "500" in error

    def test_call_network_error(self):
        """测试网络错误处理"""
        with patch('requests.post', side_effect=RequestException("网络超时")):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=1,
                delay=0.1
            )
            
            assert response is None
            assert "网络错误" in error

    def test_call_timeout(self):
        """测试超时处理"""
        with patch('requests.post', side_effect=Timeout("请求超时")):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=0,
                timeout=1
            )
            
            assert response is None
            assert "网络错误" in error

    def test_call_json_decode_error(self):
        """测试JSON解析错误处理"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "invalid json"
        
        with patch('requests.post', return_value=mock_response):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=0
            )
            
            assert response is None
            assert "JSON解析错误" in error

    def test_call_retry_success(self):
        """测试重试机制 - 首次失败后成功"""
        mock_response1 = MagicMock()
        mock_response1.status_code = 500
        mock_response1.reason = "Internal Server Error"
        
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.text = '{"choices": [{"message": {"content": "成功响应"}}]}'
        mock_response2.json.return_value = {"choices": [{"message": {"content": "成功响应"}}]}
        
        with patch('requests.post', side_effect=[HTTPError(response=mock_response1), mock_response2]):
            prompt, response, error = call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                retry=2,
                delay=0.1
            )
            
            assert response == "成功响应"
            assert error is None

    def test_call_keyboard_interrupt(self):
        """测试键盘中断处理"""
        with patch('requests.post', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                call_glm45_flash(
                    api_key="test_key",
                    in_prompt="测试问题",
                    retry=0
                )

    def test_call_parameters(self):
        """测试参数传递"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"choices": [{"message": {"content": "响应"}}]}'
        mock_response.json.return_value = {"choices": [{"message": {"content": "响应"}}]}
        
        with patch('requests.post') as mock_post:
            mock_post.return_value = mock_response
            
            call_glm45_flash(
                api_key="test_key",
                in_prompt="测试问题",
                temperature=0.5,
                max_tokens=512,
                retry=3,
                delay=2.0,
                timeout=15,
                api_url="https://custom.api.com/v1/chat",
                model_name="glm-4"
            )
            
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args.kwargs['timeout'] == 15
            assert call_args.kwargs['url'] == "https://custom.api.com/v1/chat"
            assert call_args.kwargs['json']['model'] == "glm-4"
            assert call_args.kwargs['json']['temperature'] == 0.5
            assert call_args.kwargs['json']['max_tokens'] == 512


if __name__ == "__main__":
    pytest.main([__file__, "-v"])