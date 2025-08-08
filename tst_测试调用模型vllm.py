import time
import requests

headers = {"Content-Type": "application/json"}
def call_llm(messages, enable_thinking=False, n=1, max_tokens=100,temperature=0.7):
    """同步版本的LLM调用"""
    payload = {
        "messages": messages,
        "temperature": temperature,
        "top_p": 0.8,
        "top_k": 20,
        "n": n,
        "seed": 12345,
        "max_tokens": max_tokens,
        "presence_penalty": 1.5,
        "chat_template_kwargs": {"enable_thinking": enable_thinking}
    }
    response = requests.post("http://10.1.188.13:8000/v1/chat/completions", headers=headers, json=payload)
    result = response.json()
    return result

if __name__ == '__main__':
    # 同步调用示例
    print("同步调用:")
    since = time.time()
    messages = [
        {"role": "user", "content": "你好"}
    ]
    result = call_llm(messages)
    print(result)
    print(time.time()-since)