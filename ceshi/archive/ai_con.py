import requests
import json
import time
import os
from typing import Tuple, Optional
from requests.exceptions import RequestException, HTTPError


def call_glm45_flash(
    api_key: str,
    in_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    retry: int = 2,
    delay: float = 1,
    timeout: int = 30
) -> Tuple[str, Optional[str], Optional[str]]:
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "glm-4.5-flash",
        "messages": [{"role": "user", "content": in_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    current_retry = 0
    while current_retry < retry:
        try:
            if current_retry > 0:
                sleep_time = delay * (2 ** (current_retry - 1))
                print(f"⏳ 等待 {sleep_time:.1f} 秒后重试...")
                time.sleep(sleep_time)

            response = requests.post(url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()

            response_text = response.text.strip()
            if not response_text:
                raise ValueError("API返回空内容")

            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return in_prompt, result["choices"][0]["message"]["content"], None
            else:
                return in_prompt, None, f"API响应异常: {result}"

        except HTTPError as e:
            if response.status_code == 429:
                error_msg = f"429频率超限（第{current_retry + 1}次重试）"
                resp_text = response.text[:100] if response.text else ""
                print(f"⚠️ {error_msg}，响应：{resp_text}")
                current_retry += 1
                if current_retry >= retry:
                    return in_prompt, None, f"请求失败: {error_msg}（已达最大重试次数）"
            else:
                resp_text = response.text[:100] if response.text else ""
                return in_prompt, None, f"HTTP错误: {response.status_code} {response.reason}，响应：{resp_text}"

        except RequestException as e:
            error_msg = f"网络错误（第{current_retry + 1}次重试）: {str(e)}"
            print(f"⚠️ {error_msg}")
            current_retry += 1
            if current_retry >= retry:
                return in_prompt, None, f"请求失败: {error_msg}（已达最大重试次数）"

        except json.JSONDecodeError as e:
            return in_prompt, None, f"JSON解析错误: {str(e)}"

        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            return in_prompt, None, f"未知错误: {str(e)}"

    return in_prompt, None, f"请求失败: 已重试{retry}次仍未成功"


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    API_KEY = os.getenv("GLM_API_KEY")
    if not API_KEY:
        raise EnvironmentError("请设置 GLM_API_KEY 环境变量，或在 .env 文件中配置")

    prompt = input("请输入问题：")
    _, result, error = call_glm45_flash(API_KEY, prompt)
    if error:
        print(f"❌ 错误: {error}")
    else:
        print(f"✅ 回复: {result}")
