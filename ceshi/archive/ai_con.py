import requests
import json
import time
import os
import logging
from typing import Tuple, Optional, Dict
from requests.exceptions import RequestException, HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


def create_session(max_retries: int = 3, pool_connections: int = 10, pool_maxsize: int = 10) -> requests.Session:
    """
    创建带连接池和重试策略的HTTP会话
    
    Args:
        max_retries: 最大重试次数
        pool_connections: 连接池大小
        pool_maxsize: 单个主机最大连接数
    
    Returns:
        requests.Session: 配置好的会话对象
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize
    )
    
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session


_session = create_session()


__version__ = "1.0.0"
__author__ = "Jarvis AI"


def call_glm45_flash(
    api_key: str,
    in_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    retry: int = 2,
    delay: float = 1,
    timeout: int = 30,
    api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    model_name: str = "glm-4.5-flash",
    session: requests.Session = None
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    调用 GLM-4.5-Flash 大语言模型 API。

    该函数用于与智谱AI的 GLM-4.5-Flash 模型进行交互，支持自动重试机制
    和指数退避策略，确保在网络不稳定或服务限流时能够可靠地获取响应。

    Args:
        api_key: 智谱AI API密钥，通过环境变量 GLM_API_KEY 获取
        in_prompt: 用户输入的提示文本，即发送给模型的问题或指令
        temperature: 温度参数，控制输出的随机性，范围 0-1，值越高越随机
        max_tokens: 生成响应的最大token数，默认1024
        retry: 重试次数，默认2次
        delay: 重试延迟基数（秒），每次重试延迟为 delay * 2^(重试次数-1)
        timeout: 请求超时时间（秒），默认30秒
        api_url: API请求URL，默认为智谱AI官方API地址
        model_name: 模型名称，默认为 glm-4.5-flash
        session: 可选的requests.Session对象，用于连接复用

    Returns:
        Tuple[str, Optional[str], Optional[str]]: 
        (原始输入, 模型响应内容, 错误信息)
        - 如果成功，错误信息为 None
        - 如果失败，响应内容为 None，错误信息包含具体错误描述

    Examples:
        >>> from config import config
        >>> input_prompt, response, error = call_glm45_flash(
        ...     api_key=config.API_KEY,
        ...     in_prompt="解释什么是人工智能",
        ...     temperature=config.DEFAULT_TEMPERATURE,
        ...     max_tokens=config.DEFAULT_MAX_TOKENS,
        ...     retry=config.RETRY,
        ...     delay=config.RETRY_DELAY,
        ...     timeout=config.TIMEOUT,
        ...     api_url=config.API_URL,
        ...     model_name=config.MODEL_NAME
        ... )
        >>> if error:
        ...     logger.error(f"调用失败: {error}")
        ... else:
        ...     logger.info(f"调用成功，响应长度: {len(response)}")

    Raises:
        KeyboardInterrupt: 如果用户中断程序（如Ctrl+C），会重新抛出

    Note:
        - 使用指数退避策略进行重试：第n次重试等待时间为 delay * 2^(n-1)
        - 支持处理HTTP 429频率超限错误，会自动重试
        - 所有异常信息会被捕获并返回，不会向上抛出（除KeyboardInterrupt外）
    """
    validation_error = _validate_inputs(
        api_key=api_key,
        in_prompt=in_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        retry=retry,
        delay=delay,
        timeout=timeout
    )
    if validation_error:
        return in_prompt, None, validation_error

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": in_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    logger.debug(f"准备调用GLM API，prompt长度: {len(in_prompt)}, 模型: {model_name}")

    current_retry = 0
    response = None
    while current_retry < retry:
        try:
            if current_retry > 0:
                sleep_time = delay * (2 ** (current_retry - 1))
                logger.info(f"第 {current_retry + 1} 次重试，等待 {sleep_time:.1f} 秒")
                time.sleep(sleep_time)

            http_session = session or _session
            response = http_session.post(api_url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()

            response_text = response.text.strip()
            if not response_text:
                raise ValueError("API返回空内容")

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"API调用成功，响应长度: {len(content)}")
                return in_prompt, content, None
            else:
                error_msg = f"API响应异常: {result}"
                logger.warning(error_msg)
                return in_prompt, None, error_msg

        except HTTPError as e:
            if response is not None and response.status_code == 429:
                error_msg = f"429频率超限（第{current_retry + 1}次重试）"
                resp_text = response.text[:100] if response.text else ""
                logger.warning(f"{error_msg}，响应：{resp_text}")
                current_retry += 1
                if current_retry >= retry:
                    final_error = f"请求失败: {error_msg}（已达最大重试次数）"
                    logger.error(final_error)
                    return in_prompt, None, final_error
            else:
                resp_text = response.text[:100] if (response and response.text) else ""
                status_code = response.status_code if response else "未知"
                reason = response.reason if response else "未知"
                error_msg = f"HTTP错误: {status_code} {reason}，响应：{resp_text}"
                logger.error(error_msg)
                return in_prompt, None, error_msg

        except RequestException as e:
            error_msg = f"网络错误（第{current_retry + 1}次重试）: {str(e)}"
            logger.warning(error_msg)
            current_retry += 1
            if current_retry >= retry:
                final_error = f"请求失败: {error_msg}（已达最大重试次数）"
                logger.error(final_error)
                return in_prompt, None, final_error

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            logger.error(error_msg)
            return in_prompt, None, error_msg

        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            error_msg = f"未知错误: {str(e)}"
            logger.error(error_msg)
            return in_prompt, None, error_msg

    final_error = f"请求失败: 已重试{retry}次仍未成功"
    logger.error(final_error)
    return in_prompt, None, final_error


