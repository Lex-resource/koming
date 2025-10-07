import requests
import json
import time
from requests.exceptions import RequestException


def call_glm45_flash(api_key, in_prompt, temperature=0.7, max_tokens=1024, retry=2, delay=1):
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
            time.sleep(delay * (2 ** current_retry))

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                response_text = response.text.strip()
                if not response_text:
                    raise ValueError("API返回空内容")
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return in_prompt, result["choices"][0]["message"]["content"], None
                else:
                    return in_prompt, None, f"API响应异常: {result}"

            elif response.status_code == 429:
                error_msg = f"429频率超限（第{current_retry + 1}次重试），响应：{response.text[:100]}"
                print(f"⚠️ {error_msg}")
                current_retry += 1
                if current_retry >= retry:
                    return in_prompt, None, f"请求失败: {error_msg}（已达最大重试次数）"

            else:
                return in_prompt, None, f"请求失败: {response.status_code} {response.reason}，响应：{response.text[:100]}"

        except RequestException as e:
            error_msg = f"网络错误（第{current_retry + 1}次重试）: {str(e)}"
            print(f"⚠️ {error_msg}")
            current_retry += 1
            if current_retry >= retry:
                return in_prompt, None, f"请求失败: {error_msg}（已达最大重试次数）"

        except Exception as e:
            return in_prompt, None, f"未知错误: {str(e)}"

    return in_prompt, None, f"请求失败: 已重试{retry}次仍未成功"


if __name__ == "__main__":
    API_KEY = "ec16e21437744263b28f8a7243c5e9e2.vZX9qa3hxo0vzwUw"
    prompt=input()
    print(call_glm45_flash(API_KEY, prompt)[1])