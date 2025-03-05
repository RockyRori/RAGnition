import os
import requests

class QwenClient:
    def __init__(self, api_key: str):
        self.api_key = api_key  #!!!!! 需替换为你的API密钥（建议从环境变量读取）
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"  #!!!!! 确认API地址是否最新
    
    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",  #!!!!! 认证方式若变化需修改
            "Content-Type": "application/json"
        }
        data = {
            "model": "qwen-plus",  #!!!!! 可改为其他模型如 qwen-turbo
            "input": {"messages": [{"role": "user", "content": prompt}]}
        }

        for _ in range(3):  #!!!!! 重试次数可调整
            try:
                resp = requests.post(
                    self.url,
                    json=data,
                    headers=headers,
                    timeout=10  #!!!!! 网络环境差时可增大超时时间
                )
                resp.raise_for_status()
                #!!!!! 下方解析路径需与API返回结构一致
                return resp.json()["output"]["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"Error: {str(e)}")
        return ""

# 使用示例 ======================================
if __name__ == "__main__":
    #!!!!! 以下两种方式二选一：
    # 方式1：直接写死密钥（不推荐）
    # qwen = QwenClient("your-api-key-here") 
    
    # 方式2：从环境变量读取（推荐！）
    qwen = QwenClient(os.getenv("QWEN_API_KEY"))  #!!!!! 需提前设置环境变量
    
    print(qwen.generate("如何学习深度学习？"))