def _validate_inputs(
    api_key: str,
    in_prompt: str,
    temperature: float,
    max_tokens: int,
    retry: int,
    delay: float,
    timeout: int
) -> Optional[str]:
    """
    验证输入参数的有效性

    Args:
        api_key: API密钥
        in_prompt: 输入提示
        temperature: 温度参数
        max_tokens: 最大token数
        retry: 重试次数
        delay: 重试延迟
        timeout: 超时时间

    Returns:
        Optional[str]: 如果验证失败返回错误信息，否则返回None
    """
    if not api_key or not isinstance(api_key, str) or len(api_key.strip()) == 0:
        return "API密钥不能为空"
    
    if not isinstance(in_prompt, str):
        return "输入提示必须是字符串类型"
    
    prompt_stripped = in_prompt.strip()
    if len(prompt_stripped) == 0:
        return "输入提示不能为空"
    
    if len(prompt_stripped) > 10000:
        return f"输入提示长度超过限制（最大10000字符，当前{len(prompt_stripped)}字符）"
    
    if not isinstance(temperature, (int, float)):
        return "温度参数必须是数字"
    
    if temperature < 0 or temperature > 1:
        return "温度参数必须在0-1之间"
    
    if not isinstance(max_tokens, int):
        return "最大token数必须是整数"
    
    if max_tokens <= 0 or max_tokens > 100000:
        return "最大token数必须在1-100000之间"
    
    if not isinstance(retry, int):
        return "重试次数必须是整数"
    
    if retry < 0 or retry > 10:
        return "重试次数必须在0-10之间"
    
    if not isinstance(delay, (int, float)):
        return "重试延迟必须是数字"
    
    if delay <= 0 or delay > 60:
        return "重试延迟必须在0-60秒之间"
    
    if not isinstance(timeout, int):
        return "超时时间必须是整数"
    
    if timeout <= 0 or timeout > 300:
        return "超时时间必须在1-300秒之间"
    
    return None


def setup_logging(log_level: str = "INFO", log_format: str = None):
    """
    设置日志系统配置

    Args:
        log_level: 日志级别，默认为 INFO
        log_format: 日志格式，默认为标准格式
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )


def main():
    """
    主函数：处理命令行交互
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv 未安装，将使用环境变量")

    from config import config

    setup_logging(log_level=config.LOG_LEVEL, log_format=config.LOG_FORMAT)

    config_error = config.validate()
    if config_error:
        logger.error(f"配置验证失败: {config_error}")
        raise EnvironmentError(config_error)

    logger.info("GLM-4.5-Flash API 客户端启动")

    prompt = input("请输入问题：")
    
    _, result, error = call_glm45_flash(
        api_key=config.API_KEY,
        in_prompt=prompt,
        temperature=config.DEFAULT_TEMPERATURE,
        max_tokens=config.DEFAULT_MAX_TOKENS,
        retry=config.RETRY,
        delay=config.RETRY_DELAY,
        timeout=config.TIMEOUT,
        api_url=config.API_URL,
        model_name=config.MODEL_NAME
    )
    
    if error:
        logger.error(f"调用失败: {error}")
        print(f"❌ 错误: {error}")
    else:
        logger.info(f"调用成功，响应长度: {len(result) if result else 0}")
        print(f"✅ 回复: {result}")


if __name__ == "__main__":
    main()
