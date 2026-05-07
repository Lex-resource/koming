import requests
import json
import time
import os
import logging
from typing import Tuple, Optional
from requests.exceptions import RequestException, HTTPError


logger = logging.getLogger(__name__)


def call_glm45_flash(
    api_key: str,
    in_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    retry: int = 2,
    delay: float = 1,
    timeout: int = 30,
    api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    model_name: str = "glm-4.5-flash"
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
    while current_retry < retry:
        try:
            if current_retry > 0:
                sleep_time = delay * (2 ** (current_retry - 1))
                logger.info(f"第 {current_retry + 1} 次重试，等待 {sleep_time:.1f} 秒")
                time.sleep(sleep_time)

            response = requests.post(api_url, headers=headers, json=data, timeout=timeout)
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
            if response.status_code == 429:
                error_msg = f"429频率超限（第{current_retry + 1}次重试）"
                resp_text = response.text[:100] if response.text else ""
                logger.warning(f"{error_msg}，响应：{resp_text}")
                current_retry += 1
                if current_retry >= retry:
                    final_error = f"请求失败: {error_msg}（已达最大重试次数）"
                    logger.error(final_error)
                    return in_prompt, None, final_error
            else:
                resp_text = response.text[:100] if response.text else ""
                error_msg = f"HTTP错误: {response.status_code} {response.reason}，响应：{resp_text}"
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
        print(f"❌ 错误: {error}")
    else:
        print(f"✅ 回复: {result}")


if __name__ == "__main__":
    main()
