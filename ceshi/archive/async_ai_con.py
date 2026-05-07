"""
GLM-4.5-Flash API 异步客户端

支持并发请求的异步版本，使用 aiohttp 实现。
"""

import asyncio
import aiohttp
import json
import logging
from typing import Tuple, Optional, List, Any
from aiohttp import ClientError, ClientResponseError

logger = logging.getLogger(__name__)


async def async_call_glm45_flash(
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
    异步调用 GLM-4.5-Flash 大语言模型 API。

    该函数使用 aiohttp 实现异步请求，支持并发调用，适合需要同时处理多个请求的场景。

    Args:
        api_key: 智谱AI API密钥
        in_prompt: 用户输入的提示文本
        temperature: 温度参数，控制输出的随机性
        max_tokens: 生成响应的最大token数
        retry: 重试次数
        delay: 重试延迟基数（秒）
        timeout: 请求超时时间（秒）
        api_url: API请求URL
        model_name: 模型名称

    Returns:
        Tuple[str, Optional[str], Optional[str]]: 
        (原始输入, 模型响应内容, 错误信息)
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

    logger.debug(f"异步调用GLM API，prompt长度: {len(in_prompt)}, 模型: {model_name}")

    current_retry = 0
    while current_retry < retry:
        try:
            if current_retry > 0:
                sleep_time = delay * (2 ** (current_retry - 1))
                logger.info(f"第 {current_retry + 1} 次重试，等待 {sleep_time:.1f} 秒")
                await asyncio.sleep(sleep_time)

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(api_url, headers=headers, json=data) as response:
                    if response.status == 429:
                        error_msg = f"429频率超限（第{current_retry + 1}次重试）"
                        resp_text = await response.text()
                        resp_text = resp_text[:100] if resp_text else ""
                        logger.warning(f"{error_msg}，响应：{resp_text}")
                        current_retry += 1
                        if current_retry >= retry:
                            final_error = f"请求失败: {error_msg}（已达最大重试次数）"
                            logger.error(final_error)
                            return in_prompt, None, final_error
                        continue

                    response.raise_for_status()

                    response_text = await response.text()
                    response_text = response_text.strip()
                    if not response_text:
                        raise ValueError("API返回空内容")

                    result = json.loads(response_text)
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        logger.debug(f"异步API调用成功，响应长度: {len(content)}")
                        return in_prompt, content, None
                    else:
                        error_msg = f"API响应异常: {result}"
                        logger.warning(error_msg)
                        return in_prompt, None, error_msg

        except ClientResponseError as e:
            error_msg = f"HTTP错误: {e.status} {e.message}"
            logger.error(error_msg)
            return in_prompt, None, error_msg

        except ClientError as e:
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


async def async_call_batch(
    api_key: str,
    prompts: List[str],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    retry: int = 2,
    delay: float = 1,
    timeout: int = 30,
    api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    model_name: str = "glm-4.5-flash",
    max_concurrent: int = 5
) -> List[Tuple[str, Optional[str], Optional[str]]]:
    """
    批量异步调用GLM API

    Args:
        api_key: 智谱AI API密钥
        prompts: 提示文本列表
        temperature: 温度参数
        max_tokens: 最大token数
        retry: 重试次数
        delay: 重试延迟
        timeout: 超时时间
        api_url: API地址
        model_name: 模型名称
        max_concurrent: 最大并发数

    Returns:
        List[Tuple[str, Optional[str], Optional[str]]]: 批量调用结果
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_call(prompt: str) -> Tuple[str, Optional[str], Optional[str]]:
        async with semaphore:
            return await async_call_glm45_flash(
                api_key=api_key,
                in_prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                retry=retry,
                delay=delay,
                timeout=timeout,
                api_url=api_url,
                model_name=model_name
            )

    tasks = [limited_call(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    
    return results


def call_concurrent(
    api_key: str,
    prompts: List[str],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    retry: int = 2,
    delay: float = 1,
    timeout: int = 30,
    api_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    model_name: str = "glm-4.5-flash",
    max_concurrent: int = 5
) -> List[Tuple[str, Optional[str], Optional[str]]]:
    """
    并发调用GLM API（同步入口）

    该函数提供同步接口，内部使用异步方式实现并发调用。

    Args:
        api_key: 智谱AI API密钥
        prompts: 提示文本列表
        temperature: 温度参数
        max_tokens: 最大token数
        retry: 重试次数
        delay: 重试延迟
        timeout: 超时时间
        api_url: API地址
        model_name: 模型名称
        max_concurrent: 最大并发数

    Returns:
        List[Tuple[str, Optional[str], Optional[str]]]: 并发调用结果
    """
    return asyncio.run(
        async_call_batch(
            api_key=api_key,
            prompts=prompts,
            temperature=temperature,
            max_tokens=max_tokens,
            retry=retry,
            delay=delay,
            timeout=timeout,
            api_url=api_url,
            model_name=model_name,
            max_concurrent=max_concurrent
        )
    )


if __name__ == "__main__":
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        raise EnvironmentError("请设置 GLM_API_KEY 环境变量")

    prompts = [
        "什么是人工智能？",
        "解释机器学习和深度学习的区别",
        "推荐一本AI入门书籍"
    ]

    logger.info(f"开始并发调用，共 {len(prompts)} 个请求，最大并发数: 3")
    
    results = call_concurrent(
        api_key=api_key,
        prompts=prompts,
        max_concurrent=3,
        timeout=30
    )

    for i, (prompt, response, error) in enumerate(results):
        print(f"\n=== 请求 {i+1} ===")
        print(f"问题: {prompt}")
        if error:
            print(f"错误: {error}")
        else:
            print(f"响应: {response[:100]}...")