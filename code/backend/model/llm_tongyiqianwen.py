import requests
from dotenv import load_dotenv
import os

load_dotenv()


class QwenClient:
    def __init__(self):
        self.api_key = os.getenv('tongyiqianwen')
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def ask(self, prompt):
        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"  # 必须包含的请求头
                },
                json={
                    "model": "qwen-plus",
                    "input": {"messages": [{
                        "role": "user",
                        "content": prompt
                    }]}
                },
                timeout=200  # 单位秒
            )
            response.raise_for_status()

            result = response.json()
            # 修正后的数据路径
            return result['output']['text']  # 正确访问路径

        except Exception as e:
            print(f"错误类型: {type(e).__name__}")
            print(f"错误详情: {str(e)}")
            if 'response' in locals():
                print(f"原始响应: {response.text}")
            return "请求失败，请检查API密钥和网络连接"


client = QwenClient()


def query(prompt: str) -> str:
    return client.ask(prompt)


if __name__ == "__main__":
    output = query("三国演义中的的诸葛亮、徐庶、程昱三人之间才能传导关系是什么，最终诸葛亮几倍于程昱？")
    print(output)
