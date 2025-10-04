import requests
import json
import time
import multiprocessing as mp
from typing import List, Tuple
from requests.exceptions import RequestException


def call_glm45_flash(api_key, prompt, temperature=0.7, max_tokens=1024, retry=2, delay=1):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "glm-4.5-flash",
        "messages": [{"role": "user", "content": prompt}],
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
                    return (prompt, result["choices"][0]["message"]["content"], None)
                else:
                    return prompt, None, f"API响应异常: {result}"

            elif response.status_code == 429:
                error_msg = f"429频率超限（第{current_retry + 1}次重试），响应：{response.text[:100]}"
                print(f"⚠️ {error_msg}")
                current_retry += 1
                if current_retry >= retry:
                    return prompt, None, f"请求失败: {error_msg}（已达最大重试次数）"

            else:
                return prompt, None, f"请求失败: {response.status_code} {response.reason}，响应：{response.text[:100]}"

        except RequestException as e:
            error_msg = f"网络错误（第{current_retry + 1}次重试）: {str(e)}"
            print(f"⚠️ {error_msg}")
            current_retry += 1
            if current_retry >= retry:
                return prompt, None, f"请求失败: {error_msg}（已达最大重试次数）"

        except json.JSONDecodeError:
            return prompt, None, f"JSON解析失败: 响应内容为「{response.text[:100]}」"

        except Exception as e:
            return prompt, None, f"未知错误: {str(e)}"

    return prompt, None, f"请求失败: 已重试{retry}次仍未成功"


def process_prompt(args):
    api_key, prompt, temperature, max_tokens = args
    return call_glm45_flash(api_key, prompt, temperature, max_tokens)


def batch_call_glm45_flash(
        api_key: str,
        prompts: List[str],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        max_workers: int = 2
) -> List[Tuple[str, str, str]]:
    args_list = [
        (api_key, prompt, temperature, max_tokens)
        for prompt in prompts
    ]

    max_workers = min(max_workers, 2, len(prompts))
    print(f"📌 已设置并发进程数：{max_workers}（避免频率超限）")

    with mp.Pool(processes=max_workers) as pool:
        results = pool.map(process_prompt, args_list)

    return results


if __name__ == "__main__":
    API_KEY = "ec16e21437744263b28f8a7243c5e9e2.vZX9qa3hxo0vzwUw"

    if API_KEY is None:
        print("❌ API密钥格式错误！正确格式：sk-开头 + 32位字符")
        print("获取地址：https://open.bigmodel.cn/ → 控制台 → API密钥")
        exit()

    test_prompts = [
        "请介绍一下GLM-4.5-Flash模型的主要特点",
        "用三句话总结人工智能的发展趋势",
        "解释什么是机器学习",
        "列举5种常见的编程语言及其特点"
    ]

    print(f"\n开始批量调用GLM-4.5-Flash模型，共{len(test_prompts)}个请求...\n")
    results = batch_call_glm45_flash(
        api_key=API_KEY,
        prompts=test_prompts,
        temperature=0.6,
        max_tokens=512,
        max_workers=2
    )

    for i, (prompt, response, error) in enumerate(results, 1):
        print(f"===== 请求 {i} =====")
        print(f"提示词: {prompt}")
        if error:
            print(f"❌ 错误: {error}")
        else:
            print(f"✅ 响应: \n{response}")
        print("\n" + "-" * 80 + "\n")